# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2017, All rights reserved                     #
# ----------------------------------------------------------------------------------------#
"""
    sealogfile

    SelfTest

    :copyright: (c) 2017 Seagate Technology.
    :author: Chen Chao <chao.c.chen@seagate.com>
"""

from . import utils
from . import searegex
from .testdesc import TestDescription
from .baselogfile import LogFileBase, UnProcessedException

from .dblog import DBLog
import ast

class SelfTest(LogFileBase):

    def __init__(self, teststate, f3diag=""):
        """ init"""
        LogFileBase.__init__(self, teststate.f3log)
        self._parent = teststate
        self._exec_param = ""
        self._dblogdict = {}

        self.TestNum = -1
        self.TestStat = 0
        self.TestTime = 0

        self.Parameters = {}
        self.DBLogList = []
        self.F3Diag = f3diag

    @property
    def TestName(self):
        if self.F3Diag:
            return self.F3Diag

        if self.TestNum in TestDescription:
            return TestDescription[self.TestNum].get("TestName", "Unknown Test")

        return "Unknown Test"

    @property
    def ExecutionParameter(self):
        return self._exec_param
    
    @property
    def TestDesc(self):
        try:
            return TestDescription[self.TestNum]['TestDesc']
        except IndexError:
            return "Unknown TestDesc"
    
    @property
    def STList(self):
        return [self]

    @property
    def isValidTest(self):
        return self.TestNum > 0

    @property
    def TestStateList(self):
        return self._parent.TestStateList

    @property
    def SelfTestDict(self):
        return {self.TestNum: self}

    @property
    def DBLogDict(self):
        """ All dblog in this test, type(dict of DBLog by DBLogName) readonly"""
        if not self.isProcessed:
            raise UnProcessedException(self.f3log.FileName)
        if not self._dblogdict:
            for st in self.STList:
                for dblog in st.DBLogList:
                    if dblog.Name.lower() in self._dblogdict:
                        self._dblogdict[dblog.Name.lower()].append(dblog)
                    else:
                        self._dblogdict[dblog.Name.lower()] = [dblog]
        return self._dblogdict
        
    def Process(self, stmatch, startpos=0, delay_mode=False):
        """ Process st match, startpos means match start position in while file"""
        st_raw = stmatch.group(0)
        self.Span = tuple([p+startpos for p in stmatch.span()])
        if stmatch.group('except'):
            self.TestNum = int(stmatch.group('stnum2'))
            self.TestStat = 0xFFFF
            try:
                self.TestTime = float(stmatch.group('time2'))
            except ValueError:
                self.TestTime = 0
        else:
            self.TestNum = int(stmatch.group('stnum'))
            self.TestStat = int(stmatch.group('stat'))
            self.TestTime = float(stmatch.group('time'))

        # noinspection PyBroadException
        try:
            self._exec_param = stmatch.group('exec_param').decode('utf-8').split(":")[1].strip()
        except:
            self._exec_param = ""

        self.Parameters = {}

        parammatch = searegex.RegexSTParam.search(st_raw)
        if parammatch:
            paramlist = parammatch.group('param')
            # noinspection PyBroadException
            try:
                if isinstance(paramlist, bytes):
                    paramlist = paramlist.decode('utf-8')  # Convert bytes to string
                paramlist = paramlist.replace("\r", "").replace("\n", "")
                paramlist_dict = ast.literal_eval(paramlist)
                self.TestNum = int(paramlist_dict[0][0])
                self.Parameters = paramlist_dict[2]
            except:
                import logging
                logging.exception("exception in selftest")

        if delay_mode or self.Size > utils.BIG_SELFTEST_SIZE:
            self.isProcessed = False
        else:
            self.ProcessDBLog(st_raw)

        del st_raw

    def ProcessDBLog(self, st_raw=None, progress_hook=None):
        self.DBLogList = []
        self._dblogdict = {}
        self.isProcessed = True

        if st_raw is None:
            st_raw = self.GetPartOfFile(self.Span)

        dblogs_iter = searegex.RegexDBLog.finditer(st_raw)
        count = 0
        for dblogmatch in dblogs_iter:
            dblog = DBLog(self)
            dblog.Process(dblogmatch, startpos=self.Span[0])
            self.DBLogList.append(dblog)
            count += 1
            if count > utils.MAX_DBLOG_COUNT:  # do not show DBLogs more than MAX_DBLOG_COUNT
                import logging
                logging.warning("DBLogs > %d, Skipped! ST[%s] %s" %
                                (utils.MAX_DBLOG_COUNT, self.TestNum, self.Span))
                dummy_table = DBLog(self)
                dummy_table.Name = "...... (too many tables to show)"
                dummy_table.data = ""
                dummy_table.Span = (dblog.Span[1], self.Span[1])
                self.DBLogList.append(dummy_table)
                break

            if progress_hook:
                progress_hook(dblog)
            
    def __str__(self):
        return "[%d][%s], Stat: %s, Time: %.2f, Param:%s" % (
            self.TestNum, self.TestName, self.TestStat, self.TestTime, self.Parameters)
