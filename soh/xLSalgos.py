import numpy as np 
import scipy.special as scis
import scipy.optimize as scio
import warnings
warnings.filterwarnings('ignore')

def xLSalgos(measX, measY, SigmaX, SigmaY, gamma, Qnom):
    K = np.sqrt(SigmaX[0]/SigmaY[0])
    Qhat = np.zeros((len(measX),4))
    SigmaQ = np.zeros((len(measX),4))
    Fit = np.zeros((len(measX),4))
    c1 = 0
    c2 = 0
    c3 = 0
    c4 = 0
    c5 = 0
    c6 = 0
    C1 = 0
    C2 = 0
    C3 = 0
    C4 = 0
    C5 = 0
    C6 = 0

    if Qnom == 0:
        c1 = 1/SigmaY[0]
        c2 = Qnom/SigmaY[0]
        c3 = Qnom**2/SigmaY[0]
        c4 = 1/SigmaY[0]
        c5 = Qnom/SigmaY[0]
        c6 = Qnom**2/SigmaY[0]
        C1 = 1/(K**2*SigmaY[0])
        C2 = K*Qnom/(K**2*SigmaY[0])
        C3 = K**2*Qnom**2/(K**2*SigmaY[0])
        C4 = 1/SigmaX[0]
        C5 = K*Qnom/SigmaX[0]
        C6 = K**2*Qnom**2/SigmaX[0]

    for iter in range(0, len(measX)):
        # Compute some variables used for the recursive methods
        c1 = gamma*c1 + measX[iter]**2/SigmaY[iter]
        c2 = gamma*c2 + measX[iter]*measY[iter]/SigmaY[iter]
        c3 = gamma*c3 + measY[iter]**2/SigmaY[iter]
        c4 = gamma*c4 + measX[iter]**2/SigmaX[iter]
        c5 = gamma*c5 + measX[iter]*measY[iter]/SigmaX[iter]
        c6 = gamma*c6 + measY[iter]**2/SigmaX[iter]

        C1 = gamma*C1 + measX[iter]**2/(K**2*SigmaY[iter])
        C2 = gamma*C2 + K*measX[iter]*measY[iter]/(K**2*SigmaY[iter])
        C3 = gamma*C3 + K**2*measY[iter]**2/(K**2*SigmaY[iter])
        C4 = gamma*C4 + measX[iter]**2/SigmaX[iter]
        C5 = gamma*C5 + K*measX[iter]*measY[iter]/SigmaX[iter]
        C6 = gamma*C6 + K**2*measY[iter]**2/SigmaX[iter]

        # Method 1: WLS
        #print('---Method 1---')
        Q = c2/c1
        Qhat[iter, 0] = Q
        H = 2*c1
        SigmaQ[iter, 0] = 2/H
        J = Q**2*c1 - 2*Q*c2 + c3
        Fit[iter, 0] = scis.gammaincc(((iter+1)-1)/2, J/2)

        # Method 2: WTLS -- not recursive -- implementation 2
        #print('---Method 2---')
        x = measX[0:iter+1]
        y = measY[0:iter+1]
        sx = np.sqrt(SigmaX[0:iter+1])
        sy = np.sqrt(SigmaY[0:iter+1])
        g = np.flipud((gamma**(np.arange(0, iter+1, 1))))
        Q = scio.fmin(lambda q: np.sum(g*(y-q*x)**2/(sx**2*q**2+sy**2)), Qhat[iter, 1], disp=False)
        Qhat[iter, 1] = Q
        H = 2*np.sum(g*((sy**4*x**2+sx**4*(3*Q**2*y**2-2*Q**3*x*y) - \
            sx**2*sy**2*(3*Q**2*x**2-6*Q*x*y+y**2))/((Q**2*sx**2+sy**2)**3)))
        SigmaQ[iter, 1] = 2/H
        J = np.sum(g*(y-Q*x)**2/(sx**2*Q**2+sy**2))
        Fit[iter, 1] = scis.gammaincc((2*(iter+1)-1)/2, J/2)

        # Method 3: RTLS
        #print('---Method 3---')
        Q = (-c1+K**2*c3+np.sqrt((c1-K**2*c3)**2+4*K**2*c2**2))/(2*K**2*c2)
        Qhat[iter, 2] = Q
        H = ((-4*K**4*c2)*Q**3+6*K**4*c3*Q**2+(-6*c1+12*c2)*K**2*Q+2*(c1-K**2*c3))/(Q**2*K**2+1)**3
        SigmaQ[iter, 2] = 2/H
        J = (Q**2*c1 -2*Q*c2 + c3)/(Q**2*K**2+1)
        Fit[iter, 2] = scis.gammaincc((2*(iter+1)-1)/2, J/2)

        # Method 4b: AWTLS with pre-scaling
        #print('---Method 4b---')
        r = np.roots([C5,(-C1+2*C4-C6),(3*C2-3*C5),(C1-2*C3+C6),-C2])
        r = [r[i] for i in range(0, len(r)) if r[i]==np.conj(r[i])] # discard complex-conjugate roots
        r = [i for i in r if i>0] # discard negative roots
        r = [i.real for i in r]
        r = np.array(r)
        if len(r) <= 0:
            Q = np.nan
            H = np.nan
            continue
        Jr = ((1/(r**2+1)**2)*(r**4*C4-2*C5*r**3+(C1+C6)*r**2-2*C2*r+C3))#.T
        Jr = np.array(Jr)
        J = np.min(Jr)
        Q = [r[i] for i in range(0, len(Jr)) if Jr[i]==J] # Q = r[Jr==J] # keep Q that minimizes cost function
        Q = np.array(Q)
        H = (2/(Q**2+1)**4)*(-2*C5*Q**5+(3*C1-6*C4+3*C6)*Q**4+(-12*C2+16*C5)*Q**3 \
            +(-8*C1+10*C3+6*C4-8*C6)*Q**2+(12*C2-6*C5)*Q+(C1-2*C3+C6))
        Qhat[iter, 3] = Q/K
        SigmaQ[iter, 3] = 2/H/K**2
        Fit[iter, 3] = scis.gammaincc((2*(iter+1)-1)/2, J/2)

    Fit = Fit.real
    return Qhat, SigmaQ, Fit
