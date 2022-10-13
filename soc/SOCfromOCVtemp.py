import numpy as np
import math

def SOCfromOCVtemp(ocv, temp, model):
    ocvcol = np.array([ocv]).reshape(1,)
    tempcol = np.array([temp]).reshape(1,)
    OCV = model['OCV'][0,0][0]
    SOC0 = model['SOC0'][0,0][0]
    SOCrel = model['SOCrel'][0,0][0]
    if len(tempcol) == 1:
        tempcol = tempcol[0]*np.ones(ocvcol.shape)
    diffOCV = OCV[1]-OCV[0]
    soc = np.zeros(ocvcol.shape)
    I1 = np.where(ocvcol<=OCV[0])
    I2 = np.where(ocvcol>=OCV[-1])
    I3 = np.where((ocvcol>OCV[0])&(ocvcol<OCV[-1]))
    I6 = np.where(np.isnan(ocvcol))
    if len(I1[0]) > 0:
        dz = (SOC0[1] + SOCrel[1]*tempcol) - (SOC0[0] + SOCrel[0]*temp)
        soc[I1] = (ocvcol[I1] - OCV[0])*dz[I1]/diffOCV + SOC0[0] + tempcol[I1]*SOCrel[0]
    if len(I2[0]) > 0:
        dz = (SOC0[-1] + SOCrel[-1]*tempcol) - (SOC0[-2] + SOCrel[-2]*temp)
        soc[I2] = (ocvcol[I2] - OCV[-1])*dz[I2]/diffOCV + SOC0[-1] + tempcol[I2]*SOCrel[-1]

    I4 = (ocvcol[I3] - OCV[0])/diffOCV-1
    if len(I4) > 0:
        I5 = math.floor(I4)
        I45 = I4 - I5
        omI45 = 1-I45
        soc[I3] = SOC0[I5+1]*omI45 + SOC0[I5+2]*I45
        soc[I3] = soc[I3] + tempcol[I3]*(SOCrel[I5+1]*omI45 + SOCrel[I5+2]*I45)
    soc[I6] = 0
    return soc