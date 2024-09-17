
import struct
from .dex_support import *

def parseLog(resultsFile, parseData, outputFile, requested):

    resultsFile.seek(0, 2) # last byte
    resultsFileTotalBytes = resultsFile.tell()
    resultsFile.seek(0, 0) # byte0
    thisRecordNumber = 0

    while resultsFile.tell() < resultsFileTotalBytes:
        thisRecordByte0 = resultsFile.tell()
        thisRecordNumber += 1

        testerHeader = resultsFile.read(testerHeaderSize)
        thisRecordSize, resultsKey, _ = struct.unpack(testerHeaderFormat,testerHeader)
        
        if resultsKey in (2,3,7,16,17):
            restOfRecord = resultsFile.read(thisRecordSize-testerHeaderSize)
            if crcCheck(testerHeader, restOfRecord, crcFormat, crcSize):
                restOfRecord = restOfRecord[:-crcSize]
            else:
                resultsFile.seek(thisRecordByte0)
                testerHeader = resultsFile.read(oldTesterHeaderSize)
                restOfRecord = resultsFile.read(thisRecordSize-oldTesterHeaderSize)
                restOfRecord = restOfRecord[:-1]
        else:
            resultsFile.seek(thisRecordByte0)
            testerHeader = resultsFile.read(oldTesterHeaderSize)
            restOfRecord = resultsFile.read(thisRecordSize-oldTesterHeaderSize)
            restOfRecord = restOfRecord[:-1]

        testNumber, errorCode, blockType = struct.unpack(firmareHeaderFormat,restOfRecord[:firmareHeaderSize])

        if blockType == 1:
            if crcCheck(None, restOfRecord[2:], crcFormat, crcSize):
                resultsData = restOfRecord[firmareHeaderSize:-crcSize]
            else:
                testNumber, errorCode, resultsData = processOldFirmwareHeader(restOfRecord)
        else:
            testNumber, errorCode, resultsData = processOldFirmwareHeader(restOfRecord)
        if (testNumber > -44) and (testNumber < 0):
            continue
        
        if testNumber == -44:
            returnedSpcId = parseSpcId(resultsData)
            if returnedSpcId != None:
                parseData['spcId'] = returnedSpcId

            if requested['tableCode'] == -1:
                parseScriptTable(resultsData, requested, parseData, outputFile)

            if requested['tableCode'] == -2:
                parseMatch(resultsData, requested, parseData, outputFile)
                
            if requested['tableCode'] == -99:
                parseAll(resultsData,outputFile)

        if requested['tableCode'] >= 0:
            parseData = parseResult(resultsData, requested, parseData, outputFile)
            partialResults = (testNumber & 0x8000)>0
 

            if (parseData['tseState'] == 'STATE_TEST_START') and (not partialResults):
                parseData['testSeqEvent'] += 1
                parseData['tseState'] == 'STATE_TEST_DONE'

def parse_Text_log(r_file,opened_output):
    request = {}
    request['tableCode'] = -99
    with open (r_file,'rb') as r_open:
        parseLog(resultsFile=r_open,parseData={},outputFile=opened_output,requested=request)

