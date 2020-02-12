"""
RegridDataPlane with Python Embedding
=====================================

This use case will run the MET RegridDataPlane tool to regrid data using a python embedding script to read the input data.

"""
##############################################################################
# Scientific Objective
# --------------------
#
# None. Simply regridding data to match a desired grid domain for comparisons.

##############################################################################
# Datasets
# --------
#
# | **Forecast:** ASCII sample file
#
# | **Location:** All of the input data required for this use case can be found in the sample data tarball. Click here to download: https://github.com/NCAR/METplus/releases/download/v3.0/sample_data-met_test-9.0.tgz
# | This tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#
# | **Data Source:** Unknown

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus RegridDataPlane wrapper to generate a command to run the MET tool RegridDataPlane if all required files are found.

##############################################################################
# METplus Workflow
# ----------------
#
# RegridDataPlane is the only tool called in this example. It processes a single run time, but the data does not contain any time information in the filename, so the run time is irrelevant.
#
# This use case regrids data to another domain specified with REGRID_DATA_PLANE_VERIF_GRID. This is done so that
# forecast and observation comparisons are done on the same grid. Many MET comparison tools have regridding capabilities
# built in. However, if the same file is read for comparisons multiple times, it is redundant to regrid that file each time.
# Running RegridDataPlane allows you to regrid once and use the output it many comparisons/evaluations.

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c parm/use_cases/met_tool_wrapper/RegridDataPlane/RegridDataPlane_python_embedding.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/RegridDataPlane/RegridDataPlane_python_embedding.conf

##############################################################################
# MET Configuration
# ---------------------
#
# None. RegridDataPlane does not use configuration files.
#

##############################################################################
# Running METplus
# ---------------
#
# This use case can be run two ways:
#
# 1) Passing in RegridDataPlane_python_embedding.conf then a user-specific system configuration file::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/RegridDataPlane/RegridDataPlane_python_embedding.conf -c /path/to/user_system.conf
#
# 2) Modifying the configurations in parm/metplus_config, then passing in RegridDataPlane_python_embedding.conf::
#
#        master_metplus.py -c /path/to/METplus/parm/use_cases/met_tool_wrapper/RegridDataPlane/RegridDataPlane_python_embedding.conf
#
# The former method is recommended. Whether you add them to a user-specific configuration file or modify the metplus_config files, the following variables must be set correctly:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs). This is not required to run METplus, but it is required to run the examples in parm/use_cases
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
# Example User Configuration File::
#
#   [dir]
#   INPUT_BASE = /path/to/sample/input/data
#   OUTPUT_BASE = /path/to/output/dir
#   MET_INSTALL_DIR = /path/to/met-X.Y 
#
# **NOTE:** All of these items must be found under the [dir] section.
#

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
# Output for this use case will be found in met_tool_wrapper/RegridDataPlane/regrid_py (relative to **OUTPUT_BASE**)
# and will contain the following file:
#
# * numpy_data.nc

##############################################################################
# Keywords
# --------
#
# .. note:: `RegridDataPlaneToolUseCase <https://ncar.github.io/METplus/search.html?q=RegridDataPlaneToolUseCase&check_keywords=yes&area=default>`,_`PythonEmbeddingUseCase <https://ncar.github.io/METplus/search.html?q=PythonEmbeddingUseCase&check_keywords=yes&area=default>`__