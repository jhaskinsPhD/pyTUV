#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 13:30:09 2023

@author: u6044586
"""
import os 
import sys 
import csv 
import pandas as pd 
import numpy as np 

sys.path.append('/uufs/chpc.utah.edu/common/home/u6044586/python_scripts/modules/pyTUV/')
from utils import *

###############################################################################
# Wrapper Functions to make /edit TUV input Files: 
###############################################################################

def make_single_TUV_input_file(changes:dict, j_options, savepath:str, overwrite:bool=False):
    """Function to make a single TUV input files with the var inputs in the dict 'changes' 
    to calculate the j-values corresponding to that passed for 'j_options' and saved at 
    '.../savepath/inp_YYYY_MM_DD_offset_HRpointFRAC'. Outputted filename cannot and should not 
    be changed because its needed to write & read in the corresponding TUV output files. 
    
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
                                
        (3) savepath    - a STRING corresponding to where you'd like to save the output file to. 
        
        (4) overwrite   - (OPTIONAL) a BOOL indicating whether or not to overwrite the file at savepath/ofilename 
                          if that file exists already. If not TRUE, a version string will be appended. Default is FALSE (not to overwrite). 
    OUTPUT: 
    ------- 
        (1) A TUV input files stored at: '.../savepath/inp_YYYY_MM_DD_offsetHRpointFRAC'                        
            
    REQUIREMENTS: 
    -------------
           LIBRARIES:           NONE
           CUSTOM_FUNCTIONS:    check_inputs() defined in pyTUV/utils.py 
                                write_TUV_input_file defined in pyTUV/utils.py 
                          
    AUTHOR: 
    -------
           Prof. Jessica D. Haskins    GitHub: @jhaskinsPhD  Email: jessica.haskins@utah.edu
       
    CHANGE LOG: 
    ----------
       11/20/2023    JDH Created   
       11/26/2023    JDH Removed 'ofilename' as input option & added 'savepath', overwrite' inputs.
                     Now, output filenames are automatically set in write_TUV_input_file()
                     with UTC offset info AND date in the filename to make reading TUV output easier.  
    """
    # Check the user input dictionary,"changes" & "j_options" to make sure inputs passed make sense: 
    allowed_vars, changes, j_rxns= check_inputs(changes,j_options) 
    
    # Read in the template file, make the changes requested, & write the TUV input file at savepath!   
    ofile= write_TUV_input_file(changes, j_rxns, savepath=savepath, overwrite=overwrite)
    
    # Return path to input file, the possibly modified dict, "changes" and "j_rxns" so user can see what was done... just in case! 
    return ofile, changes, j_rxns 


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
                         same name or to append a version # on it. Default is FALSE (not to overwrite).  
                         
    OUTPUT: 
    ------- 
        (1) A number of TUV input files for each day in daterange stored at: '.../savepath/inp_YYYY_MM_DD_offset_HRpointFRAC'  
        
        (2) all_changes  - a DICT containing DICTS with changes made on each day to input files. 
        
        (3) j_rxns - A list of TUV reactions that J-Values will be outputted for on each day.         
            
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
       11/26/2023    JDH updated so filenames are automatically set in write_TUV_input_file()
                     now with UTC offset info AND date in the filename to make reading output easier.  
    """ 
    
    # Fill date/time vars using daterange input if passed... 
    if daterange is not None: 
        # Figure out how many UNIQUE days you have & need to write input files for: 
        dates=[day_i for day_i in np.unique(daterange.date)]
        
        # Pull out dates: 
        changes['imonth']=[date_i.month for date_i in dates]
        changes['iday'] =[date_i.day for date_i in dates]
        changes['iyear']=[date_i.year for date_i in dates]
    
        # Pull out times in expected units of fractional hour
        fractional_hour= np.unique((daterange.hour.astype(np.int32)+daterange.minute.astype(np.int32)/60+daterange.second.astype(np.int32)/3600).tolist())
        changes['tstart']=np.min(fractional_hour)
        changes['tstop']=np.max(fractional_hour)
        changes['nt']= len(fractional_hour)
        
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
    
    # Make empty list to hold input files generated & changes made on each day!
    files=list([]); all_changes=list([])  
    
    # Loop over all days & write a new input file for each! 
    for i in range(0, len(dates)):        
        
        # Sub select the values for each key in changes at index i to have a single dict 
        # with changes ON THIS DAY ONLY to pass to the function "make_single_TUV_input_file()" 
        changes_i = get_value_at_index(changes, i)
        
        # Now go ahead and write that file (checks change_i, j_options, and filenames): 
        inpf_i, cg_i, jrx_i = make_single_TUV_input_file(changes_i, j_options, savepath=savepath, overwrite=overwrite)
        
        # Append changes to output list: 
        all_changes.append(cg_i)
        
        # Append all input files generated to output list: 
        files.append(inpf_i) 
        
    return files, all_changes, jrx_i


