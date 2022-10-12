from soc.getParamESC import getParamESC
import numpy as np

def iterEKF(vk, ik, Tk, deltat, ekfData):
    model = ekfData.model
    Q  = getParamESC('QParam',Tk,model)
    G  = getParamESC('GParam',Tk,model)
    M  = getParamESC('MParam',Tk,model)
    M0 = getParamESC('M0Param',Tk,model)
    RC = np.exp(-deltat/abs(getParamESC('RCParam',Tk,model))).reshape(-1,1)
    R  = getParamESC('RParam',Tk,model).reshape(-1,1)
    R0 = getParamESC('R0Param',Tk,model)
    eta = getParamESC('etaParam',Tk,model)
    if ik < 0:
        ik = ik*eta

    I = ekfData.priorI
    SigmaX = ekfData.SigmaX
    SigmaV = ekfData.SigmaV
    SigmaW = ekfData.SigmaW
    xhat = ekfData.xhat
    irInd = ekfData.irInd
    hkInd = ekfData.hkInd
    zkInd = ekfData.zkInd
    if abs(ik) > Q/100:
        ekfData.signIk = np.sign(ik)
    
    nx = len(xhat)
    Ahat = np.matrix(np.zeros((nx, nx)))
    Bhat = np.matrix(np.zeros((nx, 1)))
    Ahat[irInd, irInd] = np.diag(RC[0][0])
