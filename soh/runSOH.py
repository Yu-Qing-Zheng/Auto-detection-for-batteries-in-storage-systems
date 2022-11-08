import pandas as pd
import numpy as np
import scipy.io as scio
from soh.xLSalgos import xLSalgos
from soc.getParamESC import getParamESC
import importlib

def runSOH(df):
    settings = importlib.import_module('settings')
    matfile = settings.model_path+settings.model_file
    model = scio.loadmat(matfile)['model']
    curr = df['Current'].values
    temp = df['Temperature'].values
    # soc = df['SOC'].values
    diff_soc = df['SOC'].diff().values
    df['time'] = pd.to_datetime(df['time'])
    dt = settings.deltat/3600
    eta = np.zeros(np.size(curr))
    Q = np.zeros(np.size(curr))
    for i in range(0, len(curr)):
        Q[i] = getParamESC('QParam', temp[i], model)
        if curr[i] < 0:
            eta[i] = getParamESC('etaParam', temp[i], model)
        else:
            eta[i] = 1
    curr *= eta
    input_y = -(dt*eta*curr)[:-1]
    input_x = diff_soc[1:]
    maxI = np.max(np.abs(curr))
    if maxI < 10:
        maxI = 70
    binsize = 2*maxI/settings.precisionI
    n = input_x.shape[0]
    rn1 = np.ones((n), dtype=float)
    theCase = 1
    if theCase == 1:
        rn2 = rn1
        sy = binsize*np.sqrt(settings.m/12)/3600*rn2
    # socnoise = np.sqrt(2)*0.03
    sigma_soc = df['SOCBound'].values/3
    socnoise = np.zeros(np.size(input_x))# df['SOCBound'].values[1:]
    for i in range(1, df.shape[0]):
        socnoise[i-1] = np.sqrt(sigma_soc[i-1]**2 + sigma_soc[i]**2)
    sx = socnoise*rn1
    Qnom = np.mean(Q[np.where(Q>0)])
    collection = xLSalgos(input_x, input_y, sx**2, sy**2, settings.gamma, Qnom)
    Q_hat = collection[0]
    Q_hat = Q_hat[:, settings.id_awtls]
    SigmaQ = collection[1]
    SigmaQ = SigmaQ[:, settings.id_awtls]
    df['SOH'] = np.append(0, Q_hat)
    df['SOHBound'] = 3*np.sqrt(np.append(0, SigmaQ))
    return df