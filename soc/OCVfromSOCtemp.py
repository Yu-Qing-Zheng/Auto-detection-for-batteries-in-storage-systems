import numpy as np
import math

def OCVfromSOCtemp(soc, temp, model):
    soccol = np.array([soc]).reshape(1,)
    tempcol = np.array([temp]).reshape(1,)
    SOC = model['SOC'][0,0][0]
    OCV0 = model['OCV0'][0,0][0]
    OCVrel = model['OCVrel'][0,0][0]
    if len(tempcol) == 1:
        tempcol = tempcol[0]*np.ones(soccol.shape)
    diffSOC = SOC[1]-SOC[0]
    ocv = np.zeros(soccol.shape)
    I1 = np.where(soccol<=SOC[0])
    I2 = np.where(soccol>=SOC[-1])
    I3 = np.where((soccol>SOC[0])&(soccol<SOC[-1]))
    I6 = np.where(np.isnan(soccol))
    if len(I1[0]) > 0:
        dv = (OCV0[1] + OCVrel[1]*tempcol) - (OCV0[0] + OCVrel[0]*temp)
        ocv[I1] = (soccol[I1] - SOC[0])*dv[I1]/diffSOC + OCV0[0] + tempcol[I1]*OCVrel[0]
    if len(I2[0]) > 0:
        dv = (OCV0[-1] + OCVrel[-1]*tempcol) - (OCV0[-2] + OCVrel[-2]*temp)
        ocv[I2] = (soccol[I2] - SOC[-1])*dv[I2]/diffSOC + OCV0[-1] + tempcol[I2]*OCVrel[-1]

    I4 = (soccol[I3] - SOC[0])/diffSOC-1
    if len(I4) > 0:
        I5 = math.floor(I4)
        I45 = I4 - I5
        omI45 = 1-I45
        ocv[I3] = OCV0[I5+1]*omI45 + OCVrel[I5+2]*I45
        ocv[I3] = ocv[I3] + tempcol[I3]*(OCVrel[I5+1]*omI45 + OCVrel[I5+2]*I45)
    ocv[I6] = 0
    return ocv