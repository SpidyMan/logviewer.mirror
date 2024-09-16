#!/usr/bin/env python
#coding:utf-8
# Author:  CChen 
# Purpose: Report Master logfile highlight support
# Created: 9/29/2010

from wx import stc

styles = {

}

STYLE_DEFAULT = 1

STYLE_STATE = 2

STYLE_SELFTEST = 3
STYLE_SELFTEST_FAILED = 4

STYLE_DBLOG = 5
STYLE_DBLOGNAME = 6
STYLE_DBLOGDESC = 7
STYLE_DBLOGDATA = 8

styles = [
        (STYLE_STATE, "fore:red,back:yellow,bold,"),     #state
        (STYLE_SELFTEST, "fore:#006400,back:#8FBC8F,bold,"),       #selftest
        (STYLE_SELFTEST_FAILED, "fore:red,back:#8FBC8F,bold,"),       #selftest failed
        (STYLE_DBLOGNAME, "fore:blue,back:#C0C0C0,bold,"),       #dblog name
        (STYLE_DBLOGDESC, "fore:Brown,bold,"),       #dblog description
        (STYLE_DBLOGDATA, "fore:black,italic,"),       #dblog data
         ]

def initStyles(stc_editor):
    for style, stylestr in styles:
        stc_editor.StyleSetSpec(style, stylestr)
        
def setStyle(stc_editor, start, end, style):
    if start>end:
        (start,end) = (end,start)
    stc_editor.StartStyling(start, 0xff)
    stc_editor.SetStyling(end - start, style)  

def highlight(stc_editor, style, f3logobj, base_start=0):
    span = f3logobj.Span
    if style == STYLE_STATE:
        s = STYLE_STATE
        
        line = stc_editor.LineFromPosition(span[0] - base_start)
        start = stc_editor.PositionFromLine(line)
        end = stc_editor.PositionFromLine(line+1)-1
        setStyle(stc_editor, start, end, s)    #start line
        
    elif style == STYLE_SELFTEST:
        s = STYLE_SELFTEST
        if f3logobj.TestStat != 0:
            s = STYLE_SELFTEST_FAILED
        
        line = stc_editor.LineFromPosition(span[0] - base_start)
        start = stc_editor.PositionFromLine(line) + 22
        end = stc_editor.PositionFromLine(line+1)-1
        setStyle(stc_editor, start, end, s)    #start line
        
        line = stc_editor.LineFromPosition(span[1] - base_start) - 1
        start = stc_editor.PositionFromLine(line) + 22
        end = stc_editor.PositionFromLine(line+1)-1
        setStyle(stc_editor, start, end, s)    #complete line
        
    elif style == STYLE_DBLOG:
        
        #DBLog Name
        s = STYLE_DBLOGNAME
        line = stc_editor.LineFromPosition(span[0] - base_start)
        start = stc_editor.PositionFromLine(line)
        end = stc_editor.PositionFromLine(line+1)-1
        setStyle(stc_editor, start, end, s)  
        
        ##DBLog Description
        #if f3logobj.Description:
            #s = STYLE_DBLOGDESC
            #line = line + 1
            #start = stc_editor.PositionFromLine(line)
            #end = stc_editor.PositionFromLine(line+1)-1
            #setStyle(stc_editor, start, end, s)
        
        ##DBLog Data
        #s = STYLE_DBLOGDATA
        #line = line + 1
        #start = stc_editor.PositionFromLine(line)
        #line = stc_editor.LineFromPosition(span[1])
        #end = stc_editor.PositionFromLine(line)-1
        #setStyle(stc_editor, start, end, s)
        pass
    else:
        return #default
    

    