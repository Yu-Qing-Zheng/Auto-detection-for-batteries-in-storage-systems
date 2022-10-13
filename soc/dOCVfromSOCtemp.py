import numpy as np
import math

def dOCVfromSOCtemp(soc,temp,model):
    soccol = np.array([soc]).reshape(1,)
    tempcol = np.array([temp]).reshape(1,)
    SOC = model['SOC'][0,0][0]
    dOCV0 = model['dOCV0'][0,0][0]
    dOCVrel = model['dOCVrel'][0,0][0]
    diffSOC = SOC[1]-SOC[0]
    docv = np.zeros(soccol.shape)
    I1 = np.where(soccol<=SOC[0])
    I2 = np.where(soccol>=SOC[-1])
    I3 = np.where((soccol>SOC[0])&(soccol<SOC[-1]))
    I6 = np.where(np.isnan(soccol))
    if len(tempcol) == 1:
        tempcol = tempcol[0]*np.ones(soccol.shape)
    if len(I1[0]) > 0:
        dv = (dOCV0[1] + dOCVrel[1]*tempcol) - (dOCV0[0] + dOCVrel[0]*temp)
        docv[I1] = (soccol[I1] - SOC[0])*dv[I1]/diffSOC + dOCV0[0] + tempcol[I1]*dOCVrel[0]
    if len(I2[0]) > 0:
        dv = (dOCV0[-1] + dOCVrel[-1]*tempcol) - (dOCV0[-2] + dOCVrel[-2]*temp)
        docv[I2] = (soccol[I2] - SOC[-1])*dv[I2]/diffSOC + dOCV0[-1] + tempcol[I2]*dOCVrel[-1]
    
    I4 = (soccol[I3] - SOC[0])/diffSOC-1
    if len(I4) > 0:
        I5 = math.floor(I4)
        I45 = I4 - I5
        omI45 = 1-I45
        docv[I3] = dOCV0[I5+1]*omI45/dOCV0[I5+1] + dOCV0[I5+2]*I45
        docv[I3] = docv[I3] + tempcol[I3]*(dOCVrel[I5+1]*omI45 + dOCVrel[I5+2]*I45)
    docv[I6] = 0
    return docv