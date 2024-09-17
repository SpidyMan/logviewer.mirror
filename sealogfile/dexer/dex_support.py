import struct

testerHeaderFormat = '<Hbb'
testerHeaderSize = struct.calcsize(testerHeaderFormat)

oldTesterHeaderFormat = '<HLbbbb'
oldTesterHeaderSize = struct.calcsize(oldTesterHeaderFormat)

crcFormat = ">H"
crcSize = struct.calcsize(crcFormat)

firmareHeaderFormat = ">hHb"
firmareHeaderSize = struct.calcsize(firmareHeaderFormat)

def createTableHeader(requested, filename):
    headers = ""
    if filename:
        headers += "FILENAME,"

    columns = requested['header']
    colMasks = requested['mask']
    
    headers += "SERIAL_NUM,TRANS_SEQ,EVENT_DATE,SBR,TEST_SEQ_EVENT,SPC_ID," + maskData(columns,colMasks,False)
    
    return headers.encode("utf-8")


def parseResult(resultsData, requested, parseData, outputFile):
    currentTableCode = parseData['currentTableCode']
    sn = parseData['sn']
    ts = parseData['ts']
    date = parseData['date']
    sbr = parseData['sbr']
    tse = parseData['testSeqEvent']
    spcId = parseData['spcId']
    
    try:
        while len(resultsData) >= 4:
            blockSize, blockCode = struct.unpack("HH",resultsData[:4])
            if blockSize < 4 or blockSize > 512:
                print(f'invalid blockSize {testNumber}')
                return
            else:
                blockData = resultsData[4:blockSize]

                if blockCode in [11000, 11002]:
                    if requested['tableCode'] > 0:
                        parseData, maskedData = parseParametric(blockData, blockCode, parseData, requested)
                        if maskedData != None:
                            if parseData['withFilename']:
                                extraInfo = "\n%s,%s,%s,%s,%s,%s,%s," % (parseData['filename'],sn,ts,date,sbr,tse,spcId)
                            else:
                                extraInfo = "\n%s,%s,%s,%s,%s,%s," % (sn,ts,date,sbr,tse,spcId)
                            outputFile.write(extraInfo.encode("utf-8"))
                            outputFile.write(maskedData)
                    else:
                        parseData, matchedData = matchDebugTable(blockData, blockCode, parseData, requested)
                        if matchedData != None:
                            if parseData['withFilename']:
                                extraInfo = "\n%s,%s,%s,%s,%s,%s,%s," % (parseData['filename'],sn,ts,date,sbr,tse,spcId)
                            else:
                                extraInfo = "\n%s,%s,%s,%s,%s,%s," % (sn,ts,date,sbr,tse,spcId)
                            outputFile.write(extraInfo.encode("utf-8"))
                            outputFile.write(matchedData)
            resultsData = resultsData[blockSize:]
    except:
        pass #print(f'Error {testNumber}')
    return parseData

def parseParametric(blockData, blockCode, parseData, requested):
    maskedData = None
    
    if blockCode == 11000:
        currentTableCode = struct.unpack("H", blockData[:2])[0]
        parseData['currentTableCode'] = currentTableCode
        blockData = blockData[2:]
    else:
        currentTableCode = parseData['currentTableCode']

    if currentTableCode == requested['tableCode']:
        parseData['tseState'] = 'STATE_TEST_START'
        try:
            colMasks = requested['mask']
            maskedData = maskData(blockData, colMasks)
        except:
            pass
    return parseData, maskedData

def maskData(resultsData,colMasks,isByte=True):
    if 0 in colMasks:
        if isByte:
            splitChar = b','
        else:
            splitChar = ','
            
        resultsDataList = resultsData.split(splitChar)
            
        if len(colMasks) < len(resultsDataList):
            print('Not enough masks')
            return resultsData

        finalList = []
        for i in range(len(resultsDataList)):
            if colMasks[i] == 1:
                finalList.append(resultsDataList[i])

        resultsData = splitChar.join(finalList)
    
    return resultsData


def matchDebugTable(blockData, blockCode, parseData, requested):
    matchStr = requested['tableName'].encode("utf-8")
    matchedData = None
    
    if blockCode == 11000:
        currentTableCode = struct.unpack("H", blockData[:2])[0]
        parseData['currentTableCode'] = currentTableCode
        blockData = blockData[2:]
    else:
        currentTableCode = parseData['currentTableCode']

    if (currentTableCode == requested['tableCode']) & (blockData.find(matchStr) != -1):
        parseData['tseState'] = 'STATE_TEST_START'
        matchedData = blockData
        
    return parseData, matchedData


def parseSpcId(resultsData):
    if resultsData.find(b"**SPC_ID32=") != -1:
        spcIdString = resultsData.decode("utf-8").split("=",1)
        
        return spcIdString[1].split(" ",1)[0]
    else:
        return None


