from soh.xLSalgos import xLSalgos
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import MO, TU, WE, TH, FR, SA, SU
from matplotlib.dates import AutoDateLocator, ConciseDateFormatter

filename = '../Abnormal_diagnose/PLC43异常/soh_input/3_8_1.csv' 
filename = './data/3_12.csv'
df_raw = pd.read_csv(filename)
df_raw = df_raw[(df_raw['Date']>='2022-03-15 00:00')&(df_raw['Date']<'2022-03-16 00:00')]
df_raw['Date'] = pd.to_datetime(df_raw['Date'])
current = df_raw['Current'].values
soc = df_raw['SOC'].values
dt = 1/60
eta = 1
input_y = -dt*eta*current[:-1]
input_x = df_raw['SOC'].diff().values[1:]
maxI = np.max(np.abs(current))
precisionI = 2**10
m = 300
binsize = 2*maxI/precisionI
n = input_x.shape[0]
rn1 = np.ones((n), dtype=float)
theCase = 1
if theCase == 1:
    rn2 = rn1
    sy = binsize*np.sqrt(m/12)/3600*rn2
Qnom = 295
slope = 0
socnoise = np.sqrt(2)*0.03
sx = socnoise*rn1
gamma = 1#-10**(-4)
Q_hat = xLSalgos(input_x, input_y, sx**2, sy**2, gamma, Qnom)[0]
Sigma_Q = xLSalgos(input_x, input_y, sx**2, sy**2, gamma, Qnom)[1]
Fit_ = xLSalgos(input_x, input_y, sx**2, sy**2, gamma, Qnom)[2]

fig, (ax1, ax2) = plt.subplots(2, 1, dpi = 600, sharex=True)
x = df_raw['Date'].values[1:]
y_Q1 = Q_hat[:, 0]
y_Q2 = Q_hat[:, 1]
y_Q3 = Q_hat[:, 2]
y_Q4 = Q_hat[:, 3]
y_S1 = np.sqrt(Sigma_Q[:, 0])
y_S2 = np.sqrt(Sigma_Q[:, 1])
y_S3 = np.sqrt(Sigma_Q[:, 2])
y_S4 = np.sqrt(Sigma_Q[:, 3])
ax1.plot(x, y_Q1, label = 'WLS', color = 'red')
ax1.plot(x, y_Q2, label = 'WTLS', color = 'blue')
ax1.plot(x, y_Q3, label = 'RTLS', color = 'green')
ax1.plot(x, y_Q4, label = 'AWLS', color = 'purple')
ax1.plot(x, y_Q1-y_S1, label = 'S1_WLS', color = 'red', ls ='--')
ax1.plot(x, y_Q2-y_S2, label = 'S1_WTLS', color = 'blue', ls = '--')
ax1.plot(x, y_Q3-y_S3, label = 'S1_RTLS', color = 'green', ls = '--')
ax1.plot(x, y_Q4-y_S4, label = 'S1_AWLS', color = 'purple', ls = '--')
ax1.plot(x, y_Q1+y_S1, label = 'S2_WLS', color = 'red', ls = '--')
ax1.plot(x, y_Q2+y_S2, label = 'S2_WTLS', color = 'blue', ls = '--')
ax1.plot(x, y_Q3+y_S3, label = 'S2_RTLS', color = 'green', ls = '--')
ax1.plot(x, y_Q4+y_S4, label = 'S2_AWLS', color = 'purple', ls = '--')
ax1.set_ylim(0,500)
ax1.set_ylabel('Qmax (Ah)')
#ax1.legend()
ax1.grid(color = 'k', ls = '-.', lw = 0.5)
ax1.set_title('SOH of 3-8 in PLC43')

y_F1 = Fit_[:, 0]
y_F2 = Fit_[:, 1]
y_F3 = Fit_[:, 2]
y_F4 = Fit_[:, 3]
ax2.plot(x, y_F1, label = 'WLS', color = 'red')
ax2.plot(x, y_F2, label = 'WTLS', color = 'blue')
ax2.plot(x, y_F3, label = 'RTLS', color = 'green')
ax2.plot(x, y_F4, label = 'AWLS', color = 'purple')
ax2.set_ylim(-0.1, 1.1)
ax2.set_ylabel('Fit Flag')
ax2.legend()
ax2.grid(color = 'k', ls = '-.', lw = 0.5)

locator = AutoDateLocator(minticks=4, maxticks=10)
ax2.xaxis.set_major_locator(locator)
ax2.xaxis.set_major_formatter(ConciseDateFormatter(locator))
ax2.set_xlabel('Time')
plt.savefig('./fig/try.png')
