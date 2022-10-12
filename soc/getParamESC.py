from soc.getfield_mat import getfield_mat
import numpy as np
from scipy.interpolate import make_interp_spline

def getParamESC(paramName,temp,model):
    theFields = getfield_mat(model)
    match = paramName in theFields
    if not match:
        print('Parameter %s does not exist in model!' %paramName)
    else:
        fieldName = paramName
        #temp = np.array([temp]).reshape(1,)
        model_temps = model['temps'][0][0][0]
        if len(model_temps) == 1:
            if model_temps != temp:
                print('Model does not contain requested data at this temperature')
            theParam = model[fieldName][0][0][0]
            return theParam
        
        theParamData = model[fieldName][0][0]
        temp = max(min(temp,np.max(model_temps)),np.min(model_temps))
        ind = np.where(model_temps==temp)
        if len(ind) > 0:
            if theParamData.shape[0] == 1:
                theParam = theParamData[0][ind]
            else:
                theParam = theParamData[0][ind, :]
        else:
            print('here')
            theParam = make_interp_spline(model_temps, theParamData)(temp)
        return theParam