#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 15:48:59 2023

@author: u6044586
"""

import os
import sys 
import pandas as pd 
# Temporary Work Around to Import all functions in pyTUV Module from files: pyTUV.py and utils.py
sys.path.append('/uufs/chpc.utah.edu/common/home/u6044586/python_scripts/modules/pyTUV/')
from pyTUV import *
from utils import * 

# Get & print info about all allowed TUV input variables (type, default value, 
# min/max allowed, units, description), returned as a dict!  
tuv_info=get_TUV_input_info(print_info=False)

#------------------------------------------------------------------------------
# Example #1: Make a SINGLE new input TUV file at Alta in Utah on 08/17/2022 
#             at 30min intervals using specific aerosol optical depth varaibles 
#             over the range 289nm-750nm & get output of all J-Values only at 
#             Alta Surface Elevation (2.638 km) 
#------------------------------------------------------------------------------
def example1(): 
    ex1_joptions='only_MCM_js' # Set to calculate all MCM J-Values 
    
    # Vars not inputted in changes will use DEFAULT VALUES listed in tuv_info... 
    ex1_changes = dict({ 'iyear':2022,   'imonth':8,         'iday':13,      # Do calc on Aug. 13th, 2022
                           'lat':49.589,   'lon':-111.638, 'tmzone':-6,      # Do calc at Alta,UT lat/lon in timezone in MST (MST= UTC-6)
                        'tstart':0.0,    'tstop': 23.5,        'nt':48,      # Do calcs over whole day in 30min steps! 
                        'zstart':0.368,  'zstop': 119.368,     'nz':119,     # Do calc from 0.368km - 119.368 km in 119 vertical levels steps
                        'wstart': 120,   'wstop': 730,       'nwint':-156,   # Do calc over wavelength range 120-730nm in default # of steps...
                        'tauaer': 0.235, 'ssaer': 0.8,       'alpha': 0.9,   # Set aerosol optical depth, single scattering albedo, & wavelength dependence. 
                        'zout': 2.638})                                      # Get output at a single, fixed altitude (Surf Elev @ Alta =2.638km
    
    # Where you'd like to save the TUV Input Files (EDIT THIS ON YOUR COMPUTER!) 
    ex1_savepath= '/uufs/chpc.utah.edu/common/home/u6044586/python_scripts/modules/pyTUV/Outputs/TUV_Input_Files/'
    
    # What the output file should be named: NOTE: TUV Input Files should have NO EXTENSION! 
    ex1_filename= 'inp_2022_08_13'
    
    # Call the function to make the TUV input File & overwrite any file already named that!  
    changes_done, j_rxns =make_single_TUV_input_file(ex1_changes, ex1_joptions, ex1_savepath, ex1_filename, overwrite=True)

    return 

example1() 

#------------------------------------------------------------------------------
# Example #2  Make several new input TUV file at Hawthrone Elementeray in SLC,Utah  
#             to calculate all MCM J-Values at 30min intervals using the same 
#             lat/lon/aerosol characteristics in the time range 06/01/2021 - 09/01/2021
#             and get output of all J-Values only at Hathorne Elemetary Surface Elevation (1306 km) 
#------------------------------------------------------------------------------
def example2():
    ex2_joptions='only_MCM_js' # Set to calculate all MCM J-Values 
    
    # Set daterange and period of times to 30mins to do calcs on each day .... 
    ex2_daterange= pd.date_range(start='2021-06-01', end='2021-09-01', periods=None, freq='0.5H')
    
    # Vars not inputted in changes will use DEFAULT VALUES listed in tuv_info Except Date/Time which is set using 'ex2_daterange' 
    ex2_changes = dict({   'lat':40.734,  'lon':-111.872, 'tmzone':-6,    # Do calc at SLC,UT lat/lon in timezone in MST (MST= UTC-6)
                        'zstart':0.306, 'zstop': 119.306,     'nz':119,   # Do calc from 0.130km - 119.130 km in 119 vertical levels steps
                        'wstart':120,   'wstop': 730,      'nwint':-156,  # Do calc over wavelength range 120-730nm in default # of steps...
                        'izfix':2 }) # Get output at a single, fixed altitude (Surf Elev @ Hawthorn =1.306km  index # for that is=2 in np.arange(wstart,wstop) 
    
    # Where you'd like to save the TUV Input Files (EDIT THIS ON YOUR COMPUTER!) 
    ex2_savepath= '/uufs/chpc.utah.edu/common/home/u6044586/python_scripts/modules/pyTUV/Outputs/TUV_Input_Files/'
    
    make_TUV_input_file_daterange(ex2_changes, ex2_joptions, savepath=ex2_savepath, daterange=ex2_daterange)
    
    return 

    
