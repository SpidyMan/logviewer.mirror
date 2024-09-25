#!/usr/bin/env fofpython
# --------------------------------------------------------------------------------------- #
#                                                                                         #
#                                   Seagate Confidential                                  #
#                                                                                         #
# --------------------------------------------------------------------------------------- #

# ******************************************************************************
#
# VCS Information:
#                 $File: //depot/TCO/DEX/dex.py $
#                 $Revision: #4 $
#                 $Change: 449292 $
#                 $Author: alan.a.hewitt $
#                 $DateTime: 2012/04/30 11:29:44 $
#
# ******************************************************************************

import getopt,string,traceback,sys,time,os
from .parseresults import ResultsParser,VERSION

def dex_file(r_file,result_file):
    
  startTime = time.time()

  def validateFile(userOptionsKey,defaultFileName):
    # Determine if file info passed in is valid
    if userOptionsKey in userOptions:
      if not os.path.isfile(userOptions[userOptionsKey]):
        if not os.path.isdir(userOptions[userOptionsKey]):
          errMsg = "ERROR:  %s is not a valid file or directory" % (userOptions[userOptionsKey])
          # Do not exit for this error as it is not critical for viewing text results
          print(errMsg)
        # If file path was passed in but not file name, assume a default file name
        else:
          userOptions[userOptionsKey] = os.path.join(userOptions[userOptionsKey],defaultFileName)
    # If file path/name was not passed in, assume current directory and default file name
    else:
      userOptions[userOptionsKey] = defaultFileName

  # Set up defaults
  myOptionList = []
  paramFileName = "param_cd.h"
  errorCodeFileName = "codes.h"
  procErrorCodeFileName = "proc_codes.h"
  messagesFileName = "messages.h"
  userOptions = {}
  resultsFileName = r_file
  userOptions["textFileName"] = result_file
  userOptions["textResultsOnly"] = 1


  # Determine if file info passed in is valid or if defaults should be used
  validateFile("paramFile", paramFileName)
  validateFile("errorCodeFile", errorCodeFileName)
  validateFile("procErrorCodeFile", procErrorCodeFileName)
  validateFile("messagesFile", messagesFileName)

  # Find the file name to pass so the output files can use the same name as the input file
  try:
    head,tail = os.path.split(resultsFileName)
    userOptions["outputFileName"],fileExtension = tail.split(".",1)
  except:
    errMsg = "ERROR:  Not a valid results file name %s" % (resultsFileName)

  ResultsParser.createDEXHandlers(userOptions,startTime)

  # We must tell the embedded/shared callback function to NOT save the results to the results file.
  ResultsParser.saveToResultsFile = 0
  errNum, errMsg = ResultsParser.processResultsFile(resultsFileName)


dex_file('.\B04G7534_4925102601.r','zbcdw.txt')