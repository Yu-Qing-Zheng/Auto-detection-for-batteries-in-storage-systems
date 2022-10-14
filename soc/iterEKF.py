from soc.getParamESC import getParamESC
from soc.dOCVfromSOCtemp import dOCVfromSOCtemp
from soc.OCVfromSOCtemp import OCVfromSOCtemp
import numpy as np
import importlib
# from settings import numpoles

def iterEKF(vk, ik, Tk, deltat, ekfData):
    settings = importlib.import_module('settings')
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
    signIk = ekfData.signIk
    
    # EKF Step 0: Compute Ahat[k-1], Bhat[k-1]
    nx = xhat.shape[0]
    # Ahat
    Ahat = np.matrix(np.zeros((nx, nx)))
    Ahat[[irInd], [irInd]] = RC.reshape(1, -1)
    Ahat[zkInd, zkInd] = 1
    Ah = np.exp(-abs(I*G*deltat/(3600*Q)))
    Ahat[hkInd, hkInd] = Ah
    # Ahat = np.diag(np.append(RC, [0, 0]))
    # row, col = np.diag_indices_from(Ahat)
    # Ahat[row,col] = RC
    # print(Ahat)

    # Bhat
    Bhat = np.matrix(np.zeros((nx, 1)))
    Bhat[zkInd, 0] = -deltat/(3600*Q)
    Bhat[[irInd], 0] = (1-RC).reshape(1, -1)
    B = np.c_[Bhat, 0*Bhat]
    Bhat[hkInd, 0] = -abs(G*deltat/(3600*Q))*Ah*(1+np.sign(I)*xhat[hkInd])
    B[hkInd,1] = Ah-1
    # Bhat = np.matrix(np.zeros((nx, 2)))
    # Bhat[zkInd, 0] = -deltat/(3600*Q)
    # Bhat[[irInd], 0] = (1-RC).reshape(1, -1)
    # B = [Bhat, 0*Bhat]
    # print(B)
    # print(Bhat)

    # Step 1a: State estimate time update
    xhat = np.matrix(xhat.reshape(-1,1))
    xhat = Ahat*xhat + B*np.matrix(np.array([I,np.sign(I)]).reshape(-1,1)) 
    xhat[hkInd, 0] = min(1,max(-1, xhat[hkInd, 0]))
    xhat[zkInd, 0] = min(1.05,max(-0.05,xhat[zkInd, 0]))

    # Step 1b: Error covariance time update
    SigmaX = Ahat*SigmaX*Ahat.T + Bhat*SigmaW*Bhat.T

    # Step 1c: Output estimate
    yhat = OCVfromSOCtemp(xhat[zkInd, 0], Tk, model) + M0*signIk + \
         M*xhat[hkInd, 0] - np.matrix(R.reshape(-1,settings.numpoles))*xhat[irInd] - R0*ik
    
    # Step 2a: Estimator gain matrix
    Chat = np.matrix(np.zeros([1, nx]))
    Chat[0, zkInd] = dOCVfromSOCtemp(xhat[zkInd, 0], Tk, model)
    Chat[0, hkInd] = M
    Chat[0, [irInd]] = -1*R.reshape(1, -1)
    Dhat = np.matrix(np.zeros([1, 2]))
    Dhat[0, 0] = -R0
    Dhat[0, 1] = M0
    SigmaY = Chat*SigmaX*Chat.T + SigmaV# Dhat*SigmaV*Dhat.T
    L = SigmaX*Chat.T/SigmaY
    
    # Step 2b: State estimate measurement update
    r = vk - yhat
    if r**2 > 100*SigmaY:
        L[:,0] = 0.0
    xhat = xhat + L*r
    xhat[hkInd, 0] = min(1,max(-1,xhat[hkInd, 0]))
    xhat[zkInd, 0] = min(1.05,max(-0.05,xhat[zkInd, 0]))

    # % Step 2c: Error covariance measurement update  
    SigmaX = SigmaX - L*SigmaY*L.T
    if r**2 > 4*SigmaY:
        print('Bumping SigmaX')
        SigmaX[zkInd, zkInd] = SigmaX[zkInd, zkInd]*ekfData.Qbump
    temp, S, V = np.linalg.svd(SigmaX)
    S = np.diag(S)
    S_shape = S.shape
    V_shape = V.shape
    diff_shape_col = V_shape[1]-S_shape[0]
    if diff_shape_col > 0:
        add_S = np.matrix(np.zeros((S_shape[0], diff_shape_col)))
        S = np.c_[S, add_S]
    HH = V*S*V.T
    SigmaX = (SigmaX + SigmaX.T + HH + HH.T)/4
    
    ekfData.priorI = ik
    ekfData.SigmaX = SigmaX
    ekfData.xhat = xhat
    zk = xhat[zkInd, 0]
    zkbnd = 3*np.sqrt(SigmaX[zkInd,zkInd])
    return ekfData
    

if __name__ == '__main__':
    from soc.initEKF import initEKF
    import scipy.io as scio
    matfile = './soc/280Ahmodel1.mat'
    model = scio.loadmat(matfile)['model']
    # SigmaX0 = np.diag([1e-6, 1e-8, 2e-4])
    SigmaX0 = np.diag([1e-6, 1e-6, 1e-6, 1e-8, 2e-4])
    ekfData = initEKF(3.2, 25, SigmaX0, 1, 1, model)
    ekfData = iterEKF(3.2,-20, 25, 60, ekfData)
    print(ekfData.xhat)
