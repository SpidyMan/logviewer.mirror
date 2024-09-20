# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2017, All rights reserved                     #
# ----------------------------------------------------------------------------------------#
"""
    sealogfile

    F3 Logfile

    :copyright: (c) 2017 Seagate Technology.
    :author: Chen Chao <chao.c.chen@seagate.com>
"""

import os
import re
import sys
import mmap
import tempfile
from datetime import datetime

from . import utils
from . import searegex

from .dblog import DBLog
from .selftest import SelfTest
from .teststate import TestState
from .baselogfile import LogFileTypes, LogFileBase, UnProcessedException
from wiya_utils import str_it
class F3LogFile(LogFileBase):
    """ F3 logfile """
    
    def __init__(self, filename):
        LogFileBase.__init__(self, self)
        self.Product = ''
        self.Config = ''
        self.PartNum = ''
        self.SerialNo = ''
        self.SBR = ''
        self.Oper = ''
        self.ErrorMsg = ''
        self.TestStateList = []
        self.FileName = filename
        self.FileSize = os.path.getsize(self.FileName)
        self.isNRF = False
        # noinspection PyBroadException
        try:
            elements = os.path.basename(filename).split("_")
            try:
                elements.remove('')#in case of the *OPER which contains 2x '_'
            except:
                pass
            try:
                self.TS = str(int(elements[2]))
            except:
                self.TS = "0"
            try:
                self.ErrorCode = int(elements[3].split('.txt')[0])
            except:
                self.ErrorCode = 0
        except:
            pass

        self.Span = (0, self.FileSize)

        self._isF3LogFile = False
        self._config_match = None
        self._attr_match = None
        self._headersize = utils.F3LOG_HEADER_SIZE
        self._footersize = utils.F3LOG_FOOTER_SIZE
        self.stlist = None
        self.dbloglist = None
        self.stdict = {}
        self.dblogdict = {}

        self.DriveInfo = {}
        
    @property
    def FailedState(self):
        """ Failed State, type(TestState) readonly """
        if self.ErrorCode == 0:
            return None
        self.Process()
        if not self.TestStateList:
            return "N/A"

        state = self.TestStateList[-1]
        if state.StateName.upper() == "FAIL_PROC":
            state = self.TestStateList[-2]
        return state
    
    @property
    def isF3LogFile(self):
        """ Indicates this logfile is correct F3 Log. type(bool) readonly"""
        return self._isF3LogFile
    
    @property
    def TestTime(self):
        """ Testtime in seconds, type(int) readonly"""
        if not self.isProcessed:
            return -1
        if self.TestStateList:
            testtime = self.TestStateList[-1].EndTime - self.TestStateList[0].StartTime
            return testtime.seconds + testtime.days*24*3600

        return -1
    
    @property
    def STList(self):
        """ All st in this file, type(list of SelfTest) readonly"""
        if not self.isProcessed:
            raise UnProcessedException(self.FileName)
        if self.stlist is None:
            self.stlist = []
            for state in self.TestStateList:
                for st in state.STList:
                    self.stlist.append(st)    
        return self.stlist
    
    @property
    def DBLogList(self):
        """ All dblog in this file, type(list of DBLog) readonly"""
        if not self.isProcessed:
            raise UnProcessedException(self.FileName)
        if self.dbloglist is None:
            self.dbloglist = []
            for st in self.STList:
                for dblog in st.DBLogList:
                    self.dbloglist.append(dblog)    
        return self.dbloglist
    
    @property
    def SelfTestDict(self):
        """ All self in this file, type(dict of SelfTest by TestNum) readonly"""
        if not self.isProcessed:
            raise UnProcessedException(self.FileName)
        if not self.stdict:        
            for state in self.TestStateList:
                for st in state.STList:
                    if st.TestNum in self.stdict:
                        self.stdict[st.TestNum].append(st)
                    else:
                        self.stdict[st.TestNum] = [st]
        return self.stdict
    
    @property
    def DBLogDict(self):
        """ All dblog in this file, type(dict of DBLog by DBLogName) readonly"""
        if not self.isProcessed:
            raise UnProcessedException(self.FileName)
        if not self.dblogdict:
            for st in self.STList:
                for dblog in st.DBLogList:
                    if dblog.Name.lower() in self.dblogdict:
                        self.dblogdict[dblog.Name.lower()].append(dblog)
                    else:
                        self.dblogdict[dblog.Name.lower()] = [dblog]  
        return self.dblogdict
    
    def GetStateByName(self, statename):
        """ Return State by StateName"""
        if not self.isProcessed:
            raise UnProcessedException(self.FileName)

        for state in self.TestStateList:
            if state.StateName.lower() == statename.lower():
                return state
        return None
    
    def GetSTListByNum(self, stnum):
        """ Return list of SelfTest by test num"""
        re_st = searegex.RePatternNamedST % {'st': stnum}
        re_st = re.compile(re_st, re.DOTALL)
        re_st_winfof = searegex.RePatternNamedSTWinFOF % {'st': stnum}
        re_st_winfof = re.compile(re_st_winfof, re.DOTALL)
        content = self.GetPartOfFile(self.Span)

        st_list = []
        for re_st in (re_st, re_st_winfof):
            iter_sts = re_st.finditer(content)
            for stmatch in iter_sts:
                st = SelfTest(self)
                st.Process(stmatch, startpos=self.Span[0])
                st_list.append(st)

        return st_list
    
    def GetDBLogByName(self, dblogname):
        """ Return a list of Dblog named dblogname """

        if self.isNRF:
            return self.GetNRFTable(dblogname)

        re_dblog = re.compile(searegex.RePatternNamedDBLog % dblogname, re.DOTALL)

        def find_dblogs(data_span, startpos=0, spc_id=None):
            data = self.GetPartOfFile(data_span)
            iter_dblogs = re_dblog.finditer(data)

            dblogs = []
            for dblogmatch in iter_dblogs:
                dblog = DBLog(self, spc_id=spc_id)
                dblog.Process(dblogmatch, startpos=startpos)
                dblogs.append(dblog)
            return dblogs

        # find spc_id first
        dblog_list = []

        re_spc = re.compile(searegex.RePatternSPCID, re.DOTALL)
        iter_spc = re_spc.finditer(self.GetPartOfFile(self.Span))

        spc_found = False
        last_spc_info = None

        for spc_match in iter_spc:
            span = tuple([pos + self.Span[0] for pos in spc_match.span()])

            if last_spc_info is not None:
                # find dblogs from last spc to current
                last_span, last_spc_id = last_spc_info
                db_logs = find_dblogs((last_span[1], span[0]), last_span[1], last_spc_id)
                dblog_list.extend(db_logs)
                spc_found = True

            # save last spc info
            last_spc_info = (span, spc_match.group("spc"))

        if spc_found is False or last_spc_info is None:
            # find dblogs for full span
            last_span, last_spc_id = self.Span, None
        else:
            # find dblogs from last spc postion to end
            last_span, last_spc_id = last_spc_info
            last_span = (last_span[1], self.Span[1])

        db_logs = find_dblogs(last_span, last_span[0], last_spc_id)
        dblog_list.extend(db_logs)

        return dblog_list

    def GetNRFTable(self, dblogname):
        """ Return a list of Dblog named dblogname """
        table_data = utils.parse_NRF_text(self.FileName, table=dblogname, lines=-1, header=True)

        header, data = table_data.split("\n", 1)

        dblog = DBLog(self, spc_id=None)
        dblog.Name = dblogname
        dblog.Span = (0, 0)
        dblog.Description = header.split(",")
        dblog.data = data.replace(",", " ")

        return [dblog, ]

    def GetStateByPos(self, position):
        seq = 0
        for state in self.TestStateList:
            if state.Span[1] > position:
                return state, seq
            seq += 1
        return None, -1
        
    def ReleaseMemory(self):
        """ Clear states,st,dblog list and set isProcessed to False"""
        self.isProcessed = False
        
        self.TestStateList = []
        self.stlist = None
        self.dbloglist = None
        self.stdict.clear()
        self.dblogdict.clear()
    
    def ReProcess(self):
        """ Re process this file"""
        self.isProcessed = False
        self.Process()

    def getHeaderFooter(self):
        if self.FileSize <= 0:
            return "", ""

        if self.isNRF:
            header = utils.parse_NRF_text(self.FileName, lines=2000)
            return header, ""

        header = self.GetPartOfFile((0, self._headersize))
        footer_start = 0
        if self.FileSize > self._footersize:
            footer_start = self.FileSize-self._footersize
        footer = self.GetPartOfFile((footer_start, self.FileSize))

        return header, footer

    def PreProcess(self):
        """ Preprocess this file, to get basic config info in file header """
        if self.isProcessed:
            return

        header, footer = self.getHeaderFooter()
        config = searegex.RegexConfigInfo.search(header)
        if not config:
            config = searegex.RegexConfigInfo2.search(header)
        config and self._crunchConfig(config)

        attrs = searegex.RegexDriveAttrsBlock.search(header)
        attrs and self._crunchDriveAttrs(attrs)
        
        ec = searegex.RegexErrorCode.search(footer)
        if not ec:
            ec = searegex.RegexErrorCode2.search(footer)
        ec and self._crunchErrorCode(ec)

    def Process(self, skip_header_footer=False, process_hook=None):
        """ Process this file """
        if self.isProcessed:
            if self.isNRF:
                if not self._isF3LogFile:
                    self.PreProcess()
                return
        
        self.stlist = None
        self.dbloglist = None
        self.stdict.clear()
        self.dblogdict.clear()
        self.TestStateList = []

        if self.FileSize <= 0:
            return

        if not skip_header_footer:
            header, footer = self.getHeaderFooter()

            config = searegex.RegexConfigInfo.search(header)
            if not config:
                config = searegex.RegexConfigInfo2.search(header)
            config and self._crunchConfig(config)

            attrs = searegex.RegexDriveAttrsBlock.search(header)
            attrs and self._crunchDriveAttrs(attrs)

            ec = searegex.RegexErrorCode.search(footer)
            if not ec:
                ec = searegex.RegexErrorCode2.search(footer)
            ec and self._crunchErrorCode(ec)
        self._addInfoState()

        process_hook and process_hook("Begin", self)

        # find all states
        f = open(self.FileName, "rb")
        content = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        iter_states = searegex.RegexState.finditer(content)

        seq = 0
        for statematch in iter_states:
            state = TestState(self, seq=seq)
            state.Process(statematch, startpos=self.Span[0])
            if self.TestStateList:
                last_state = self.TestStateList[-1]
                last_state.Span = (last_state.Span[0], state.Span[0])
                self.TestStateList[-1] = last_state
            self.TestStateList.append(state)
            process_hook and process_hook("State", state)
            seq += 1

        # check incomplete state
        startpos = self.TestStateList and self.TestStateList[-1].Span[1] or 0
        last_state_matches = searegex.RegexStateBegin.finditer(content, startpos)

        for match in last_state_matches:
            state = TestState(self, seq=seq)
            state.Span = (match.span()[0], self.Span[1])
            state.StateName = match.group('statename2') or match.group('statename')
            state._stlist = None
            state._dbloglist = None
            state.isProcessed = True
            if self.TestStateList:
                last_state = self.TestStateList[-1]
                old_span = last_state.Span
                last_state.Span = (old_span[0], state.Span[0]-1)

            self.TestStateList.append(state)
            process_hook and process_hook("State", state)
            seq += 1

        if len(self.TestStateList) > 0:
            self.Type = LogFileTypes.F3
            last_state = self.TestStateList[-1]
            last_state.Span = (last_state.Span[0], self.Span[1])
        else:
            # for WinFOF bench result
            state = TestState(self, seq=seq)
            state.Span = self.Span
            state.Seq = 0
            state.StateName = 'BenchTest'
            state.StartTime = datetime.now()
            state.EndTime = datetime.now()
            state._stlist = None
            state._dbloglist = None
            state.isProcessed = True
            if len(state.STList) > 0:
                self.TestStateList.append(state)
                process_hook and process_hook("State", state)
                self.Oper = 'Bench'
                self.Type = LogFileTypes.Bench
            else:
                self.Oper = os.path.basename(self.FileName)
                self.Type = LogFileTypes.Unknown

        if not self.SerialNo:
            self.SerialNo = os.path.basename(self.FileName).split("_")[0]

        self.isProcessed = True
        content.close()
        f.close()

        process_hook and process_hook("Done", self)

    def _crunchConfig(self, match):
        """ class internal use: Crunch file header to get Config Info """
        self.Product = str_it(match.group('prod'))
        self.Config = str_it(match.group('config'))
        self.PartNum = str_it(match.group('scn'))
        self.SBR = str_it(match.group('sbr'))
        self.Oper = str_it(match.group('oper')) or str_it(match.group('oper2'))
        self.SerialNo = str_it(match.group('sn'))
        self._isF3LogFile = True
        self._config_match = str_it(match)

    def _crunchDriveAttrs(self, match):
        """ class internal use: Crunch file header to get Drive Attributes"""
        attrsblock = match.group('attrsblock')
        iter_attrs = searegex.RegexDriveAttr.finditer(attrsblock)
        for attr in iter_attrs:
            name = str_it(attr.group('name').strip())
            value = str_it(attr.group('value').strip())
            self.DriveInfo[name] = value
            

        # noinspection PyBroadException
        try:
            cms_family = self.DriveInfo.get('CMS_FAMILY')
            if not self.Product:
                self.Product = cms_family or "unknown"
            elif self.Product.find("-.-") >= 0 and cms_family:
                self.Product = cms_family
            self.Config = self.Config or self.DriveInfo.get('CMS_CONFIG') or "unknown"
            self.PartNum = self.PartNum or self.DriveInfo.get('PART_NUM') or "unknown"
            self.SBR = self.SBR or self.DriveInfo.get('SUB_BUILD_GROUP') or "unknown"
            self.Oper = self.Oper or self.DriveInfo.get('VALID_OPER') or "unknown"
            if self.DriveInfo.get('LODT', 'None') == 'CST':
                self.Oper = 'CST2'
            self.SerialNo = self.SerialNo or self.DriveInfo.get('HDA_INFO', '').split('_')[0]
            if self.SerialNo and len(self.SerialNo) != 8:
                self.SerialNo = ""
        except:
            pass
        finally:
            self._isF3LogFile = True
        self._attr_match = match
        
    def _crunchErrorCode(self, match):
        """ class internal use: Crunch file footer to get Error Info"""
        if int(match.group('ec')):
           self.ErrorCode = int(match.group('ec'))

        self.ErrorMsg = match.group('ecmsg').strip()
    def convert_drive_info(self,drive_info):
        converted_info = {}
        for key, val in drive_info.items():
            # Convert key to string if it's bytes
            if isinstance(key, bytes):
                key = key.decode('utf-8')
            
            # Convert value to the appropriate type
            if isinstance(val, bytes):
                try:
                    # First, try to convert to an integer
                    val = int(val.decode('utf-8'))
                except ValueError:
                    try:
                        # If it fails, try to convert to a float
                        val = float(val.decode('utf-8'))
                    except ValueError:
                        # If both fail, keep it as a string
                        val = val.decode('utf-8')
            
            # Add the converted key-value pair to the new dictionary
            converted_info[key] = val
        
        return converted_info

    def _addInfoState(self):
        # add a fake Drive Attributes State
        if self._attr_match or self._config_match:
            state_attrs = TestState(self)
            state_attrs.StateName = "DRV_ATTRS"
            state_attrs.isProcessed = True

            st = SelfTest(state_attrs)
            st.TestNum = -2

            if self._attr_match:
                dblog_attr = DBLog(st)
                dblog_attr.Name = "DRIVE_ATTRIBUTES"
                dblog_attr.Description = ["Attribute", "Value"]
                dblog_attr.Span = self._attr_match.span()
                self.DriveInfo = self.convert_drive_info(self.DriveInfo)
                dblog_attr.data = "\n".join(["%s\t%s" % (key, val) for key, val in self.DriveInfo.items()])
                st.DBLogList.append(dblog_attr)

            if self._config_match:
                dblog_cfg = DBLog(st)
                dblog_cfg.Name = "DRIVE_CONFIG"
                dblog_cfg.Description = ["Config", "Value"]
                dblog_cfg.Span = self._config_match.span()
                dblog_cfg.data = "Product %s\nConfig %s\nPart_Num %s\nSBR %s\nOper %s\nSerial_No %s" % (
                    self.Product, self.Config, self.PartNum, self.SBR, self.Oper, self.SerialNo)
                st.DBLogList.append(dblog_cfg)
            state_attrs._stlist = [st]

            span = ((self._attr_match or self._config_match).span()[0],
                    (self._config_match or self._attr_match).span()[1])
            state_attrs.Span = st.Span = span
            self.TestStateList.append(state_attrs)

    def PrintHeaderInfo(self, output=sys.stdout):
        """ Print header info"""
        output.write((r'Product   : %s\nConfig    : %s\nSCN       : %s\nSerial No : %s\nSBR       : %s\n' +
                     r'OPER      : %s\nErrorCode : %s\nSIZE      : %d\nTestTime  : %d\n')
                     % (self.Product, self.Config, self.PartNum, self.SerialNo,
                        self.SBR, self.Oper, self.ErrorCode, self.Size, self.TestTime))
        
    def PrintLogInfo(self, output=sys.stdout):
        """ Print this log details info"""
        self.PrintHeaderInfo(output)
        for state in self.TestStateList:
            output.write('*'*30 + '\n')
            output.write(str(state)+'\n')
            for st in state.STList:
                output.write(str(st)+'\n')
                for dblog in st.DBLogList:
                    output.write(str(dblog)+'\n')
