#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 15:48:59 2023

@author: u6044586
"""

import os
import sys 
import pandas as pd 
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates

# Temporary Work Around to Import all functions in pyTUV Module from files: pyTUV.py and utils.py
sys.path.append('/uufs/chpc.utah.edu/common/home/u6044586/python_scripts/modules/pyTUV/')
from pyTUV import *
from utils import * 

# Get & print info about all allowed TUV input variables (type, default value, 
# min/max allowed, units, description), returned as a dict!  
tuv_info=get_TUV_input_info(print_info=True) # If you don't want to print every time, set print_info=False.

#------------------------------------------------------------------------------
# Example #1a: Make a SINGLE new input TUV file 
#------------------------------------------------------------------------------
def example1a_write_single_input(savepath:str=''): 
    """Make a SINGLE new input TUV file at Alta in Utah on 08/17/2022 
    at 30min intervals using specific aerosol optical depth varaibles 
    over the range 289nm-750nm & get output of all J-Values only at 
    Alta Surface Elevation (2.638 km).
    
    INPUT: 
    ------
       (1) savepath - path where new TUV input files should be saved on your computer. 
                   If not passed, will be saved at '.../pyTUV/Examples/Example1/TUV_InputFiles/'
    OUTPUT: 
    ------ 
       (1) A New TUV input file saved at 'savepath' or if none passed, 
            saved at '.../pyTUV/Examples/Example1/TUV_InputFiles/'
    """
    if savepath=='': 
        paths= get_my_relative_paths() # Call function that tells us where you have pyTUV saved on your computer. 
        savepath=paths['Example1_Inputs']# Should point to '.../pyTUV/Examples/Example1/TUV_InputFiles/'
        
    joptions='only_MCM_js' # Set to calculate all MCM J-Values 
    
    # Vars not inputted in changes will use DEFAULT VALUES listed in tuv_info... 
    changes = dict({ 'iyear':2021,   'imonth':8,         'iday':13,      # Do calc on Aug. 13th, 2022
                       'lat':40.589,   'lon':-111.638, 'tmzone':-6,      # Do calc at Alta,UT lat/lon in timezone in MST (MST= UTC-6)
                    'tstart':0.0,    'tstop': 23.5,        'nt':48,      # Do calcs over whole day in 30min steps! 
                    'zstart':0.368,  'zstop': 119.368,     'nz':119,     # Do calc from 0.368km - 119.368 km in 119 vertical levels steps
                    'wstart': 120,   'wstop': 730,       'nwint':-156,   # Do calc over wavelength range 120-730nm in default # of steps...
                    'tauaer': 0.235, 'ssaer': 0.8,       'alpha': 0.9,   # Set aerosol optical depth, single scattering albedo, & wavelength dependence. 
                      'zout': 2.638})                                    # Get output at a single, fixed altitude (Surf Elev @ Alta =2.638km)
    
    # Call the function to make the TUV input File & overwrite any file already named that!  
    inp_file, changes_done, j_rxns = make_single_TUV_input_file(changes, joptions, savepath, overwrite=True)
        
    return inp_file

#------------------------------------------------------------------------------
# Example #1b  Read in a SINGLE TUV Output File as a pandas dataframe:  
#------------------------------------------------------------------------------
def example1b_read_single_output(output_file:str =''): 
    """Function to read in the output of a single TUV file. For user ease, we have 
    included the output files that TUV generates in example1_write_single_input() 
    at the path '.../pyTUV.Examples/Example1/TUV_OutputFiles/'. But normally, you'll have to 
    run TUV on you own to generate this output file! Our python functionality does NOT include this. """

    # NOTE: By default, ouput files have the same name as the input files, but have 'out_' before them instead of 'inp_'
    # and contain important info about the date & UTC offset used in the calculation. This is the corresponding output
    # file of the input that would be generated in example1_write_single_input() which is named: 
    # 'inp_2021_08_13_offset_neg6' (and has no extension b/c TUV inputs do NOT have an extension!)
    if output_file=='': 
        paths= get_my_relative_paths() # Call function that tells us where you have pyTUV saved on your computer. 
        out_savepath=paths['Example1_Outputs'] # Should point to '.../pyTUV/Examples/Example1/TUV_OutputFiles/'
        
        # Set path to the TUV Output File you want to open 
        output_file= os.path.join(out_savepath, 'out_2021_08_13_offset_neg6.txt')
   
    # Now we will call the function that reads in the output file. TUV Output Files 
    # are stored with fractional_UTC_hour and TUV_rxns as column headers. Our function 
    # converts this back to Datetime_Locals (using the date & UTC offset) and has the 
    # ability to map the TUV reactions to their MCM J-value name if map_to_MCM is set to True. 
    # We will do both & plot the (identical output) so you can see the differences! 
        
    # Read in the output and DO map the TUV rxns to their MCM J-Value Name:                                                                          
    df_MCMnames=read_single_TUV_output(output_file, map_to_MCM=True)    
        
    # Read in the output and DO NOT map the TUV rxns to their MCM J-Value Name:                                                                          
    df_TUVrxns=read_single_TUV_output(output_file, map_to_MCM=False)   
    
    # Optional Note: This is done by calling the (utility function) which maps TUV rnxs --> MCM names.  
    jmap=build_jmapping_dict(only_MCM_Js= True)     
    
    # Thus, if we want to know which J-Value Corresponds to a TUV rxn... 
    TUV_rxn= list(jmap.keys())[0]
    MCM_name=jmap[TUV_rxn] 
    print('The TUV Reaction: {} corresponds to the MCM J-Value Name: {}'.format(TUV_rxn, MCM_name))
    
    # Now let's plot & compare the output of the two dataframes for this rxn/Jname... Their values should be the same! 
    fig, ax1 = plt.subplots(nrows=1,ncols=1,figsize=(14, 5)) 
    ax1.plot(df_MCMnames['Datetime_Local'], df_MCMnames[MCM_name], color='r', marker='o',label=MCM_name)
    ax1.plot(df_TUVrxns['Datetime_Local'], df_TUVrxns[TUV_rxn], color='b', marker='.',label=TUV_rxn)
    
    # Format labels, ticks, etc. 
    ax1.set_xlabel('Local Date & Time'); ax1.set_ylabel(r'Photolysis Frequency ($s^{-1}$)')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%D %I%p')) # Tells it how to display the date/ hours
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=2)) # plots a major tick each 2 hours
    ax1.xaxis.set_minor_locator(mdates.HourLocator(interval=1)) # plots a minor tick each 1 hours
    ax1.minorticks_on(); plt.xticks(rotation=30, ha='right'); ax1.tick_params(which='major', length=5, width=2)
    ax1.legend(); plt.tight_layout(); plt.grid(); plt.show() 
    
    # Now suppose you wanted to export this data into a .mat file to use in F0AM? 
    # you can do that by calling this function from pyTUV.py which will export the 
    # df into a matlab struct stored in a .mat file! 
    export_js_to_mat(df_MCMnames, outpath=out_savepath, outfile='tuv_output')
        
    return df_MCMnames, df_TUVrxns
    
#------------------------------------------------------------------------------
# Example #2a  Make several new input TUV files over a range of dates at same lat/lon: 
#------------------------------------------------------------------------------
def example2a_write_daterange_input(savepath:str= ''):
    """Make several new input TUV files at Hawthrone Elementeray in SLC,Utah  
    to calculate all MCM J-Values at 30min intervals using the same 
    lat/lon/aerosol characteristics in the time range 06/01/2021 - 06/07/2021
    and get output of all J-Values only at Hathorne Elemetary Surface Elevation (1306 km). 
    
    INPUT: 
    ------
       (1)  savepath - path where new TUV input files should be saved on your computer. 
                   If not passed, will be saved at .../pyTUV/Examples/Example2/TUV_InputFiles/
                   
    OUTPUT: 
    ------ 
       (1)   A range of new TUV input files saved at 'savepath' or if none passed, 
             saved at '.../pyTUV/Examples/Example2/TUV_InputFiles/'
       
    """
    if savepath=='': 
        paths= get_my_relative_paths() # Call function that tells us where you have pyTUV saved on your computer. 
        savepath=paths['Example2_Inputs'] # Should point to '.../pyTUV/Examples/Example2/TUV_InputFiles/'
        
    joptions='only_MCM_js' # Set to calculate all MCM J-Values 
    
    # Set daterange and period of times to 30mins to do calcs on each day .... 
    daterange= pd.date_range(start='2021-06-01', end='2021-06-07', periods=None, freq='0.5H')
    
    # Vars not inputted in changes will use DEFAULT VALUES listed in tuv_info Except Date/Time which is set using 'ex2_daterange' 
    changes = dict({   'lat':40.734,  'lon':-111.872, 'tmzone':-6,    # Do calc at SLC,UT lat/lon in timezone in MST (MST= UTC-6)
                    'zstart':0.306, 'zstop': 119.306,     'nz':119,   # Do calc from 0.130km - 119.130 km in 119 vertical levels steps
                    'wstart':120,   'wstop': 730,      'nwint':-156,  # Do calc over wavelength range 120-730nm in default # of steps...
                    'zout':1.306}) # Get output at a single, fixed altitude (Surf Elev @ Hawthorn =1.306km)
    
    inp_files, all_changes, j_rxns = make_TUV_input_file_daterange(changes, joptions, savepath=savepath, daterange=daterange,overwrite=True)

    return inp_files, all_changes

#------------------------------------------------------------------------------
# Example #2b  Make several new input TUV files over a range of dates at same lat/lon: 
#------------------------------------------------------------------------------
def example2b_read_daterange_input(output_dir:str=''):
    """Function to read in a range of TUV outputs stored in a single directory
    and concatenate them all into a SINGLE pandas dataframe. For user ease, we have 
    included the output files that TUV generates in example2a_write_daterange_input() 
    at the path '.../pyTUV.Examples/Example2/TUV_OutputFiles/'. But normally, you'll have to 
    run TUV on you own to generate this output file! Our python functionality does NOT include this."""
    
    # NOTE: By default, ouput files have the same name as the input files, but have 'out_' before them instead of 'inp_'
    # and contain important info about the date & UTC offset used in the calculation.
    if output_dir=='': 
        paths= get_my_relative_paths() # Call function that tells us where you have pyTUV saved on your computer. 
        output_dir=paths['Example2_Outputs'] # Should point to '.../pyTUV/Examples/Example2/TUV_OutputFiles/'
    
    # Now we will call the function that reads in all the the output files stored 
    # under the output_dir. TUV Output Files are stored with fractional_UTC_hour and 
    # TUV_rxns as column headers. Our function converts this back to Datetime_Locals 
    # (using the date & UTC offset), concatenates all the data from ALL FILES into a single df, 
    # and has the ability to map the TUV reactions to their MCM J-value name if map_to_MCM is 
    # set to True. We will do both & plot the (identical output) so you can see the differences! 
        
    # Read in the outputs, concatenate them in a single DF, and DO map the TUV rxns to their MCM J-Value Name:                                                                          
    df_MCMnames=read_n_combo_TUV_outputs(output_dir, map_to_MCM=True)
        
    # Read in the outputs, concatenate them in a single DF, and DO NOT map the TUV rxns to their MCM J-Value Name:                                                                          
    df_TUVrxns=read_n_combo_TUV_outputs(output_dir, map_to_MCM=False)
    
    # Optional Note: This is done by calling the (utility function) which maps TUV rnxs --> MCM names.  
    jmap=build_jmapping_dict(only_MCM_Js= True)    
    
    # Thus, if we want to know which J-Value Corresponds to a TUV rxn... 
    TUV_rxn= list(jmap.keys())[0]
    MCM_name=jmap[TUV_rxn] 
    print('The TUV Reaction: {} corresponds to the MCM J-Value Name: {}'.format(TUV_rxn, MCM_name))
    
    # Now let's plot & compare the output of the two dataframes for this rxn/Jname... Their values should be the same! 
    fig, ax1 = plt.subplots(nrows=1,ncols=1,figsize=(14, 5)) 
    ax1.plot(df_MCMnames['Datetime_Local'], df_MCMnames[MCM_name], color='r', marker='o',label=MCM_name)
    ax1.plot(df_TUVrxns['Datetime_Local'], df_TUVrxns[TUV_rxn], color='b', marker='.',label=TUV_rxn)
    
    # Format labels, ticks, etc. 
    ax1.set_xlim([min(df_MCMnames['Datetime_Local']), max(df_MCMnames['Datetime_Local'])])
    ax1.set_xlabel('Local Date & Time'); ax1.set_ylabel(r'Photolysis Frequency ($s^{-1}$)')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%D %I%p')) # Tells it how to display the date/ hours
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=6)) # plots a major tick each 2 hours
    ax1.xaxis.set_minor_locator(mdates.HourLocator(interval=3)) # plots a minor tick each 1 hours
    ax1.minorticks_on(); plt.xticks(rotation=30, ha='right'); ax1.tick_params(which='major', length=5, width=2)
    ax1.legend(); plt.tight_layout(); plt.grid(); plt.show() 
    
    # Now suppose you wanted to export this data into a .mat file to use in F0AM? 
    # you can do that by calling this function from pyTUV.py which will export the 
    # df into a matlab struct stored in a .mat file! 
    export_js_to_mat(df_MCMnames, outpath=output_dir, outfile='tuv_output')
    
    return df_MCMnames, df_TUVrxns

#------------------------------------------------------------------------------
# Example #3  Example of FULL DATA FLOW for HASKINS-GROUP users at UUtah 
#             (including running TUV using bash script, run_TUV_batch.sh). 
#------------------------------------------------------------------------------ 
def Haskins_Group_FULL_Example(): 
    """Function to show off how members of the Haskins Group at Utah can use all these 
    functions together. Instructions are specific to how our group runs TUV in batch mode 
    & will not be particularly useful for users outside our group. 
    
    NOTE: This is how Example1a and Example1b wrap together to generate & rad in a SIGNLE file. 
        You could do the same sort of thing for Exampl2a and Example2b if you wanted to generate 
        & read in MULTIPLE files. It's not included, since its redundant once you understand STEP #2.
        More documentation for using pyTUV is provided in the Haskins Group Notion. '
    """
        
    ###########################################################################
    # STEP 1: Generate a TUV input File
    ###########################################################################
    # Tell us where to save your new TUV Input files that will be generated. 
    # We will use an existing directory stored under .../pyTUV/ so you can run the 
    # full example w/o changes, but normally, you'd need to input 'input_savepath'! 
    paths= get_my_relative_paths() # Call function that tells us where you have pyTUV saved on your computer. 
    input_savepath=paths['Example1_Inputs'] # Should point to '.../pyTUV/Examples/Example1/TUV_InputFiles/'
    
    joptions='only_MCM_js' # Set to calculate all MCM J-Values 
    
    # Vars not inputted in changes will use DEFAULT VALUES listed in tuv_info... 
    changes = dict({ 'iyear':2021,   'imonth':8,         'iday':13,      # Do calc on Aug. 13th, 2022
                       'lat':40.589,   'lon':-111.638, 'tmzone':-6,      # Do calc at Alta,UT lat/lon in timezone in MST (MST= UTC-6)
                    'tstart':0.0,    'tstop': 23.5,        'nt':48,      # Do calcs over whole day in 30min steps! 
                    'zstart':0.368,  'zstop': 119.368,     'nz':119,     # Do calc from 0.368km - 119.368 km in 119 vertical levels steps
                    'wstart': 120,   'wstop': 730,       'nwint':-156,   # Do calc over wavelength range 120-730nm in default # of steps...
                    'tauaer': 0.235, 'ssaer': 0.8,       'alpha': 0.9,   # Set aerosol optical depth, single scattering albedo, & wavelength dependence. 
                      'zout': 2.638})                                    # Get output at a single, fixed altitude (Surf Elev @ Alta =2.638km)
       
    # Call the function to make the TUV input File & overwrite any file already named that!  
    inp_file, changes_done, j_rxns = make_single_TUV_input_file(changes, joptions, savepath=input_savepath, overwrite=True)
        
    # We'll print the input file name so you can see what it's named! Compare this to what 
    # the output file is called in step 3:                                                                                                         
    print("The TUV input filename:'{}'".format(os.path.basename(inp_file))) 
              
    ###########################################################################
    # STEP 2: RUN THE TUV MODEL 
    ###########################################################################
    #   To RUN TUV using this input file, open an XFCE Terminal on Notchpeak and 
    #   navigate into the Haskins-Group1/GroupSoftware/TUV directory: 
    #  
    #       >> cd /uufs/chpc.utah.edu/common/home/haskins-group1/GroupSoftware/TUV/
    #
    #   Once there, call our Bash-Script that runs TUV in batch mode, 'run_TUV_batch.sh'
    #   with 'arg1' pointing to the directory where the TUV input files you just made in example1() 
    #   are stored & 'arg2' pointing to where you want to store the output files from TUV. 
    #   Generally, this command will look like this. Note, the SPACE between the bash script 
    #   name and args is IMPORTANT, do NOT skip! 
    #       >> bash run_TUV_batch.sh "path/to/TUV_input_dir" "path/to/TUV_output_dir"
    #
    #   NOTE: The input/output path arguements should be the path that occurs AFTER "/uufs/chpc.utah.edu/common/home/"
    #         So, if the ACTUAL directories were: 
    #                 input_dir= "/uufs/chpc.utah.edu/common/home/haskins-group1/jhask/TUV_Input_Dir/"
    #                 output_dir= "/uufs/chpc.utah.edu/common/home/haskins-group1/jhask/TUV_Output_Dir/"
    #          
    #         You would run TUV in batch mode by doing: 
    #    
    #	       >> bash run_TUV_bath.sh "haskins-group1/jhask/TUV_Input_Dir/" "haskins-group1/jhask/TUV_Output_Dir/"
    #                                  ^SPACE                               ^SPACE     
    #
    #   Doing this will create TUV output file(s) stored arg2 with the same name 
    #   as the input files in arg1. By default they have the form: 
    #   
    #        Input Files:  'inp_YYYY_MM_DD_offset_HR' 
    #        Output Files: 'out_YYY_MM_DD_offset_HR'
    #
    #   NOTE: It is important NOT TO CHANGE the filenames because the python output 
    #         reader in Step 3 expects the date and UTC offset in the output filename 
    #         in this exact form and the output filename is set based on the input 
    #         filename in the bash script. 
    
    ###########################################################################
    # STEP 3: READ IN THE (SINGLE) OUTPUT AS A PANDAS DATAFRAME 
    ###########################################################################
    # Let's now pretend you just ran TUV on this example output file. 
    # How would you read that output it back into python as a pandas dataframe? 
    
    # First, we need the name of the file stored at this output_savepath to open it using 'read_single_TUV_output)'. 
    # By default, ouput files have the same name as the input files, but have 'out_' 
    # before them instead of 'inp_'and contain important info about the date & UTC offset 
    # used in the calculation. Here, we've included the output that Step 1 would generate 
    # so you don't have to change anything for this example to work. But normally, you'd 
    # need to input the output_file for this function to work: 
    output_file= os.path.join(paths['Example1_Outputs'] , 'out_2021_08_13_offset_neg6.txt')

    # We'll print the file so you can see what it's named! Compare this to what the input file was called:                                                                                                         
    print("The TUV output filename:'{}'".format(os.path.basename(output_file)))
         
    # Now we will call the function that reads in the output file. TUV Output Files 
    # are stored with fractional_UTC_hour and TUV_rxns as column headers. Our function 
    # converts this back to Datetime_Locals (using the date & UTC offset) and has the 
    # ability to map the TUV reactions to their MCM J-value name if map_to_MCM is set to True. 
    # We will do both & plot the (identical output) so you can see the differences! 
    
    # Read in the output and DO map the TUV rxns to their MCM J-Value Name:                                                                          
    df_MCMnames=read_single_TUV_output(output_file, map_to_MCM=True)    
    
    # Read in the output and DO map the TUV rxns to their MCM J-Value Name:                                                                          
    df_TUVrxns=read_single_TUV_output(output_file, map_to_MCM=False)    

    # Optional Note: This is done by calling the (utility function) which maps TUV rnxs --> MCM names.  
    jmap=build_jmapping_dict(only_MCM_Js= True)     
    
    # Thus, if we want to know which J-Value Corresponds to a TUV rxn... 
    TUV_rxn= list(jmap.keys())[0]
    MCM_name=jmap[TUV_rxn] 
    print('The TUV Reaction: {} corresponds to the MCM J-Value Name: {}'.format(TUV_rxn, MCM_name))
    
    # Now let's plot & compare the output of the two dataframes for this rxn/Jname... Their values should be the same! 
    fig, ax1 = plt.subplots(nrows=1,ncols=1,figsize=(14, 5)) 
    
    ax1.plot(df_MCMnames['Datetime_Local'], df_MCMnames[MCM_name], color='r', marker='o',label=MCM_name)
    ax1.plot(df_TUVrxns['Datetime_Local'], df_TUVrxns[TUV_rxn], color='b', marker='.',label=TUV_rxn)
    
    # Format labels, ticks, etc. 
    ax1.set_xlabel('Local Date & Time'); ax1.set_ylabel(r'Photolysis Frequency ($s^{-1}$)')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%D %I%p')) # Tells it how to display the date/ hours
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=2)) # plots a minor tick each 3 hours
    ax1.xaxis.set_minor_locator(mdates.HourLocator(interval=1)) # plots a minor tick each 3 hours
    ax1.minorticks_on(); plt.xticks(rotation=30, ha='right'); ax1.tick_params(which='major', length=5, width=2)
    ax1.legend(); plt.tight_layout(); plt.grid(); plt.show() 
    
    # Now suppose you wanted to export this data into a .mat file to use in F0AM? 
    # you can do that by calling this function from pyTUV.py which will export the 
    # df into a matlab struct stored in a .mat file! 
    out_savepath=paths['Example1_Outputs'] # Should point to '.../pyTUV/Examples/Example1/TUV_OutputFiles/'
    export_js_to_mat(df_MCMnames, outpath=out_savepath, outfile='tuv_output')
    
    return df_MCMnames, df_TUVrxns