###############################################################################
# Wrapper Functions to read outputted TUV Files into python/MATLAB ... 
###############################################################################

def read_single_TUV_output(outfile, map_to_MCM:bool=True): 
    """Function to read in a single output TUV.txt file as a pandas Dataframe. 
    Option to convert TUV Rxns to MCM/F0AM corresponding names for Jvalues. 
    
    INPUT:  
    ------
        
        (1) outfile    - STR containing filename with path & extension of the TUV output
                         file you want to read in as a pandas dataframe 
     
        (2) map_to_MCM - BOOL indicating whether or not to use TUV rxns as column 
                         names (map_to_MCM=FALSE) in output dataframe or MCM J-Value names (map_to_MCM=TRUE). 
                         Default is set to TRUE ( to use MCM J-Value Names as column headers). 
                                                      
    OUTPUT: 
    ------- 
        (1) df         - Pandas DataFrame with either TUV Rxns as columns or MCM J-value 
                         names as columns, a column with Local_Datetime that takes into account 
                         the UTC offset read in from outfile name, and UTC_Datetime as the df index.                       
            
    REQUIREMENTS: 
    -------------
           LIBRARIES:           import sys 
                                import os
                                import csv 
                                import pandas as pd 
                                import numpy as np 
                                
          CUSTOM_FUNCTIONS:     build_jmapping_dict()  defined in pyTUV/utils.py
                                get_date_and_UTC_offset_from_filename() defined in pyTUV/utils.py
                                convert_to_datetimes() defined in pyTUV.utils.py
                          
     AUTHOR: 
     -------
           Prof. Jessica D. Haskins    GitHub: @jhaskinsPhD  Email: jessica.haskins@utah.edu
       
     CHANGE LOG: 
     ----------
       11/26/2023    JDH Created          
    """
    
    # Check to make sure the output file exists before it reading in 
    if os.path.isfile(outfile) !=True: 
        raise ValueError("The inputted file for 'outfile'='"+file+"' could not be found/does not exist.\n"+ 
                         "Please check that the path/name of the output file you want to read in is correct."
                         ).with_traceback(sys.exc_info()[2])

    # Create the dictionary that can map TUV rxns to their MCM J-Value! 
    j_map= build_jmapping_dict(only_MCM_Js= False, return_reverse=False)
    
    # Open the file and read it in line by line: 
    with open(outfile, "r",errors="ignore") as f: 
        reader = csv.reader(f, delimiter="\t")
        
        # Initialize vars we fill in reading the file. 
        map_cols=dict({});  in_headers=False; in_data=False
        for row in reader:
            line = " ".join(row)  # read line by line. 
            
            # Check current line to see if you're still in header lines or not! 
            if 'values at z = ' in line and in_headers is True: in_headers= False 
            
            # Create a dictionary with RXN # as key and either RXN or MCM-J name as Key to map 
            # column #s to a "readable" dataframe column name. Strugure looks like: 
            #   '41 = ClONO2 -> Cl + NO3'  
            if in_headers is True: 
                col_n=line.split('=')[0].replace(' ','') # Get column # of this rxn
                j_rxn= ''.join(line.split('=')[1:]).replace(' ','') # Get rxn without spaces! 
                if map_to_MCM is True and j_rxn in list(j_map.keys()): 
                    map_cols[col_n]=j_map[j_rxn] # Assign col # to J## in MCM ... 
                else: 
                    map_cols[col_n]= j_rxn       # Assign col # to TUV Rxn    

            if (in_data is True) and ('------' not in line ): 
                # Append the j-values to the dataframe at this point in time. 
                splt= [float(item) for item in line.split(" ") if item !=''] 
                df.loc[len(df)]=np.array(splt)
            
            # Check curreent line for stuff that signals the NEXT line has something we care about in it... 
            if 'Photolysis rate coefficients,' in line and in_headers is False: 
                in_headers=True # Have passed line signaling headers for photo columns begins on the next line
                
            if 'time, hrs.  sza, deg.' in line: # Line signaling data begins after this! 
                in_data=True 
                # Create the dataframe with columns for UTC fractional hour and SZA (which are always in TUV output files). 
                df=pd.DataFrame(columns= ['frc_hr_UTC', 'SZA']+ list(map_cols.values()))
           
    # Extract the date and UTC offset from the output filename: 
    date, utc_offset =get_date_and_UTC_offset_from_filename(outfile)
        
    # Convert all fractional hours in UTC to pandas datetime objects with 
    # and add columns for Local_Datetime (accounting for offset) and UTC_Datetime 
    # to the df, drop the column 'frc_hr_UTC', and set UTC_Datetime as df index! 
    df = convert_to_datetimes(df, date, utc_offset)
    
    return df 