def parseScriptTable(resultsData, requested, parseData, outputFile):
    returnResult = None
    state = parseData['state']
    tableName = requested['tableName'].encode("utf-8")

    ## NOTE: '\n' is at the beginning of line. That means if you find '\n',
    ##       save current data to output file and create new one
    
    if state == 'TABLE_SEARCH':
        # Search table name
        if resultsData.find(tableName) != -1:
            # Found new table. Reset header
            parseData['state'] = 'ADD_HEADER'
            
    elif state == 'ADD_HEADER':
        # Here is header start.
        parseData['curHeader'] = resultsData
        parseData['state'] = 'FIND_HEADER_END'

    elif state == 'FIND_HEADER_END':
        # Check whether header ends
        if resultsData.find(b"\n") == -1:
            # still header
            parseData['curHeader'] += resultsData
            
        else:
            # \n found meaning table starts now. Write header to file
            parseData = writeScriptTableHeader(parseData, outputFile)
            parseData['state'] = 'TABLE_DATA'

            # Create new data row
            parseData['data'] = resultsData

    elif state == 'TABLE_DATA':
        if resultsData.find(b":::") != -1:
            # End of table
            writeScriptTable(parseData, outputFile)
            parseData['state'] = 'TABLE_SEARCH'
            parseData['testSeqEvent'] += 1

        elif resultsData.find(b"\n") != -1:
            # New row. Write existing data to file
            writeScriptTable(parseData, outputFile)

            # Create new row
            parseData['data'] = resultsData           
            
        else:
            # Continue adding data
            parseData['data'] += resultsData            
        
    return parseData



def writeScriptTableHeader(parseData, outputFile):
    cur = ','.join(parseData['curHeader'].decode("utf-8").split())
    if 'prvHeader' in parseData:
        if parseData['prvHeader'] == cur:
            return parseData
        header = "\n"
    else:
        header = ""
        
    
          
    if parseData['withFilename']:
        header += "FILENAME,"
    header += "SERIAL_NUM,TRANS_SEQ,EVENT_DATE,SBR,TEST_SEQ_EVENT,SPC_ID,"
    outputFile.write(header.encode("utf-8"))

    outputFile.write(cur.encode("utf-8"))
    parseData['prvHeader'] = cur

    return parseData


def writeScriptTable(parseData, outputFile):
    sn = parseData['sn']
    ts = parseData['ts']
    date = parseData['date']
    sbr = parseData['sbr']
    tse = parseData['testSeqEvent']
    spcId = parseData['spcId']
    
    if parseData['withFilename']:
        data = "\n%s,%s,%s,%s,%s,%s,%s," % (parseData['filename'],sn,ts,date,sbr,tse,spcId)
    else:
        data = "\n%s,%s,%s,%s,%s,%s," % (sn,ts,date,sbr,tse,spcId)
    outputFile.write(data.encode("utf-8"))

    data = ','.join(parseData['data'].decode("utf-8").split())
    outputFile.write(data.encode("utf-8"))
    
    return



def parseMatch(resultsData, requested, parseData, outputFile):
    returnResult = None
    state = parseData['state']
    matchStr = requested['tableName'].encode("utf-8")

    if resultsData.find(matchStr) != -1:
        sn = parseData['sn']
        ts = parseData['ts']
        date = parseData['date']
        sbr = parseData['sbr']
        tse = parseData['testSeqEvent']
        spcId = parseData['spcId']

        if parseData['withFilename']:
            data = "\n%s,%s,%s,%s,%s,%s,%s," % (parseData['filename'],sn,ts,date,sbr,tse,spcId)
        else:
            data = "\n%s,%s,%s,%s,%s,%s," % (sn,ts,date,sbr,tse,spcId)

        outputFile.write(data.encode("utf-8"))

        data = resultsData.decode("utf-8").split('\n')
        outputFile.write(data[1].encode("utf-8"))
    return

    

def writeMatchHeader(outputFile, withFilename):
    header = ""
    if withFilename:
        header += "FILENAME,"
    header += "SERIAL_NUM,TRANS_SEQ,EVENT_DATE,SBR,TEST_SEQ_EVENT,SPC_ID,match"
    outputFile.write(header.encode("utf-8"))

    return


def crcCheck(header, record, crcFormat, crcSize):
    # Get the tester CRC which is the last 2 bytes in the record
    crcCheck =  struct.unpack(crcFormat,record[len(record)-crcSize:])[0]

    # Calculate the tester CRC; CRC entire rec except for the tester CRC on the end
    if header == None:
        rec = record[:-crcSize]
    else:
        rec = header + record[:-crcSize]
    crc = calcCRC(rec,len(rec),604)
    crc = crc & 0xFFFF

    if crcCheck != crc:
        return False
    else:
        return True

def calcCRC(data,sizein,crc):
    for i in range(0,sizein):
        c1 = crc & 0x00AA
        c2 = c1 ^ data[i]
        crc = crc + (c2 & 0x00FF)
    return crc


def processOldFirmwareHeader(resultsSector):
    dataHeaderSize = struct.calcsize('>hH' + '10H')
    dataHeader = resultsSector[:dataHeaderSize]
    resultsData = resultsSector[dataHeaderSize:]
    testNumber, errorCode = struct.unpack('>hH',dataHeader[:4])

    return testNumber, errorCode, resultsData

def filenameExtraction(filename):
    splitData = filename.split('.')
    sn = splitData[0]

    ## file format
    ## SN.time.r.zip
    ## B04AA40H.4405183732.r.zip
    ## B04G7512.3a10132314.r.zip
    ## year-month-date-hour-min-sec
    ## 2024-04-10 02:44:45 = 4-4-10-02-44-45

    d = splitData[1]
    
    if (len(d) == 11):
        date = f'202{d[0]}-{int(d[1],16)}-{d[3:5]} {d[5:7]}:{d[7:9]}:{d[9:]}'
    else:
        date = f'202{d[0]}-0{d[1]}-{d[2:4]} {d[4:6]}:{d[6:8]}:{d[8:]}'
    
    return sn, date
