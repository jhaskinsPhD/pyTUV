#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 13:30:09 2023

@author: u6044586
"""
import sys 
import pandas as pd 
import numpy as np 

sys.path.append('/uufs/chpc.utah.edu/common/home/u6044586/python_scripts/modules/pyTUV/')
from utils import *

###############################################################################
# Wrapper Functions to make /edit TUV input Files: 
###############################################################################

def make_single_TUV_input_file(changes:dict, j_options, savepath:str, ofilename:str='', overwrite:bool=False):
    """Function to make a single TUV input files with the var inputs in the dict 'changes' 
    to calculate the j-values corresponding to that passed for 'j_options' and saved at 
    '.../savepath/ofilename'.
    
    INPUT:  For examples, see 'pyTUV/examples.py'
    ------
        (1) changes    - a DICTIONARY with TUV input variales as the key and values to use 
                          for each TUV input accordingly to write to the input file. 
        
        (2) j_options  - a STRING or LIST/ARRY denoting which j-values or reactions to calculate Js for. Valid options are: 
            
                            (a) a STRING (case-insensitive) equal to one of the following:  
                                 - 'only_MCM_js' which sets all rxns with a direct MCM analogous J-value to 'T' and all others to 'F'.
                                 - 'all_js' which sets all photolysis rxns to 'T'.
                                 
                            (b) a LIST or ARRAY of strings like one of the following: 
                                 - ['these_js', 'J1','J3', 'Jn21'] 
                                 - ['these_rxns', 'O3 -> O2 + O(1D)'] 
                                 
                                where the first item in the LIST or ARRAY indicates whether a list of MCM 
                                J-names you want to calculate comes after or if a list of TUV reactions 
                                you want to calculate comes after. If you pass input like this, you will 
                                get an error if the first item isn't one of the allowed cases, or if the 
                                J-name or Rxn following those cases is not found. NOTE: In such input lists, 
                                the first items are case insensitive, Jnames are case insensitive, and rxns 
                                are SPACE insensitive.
                                
        (2) savepath    - a STRING corresponding to where you'd like to save the output file to. 
        
        (3) ofilename   - (OPTIONAL) a STRING corresponding to the filename of the input file you'd like to write. 
                            If none is given, its called 'inp_YYYY_MM_DD' by default. 
        (4) overwrite   - (OPTIONAL) a BOOL indicating whether or not to overwrite the file at savepath/ofilename 
                          if that file exists already. If not TRUE, a version string will be appended. Default is FALSE (not to overwrite). 
    OUTPUT: 
    ------- 
        (1) A TUV input files stored at: '.../savepath/inp_YYYY_MM_DD'                        
            
    REQUIREMENTS: 
    -------------
           LIBRARIES:           NONE
           CUSTOM_FUNCTIONS:    check_inputs() defined in pyTUV/utils.py 
                                check_filename() defined in pyTUV/utils.py
                                write_TUV_input_file defined in pyTUV/utils.py 
                          
    AUTHOR: 
    -------
           Prof. Jessica D. Haskins    GitHub: @jhaskinsPhD  Email: jessica.haskins@utah.edu
       
    CHANGE LOG: 
    ----------
       11/20/2023    JDH Created     
    """
    # Check the user input dictionary,"changes" & "j_options" to make sure inputs passed make sense: 
    allowed_vars, changes, j_rxns= check_inputs(changes,j_options) 
    
    # Check that the output directory exists, and whether a file with that ofilename
    # already exists or not... with option to update the name if so to either overwrite 
    # that file or append a new version # to that file to distinguish it from previous versions... 
    output_file= check_filename(filename=ofilename, ext='no_ext', savepath=savepath, # Note: TUV inputs must have NO EXTENSION! 
                                overwrite=overwrite, return_full=True)
    
    # Read in the template file, make the changes requested, & write the output file!  
    write_TUV_input_file(changes, j_rxns, output_file)
    
    return changes, j_rxns 


def make_TUV_input_file_daterange(changes, j_options, savepath:str,  
                                  daterange:pd.core.indexes.datetimes.DatetimeIndex=None, overwrite:bool=False):
    """Function to make a NUMBER of different TUV input files over a range of times/dates.
    
    INPUT: NOTE: For examples, see "pyTUV/examples.py"
    ------
        (1) changes - a DICTIONARY with TUV input variales as the key and values of EITHER (mix & match allowed): 
                            (a) a single value (used for ALL calculations on all days/ times)
                                                       OR 
                            (b) a LIST/ARRAY of values you'd like to change on EACH DIFFERENT DAY 
                            
                      Variables entered with a single value will be replicated to the same len as those
                      that change in time, but lens of arrays must = len of # of days in daterange!
         
        (2) j_options  - A STRING or LIST/ARRY denoting which j-values or reactions to calculate Js for. Valid options are: 
            
                            (a) a STRING (case-insensitive) equal to one of the following:  
                                 - 'only_MCM_js' which sets all rxns with a direct MCM analogous J-value to 'T' and all others to 'F'.
                                 - 'all_js' which sets all photolysis rxns to 'T'.
                                 
                            (b) a LIST or ARRAY of strings like one of the following: 
                                 - ['these_js', 'J1','J3', 'Jn21'] 
                                 - ['these_rxns', 'O3 -> O2 + O(1D)'] 
                                 
                                where the first item in the LIST or ARRAY indicates whether a list of MCM 
                                J-names you want to calculate comes after or if a list of TUV reactions 
                                you want to calculate comes after. If you pass input like this, you will 
                                get an error if the first item isn't one of the allowed cases, or if the 
                                J-name or Rxn following those cases is not found. NOTE: In such input lists, 
                                the first items are case insensitive, Jnames are case insensitive, and rxns 
                                are SPACE insensitive.
        
        (3) savepath   - a STR corresponding to the directory where outputted TUV input files should be saved. 
        
        (4) daterange  - (OPTIONAL) a PANDAS DATERANGE OBJECT listing all dates/times you want to run the model at. 
                         This input is used to fill values in "changes" for imonth, iday, iyear, tstart, tstop, & nt.
                         Useful if you want to run the model over a number of days with the same lat/lon/ other vars 
                         in which case you just pass the stagnant vars in changes and the daterange input. 
                         
                         For example, if you want to run the model in 30min chunks between 1/1/2023 - 1/7/2023 (M/D/Y): 
                         daterange = pd.date_range(start='2023-01-01', end='2023-01-07',freq='0.5H')
                         
        (5) overwrite  - (OPTIONAL) a BOOL indicating whether or not to overwrite a file in savepath that has the 
                         same name ('inp_YYYY_MM_DD') or to append a version # on it. Default is FALSE (not to overwrite).  
                         
    OUTPUT: 
    ------- 
        (1) A number of TUV input files for each day in daterange stored at: '.../savepath/inp_YYYY_MM_DD'                       
            
    REQUIREMENTS: 
    -------------
           LIBRARIES:           import sys 
                                import pandas as pd 
                                import numpy as np 
                                
          CUSTOM_FUNCTIONS:     get_value_at_index()  defined in pyTUV/utils.py
                                make_single_TUV_input_file() defined above 
                          
     AUTHOR: 
     -------
           Prof. Jessica D. Haskins    GitHub: @jhaskinsPhD  Email: jessica.haskins@utah.edu
       
     CHANGE LOG: 
     ----------
       11/20/2023    JDH Created      
    """ 
    
    # Fill date/time vars using daterange input if passed... 
    if daterange is not None: 
        # Pull out dates: 
        changes['imonth']=daterange.month.astype(np.int32).tolist()
        changes['iday'] =daterange.day.astype(np.int32).tolist()
        changes['iyear']=daterange.year.astype(np.int32).tolist()
    
        # Pull out times in expected units of fractional hour
        fractional_hour= np.unique((daterange.hour.astype(np.int32)+daterange.minute.astype(np.int32)/60+daterange.second.astype(np.int32)/3600).tolist())
        changes['tstart']=np.min(fractional_hour)
        changes['tstop']=np.max(fractional_hour)
        changes['nt']= len(fractional_hour)
        
        # Figure out how many UNIQUE days you have & need to write input files for: 
        days=[day_i.replace('-','_') for day_i in np.unique(daterange.date.astype(str))]
    
    # Check that all input arrays are the same length (if not 1) 
    lens=np.unique([len(changes[key]) for key in list(changes.keys()) if (type(changes[key]) in [list, type(np.ones(2))]) and len(changes[key]) >1] )
    if len(lens) > 1: 
        len_dict={key:'len='+str(len(changes[key]))+'/n' for key in list(changes.keys())}
        raise ValueError('All input lists/arrays must be the same length if they are not a single value. You passed: \n'+
                         len_dict).with_traceback(sys.exc_info()[2]) 
    
    # Force all single values to become a list of the same length as all the rest of the vars. 
    for key in list(changes.keys()): 
        if type(changes[key]) not in [list, type(np.ones(2))]: 
            changes[key]=[changes[key]]*lens[0]
    
    all_changes=list([]) # make empty list to hold changes made on each day! 
    
    # Loop over all values in arrays: 
    for i in range(0, len(days)):
        ofile_i='inp_'+days[i]
        
        # Sub select the values for each key in changes at index i to have a single dict 
        # with changes ON THIS DAY ONLY to pass to the function "make_single_TUV_input_file()" 
        changes_i = get_value_at_index(changes, i)
        
        # Now go ahead and write that file (checks change_i, j_options, and filenames): 
        cg_i, jrx_i = make_single_TUV_input_file(changes_i, j_options, savepath=savepath, ofilename=ofile_i, overwrite=overwrite)
        
        # Append changes to output list: 
        all_changes.append(cg_i)
        
    return all_changes, jrx_i

