def read_n_combo_TUV_outputs(file_dir, map_to_MCM:bool=True):
    """Function to read in multiple outputted TUV.txt files in a file_dir and 
    combine output of all files into a single outputted pandas Dataframe. 
    Option to convert TUV Rxns to MCM/F0AM corresponding names for Jvalues. 
    
    INPUT:  
    ------
        (1) file_dir   - STR containing path to directory with only TUV output files within it 
                         that you want to read in and combine into a single pandas df.  
     
        (2) map_to_MCM - BOOL indicating whether or not to use TUV rxns as column 
                         names (set to FALSE) in output dataframe or MCM J-Value names (set to TRUE). 
                         Default is set to TRUE (use MCM J-Value Names)... 
                                                      
    OUTPUT: 
    ------- 
        (1) df         - Pandas DataFrame with either TUV Rxns as columns or MCM J-value 
                         names as columns and time as index with ALL output from files in file_dir.                        
            
    REQUIREMENTS: 
    -------------
           LIBRARIES:           import sys 
                                import os
                                import pandas as pd 
                                
          CUSTOM_FUNCTIONS:     read_single_TUV_output()  defined above 
                          
     AUTHOR: 
     -------
           Prof. Jessica D. Haskins    GitHub: @jhaskinsPhD  Email: jessica.haskins@utah.edu
       
     CHANGE LOG: 
     ----------
       11/26/2023    JDH Created          
    """
    # Check that output file directory exists! 
    if os.path.isdir(file_dir) != True: 
        raise ValueError("The inputted file directory: '"+file_dir+"' could not be found/does not exist. Check that the path inputted is correct."
                         ).with_traceback(sys.exc_info()[2])

    # Get a list of all files in file_dir (not recursive) that exist with path attached! 
    files = [os.path.join(file_dir, f) for f in os.listdir(file_dir) if os.path.isfile(os.path.join(file_dir, f))]    
    
    # Loop over all files
    for i,f in enumerate(files):
        if i==0:  # On first iteration, read in the file as a df:  
            df= read_single_TUV_output(f, map_to_MCM=map_to_MCM)
        else: # On subsequent iterations, read them in, the concatonate with old df! 
            df_i= read_single_TUV_output(f, map_to_MCM=map_to_MCM)
            df=pd.concat([df, df_i], axis=0) # Concatenate! 
            
    return df 





