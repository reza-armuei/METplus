from __future__ import print_function

import pandas as pd
import os
import sys
        
import read_xiv_met as inn

########################################################################

# Mapping of NRL Innovation "jvar" ID's to human-readable strings
jvar_map = {'1':'GHGT',
            '2':'TVRT',
            '3':'UWND',
            '4':'VWND',
            '5':'PSRH',
            '6':'OMXR',
            '7':'WDIR',
            '8':'WSPD',
            '9':'THCK',
            '10':'MSLP',
            '11':'PSTN',
            '12':'TDPD',
            '13':'BTDK',
            '14':'TPPW',
            '15':'QMXR',
            '16':'TPOT',
            '17':'RFRA'}

print('Python Script:\t', sys.argv[0])

   ##
   ##  input file specified on the command line
   ##  load the data into the numpy array
   ##

if len(sys.argv) == 2:
    # Read the input file as the first argument
    input_file = os.path.expandvars(sys.argv[1])
    try:
        print("Input File:\t" + repr(input_file))

        # Read and format the input 11-column observations:
        #   (1)  string:  Message_Type
        #   (2)  string:  Station_ID
        #   (3)  string:  Valid_Time(YYYYMMDD_HHMMSS)
        #   (4)  numeric: Lat(Deg North)
        #   (5)  numeric: Lon(Deg East)
        #   (6)  numeric: Elevation(msl)
        #   (7)  string:  Var_Name(or GRIB_Code)
        #   (8)  numeric: Level
        #   (9)  numeric: Height(msl or agl)
        #   (10) string:  QC_String
        #   (11) numeric: Observation_Value

        #point_data = pd.read_csv(input_file, header=None, delim_whitespace=True, keep_default_na=False,
        #                  names=['typ', 'sid', 'vld', 'lat', 'lon', 'elv', 'var', 'lvl', 'hgt', 'qc', 'obs'],
        #                  dtype={'typ':'str', 'sid':'str', 'vld':'str', 'var':'str', 'qc':'str'}).values.tolist()

        # Get a file object from the NRL input file
        fobj = inn.from_file(input_file)

        # If you want everything in the file for further inspection, use as_dataframe()
        # If you want to subset to the MET 11-column ASCII format for ASCII2NC, use as_met_dataframe() and set the corresponding METplus
        # [user_env_vars]
        #df = fobj.as_dataframe()
        df = fobj.as_met_dataframe()
        
        # Remap the 'var' column to human strings
        col_dtypes = {'typ':'str',
                      'sid':'str',
                      'vld':'str',
                      'lat':'float64',
                      'lon':'float64',
                      'elv':'float64',
                      'var':'str',
                      'lvl':'float64',
                      'hgt':'float64',
                      'qc':'str',
                      'obs':'float64'}
        df = df.replace({"var":jvar_map})
        df = df.astype(col_dtypes)
        
        # Convert the returned dataframe into a list of lists for MET to handle
        point_data = df.values.tolist()

        print("Data Length:\t" + repr(len(point_data)))
        print("Data Type:\t" + repr(type(point_data)))
    except NameError:
        print("Can't find the input file")
else:
    print("ERROR: read_ascii_point.py -> Must specify exactly one input file.")
    sys.exit(1)

########################################################################
