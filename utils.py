#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 13:29:33 2023

@author: u6044586
"""
import os 
import sys 
import re
import inspect 
import pandas as pd 
import numpy as np 
from collections import OrderedDict

###############################################################################
# 1 - Helper Functions widely referenced and used in various sub-functions: 
###############################################################################   
def get_my_relative_paths(): 
    """Function used to identify where you've installed the pTUV on 
    your computer so we can tell it how to find all the relative inputs it needs!""" 
    
    pyTUV_path=os.path.dirname(os.path.abspath(__file__))
            
    paths=dict({'TUV_Template_Info_DF.xlsx':   os.path.join(pyTUV_path, 'Input_Data/TUV_Template_Info_DF.xlsx'),
                'TUV_to_MCM_J_mapping.xlsx':   os.path.join(pyTUV_path, 'Input_Data/TUV_to_MCM_J_mapping.xlsx'),
                'TUV_InputFile_Template':          os.path.join(pyTUV_path, 'Input_Data/TUV_InputFile_Template'),
                'Outputs':                     os.path.join(pyTUV_path, 'Outputs/' )}) 
    
    # Check that all the stuff in paths exists.. pops an error if not! 
    for key in list(paths.keys()): 
        file= check_filename(paths[key], return_full=True)
    
    return paths 
        
def _parse_filename(filename, quiet:bool=True): 
    """Function to take some input string of a filename and seperate it into its 
    path, extension, and actual name. Helper function for check_filename().
    
    INPUTS: 
    -------
       (1) filename - STR with full path and filename  
       
       (2) quiet    - BOOL of whether or not to print output. Default is True. 
    
    OUTPUTS: 
    --------
       (1) opath - STR containing ONLY the path to the file  
                   NOTE: This outputdoes not have a '/' after it, so use os.path.join() 
                         to combine the path with filename! 
                         
       (2) oname - STR containing ONLY the filename
       
       (3) oext - STR contaiing ONLY the file's extension. (e.g. '.m', '.txt', ''.py')
        
    REQUIREMENTS: 
    -------------
        LIBRARIES:           import os
        CUSTOM FUNCTIONS:    None
    
    AUTHOR: 
    -------
        Dr. Jessica D. Haskins (jessica.haskins@utah.edu) GitHub: @jhaskinsPhD
    
    CHANGE LOG: 
    ----------
    10/03/2023    JDH Created 
     
    """
    # Split filename into name/ extension: 
    [path_and_name,oext] = os.path.splitext(filename)
    
    # Split the file minus its extnsion (if it has one) into the savepath & name 
    opath, oname= os.path.split(path_and_name)
    
    # Print intput/ output if quiet is False: 
    if quiet is False: 
        print("Original Filename = '{}'".format(filename))
        print("    path='{}'\n    name='{}'\n    ext='{}'".format(opath,oname,oext))
        
    return opath, oname, oext
    

def check_filename(filename:str='', default_name:str= '', ext:str='', 
                   savepath:str='', overwrite: bool=False, return_full:bool=False,
                   quiet: bool =True): 
    """ Highly flexible function to check if a file path is valid, if that file 
    exists already, with options to rename the file following some naming 
    convention with an updated version # if you don't want to overwrite the existing file and 
    an option to either return the path/name.extension as a full string or as separate outputs. 
    
    INPUTS: 
    -------
    
            (1) filename     - STR with filename. Valid forms for this can inlude path/extension or not: 
                            
                '/path/to/my_file.txt' - name with path and extension  
                'my_file.txt'          -  name with extension 
                'my_file'              - name without path or extension
            
            (2) default_name - (OPTIONAL) STR with a "default" filename. Accepted forms for this can 
                                inlude path/ extension or not, as above. 
               
            (3)  ext         - (OPTIONAL) STR of the file's extension. NOTE: If this arg is 
                                not passed, either 'filename ' or 'default_name' must contain 
                                the extension of the file UNLESS 'no_ext' is passed... 
                            
            (4) savepath    - (OPTIONAL) STR with path of the file.NOTE: If this arg is 
                                not passed, either 'filename ' or 'default_name' must contain 
                                the path of the file. 
                                
            (5) overwrite    - (OPTIONAL) BOOLEAN indicating whether you'd like  to overwrite 
                                the file if it exists. Default is FALSE which will create a new 
                                file with a version # string attached to it like my_file_v3.txt
            
            (6) return_full  - (OPTIONAL) BOOLEAN  indicating whether you'd like to return
                                a STR with the absolute path to the file+ext (if True) or 
                                if you'd like to return a list containing the [path, file+ext]. 
                                Default is to return a list seperating path from file... 
                                
            (7) quiet        - (OPTIONAL) BOOLEAN indicating whether or not to print 
                                "pass" + filename or not. Default is set to FALSE (suppress "pass" output).
    
    OUTPUT: 
    ------- 
        EITHER:                                
               [savepath, filename+ext] - LIST with (updated) strings if return_full=FALSE (DEFAULT) 
        OR: 
                savepath+filename+ext   - STR of absolute path to file if return_full=TRUE
    REQUIREMENTS: 
    -------------
        LIBRARIES:           import os 
                             import sys 
                             import re 
                             import inspect 
            
        CUSTOM FUNCTIONS:    _parse_filename()     (defined above).       
        
    AUTHOR: 
    -------
        Prof. Jessica D. Haskins    GitHub: @jhaskinsPhD  Email: jessica.haskins@utah.edu
    
    CHANGE LOG: 
    ----------
    1/18/2022    JDH Created 
    7/19/2022    JDH add "quiet" option. 
    10/12/2023   JDH added user input parsing errors, updated version # creation using regex, 
                    & updated default "savepath" to be set to directory of the script calling this function
                    + drastically updated documnetation. Now depends on regex & inspect libraries. 
    
    """
    ###############################################################################################
    # (A) Parse user inputs for erros & figure out what combo of name/path/extension options were used
    ###############################################################################################
    using_default=False # Set boolean to indicate if we're using the default name (vs the filename)... initally False!
    opath=None
    
    # (A1) Determine if the user passed input to savepath or not & set opath if they did to 'savepath' 
    if len(savepath) ==0:
        opath_defined=False 
    else:
        opath=savepath; opath_defined=True
            
    # (A2) If the user didn't pass "filename", but did pass a default_name, set filename to default_name:  
    if len(filename)==0 and len(default_name) >0: 
        filename=default_name; using_default=True; 
    
    # (A3) If they didn't specify either a filename or a default name, throw an error
    elif len(filename)==0 and len(default_name)==0: 
        raise ValueError("INPUT ERROR (A.3) in check_filename(): \n"+
                         "   You must specify either 'filename' or a 'default_name' as input arguements.").with_traceback(sys.exc_info()[2])
    
    # Create string to define whether you're using 'default_name' or 'filename' as input... 
    inp_type='default_filename'if using_default is True else 'filename' 
    
    # Parse the filename to see if it has a path/name/extension attached to it! 
    ipath, name_only, iext = _parse_filename(filename)
    
    # Set boolean to indicate if the filename contains a path or not.. 
    path_in_filename=True  if len(ipath)>0 else False 
    
    # (A.4) Check parsed extension, make sure it matches input to "ext", and that some extension is defined! 
    if len(ext) > 0 and ext !='no_ext': 
        # (A.4.1) If user passed input for ext, remove spaces and make sure it has the 
        #     period in front of it in the "ext" var for the file's extension...
        ext='.' +ext.strip() if (('.' not in ext) or (ext.strip()[0]!='.')) else ext.strip()
        
        # (A.4.2) Throw an error if the parsed extension doesn't match the input extension! 
        if len(iext) > 0 and ext != iext and ext !='no_ext': 
            raise ValueError("INPUT ERROR (A.4.2) in check_filename():\n"+
                             "    You passed inconsistent extensions in the input for '"+inp_type+"',  and 'ext'.\n"+
                             "        '"+inp_type+"' = '"+filename+"\n"+
                             "        'ext' = '"+ext+"'\n"
                             "    Check_filename() thinks: '"+iext +"' != '"+ext+"'.").with_traceback(sys.exc_info()[2])
    
    # (A.4.3)If no extension was passed, used iext as the extension!
    if (len(ext)==0) or (ext!='no_ext') and len(iext) >0: 
        ext=iext
    
    # (A.4.4) Throw an error if no file extension can be found: 
    elif len(ext)==0 and len(iext)==0 and ext !='no_ext': 
        raise ValueError("INPUT ERROR (A.4.4) in check_filename():\n"+
                         "    You must include the extension of the file you wish to 'check' for one of the following input arguements: \n"+
                         "       (1)'filename'\n"+
                         "       (2) 'default_name'\n"+
                         "       (3) 'ext'").with_traceback(sys.exc_info()[2])
    
    elif ext =='no_ext': ext =''
    
    ###########################################################################
    # (B) Figure out the file's path, name, and extension! 
    ###########################################################################
    
    # (B.1) If no savepath is defined and there IS a path in the filename, use that as opath... 
    if opath_defined is False and path_in_filename is True: 
        opath=ipath; opath_defined=True        
    
    # (B.2) If there is NOT a path in the filename/default_name set opath to the path 
    #       of the file that called this function. 
    if opath_defined is False and path_in_filename is False: 
            
        # Get the filename of the script that called this function: 
        parent_filename=inspect.stack()[1].filename
                
        # Set opath to the path of the parent script & tell the rest of the code we found opath! 
        opath, dum= os.path.split(parent_filename); opath_defined=True
                
        # Print warning that we arbitrarily set the savepath...
        raise Warning("No 'savepath' could be found in the input args. It will be set it to the following path,\n"+
                      "    corresponding to that of the script that called check_filename(): \n\n"+
                      "savepath = '"+opath+"'")
    
    if opath_defined is False: 
        raise ValueError('DEBUGGING ISSUE: The path to the file in check_filename() was not ever assigned... ')
    
    # Check that the output path actually exists! 
    if not os.path.exists(opath): 
        raise NotADirectoryError("In check_filename(), the following parsed directory of the file to 'check' does not exist: \n\n"+ 
                                 "   path_checked ='"+opath+"'\n\n"+
                                 "Your inputs this was parsed from were: \n"
                                 "   "+inp_type+" = '"+filename+"'\n"+ 
                                 "   savepath = '"+savepath+"'\n\n"+
                                 "If the path_checked looks wrong compared to these, its an issue within check_filename()...").with_traceback(sys.exc_info()[2])
                                 
    # Define the absolute path of the file you're checking... 
    fullname=os.path.join(opath,name_only+ext)
    
    ###########################################################################
    # (C) Do file overwriting / renaming if asked... 
    ###########################################################################
    n=1; #initialize counter variable! 
    
    # If/ While what we have set "fullname" to exits already ...  
    while os.path.isfile(fullname):
        
        ##########  C.1 Delete file if it exists & "overwrite" is True ########
        if overwrite is True:
            os.remove(fullname); just_file=name_only+ext
            
        ##########  C.2 Otherwise append a version # to the file ##############
        else:
            # Use a regex string to pull out the last version # of file
            # This regex looks for 1+ # following "_v" ... Pulls out ['39'] from 'my_file_v39.txt'
            last_ver=re.findall(r'j([a-zA-Z0-9]+)',name_only)
            
            # C.2.1 If the file exists but does NOT have a version #, then add one! 
            if len(last_ver) == 0: 
                just_file=name_only+'_v'+str(n)+ext
            
            # C.2.2 If the file exists and DOES have a version number already... 
            else: 
                # Update version # to be +1 and convert to a string. 
                new_ver='_v'+str(np.int32(last_ver[0]) +n)
                                 
                # Then get the old name, without the version #, and update "just_file"
                just_file=name_only.split('_v'+last_ver[0])[0]+new_ver
            
            # After changing the filename accordingly, update "fullname" to check if it exists! 
            fullname=os.path.join(opath,just_file)
            
        n=n+1 # Update counter variable! 
            
        # You now havea valid (unique) file path, name, extension combo!
        if os.path.isfile(fullname) is False: break 
    
    ###########################################################################
    # (D) Prep Output
    ###########################################################################
    
    # Print "PASS" info once we get here if asked... 
    if quiet is False: print('Check_filename() found no errors for:'+ fullname)
    
    # Decide what to return to the user... 
    if return_full is True: 
        return fullname
    
    else: # Have to add '/' after opath because pullit it out with os doesn't keep it & 
          # os.path.join() adds it for us when we make fullname...  
        return [opath+'/', just_file]

def get_TUV_input_info(info_only:bool=True, print_info:bool=True):
    """Helper function to read in all the info about allowed TUV Input Vars. 
    If info_only is passed, only info relevant to users is passed back, otherwise, 
    all info is returned (and used to set allowed limits! in check_inputs().""" 
    # Get the paths to all the input files (we need the template file here). 
    paths= get_my_relative_paths() 
    
    # Read in Info About TUV Inputs/Limits and put into a dictionary
    # and make sure default values of vars are read in as correct python types... 
    # NOTE: Change file where are these are set if using new version & it has new limits, 
    #       rather than changing those values/limits here. To see where this file lives do: 
    #print(paths['TUV_Template_Info_DF.xlsx'])
    tuv_df=format_default_types(pd.read_excel(paths['TUV_Template_Info_DF.xlsx']))
    
    allowed_vars=dict({}) # Create empty dict to hold info about all allowed vars that are TUV inputs: 
    for i in tuv_df.index:
        
        if info_only==False: # Return everything! 
            allowed_vars[tuv_df.loc[i,'Variable'] ]=dict({
                'Type':tuv_df.loc[i,'Var_Type'],
                'Type_Details': tuv_df.loc[i,'Type_Desc'], 
                'Default_Value':tuv_df.loc[i,'Default_Value'],
                # Force all limits to be floating point numbers unless they're stings. 
                'Min_Value': np.float64(tuv_df.loc[i,'Min_Value']) if type(tuv_df.loc[i,'Min_Value'])!=str else tuv_df.loc[i,'Min_Value'],
                'Max_Value': np.float64(tuv_df.loc[i,'Max_Value']) if type(tuv_df.loc[i,'Max_Value'])!=str else tuv_df.loc[i,'Max_Value'],
                # Whether or not a user SHOULD be able to edit this input or if its automatically calc'd! 
                'Locked_TF': tuv_df.loc[i,'Locked'], 
                'Units': 'N/A' if type(tuv_df.loc[i,'Units'])!=str else tuv_df.loc[i,'Units'], 
                'Description': tuv_df.loc[i,'Description'], 
                'Line_No':np.int32(tuv_df.loc[i,'Line_No']) })
            
        else: # Return only info relevant to the user: 
            allowed_vars[tuv_df.loc[i,'Variable'] ]=dict({
                'Type':tuv_df.loc[i,'Var_Type'],
                'Default_Value':tuv_df.loc[i,'Default_Value'],
                # Force all limits to be floating point numbers unless they're stings. 
                'Min_Value': np.float64(tuv_df.loc[i,'Min_Value']) if type(tuv_df.loc[i,'Min_Value'])!=str else tuv_df.loc[i,'Min_Value'],
                'Max_Value': np.float64(tuv_df.loc[i,'Max_Value']) if type(tuv_df.loc[i,'Max_Value'])!=str else tuv_df.loc[i,'Max_Value'],
                'Units': 'N/A' if type(tuv_df.loc[i,'Units'])!=str else tuv_df.loc[i,'Units'], 
                'Description': tuv_df.loc[i,'Description'] })
    
    #Display all this information nicely: 
    if info_only==True and print_info ==True:       
        for n,var in enumerate(list(allowed_vars.keys())): 
            print("#{} VARIABLE = '{}'".format(n, var))
            print('    Type={}   Units={}   Default_Value= {}  Min_Value={}  Max_Value={}'.format(allowed_vars[var]['Type'], 
                                                                                                   allowed_vars[var]['Units'],
                                                                                                   allowed_vars[var]['Default_Value'],
                                                                                                   allowed_vars[var]['Min_Value'],
                                                                                                   allowed_vars[var]['Max_Value']))
            print('    Description= {}'.format(allowed_vars[var]['Description'])+'\n')
            
    return allowed_vars
###############################################################################
# 2 - Helper Functions used in check_inputs() called within function write_TUV_input_file()  
###############################################################################
def build_jmapping_dict(only_MCM_Js:bool = True, return_reverse=False):
    """Read in data to map TUV reactions to appropriate F0AM/MCM J-Value. 
    By Default, returns TUV Rxn as key, and MCM_jname as value, unless in reverse.
    Called in check_joptions() within check_inputs() to make new TUV input files 
    and in reading TUV output. 
    """
    # Get the paths to all the input files (we need the template file here). 
    paths= get_my_relative_paths()
    
    # Read in all the info about how TUV rxns map to MCM J-names (in F0AM): 
    jdat=pd.read_excel(paths['TUV_to_MCM_J_mapping.xlsx'], index_col=0).fillna('None')
    
    # Dump everything into a dictionary: 
    j_map=dict({}) 
    for index, row in jdat.iterrows():
        if row['MCM_Jval'] != 'None': #TUV rxn as key, MCM value as value 
            j_map[row['TUV_Reaction'].replace(' ','')]= row['MCM_Jval'].replace(' ' ,'')
            
        if only_MCM_Js is False and row['MCM_Jval'] == 'None': # TUV rxn as key, no value.... 
            j_map[row['TUV_Reaction'].replace(' ','')]= 'None' 
                
    if return_reverse is True: # Also return a reverse dictionary. 
        jmap_rev=dict({}) # w/ MCM as key and TUV rxn as value.... 
        for key in list(j_map.keys()): 
            if j_map[key] != 'None': 
                jmap_rev[j_map[key]]=key
            elif (only_MCM_Js==False) and (j_map[key]=='None') and (j_map[key] not in list(jmap_rev.keys())): 
                jmap_rev[j_map[key]]=[key]
            elif(only_MCM_Js== False) and (j_map[key]=='None') and (j_map[key] in list(jmap_rev.keys())): 
                jmap_rev[j_map[key]]=jmap_rev[j_map[key]]+[key]
        return j_map, jmap_rev
    else:
        return j_map
    
    
def check_joptions(j_options):
    """Function to ensure user arguements passed to j_options are valid. Returns a list of 
    TUV rxns the user wants to calculate J-values for regardless of input type. Called within check_inputs(). """
    
    # Make sure user passed an allowed J_options input:
    bad_j=False
    if type(j_options) ==str and j_options.lower() not in ['only_mcm_js', 'all_js']: bad_j=True
    elif any([type(j_options)==type(this) for this in [list(['j']), np.array(['j'])]]) and \
        j_options[0].lower() not in ['these_mcm_js', 'these_tuv_rxns']: bad_j=True
    
    # Big error explaining all possible inputs for "J_options": 
    if bad_j==True: 
        raise ValueError("Input for j_options not recognized. Valid options must be one of these: \n"+ 
                         "    (1) a STRING (case-insensitive) equal to one of the following: \n"  
                         "            - 'only_MCM_js' which sets all rxns with a direct MCM analogous J-value to 'T' and all others to 'F'. \n\n"+
                         "            - 'all_js' which sets all photolysis rxns to 'T'. \n" +
                         "    (2) a LIST or ARRAY of strings like one of the following: \n"+
                         "            - ['these_js', 'J1','J3', 'Jn21'] \n"+
                         "            - ['these_rxns', 'O3 -> O2 + O(1D)'] \n"+
                         "        where the first item in the LIST or ARRAY indicates whether a list of MCM J-names you want to calculate comes after \n"+ 
                         "       or if a list of TUV reactions you want to calculate comes after it. If you pass input like this, \n"+ 
                         "       you will get an error if the first item isn't one of the allowed cases, or if the J-name or Rxn is not found. \n" +
                         "       NOTE: In such input lists, the first items are case insensitive, Jnames are case insensitive, and rxns are SPACE insensitive." \
                         ).with_traceback(sys.exc_info()[2]) 
        
    # Read "joptions" and get a list of all TUV rxns to set to True: 
    if type(j_options) ==str and j_options.lower()=='only_mcm_js': 
        # Calculate only j-values with a direct MCM analoge, calc all! 
        js=build_jmapping_dict(only_MCM_Js=True)
        j_rxns=list(js.keys())
    elif type(j_options) == str and j_options.lower()=='all_js': 
        # Calculate all possible j-values in TUV 
        js=build_jmapping_dict(only_MCM_Js=False)
        j_rxns=list(js.keys())
    elif any([type(j_options)==type(this) for this in [list(['j']), np.array(['j'])]]): 
        # User has passed either a list of J-names in MCM or a list of rxns to turn on... 
        these=j_options[1:] # list of j-names/rxns comes after first string... 
        js,js_rev=build_jmapping_dict(only_MCM_Js=False) # get all Js (rxns & keys). 
        
        # If they passed a list of Jnames they want to set to True.... 
        if j_options[0].lower()=='these_mcm_js': 
            
            # Get list of all allowed jnames in lower case (e.g. ['j1', 'j3', 'jn21'])
            allowed_jnames= [key.lower() for key in list(js_rev.keys())]
            
            # Figure out if there are any J-s you can't find they inputted: 
            cant_find= [key for key in these if key.lower() not in allowed_jnames] 
            if len(cant_find) > 0: 
                raise ValueError("For the following MCM J-Names, there's NO direct analogous rxn available in TUV:\n"+ 
                                 "    " + ", ".join(cant_find) + "\n"+
                                 "You should either remove these from your list/array of 'j_options[1:]' OR check the file:\n"+
                                 "    '.../pyTUV/Input_Data/TUV_to_MCM_mapping.xlsx'\n" 
                                 "to see what TUV rxns are available & what MCM J-name we think each maps to. \n"+ 
                                 "It's possible we didn't map that specific J-name to the rxn it does correspond to in MCM/F0AM"+ 
                                 "and you could fix this by adding that J-name to the right rxn in this file to subvert this error.").with_traceback(sys.exc_info()[2]) 
            else:
                j_rxns= [js_rev[key] for key in these] # Get RXN corresponding to key names they want! 
        
        # If they passed a list of Jnames they want to set to True....                                                          
        elif j_options[0].lower=='these_tuv_rxns': 
            # Get list of all allowed rxns with no spaces (e.g. ['O3->O2+O(1D)'])
            allowed_rxns= ["'"+key.repalce(' ' ,'')+"'" for key in list(js.keys())]
            
            # Figure out if there are any rxns you can't find they inputted: 
            cant_find= ["'"+key+"'" for key in these if "'"+key.replace (' ' ,'')+"'" not in allowed_rxns] 
            if len(cant_find) > 0: 
                raise ValueError("We could not find a reaction allowed in TUV corresponding to the following Rxns you inputted in the list/array 'j_options':\n"+ 
                                 "    " + "\n ".join(cant_find) + "\n"+
                                 "You should either remove these from your list/array of 'j_options[1:]' OR check the reaction you want is in the following list \n"+ 
                                 "(only spacing is disregarded. It needs to match the capitolization & rxn text exactly as it is in TUV):\n"+ 
                                 "Allowed_Rxns=["+ " ,".join(allowed_rxns)+"]").with_traceback(sys.exc_info()[2]) 
            else:
                j_rxns= these # RXNs they want w/o errors.  
    
    return j_rxns


def format_default_types(tuv_df:pd.DataFrame): 
    """Helper function called in get_and_set_lims() to ensure "Default_Values" 
    in the dataframe "tuv" are the appropriate python Type for the function 
    check_inputs() and its sub-functions to work properly..."""
    
    for index  in tuv_df.index:
        if tuv_df.loc[index,'Var_Type']=='np.int32': 
            tuv_df.at[index,'Default_Value']=np.int32(tuv_df.loc[index,'Default_Value'])
        elif tuv_df.loc[index,'Var_Type']=='np.float64': 
            tuv_df.at[index,'Default_Value']=np.float64(tuv_df.loc[index,'Default_Value'])
        elif tuv_df.loc[index,'Var_Type']=='bool' and type(tuv_df.loc[index,'Default_Value'])!=bool:
            if tuv_df.loc[index,'Default_Value']=='FALSE': 
                tuv_df.at[index,'Default_Value']=False
            elif tuv_df.loc[index,'Default_Value']=='TRUE':
                tuv_df.at[index,'Default_Value']=True 
        elif tuv_df.loc[index,'Var_Type']=='str' and type(tuv_df.loc[index,'Default_Value'])!=str: 
            tuv_df.at[index,'Default_Value']=str(tuv_df.loc[index,'Default_Value']) 
                
    return tuv_df 
    

def get_and_set_lims(variable_changes): 
    """Helper function called in check_inputs() that reads in an Excel File that 
    defines the variables expected in TUV, their data types, their descriptions, 
    units, default values, and valid ranges and updates those limits that 
    depend on user input vars as apporpriate. Returns updated variable_changes 
    and list of allowed vars... """
    
    # read in info about allowed variables; 
    allowed_vars= get_TUV_input_info(info_only=False)
    
    # Check if looping over zenith or time... and set lims as appropriate. 
    lzenit= False if 'lzenit' not in list(variable_changes.keys()) else variable_changes['lzenit']
    for var in ['tstart','tstop']:    
        if lzenit==True: 
            # Loops over ZENITH ANGLE if True, set lims to 0-180 & Units to degrees! 
            allowed_vars[var]['Min_Value']=0 
            allowed_vars[var]['Max_Value']=180 
            allowed_vars[var]['Units']='degrees'
        else: 
            # Loops over TIME if True, set lims to 0-24 & Units to Fractional_hours! 
            allowed_vars[var]['Min_Value']=0 
            allowed_vars[var]['Max_Value']=24 
            allowed_vars[var]['Units']='fractional_hours'    
    
    # Check to see if user wants to change Vertical levels where calcs are done & update lims accordingly... 
    zbase=allowed_vars['zbase']['Default_Value'] if 'zbase' not in list(variable_changes.keys()) else variable_changes['zbase']
    zstart=allowed_vars['zstart']['Default_Value'] if 'zstart' not in list(variable_changes.keys()) else variable_changes['zstart']
    zstop=allowed_vars['zstop']['Default_Value'] if 'zstop' not in list(variable_changes.keys()) else variable_changes['zstop']      
    for var in ['zbase', 'zout','ztop']: 
        if var !='ztop': 
            allowed_vars[var]['Min_Value']=zstart # must be > zstart 
        else: 
            allowed_vars[var]['Min_Value']=zbase # must be > zbase 
        allowed_vars[var]['Max_Value']=zstop # must be < zstop 
    
    # Set lims for  iwfix" and "izfix" accordingly... 
    allowed_vars['iwfix']['Max_Value']=allowed_vars['nwint']['Default_Value'] if 'nwint' not in list(variable_changes.keys()) else variable_changes['nwint']
    allowed_vars['izfix']['Max_Value']=allowed_vars['nz']['Default_Value'] if 'nz' not in list(variable_changes.keys()) else variable_changes['nz']

    return allowed_vars 
    
    return allowed_vars

def bound_err(cvar:str, value, allowed, gt_gteq:str,extra_allowed:list=list([])): 
    """Wrapper function to format bounding error messages called in check_inputs()"""
    err= 'Input value for "'+cvar+'" must be '+gt_gteq+' '+str(allowed)+'. You entered: '+cvar+' = '+str(value)
    return err 

###############################################################################
# 3 - Helper Functions used exclusively in function write_TUV_input_file() 
###############################################################################
def is_scientific_notation(s):
    """Helper function called in write_TUV_input_file() to determine if a string 
    contains scientific notation or not like '9.999E+02'"""
    
    # Define a regular expression pattern for scientific notation
    pattern = r'^[+-]?\d+(\.\d+)?[eE][+-]?\d+$'

    # Use re.match to check if the string matches the pattern
    return bool(re.match(pattern, s))


def format_scientific_notation(template, new_value):
    """Helper function called in write_TUV_input_file() to extract formatting 
    of template string in scientific notation and modify the user input value 
    to be identically formatted. """
    
    # Extract the formatting details from the template
    template_parts = template.split('E')
    before_decimal = sum([1 for v in template_parts[0].split('.')[0] if v.isnumeric()])
    after_decimal = sum([1 for v in template_parts[0].split('.')[1] if v.isnumeric()])
    
    # First pass at formatting the new value like that in the template: 
    template_mantissa_format = '{:0' + str(before_decimal+after_decimal+1)+'.' +str(after_decimal)+ 'f}'
    template_exponent_format = '{:+03d}'

    # Second pass at formating the new value
    new_mantissa, new_exponent = f'{new_value:E}'.split('E')
    
    # and final pass at formatting the new value ... used to keep same # in front/behind decimal before E notation. 
    multiply= 10**(before_decimal-1) # 2 digits = 10, 3 =100, 4 = 1000 
    exp_minus =before_decimal-1 # 2 digits =*10, minus =1, 3 digits = *100, minus = 2
    new_formatted = template_mantissa_format.format(float(new_mantissa)*multiply) + 'E' + template_exponent_format.format(int(new_exponent)-exp_minus)

    return new_formatted

###############################################################################
# 4 -Main Functions that are called within wrapper functions in pyTUV.py
###############################################################################
def check_inputs(variable_changes, j_options): 
    """Function to check that user input changes are in allowed ranges. 
    Returns dict "allowed_vars" and a modified version of input "variable_changes".
    Will error out if baddies found!"""
   
    # Get a list of all allowed Variables and their min/max values given the user's 
    # desired variable changes (since some lims depend on var inputs!) 
    allowed_vars = get_and_set_lims(variable_changes)
    
    bypass_min=list([]) # Make empty list of vars to bypass checking mins on ... 
    
    # Loop over all vars the user wants to change ... 
    for cvar in list(variable_changes.keys()): 
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # Make sure Vars are actual Inputs to TUV & Are formatted correctly...  
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        value=variable_changes[cvar] # Get value user wants to set cvar to .. 
        
        # Check to make sure var is actually an input (so script can actully find the line to modify) 
        if cvar not in list(allowed_vars.keys()): 
            raise ValueError('The variable, "'+cvar+'" was not recognized as a TUV input variable. \n'+
                             '    Perhaps a Spelling/Capitolization Error? (Should be all lowercase.)').with_traceback(sys.exc_info()[2]) 
        
        # Check to make sure var is one the user should be allowed to change. Locked vars are those that should NOT be changed or are cal'd automatically. 
        if allowed_vars[cvar]['Locked_TF'] is True: 
            raise ValueError('You should NOT be modifying this input. It is either required (i/o filename) or calculated automatically in this script.').with_traceback(sys.exc_info()[2]) 
        
        # Convert bool variables to appropriate strings if entered as actual bools or as a string other than "T" or "F": 
        if (allowed_vars[cvar]['Type'] == 'bool'):  
            assign='?'
            if type(value)==bool: 
                assign = 'T' if value ==True else 'F'
            elif type(value)==str: 
                if value.lower() in ['t','true']: assign ='T' 
                elif value.lower in ['f','false']: assign ='F'
            if assign=='?': 
                raise ValueError('Input for "'+cvar+' must be either: \n' +
                                 '    (1) A (case insensitive) string containing one of ["t","true","f","false"] \n'+ 
                                 '    (2) A python boolean variable with a value of either "TRUE" or "FALSE" \n'+ 
                                 'You entered: '+cvar+'='+str(value)).with_traceback(sys.exc_info()[2]) 
            else: 
                variable_changes[cvar]=assign 
             
        # Check to see if value is supposed to be numerical (float or int) & make sure value is numerical! 
        if (allowed_vars[cvar]['Type'] != 'str') and (allowed_vars[cvar]['Type'] != 'bool'):
            allowed=[np.int32, np.int64, int, np.float32, np.float64, float]
            is_numeric=[True if type(variable_changes[cvar])==this_type else False for this_type in allowed] 
            if not any(is_numeric):
                try: 
                    if allowed_vars[cvar]['Type'] =='np.float64':
                        value=np.float64(value) 
                    elif allowed_vars[cvar]['Type'] =='np.int32':
                        value=np.int32(value) 
                except ValueError:  
                    raise ValueError('Input for "'+cvar+'" must be numeric (types allowed=[np.int32, np.int64, int, np.float32, np.float64, float]).\n'+
                                 'You entered '+cvar+'='+str(value)+' with type='+str(type(value))).with_traceback(sys.exc_info()[2]) 
        
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # Variable Specific Value/Range Allowed Checks: 
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%    
        if (cvar=='nstr') and (np.mod(value,2)!=0): # Nstr must be even. 
            raise ValueError(bound_err(cvar, value, '', 'an even number')).with_traceback(sys.exc_info()[2]) 
         
        if (cvar=='nwint') and (value <0) and (value not in [-156, -7]): 
            raise ValueError(bound_err(cvar, value, '', 'positive UNLESS it is set to -156 (Default for Trop/Strat) OR -7(Trop/Fast-TUV)')).with_traceback(sys.exc_info()[2]) 
        elif (cvar=='nwint') and (value <0) and (value in [-156, -7]): 
            bypass_min.append(cvar)
            
        if cvar in ['psurf','zaird','ztemp','tauaer'] and value < 0: 
            default=allowed_vars[cvar]['Default_Value']
            bypass_min.append(cvar)
            if value!=default: 
                variable_changes[cvar]=default
                print('NOTE: Value for '+cvar+' was negative (which is allowed, indicating a Default Value should be used). \n'+
                  '      This value was updated from: '+cvar+'='+str(value)+' to the expected default value of: '+cvar+'='+str(default)+'.\n'+ 
                  '      This change should NOT impact your calculation, just helps format the input files better...') 

        # Check for min/max value compliance when bound is NOT a NaN or Str or in bypass list! 
        if (type(allowed_vars[cvar]['Min_Value'])!= str) and (np.isnan(allowed_vars[cvar]['Min_Value'])==False) and \
            (value < allowed_vars[cvar]['Min_Value']) and (cvar not in bypass_min): 
            raise ValueError(bound_err(cvar, value, allowed_vars[cvar]['Min_Value'], '>')).with_traceback(sys.exc_info()[2]) 

        if (type(allowed_vars[cvar]['Max_Value'])!= str) and (np.isnan(allowed_vars[cvar]['Max_Value'])==False) and \
            (value > allowed_vars[cvar]['Max_Value']):     
            raise ValueError(bound_err(cvar, value, allowed_vars[cvar]['Max_Value'], '<=')).with_traceback(sys.exc_info()[2]) 
        
        # Delete vars for easy updates on next loop. 
        del value, cvar
    
    # Check that J-Options are set correctly & return list of Js to turn on! 
    j_rxns_to_calc= check_joptions(j_options)
    
    # Count # of j-rxns and add/update the var "nmj" (# of js to do calc on) in "changes" 
    # (done after checking if value "can" be set/ if locked or not ... ) 
    variable_changes['nmj']=len(np.unique(j_rxns_to_calc)) 
    
    # Reorder the vars in variable_changes so they appear in the same order they do on the lines in the template file: 
    ln_no=[allowed_vars[cvar]['Line_No'] for cvar in list(allowed_vars.keys())] # List of line #s each var appear on 
    keys=[cvar for cvar in list(allowed_vars.keys())] # List of keys correspondiong to line # in ln_no list... 
    sort_ind=np.argsort(ln_no) # Get indexes that would sort list, ln_no 
    key_order=[keys[ind] for ind in sort_ind] # Re oder list "keys" to get keys in order they appear on lines: 
        
    # Create an ORDERED DICTIONARY where keys appear in order corresponding to line nos they appear on in template file. 
    var_changes = OrderedDict({key: variable_changes[key] for key in key_order if key in list(variable_changes.keys())})
    
    return allowed_vars, var_changes,j_rxns_to_calc


def write_TUV_input_file(variable_changes, j_rxns, output_file:str='', verbose:bool=True):
    """Function to read in the template file, change the vars in 'variable_changes', 
    turn on the J-value calculations for rxns in 'j_rxns' and write a new TUV 
    input file accordingly to 'output_file'""" 
    
    # Get a list of ALL photolysis reactions in the template file: 
    js= build_jmapping_dict(only_MCM_Js=False, return_reverse=False)
    allowed_rxns=list(js.keys()) # has NO SPACES!
    
    # Get the paths to all the input files (we need the template file here). 
    paths= get_my_relative_paths()
        
    # Read in the template file
    with open(paths['TUV_InputFile_Template'], 'r') as infile:
        lines = infile.readlines()
            
    # Modify the values based on the provided changes
    for i, line in enumerate(lines):
        ######################################################################################################
        # First lop over all variables you want to change & update those lines first since they apppear first! 
        ######################################################################################################
        for variable, new_value in variable_changes.items():
            # Make sure you're parsing the "new"/potentially updated line ... 
            line=lines[i] 
            
            var2check=variable+' ='
            # Check if the variable is present in the line
            if var2check in line:
                # Split the line into 3 chunks of 20 char len variable definitions, each seperated by 3 spaces! 
                chunks = [line[0:20], line[23:43],line[46:66]]
                
                # Find the (column) index of the chunk containing the variable (col0, col1, col2)
                chunk_index = next(index for index, chunk in enumerate(chunks) if var2check in chunk)
                
                # Find the index where the variable definition starts in the chunk 
                #(e.g. where 'lon =' appears in 'lon =        -87.250')... Usually 0,23,46
                start_index = chunks[chunk_index].index(var2check)
                
                if start_index in [0,23,46]: # Make sure it STARTS were vars start in chunks.. otherwise its a halfsie! 
                    
                    # Pull out the variable declaration only: (e.g. extract 'lon =' in 'lon =        -87.250')
                    variable_dec= chunks[chunk_index][start_index:start_index+len(var2check)]
                                    
                    # Extract ONLY the variable value currently assigned (including preceding spaces) 
                    # e.g. '        -87.250' in 'lon =        -87.250'
                    fullvarvalue=chunks[chunk_index][start_index+len(var2check):]
                    
                    # And now pull out the actual value, no spaces (e.g. '-87.250')
                    var_value=fullvarvalue[[i for i,char in enumerate(fullvarvalue) if char!= ' '][0]:]
                    
                    #################################################################################
                    # Format the NEW Value in the SAME WAY the one in the template is Formatted: 
                    #################################################################################
                    #(1) For #s not in scientific notation, with DECIMALS, use same # before/ after Decimal!  
                    if '.' in var_value and is_scientific_notation(var_value)==False and \
                        'T' not in var_value and 'F' not in var_value: 
                        # Extract the number of decimal places used in the original value assigned! 
                        decimal_places = len(var_value.split('.')[-1])
                        
                        # Format the NEW value in the same way: 
                        new_value= "{:.{prec}f}".format(new_value, prec=decimal_places)
                        
                    #(2) For #s in scientific notation, use same # before/ after Decimal, but in E notation...   
                    elif is_scientific_notation(var_value):
                        new_value = format_scientific_notation(var_value, new_value)
                        
                    #(3) For INTEGERS, use precision = 0, no decimals:      
                    elif '.' not in var_value and is_scientific_notation(var_value)==False and \
                        'T' not in var_value and 'F' not in var_value:
                        # Format the NEW value in the same way: 
                        new_value= "{:.{prec}f}".format(new_value, prec=0)
                        
                    #(4) For T/F strings, just make sure spaces are rmeoved:      
                    elif (('T' in var_value) or ('F' in var_value)) and \
                    is_scientific_notation(var_value)==False and '.' not in var_value: 
                        new_value=new_value.replace(' ','') 
                        
                    # Figure out how many spaces to put in between the var def and value to make a len 20 char! 
                    nspaces =20 -len(variable_dec) - len(new_value)
                    
                    # Now stich the variable delcartion, # of spaces & new value together 
                    # to redefine the chunk, hopefully in the same format! 
                    new_chunk=variable_dec+(' '*nspaces)+new_value
                        
                    # Update the value for this arg while maintaining the original formatting
                    chunks[chunk_index] = new_chunk
                    
                    # Combine the chunks back into the line seperated by 3 spaces & with a new line char at end. 
                    line='   '.join(chunks)+'\n' # update line so subsequent changes on same line are included! 
                    lines[i] = line # update "Lines" so stuff is actually written to output file 
                                        
                    del  new_chunk, variable_dec, new_value, nspaces, var_value, fullvarvalue
                del chunk_index, chunks, start_index, var2check

        #######################################################################
        # After all INPUT VARS have been set, move on to changing Js as Needed. 
        #######################################################################
        for rxn in allowed_rxns: # Loop over all allowed reactions (NOTE: rxns don't have spaces in allowed_rxns!) 
            if rxn in line.replace(' ','') and rxn in j_rxns: # if this is a rxn you wanted to change & its on this line 
                line='T'+line[1:] # Then set it to "TRUE" to do calc: 
            elif rxn in line.replace(' ', '') and rxn not in j_rxns: # if the rxn is on the line but its NOT one to change... 
                line ='F'+line[1:]  # Then set it to "False" and don't calc it! 
        lines[i]=line # Update "Lines" so stuff is actually written to output file! 
                      
    ###########################################################################
    # Write the actual TUV input File: 
    ###########################################################################
    
    # Now write the lines to the new output file! 
    with open(output_file, 'w') as outfile:
        outfile.writelines(lines)
            
    # Tell the people where you saved their file! 
    if verbose is True: print('Output File Saved at: '+output_file)
    
    return     

###############################################################################
# 5 - Helper Functions used exclusively in function make_TUV_input_file_daterange() in pyTUV.py
###############################################################################
def get_value_at_index(data_dict, index):
    """Helper function to subselect data at 'index' from a dictionary, 'data_dict',  with lists as values. 
    Called within make_TUV_input_file_daterange()/ """
    selected_values = {}
    
    for key, value in data_dict.items():
        if isinstance(value, (list, np.ndarray)) and len(value) > index:
            selected_values[key] = value[index]
        else:
            selected_values[key] = None  # Or any default value you prefer
    
    return selected_values

