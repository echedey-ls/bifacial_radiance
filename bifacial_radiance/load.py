# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 08:38:45 2019

@author: cdeline, sayala

loadBFRresults.py - load bifacial_radiance results. Module to load and clean 
bifacial_radiance irradiance result files, csv format, usually stored in RadianceScene\results folder.
This functions are still in development

"""


def loadRadianceObj(savefile=None):
    '''
    Load the pickled radiance object for further use
    usage: (once you're in the correct local directory)
      demo = bifacial_radiance.loadRadianceObj(savefile)
    
    Parameters
    ----------
    savefile :   optional savefile.  Otherwise default to save.pickle
            
    '''
    import pickle
    
    if savefile is None:
        savefile = 'save.pickle'
    with open(savefile,'rb') as f:
        loadObj= pickle.load(f)
    
    print('Loaded file {}'.format(savefile))
    return loadObj


def read1Result(filetitle):
    '''
    read1Result(filetitle):   
    Read bifacial_radiance .csv result files
    
    PARAMETERS
    -----------
    filetitle: usually found in the results folder, must be a csv with the following headers:
        x	y	z	rearZ	mattype	rearMat	Wm2Front	Wm2Back	Back/FrontRatio

    Returns
    -------
    resultsDict: a panda dataframe with all of the info from the CSV. Columns headers are 
    resultsDict['x'], resultsDict['y'], resultsDict['z'], resultsDict['rearZ']
    resultsDict['mattype'], resultsDict['rearMat'], resultsDict['Wm2Front'], resultsDict['Wm2Back']
    resultsDict['BackFrontRatio'],
    '''
    import pandas as pd
    
    resultsDict={}
    
    x_all=[]; y_all=[]; z_all=[]; rearZ_all=[]
    mattype_all=[]; rearMat_all=[];
    Wm2Front_all=[]; Wm2Back_all=[]; BackFrontRatio_all=[]
 
    headeracquired= 0
    headererror = 0

    xloc=0
    yloc=1
    zloc=2
    zrearloc=3
    matloc=4
    matrearloc=5
    wm2frontloc=6
    wm2backloc=7
    backfrontratioloc=8
    
    with open(filetitle, "r") as filestream:
    
        for line in filestream:
            if headeracquired == 0:
                header = line.split(",")
                        
                if header[matrearloc] != 'rearMat': print ("Issue reading " + header [matrearloc]) ; headererror = 1

                # x	y	z	rearZ	mattype	rearMat	Wm2Front	Wm2Back	Back/FrontRatio
        
                headeracquired = 1
                
                if headererror == 1:
                    print "STOPPING File Read because of headers issue (expected data might not be where we think it is! Stop roll and check!"
                    continue
                
            else:
                
                if headererror == 1:
                    continue

                currentline=line.split(",")                    

                x_all.append(float(currentline[xloc]))
                y_all.append(float(currentline[yloc]))
                z_all.append(float(currentline[zloc]))
                rearZ_all.append(float(currentline[zrearloc]))
                mattype_all.append(currentline[matloc])
                rearMat_all.append(currentline[matrearloc])
                Wm2Front_all.append(float(currentline[wm2frontloc]))
                Wm2Back_all.append(float(currentline[wm2backloc]))
                BackFrontRatio_all.append(float(currentline[backfrontratioloc]))
                
    df = ({'x': x_all, 'y': y_all, 'z': z_all, 'rearZ': rearZ_all, 'mattype': mattype_all,
                 'rearMat': rearMat_all, 'Wm2Front': Wm2Front_all, 'Wm2Back': Wm2Back_all, 
                 'BackFrontRatio': BackFrontRatio_all})
    
    df = pd.DataFrame.from_records(df)
    
    resultsDict = df
    
    return resultsDict;            

def _loadTrackerDict(trackerdict, fileprefix=None):
    '''
    Load a trackerdict by reading in the \results\ directory.
   
    It will then save the Wm2Back, Wm2Front and backRatio by reading in all valid files in the
    \results\ directory.  Note: it will match any file ending in '_key.csv'
    
    Parameters
    --------------
    trackerdict:    You need to pass in a valid trackerdict with correct keys from RadianceObj.set1axis()
    fileprefix:     (None): optional parameter to specify the initial part of the savefile prior to '_key.csv'
    
    Returns
    -------------
    trackerdict:    dictionary with additional ['Wm2Back'], ['Wm2Front'], ['backRatio']
    totaldict:      totalized dictionary with ['Wm2Back'], ['Wm2Front']

    '''        
    import re, os
    import pandas as pd
    import numpy as np

    
    def _readResults(selectfile):
        ''' load in Wm2Front and Wm2Back, neglecting certain materials
        returns: tuple of np.array:  Wm2Front, Wm2Back
        '''
        temp = pd.read_csv('results\\'+selectfile)
        # check for 'sky' or 'tube' or 'pole' or 'ground in the front or back material and substitute NaN.
        matchers = ['sky','pole','tube','bar','ground', '3267', '1540']
        NaNindex = [i for i,s in enumerate(temp['mattype']) if any(xs in s for xs in matchers)]
        NaNindex2 = [i for i,s in enumerate(temp['rearMat']) if any(xs in s for xs in matchers)]
        #NaNindex += [i for i,s in enumerate(frontDict['mattype']) if any(xs in s for xs in matchers)]    
        for i in NaNindex:
            temp['Wm2Front'][i] = np.NAN 
        for i in NaNindex2:
            temp['Wm2Back'][i] = np.NAN

        return(np.array(temp['Wm2Front']), np.array(temp['Wm2Back']))
    # End _readResults subroutine
    
        
    # get list of filenames in \results\
    filelist = sorted(os.listdir('results'))
    
    print('Loading {} files'.format(filelist.__len__()))
    for key in sorted(trackerdict):
        if fileprefix is None:
            r = re.compile(".*_" + re.escape(key) + ".csv")
        else:   
            r = re.compile(fileprefix + re.escape(key) + ".csv")
        try:
            selectfile = filter(r.match,filelist)[0]
        except IndexError:
            continue
        
        (Wm2Front,Wm2Back) = _readResults(selectfile) #return numpy arrays
        try:
            Wm2FrontTotal += Wm2Front
            Wm2BackTotal += Wm2Back
        except NameError:
            Wm2FrontTotal = Wm2Front
            Wm2BackTotal = Wm2Back
        trackerdict[key]['Wm2Front'] = list(Wm2Front)
        trackerdict[key]['Wm2Back'] = list(Wm2Back)
        trackerdict[key]['backRatio'] = list(Wm2Back / Wm2Front)
        finalkey = key
    totaldict = {'Wm2Front':Wm2FrontTotal, 'Wm2Back':Wm2BackTotal}
    
    print('final key loaded: {}'.format(finalkey))
    return(trackerdict, totaldict)
    #end loadTrackerDict subroutine.  set demo.Wm2Front = totaldict.Wm2Front. demo.Wm2Back = totaldict.Wm2Back
    
    

def cleanResult(resultsDict, sensorsy, numpanels, Azimuth_ang):
    '''
    Load a trackerdict by reading in the \results\ directory.
   
    It will then save the Wm2Back, Wm2Front and backRatio by reading in all valid files in the
    \results\ directory.  Note: it will match any file ending in '_key.csv'
    
    Parameters
    --------------
    trackerdict:    You need to pass in a valid trackerdict with correct keys from RadianceObj.set1axis()
    fileprefix:     (None): optional parameter to specify the initial part of the savefile prior to '_key.csv'
    
    Returns
    -------------
    trackerdict:    dictionary with additional ['Wm2Back'], ['Wm2Front'], ['backRatio']
    totaldict:      totalized dictionary with ['Wm2Back'], ['Wm2Front']

    '''        
    import re, os
    import pandas as pd
    import numpy as np


    def _readResults(selectfile):
        ''' load in Wm2Front and Wm2Back, neglecting certain materials
        returns: tuple of np.array:  Wm2Front, Wm2Back
        '''
        temp = pd.read_csv('results\\'+selectfile)
        # check for 'sky' or 'tube' or 'pole' or 'ground in the front or back material and substitute NaN.
        # matchers 3267 and 1540 is to get rid of inner-sides of the module.
        matchers = ['sky','pole','tube','bar','ground', '3267', '1540']
        NaNindex = [i for i,s in enumerate(temp['mattype']) if any(xs in s for xs in matchers)]
        NaNindex2 = [i for i,s in enumerate(temp['rearMat']) if any(xs in s for xs in matchers)]
        #NaNindex += [i for i,s in enumerate(frontDict['mattype']) if any(xs in s for xs in matchers)]    
        for i in NaNindex:
            temp['Wm2Front'][i] = np.NAN 
        for i in NaNindex2:
            temp['Wm2Back'][i] = np.NAN

        return(np.array(temp['Wm2Front']), np.array(temp['Wm2Back']))
    # End _readResults subroutine

        
    # get list of filenames in \results\
    filelist = sorted(os.listdir('results'))
    
    print('Loading {} files'.format(filelist.__len__()))
    for key in sorted(trackerdict):
        if fileprefix is None:
            r = re.compile(".*_" + re.escape(key) + ".csv")
        else:   
            r = re.compile(fileprefix + re.escape(key) + ".csv")
        try:
            selectfile = filter(r.match,filelist)[0]
        except IndexError:
            continue
        
        (Wm2Front,Wm2Back) = _readResults(selectfile) #return numpy arrays
        try:
            Wm2FrontTotal += Wm2Front
            Wm2BackTotal += Wm2Back
        except NameError:
            Wm2FrontTotal = Wm2Front
            Wm2BackTotal = Wm2Back
        trackerdict[key]['Wm2Front'] = list(Wm2Front)
        trackerdict[key]['Wm2Back'] = list(Wm2Back)
        trackerdict[key]['backRatio'] = list(Wm2Back / Wm2Front)
        finalkey = key
    totaldict = {'Wm2Front':Wm2FrontTotal, 'Wm2Back':Wm2BackTotal}
    
    print('final key loaded: {}'.format(finalkey))
    return(trackerdict, totaldict)
    #end loadTrackerDict subroutine.  set demo.Wm2Front = totaldict.Wm2Front. demo.Wm2Back = totaldict.Wm2Back
        
        
def deepcleanResult(resultsDict, sensorsy, numpanels, Azimuth_ang, automatic=True):
    '''
    cleanResults(resultsDict, sensorsy, numpanels, Azimuth_ang) 
    cleans results read by read1Result for 1 UP and 2UP configurations.
    Aks user to select material of the module (usually the one with the most results) 
    and removes sky, ground, and other materials (side of module, for exmaple)
    
    2DO: add automatization of panel select.
    
    PARAMETERS
    -----------
    sensorsy     For the interpolation routine. Can be more than original sensory or same value.
    numpanels    1 or 2
    Azimuth_Ang   of the tracker for the results generated. So that it knows if sensors 
                   should be flipped or not. Particular crucial for 2 UP configurations.
    automatic      Automaticatlly detects module and ignores Ground, torque tube and sky values. If set to off, user gets queried about the right surfaces.
    
    Returns
    -------
    Frontresults, Backresults;     dataframe with only values of the material selected, 
                                   length is the number of sensors desired.

    '''
    import numpy as np
    from scipy.interpolate import interp1d
    
    fronttypes = resultsDict.groupby('mattype').count() 
    backtypes = resultsDict.groupby('rearMat').count()
    
    if numpanels == 2:

        if automatic == True:
            panBfrontmat = resultsDict[resultsDict['mattype'].str.contains('a0.PVmodule.6457')]
            panelB = panBfrontmat[panBfrontmat['rearMat'].str.contains('a0.PVmodule.2310')] # checks rear mat is also panel B only.

            panAfrontmat = resultsDict[resultsDict['mattype'].str.contains('a1.PVmodule.6457')]
            panelA = panAfrontmat[panAfrontmat['rearMat'].str.contains('a1.PVmodule.2310')]

        else: 
            print "Front type materials index and occurrences: "
            for i in range (0, len(fronttypes)):
                print i, " --> ", fronttypes['x'][i] , " :: ",  fronttypes.index[i]
            
            
            panBfront = int(raw_input("Panel a0 Front material "))  # Python 2
            panAfront = int(raw_input("Panel a1 Front material "))
            
            panBfrontmat = fronttypes.index[panBfront]
            panAfrontmat = fronttypes.index[panAfront]
            
            print "Rear type materials index and occurrences: "
            for i in range (0, len(backtypes)):
                print i, " --> ", backtypes['x'][i] , " :: ",  backtypes.index[i]
            
            panBrear = int(raw_input("Panel a0 Rear material "))  # Python 2
            panArear = int(raw_input("Panel a1 Rear material "))
              
            panBrearmat = backtypes.index[panBrear]
            panArearmat = backtypes.index[panArear]
               
            # Masking only modules, no side of the module, sky or ground values.
            panelB = resultsDict[(resultsDict.mattype == panBfrontmat) & (resultsDict.rearMat == panBrearmat)]
            panelA = resultsDict[(resultsDict.mattype == panAfrontmat) & (resultsDict.rearMat == panArearmat)]
            #panelB = test[(test.mattype == 'a10.3.a0.PVmodule.6457') & (test.rearMat == 'a10.3.a0.PVmodule.2310')]
            #panelA = test[(test.mattype == 'a10.3.a1.PVmodule.6457') & (test.rearMat == 'a10.3.a1.PVmodule.2310')]
        
        
        # Interpolating to original or givne number of sensors (so all hours results match after deleting wrong sensors).
        # This could be a sub-function but, hmm..
        x_0 = np.linspace(0, len(panelB)-1, len(panelB))    
        x_i = np.linspace(0, len(panelB)-1, int(sensorsy/2))
        f_linear = interp1d(x_0, panelB['Wm2Front'])
        panelB_front = f_linear(x_i)
        f_linear = interp1d(x_0, panelB['Wm2Back'])
        panelB_back = f_linear(x_i)
        
        # Interpolating to 200 because
        x_0 = np.linspace(0, len(panelA)-1, len(panelA))    
        x_i = np.linspace(0, len(panelA)-1, int(sensorsy/2))
        f_linear = interp1d(x_0, panelA['Wm2Front'])
        panelA_front = f_linear(x_i)
        f_linear = interp1d(x_0, panelA['Wm2Back'])
        panelA_back = f_linear(x_i)
        

        #INVERTING MODULES IF IT IS PAST NOON
        if Azimuth_ang > 180:
            temp=panelA_front
            sumFrontA=temp[::-1]
            temp=panelA_back
            sumBackA=temp[::-1]
            
            temp=panelB_front
            sumFrontB=temp[::-1]
            temp=panelB_back
            sumBackB=temp[::-1]
    
            Frontresults=np.append(sumFrontA,sumFrontB)
            Backresults=np.append(sumBackA,sumBackB)
    
        else:
            Frontresults=np.append(panelB_front,panelA_front)
            Backresults=np.append(panelB_back,panelA_back)

    else:  # ONLY ONE MODULE
        

        if automatic == True:
            panBfrontmat = resultsDict[resultsDict['mattype'].str.contains('a0.PVmodule.6457')]
            panelB = panBfrontmat[panBfrontmat['rearMat'].str.contains('a0.PVmodule.2310')] # checks rear mat is also panel B only.


        else:
            
            print "Front type materials index and occurrences: "
            for i in range (0, len(fronttypes)):
                print i, " --> ", fronttypes['x'][i] , " :: ",  fronttypes.index[i]
                    
            panBfront = int(raw_input("Panel a0 Front material "))  # Python 2
            panBfrontmat = fronttypes.index[panBfront]
        
            print "Rear type materials index and occurrences: "
            for i in range (0, len(backtypes)):
                print i, " --> ", backtypes['x'][i] , " :: ",  backtypes.index[i]
            
            panBrear = int(raw_input("Panel a0 Rear material "))  # Python 2
            panBrearmat = backtypes.index[panBrear]
            
            # Masking only modules, no side of the module, sky or ground values.
            panelB = resultsDict[(resultsDict.mattype == panBfrontmat) & (resultsDict.rearMat == panBrearmat)]
            #panelB = test[(test.mattype == 'a10.3.a0.PVmodule.6457') & (test.rearMat == 'a10.3.a0.PVmodule.2310')]
        
        
        # Interpolating to 200 because
        x_0 = np.linspace(0, len(panelB)-1, len(panelB))    
        x_i = np.linspace(0, len(panelB)-1, sensorsy)
        f_linear = interp1d(x_0, panelB['Wm2Front'])
        panelB_front = f_linear(x_i)
        f_linear = interp1d(x_0, panelB['Wm2Back'])
        panelB_back = f_linear(x_i)
    
        
        #INVERTING MODULES IF IT IS PAST NOON
        if Azimuth_ang > 180:
            
            temp=panelB_front
            sumFrontB=temp[::-1]
            temp=panelB_back
            sumBackB=temp[::-1]
    
            Frontresults=sumFrontB
            Backresults=sumBackB
    
        else:
            
            Frontresults=panelB_front
            Backresults=panelB_back
            
    return Frontresults, Backresults;    # End Deep clean Result subroutine.
    
    