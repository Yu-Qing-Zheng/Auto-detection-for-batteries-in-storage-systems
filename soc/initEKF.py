from soc.ekfData import ekfData
from soc.SOCfromOCVtemp import SOCfromOCVtemp
from settings import numpoles
import numpy as np

def initEKF(v0, T0, SigmaX0, SigmaV, SigmaW, model):
    # initial state description
    ir0 = np.arange(0,numpoles)
    hk0 = 0
    SOC0 = SOCfromOCVtemp(v0, T0, model)[0].reshape(-1,1)
    # xhat = np.array([ir0, hk0, SOC0]).reshape(1, -1)
    xhat = np.append(ir0, hk0)
    xhat = np.matrix(np.append(xhat, SOC0).reshape(-1,1))
    irInd = list(range(0, numpoles))
    hkInd = np.max(irInd) + 1
    zkInd = hkInd+1
    Qbump = 5
    priorI = 0
    signIk = 0
    ekfData0 = ekfData(
                      xhat, model,
                      irInd, hkInd, zkInd, 
                      SigmaX0, SigmaV, SigmaW, Qbump, 
                      priorI, signIk, 
                      )
    return ekfData0

