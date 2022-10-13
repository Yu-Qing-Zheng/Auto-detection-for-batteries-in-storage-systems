% runEKF: Runs an extended Kalman filter for saved E2 dynamic data and 
% an E2 cell model.
%
% Copyright (c) 2016 by Gregory L. Plett of 
% University of Colorado Colorado Springs (UCCS). 
%
% This work is licensed under a Creative Commons 
% Attribution-NonCommercial-ShareAlike 4.0 Intl. License, v. 1.0
%
% It is provided "as is", without express or implied warranty, for 
% educational and informational purposes only.
%
% This file is provided as a supplement to: Plett, Gregory L., "Battery
% Management Systems, Volume II, Equivalent-Circuit Methods," Artech House, 
% 2015.

% % % Load model file corresponding to a cell of this type
% % load E2model
% % 
% % % Load cell-test data to be used for this batch experiment
% % % Contains variable "DYNData" of which the field "script1" is of 
% % % interest. This has sub-fields time, current, voltage, soc.
% %  load('E2_DYN_35_P25'); T = 25;
% % % load('E2_DYN_15_P05'); T = 5;
% % 
% % time    = DYNData.script1.time(:);   deltat = time(2)-time(1);
% % time    = time-time(1); % start time at 0
% % current = DYNData.script1.current(:); % discharge > 0; charge < 0.
% % voltage = DYNData.script1.voltage(:);
% % soc     = DYNData.script1.soc(:);
% % 
% % % Reserve storage for computed results, for plotting
% % sochat = zeros(size(soc));
% % socbound = zeros(size(soc));
modelfile = './280Ahmodel.mat'
load(modelfile);
deltat = 60;

%        filename = ['../datapick/batteries_series/1month/', ...
%            num2str(i), '_', num2str(j), '.csv'];
plc_id = '32';
% filename = ['../train_set/SOC/input_',plc_id,'.csv'];
filename = ['./2_9.csv'];
raw1bat = readtable(filename);
rawDate = raw1bat(:,2);
Date = table2array(rawDate);
%         Date = char(Date);
%         date = strings(length(Date(:,1)), length(Date(1,:)));
%         for k = 1:length(Date(:,1)),
%             date(k) = append(Date(i,:));
%         end

%        rawTemp = raw1bat(:,5);
%        Temp = table2array(rawTemp);
rawTime = raw1bat(:,7);
rawTime = table2array(rawTime)'; rawTime = rawTime(1:end);
rawV = raw1bat(:, 4);
rawV = table2array(rawV)'; rawV = rawV(1:end);
rawI = raw1bat(:, 5);
rawT = raw1bat(:, 6);
rawI = table2array(rawI)'; rawI = rawI(1:end);
rawT = table2array(rawT)'; rawT = rawT(1:end);
t1 = rawTime(1)/deltat; t2 = rawTime(end)/deltat;
V = rawV; I = rawI/10; T = rawT;
%V = interp1(rawTime, rawV, t1:t2, 'linear');
%I = interp1(rawTime, rawI, t1:t2, 'linear');
time = (t1:t2)*deltat;
V = V(:); I = I(:); T = T(:); Date = Date(:);
% Covariance values
SigmaX0 = diag([1e-6 1e-8 2e-4]); % uncertainty of initial state
SigmaV = 2e-1; % Uncertainty of voltage sensor, output equation
SigmaW = 2e-1; % Uncertainty of current sensor, state equation
disp(SigmaV)
ekfData = initEKF(V(1),T(1),SigmaX0,SigmaV,SigmaW,model);
sochat = zeros(size(V));
socbound = zeros(size(V));
% Create ekfData structure and initialize variables using first
% voltage measurement and first temperature measurement
% % ekfData = initEKF(voltage(1),T,SigmaX0,SigmaV,SigmaW,model);

% Now, enter loop for remainder of time, where we update the SPKF
% once per sample interval
hwait = waitbar(0,'Computing...'); 
for k = 1:length(V),
  vk = V(k); % "measure" voltage
  ik = I(k); % "measure" current
  Tk = T(k);          % "measure" temperature
  
  % Update SOC (and other model states)
  [sochat(k),socbound(k),ekfData] = iterEKF(vk,ik,Tk,deltat,ekfData);
  % update waitbar periodically, but not too often (slow procedure)
  if mod(k,1000)==0,
    waitbar(k/length(I),hwait);
  end;
end
close(hwait);
  
% Plot estimate of SOC
figure(1); clf; plot(time/60,100*soc,'k',time/60,100*sochat,'m'); hold on
plot([time/60; NaN; time/60],[100*(sochat+socbound); NaN; 100*(sochat-socbound)],'m');
title('SOC estimation using EKF');
xlabel('Time (min)'); ylabel('SOC (%)');
legend('Truth','Estimate','Bounds'); ylim([0 120]); grid on

% Display RMS estimation error to command window
fprintf('RMS SOC estimation error = %g%%\n',sqrt(mean((100*(soc-sochat)).^2)));

% Plot estimation error and bounds
figure(2); clf; plot(time/60,100*(soc-sochat),'m'); hold on
h = plot([time/60; NaN; time/60],[100*socbound; NaN; -100*socbound],'m');
title('SOC estimation errors using EKF');
xlabel('Time (min)'); ylabel('SOC error (%)'); ylim([-6 6]); 
set(gca,'ytick',-6:2:6);
legend('Error','Bounds','location','northwest'); 
grid on

% Display bounds errors to command window
ind = find(abs(soc-sochat)>socbound);
fprintf('Percent of time error outside bounds = %g%%\n',...
        length(ind)/length(soc)*100);