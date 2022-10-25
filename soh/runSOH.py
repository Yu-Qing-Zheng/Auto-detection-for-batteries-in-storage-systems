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
    precisionI = 2**10
    m = 300
    binsize = 2*maxI/precisionI
    n = input_x.shape[0]
    rn1 = np.ones((n), dtype=float)
    theCase = 1
    if theCase == 1:
        rn2 = rn1
        sy = binsize*np.sqrt(m/12)/3600*rn2
    socnoise = np.sqrt(2)*0.03
    sx = socnoise*rn1
    Qnom = np.mean(Q[np.where(Q>0)])
    gamma = 1#-10**(-4)
    collection = xLSalgos(input_x, input_y, sx**2, sy**2, gamma, Qnom)
    Q_hat = collection[0]
    Q_hat = Q_hat[:, settings.id_awtls]
    SigmaQ = collection[1]
    SigmaQ = SigmaQ[:, settings.id_awtls]
    df['SOH'] = np.append(np.nan, Q_hat)
    df['SOCBound'] = np.sqrt(np.append(np.nan, SigmaQ))
    return df