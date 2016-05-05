## FAM_NMRbot execution script    v.20140226
##  Custom python script for >= Topspin 2.5.
##  Loads and runs preselected list of parameter sets on series of samples.
##  To modify for your own experiment series, change parlt list entries to your 
##  choice of parameter sets that will be run in order.
##  written by L.Clos (lclos@nmrfam.wisc.edu)
##  To access, place this file in <Topspin home>/exp/stan/nmr/py/user/
##  Type this file name in Topspin command line to start
################################################################################
# import FAM_Tools library
try:
    toppath = sys.getEnviron()['XWINNMRHOME'] #TOPSPINver < 3,1
except:
    toppath = sys.registry['XWINNMRHOME'] #TOPSPINver > 3.1
sys.path.append(toppath+'/exp/stan/nmr/py/user')
from FAM_Tools import *
## This is only section user should modify #####################################
title = 'NMRbot_standard_title' # title should not have spaces
funclt = [] # list of NMRbot manual input methods.  Full list below can be 
            # uncommented and modified to select info to be asked during setup.
#funclt = ['series_watstd','sample_num','sample_names','sample_solvs',\
#          'sample_positions','sample_parlts','sample_folderformat',\
#          'sample_conds','sample_NSmult','sample_expadapt','series_getprosol',\
#          'series_findH2Ooffset','series_wobb','series_shimcmd','series_autogain']
parlt = ['standard1D'] # list of parameter set names to choose from
extratxt = 'This is extra text to describe purpose'
## DO NOT modify below #########################################################
exprun = NMRbot(title) # instantiate NMRbot object
exprun.initiate_newrun(funclt,parlt,extratxt) # initiate NMRbot input wizard
