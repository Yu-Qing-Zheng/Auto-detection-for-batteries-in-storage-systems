from settings import model_path, model_file, SigmaX0, SigmaV, SigmaW, deltat
from soc.iterEKF import iterEKF
from soc.initEKF import initEKF
from energy.current_parameter import current_parameter
import scipy.io as scio
import numpy as np
import pandas as pd

def runEKF(df):
    matfile = model_path+model_file
    model = scio.loadmat(matfile)['model']
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values(by='time', ascending=True)
    df = df.reset_index(drop=True)
    df['time'] = df.index.values*deltat
    temperature = df['Temperature'].values
    current = df['Current'].values
    voltage = df['Voltage'].values
    sochat = np.array([])
    socbound = np.array([])
    # sochat = np.zeros(np.size(soc))
    # socbound = np.zeros(np.size(soc))
    ekfData = initEKF(voltage[0], temperature[0], np.diag(SigmaX0), SigmaV, SigmaW, model)
    sochat0 = ekfData.xhat[ekfData.zkInd, 0]
    socbound0 = 3*np.sqrt(ekfData.SigmaX[ekfData.zkInd,ekfData.zkInd])
    sochat = np.append(sochat, sochat0)
    socbound = np.append(socbound, socbound0)
    for i in range(1, df.shape[0]):
        vk = voltage[i]
        ik = current[i]
        Tk = temperature[i]
        ekfData = iterEKF(vk,ik,Tk,deltat,ekfData)
        sochatk = ekfData.xhat[ekfData.zkInd, 0]
        socboundk = 3*np.sqrt(ekfData.SigmaX[ekfData.zkInd,ekfData.zkInd])
        sochat = np.append(sochat, sochatk)
        socbound = np.append(socbound, socboundk)

    df['SOC'] = sochat
    df['SOCBound'] = socbound
    return df