from soc.getfield_mat import getfield_mat
import numpy as np
from scipy.interpolate import make_interp_spline
import importlib
from settings import numpoles

def getParamESC(paramName,temp,model):
    settings = importlib.import_module('settings')
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
            theParam = model[fieldName][0][0]
            return theParam
        
        theParamData = model[fieldName][0][0]
        if theParamData.shape[0] == 1 and theParamData.shape[1] != len(model_temps):
            theParam = theParamData[0].reshape(-1,1)
            return theParam
    
        temp = max(min(temp,np.max(model_temps)),np.min(model_temps))
        ind = np.where(model_temps==temp)
        if len(ind[0]) > 0:
            ind = np.array(ind).reshape(1,)
            if paramName in ['RCParam', 'RParam']:
                if theParamData.shape[0] == 1:
                    theParam = theParamData[ind[0]].reshape(-1,1)
                else:
                    theParam = theParamData[ind[0],:].reshape(-1,1)
            else:
                if model_temps.shape[0] == theParamData.shape[1]:
                    if theParamData.shape[0] == 1:
                        theParam = np.array(theParamData[0, ind[0]]).reshape(-1,1)
                    else:
                        theParam = np.array(theParamData[:, ind[0]]).reshape(-1,1)
                if model_temps.shape[0] == theParamData.shape[0]:
                    if theParamData.shape[0] == 1:
                        theParam = theParamData[ind[0], :].reshape(1,-1)
                    else:
                        theParam = theParamData[ind[0], :].reshape(1,-1)
        else:
            if paramName in ['RCParam', 'RParam']:
                theParam = np.array([])
                for i in range(0, settings.numpoles):
                    theParam_i = make_interp_spline(model_temps, theParamData[:,i])(temp)
                    theParam = np.append(theParam, theParam_i)
            else:
                if model_temps.shape[0] == theParamData.shape[1]:
                    theParam = make_interp_spline(model_temps, theParamData[0])(temp)
                    theParam = np.array([theParam]).reshape(-1,1)
                else:
                    theParam = make_interp_spline(model_temps, theParamData)(temp).reshape(1,-1)
    return theParam
                