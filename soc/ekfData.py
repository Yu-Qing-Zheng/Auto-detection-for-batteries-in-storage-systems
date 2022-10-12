class ekfData(object):
    def __init__(self, 
                 xhat, model,
                 irInd, hkInd, zkInd, 
                 SigmaX, SigmaV, SigmaW, Qbump, 
                 priorI, signIk, 
                 ):
        
        self.irInd = irInd
        self.hkInd = hkInd
        self.zkInd = zkInd

        self.SigmaX = SigmaX
        self.SigmaV = SigmaV
        self.SigmaW = SigmaW
        self.Qbump = Qbump

        self.priorI = priorI
        self.signIk = signIk

        self.model = model
        self.xhat = xhat