# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------#
# Property of Seagate Technology, Copyright 2017, All rights reserved                     #
# ----------------------------------------------------------------------------------------#
"""
    sealogfile

    Base Logfile

    :copyright: (c) 2017 Seagate Technology.
    :author: Chen Chao <chao.c.chen@seagate.com>
"""
import wx
import mmap


class UnProcessedException(RuntimeError):
    """Indicates a logfile was UnProcessed."""
    def __init__(self, filename):
        Exception.__init__(self)
        self.filename = filename

    def __repr__(self):
        return "<UnProcessedException: logfile %s is unprocessed!>" % self.filename


class LogFileTypes(object):
    F3 = "F3"
    M8 = "M8"
    Bench = "Bench"
    Unknown = "Unknown"


class LogFileBase(object):
    def __init__(self, f3log):
        self.f3log = f3log
        self.Type = LogFileTypes.Unknown
        self.Span = (0, 0)
        self.isProcessed = False

    @property
    def Size(self):
        return self.Span[1] - self.Span[0]

    # comparators
    @staticmethod
    def sort_by_span(log1, log2):
        """ comparator for Span"""
        if log1.Span[0] < log2.Span[0]:
            return -1
        elif log1.Span[0] > log2.Span[0]:
            return 1
        else:
            return 0
        
    # public methods
    def GetPartOfFile(self, span):
        f = open(self.f3log.FileName, "rb")
        try:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            start, end = span
            content = mm[start:end]
            mm.close()
            return content
        except WindowsError:
            style=wx.OK | wx.ICON_INFORMATION
            parent=None
            msg="Memory Not enough, pls don't open many windows at the same time and close current windows and try again"
            title=""
            dlg = wx.MessageDialog(parent, msg, title, style)
            result = dlg.ShowModal()
            dlg.Destroy()
        finally:
            f.close()

    def regex_search(self, regex, span, first=True):
        match = None
        content = self.GetPartOfFile(span)
        for match in regex.finditer(content):
            if first:
                break
        return match
