# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2017, All rights reserved                     #
# ----------------------------------------------------------------------------------------#
"""
    sealogfile

    DBLog

    :copyright: (c) 2017 Seagate Technology.
    :author: Chen Chao <chao.c.chen@seagate.com>
"""

from .baselogfile import LogFileBase
from .utils import split_db_table_line


################################
# DBLog Settings
################################
NoDescriptionTables = ['P000_DEBUG_DATA', 'P000_XFR_FUNCTION', 'P159_FIFO', 'P193_POLYCHROME',
                       'P193_MONOCHROME', 'P130_SYS_RZDT', 'P011_SRVO_DIAG_RESP', 'P_TEST_PARAMETERS']


SpecialSeparator = {
    "P_AFH_DH_MEASURED_TCC": "  ",
    "DRIVE_ATTRIBUTES": "\t",
}


class DBLog(LogFileBase):
    """ Comparators for DBLog """
    @staticmethod
    def sort_by_name(dblog1, dblog2):
        """ comparator for DBLogName"""
        return cmp(dblog1.Name, dblog2.Name)

    @classmethod
    def GetSep(cls, table_name, default=" "):
        return SpecialSeparator.get(table_name, default)

    def __init__(self, st, spc_id=None):
        """ init"""
        LogFileBase.__init__(self, st.f3log)
        self._parent = st
        self._data_span = None
        self.data = None

        self.Name = None
        self.SPCID = spc_id
        self.Description = []

    @property
    def Data(self):
        if self.data is None:
            self.data = self.GetPartOfFile(self._data_span).replace(",", " ")
        return self.data

    @property
    def hasDescription(self):
        """ return True if this dbtable have description line """
        # noinspection PyBroadException
        try:
            int(self.Name)
            return False
        except ValueError:
            return self.Name not in NoDescriptionTables
    
    @property
    def DBLogList(self):
        """ return [self], for compatibility """
        return [self]
    
    @property
    def STList(self):
        """ return parent SelfTest, for compatibility """
        from .selftest import SelfTest
        if isinstance(self._parent, SelfTest):
            return [self._parent, ]
        return []

    @property
    def TestStateList(self):
        """ return [self._parent.TestStateList], for compatibility """
        return self._parent.TestStateList

    @property
    def SelfTestDict(self):
        """ return self._parent.SelfTestDict, for compatibility"""
        return self._parent.SelfTestDict

    @property
    def DBLogDict(self):
        """ return {self.Name: self}, for compatibility"""
        return {self.Name: self}

    def Process(self, dblogmatch, startpos=0):
        """ Process dblog match, startpos means match start position in while file"""
        self.Span = tuple([p+startpos for p in dblogmatch.span()])
        self.Name = dblogmatch.group('dblogname')

        # todo: Dblogs have no description:
        # P000_DEBUG_DATA , P000_XFR_FUNCTION
        # P159_FIFO
        # P193_POLYCHROME
        if not self.hasDescription:
            self.Description = []
            self._data_span = (startpos + dblogmatch.span("dblogdesp")[0],
                               startpos + dblogmatch.span("dblogdata")[1])
        else:
            desp = dblogmatch.group('dblogdesp').strip()
            self.Description = split_db_table_line(desp)
            if len(self.Description) == 1:
                desp = desp.decode('utf-8')
                self.Description = desp.split(',')

            self._data_span = tuple([p+startpos for p in dblogmatch.span("dblogdata")])

        self.isProcessed = True
    
    def __str__(self):
        return "    Name:%s Desp:%s Span:%s  Size:%d " % (self.Name, self.Description, 
                                                          self.Span, self.Size)

    def __getitem__(self, index):
        sep = DBLog.GetSep(self.Name)
        if isinstance(index, int):
            lines = self.Data.strip().split('\n')
            line = lines[index].strip()
            values = split_db_table_line(line, sep=sep)
            if len(values) == 1:
                values = line.split(',')
            return values
        elif isinstance(index, str):
            res = []
            if index in self.Description:
                index = self.Description.index(index)
                lines = self.Data.strip().split('\n')
                for line in lines:
                    values = split_db_table_line(line, sep=sep)
                    if len(values) == 1:
                        values = line.split(',')
                    res.append(values[index])
            return res
