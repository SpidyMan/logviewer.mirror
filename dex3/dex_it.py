# Edited from dex.py 
# to suppor function calling from other script without argument parser.


import sys,time,os
try:
  from .parseresults import ResultsParser,VERSION
except ImportError:
  from parseresults import ResultsParser,VERSION


def validateFile(userOptions,userOptionsKey,defaultFileName):
  if userOptionsKey in userOptions:
    if not os.path.isfile(userOptions[userOptionsKey]):
      if not os.path.isdir(userOptions[userOptionsKey]):
        print("ERROR:  %s is not a valid file or directory" % (userOptions[userOptionsKey]))
      else:
        userOptions[userOptionsKey] = os.path.join(userOptions[userOptionsKey],defaultFileName)

  else:
    userOptions[userOptionsKey] = defaultFileName


def dex_file(r_file,output_file):
    startTime = time.time()
    paramFileName = "param_cd.h"
    errorCodeFileName = "codes.h"
    procErrorCodeFileName = "proc_codes.h"
    messagesFileName = "messages.h"

    userOptions = {}
    userOptions["textResultsOnly"] = 1
    resultsFileName = r_file
    userOptions["textFileName"] = output_file
    print(f'rfile:{resultsFileName}')
    # Determine if file info passed in is valid or if defaults should be used
    validateFile(userOptions,"paramFile", paramFileName)
    validateFile(userOptions,"errorCodeFile", errorCodeFileName)
    validateFile(userOptions,"procErrorCodeFile", procErrorCodeFileName)
    validateFile(userOptions,"messagesFile", messagesFileName)

    # Find the file name to pass so the output files can use the same name as the input file
    try:
      head,tail = os.path.split(resultsFileName)
      userOptions["outputFileName"],fileExtension = tail.split(".",1)
    except:
      print("ERROR:  Not a valid results file name %s" % (resultsFileName))
      return


    ResultsParser.createDEXHandlers(userOptions,startTime)
    # We must tell the embedded/shared callback function to NOT save the results to the results file.
    ResultsParser.saveToResultsFile = 0
    errNum, errMsg = ResultsParser.processResultsFile(resultsFileName)
    print("DEX Run-Time errorCode: ", errNum, errMsg)
    return resultsFileName


    
if __name__ == "__main__":
  dex_file('B04G7534.4925102601.r','B04G7534.4925102601.txt')
  