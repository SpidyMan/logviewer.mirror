#!/usr/bin/env python
#coding:utf-8
# Author:  CChen 
# Purpose: Search Frame
# Created: 8/10/2009

import os
import mmap
import threading

import wx
import wx.py
import wx.stc
from wx.lib.anchors import LayoutAnchors
import wx.lib.filebrowsebutton as filebrowse

# from . import utils
# from . import searcheng
# from .tools import wxwidgets
import utils
import searcheng
from tools import wxwidgets


def create(parent):
    return PanelSearch(parent, id=-1,    
                       pos=wx.Point(0, 0), size=wx.Size(-1, -1),
                       style=wx.TAB_TRAVERSAL,name='')

[wxID_PANELSEARCH, wxID_PANELSEARCHBUTTONCLOSE, wxID_PANELSEARCHBUTTONCOPY, 
 wxID_PANELSEARCHBUTTONCOUNT, wxID_PANELSEARCHBUTTONNEXT, 
 wxID_PANELSEARCHBUTTONSHOWLIST, wxID_PANELSEARCHCHECKBOXCASE, 
 wxID_PANELSEARCHCHECKBOXHIGHLIGHT, wxID_PANELSEARCHCHECKBOXREGULAR, 
 wxID_PANELSEARCHCHECKBOXWHOLEWORD, wxID_PANELSEARCHLISTCTRLRESULTS, 
 wxID_PANELSEARCHRADIOBUTTONBACKWARD, wxID_PANELSEARCHRADIOBUTTONFORWARD, 
 wxID_PANELSEARCHSEARCHWORD, wxID_PANELSEARCHSTATICBOXDIRECTION, 
 wxID_PANELSEARCHSTATICTEXTSEARCH, 
] = [wx.NewId() for _init_ctrls in range(16)]


class SearchDirection(object):
    Forward = 'Forward'
    Backward = 'Backward'


class SearchConfig(object):
    def __init__(self, highlight=True, case=False, wholeword=False,
                 regular=False, direction = SearchDirection.Backward, word=''):
        self.Highlight = highlight
        self.Case = case
        self.Wholeword = wholeword
        self.Regular = regular
        self.Direction = direction
        self.SearchWord = word
        self.CurrentLine = 0
        self.MaxLine = -1
        self.IncludeSubDir = False
        self.Directory = ''
        self.FileFilter = []
        
    def isEqual(self, obj):
        return (obj) and \
               (self.Highlight == obj.Highlight) and (self.Case == obj.Case) and \
               (self.Wholeword == obj.Wholeword) and (self.Regular == obj.Regular) and \
               (self.SearchWord == obj.SearchWord) and (self.IncludeSubDir == obj.IncludeSubDir) and \
               (self.Directory == obj.Directory) and (self.FileFilter == obj.FileFilter)


class PanelSearch(wx.Panel):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=wxID_PANELSEARCH, name='PanelSearch',
              parent=prnt, pos=wx.Point(483, 278), size=wx.Size(448, 494),
              style=wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(440, 464))
        self.SetAutoLayout(True)
        prnt.SetMinSize(wx.Size(448, 100))
        self.Bind(wx.EVT_SIZE, self.OnPanelSearchReSize)

        self.staticTextSearch = wx.StaticText(id=wxID_PANELSEARCHSTATICTEXTSEARCH,
              label='Search: ', name='staticTextSearch', parent=self,
              pos=wx.Point(8, 24), size=wx.Size(41, 13), style=0)

        self.searchWord = wx.ComboBox( 
              id=wxID_PANELSEARCHSEARCHWORD,
              name='searchWord', parent=self, pos=wx.Point(56, 16),
              size=wx.Size(272, 21), style=0, value='')

        self.searchWord.SetConstraints(LayoutAnchors(self.searchWord, True,
              True, True, False))
        self.searchWord.Bind(wx.EVT_KEY_DOWN, self.OnSearchWordKeyDown)

        self.buttonCount = wx.Button(id=wxID_PANELSEARCHBUTTONCOUNT,
              label='Count', name='buttonCount', parent=self, pos=wx.Point(336,
              48), size=wx.Size(96, 23), style=0)
        self.buttonCount.SetConstraints(LayoutAnchors(self.buttonCount, False,
              True, True, False))
        self.buttonCount.Bind(wx.EVT_BUTTON, self.OnButtonCount,
              id=wxID_PANELSEARCHBUTTONCOUNT)

        self.buttonClose = wx.Button(id=wx.ID_CANCEL,
              label='Close', name='buttonClose', parent=self, pos=wx.Point(336,
              80), size=wx.Size(96, 23), style=0)
        self.buttonClose.SetConstraints(LayoutAnchors(self.buttonClose, False,
              True, True, False))
        self.buttonClose.Bind(wx.EVT_BUTTON, self.OnButtonClose,
              id=wx.ID_CANCEL)
        
        self.checkBoxCase = wx.CheckBox(id=wxID_PANELSEARCHCHECKBOXCASE,
              label='Case sensitivity', name='checkBoxCase', parent=self,
              pos=wx.Point(8, 56), size=wx.Size(160, 13), style=0)
        self.checkBoxCase.SetValue(False)

        self.checkBoxWholeword = wx.CheckBox(id=wxID_PANELSEARCHCHECKBOXWHOLEWORD,
              label='Match whole word', name='checkBoxWholeword', parent=self,
              pos=wx.Point(8, 80), size=wx.Size(168, 13), style=0)
        self.checkBoxWholeword.SetValue(False)

        self.radioButtonForward = wx.RadioButton(id=wxID_PANELSEARCHRADIOBUTTONFORWARD,
              label='Forward', name='radioButtonForward', parent=self,
              pos=wx.Point(208, 72), size=wx.Size(81, 13), style=0)
        self.radioButtonForward.SetValue(True)

        self.radioButtonBackward = wx.RadioButton(id=wxID_PANELSEARCHRADIOBUTTONBACKWARD,
              label='Backward', name='radioButtonBackward', parent=self,
              pos=wx.Point(208, 96), size=wx.Size(81, 13), style=0)

        self.staticBoxDirection = wx.StaticBox(id=wxID_PANELSEARCHSTATICBOXDIRECTION,
              label='Direction', name='staticBoxDirection', parent=self,
              pos=wx.Point(192, 48), size=wx.Size(120, 72), style=0)

        self.checkBoxRegular = wx.CheckBox(id=wxID_PANELSEARCHCHECKBOXREGULAR,
              label='Regular experssion', name='checkBoxRegular', parent=self,
              pos=wx.Point(8, 104), size=wx.Size(152, 13), style=0)
        self.checkBoxRegular.SetValue(False)
        
        wx.StaticText(self, -1, "Transparency:", pos=wx.Point(8, 128))
        slider = wx.Slider(self, -1, 255, 95, 255, (80, 124), (110, -1), 
            wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
        slider.SetTickFreq(10)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.OnTransparentTicks, slider)
        

        self.listCtrlResults = wx.ListBox(id=wxID_PANELSEARCHLISTCTRLRESULTS,
              name='listCtrlResults', parent=self, pos=wx.Point(0, 160),
              size=wx.Size(440, 304), style=wx.LB_HSCROLL)
        self.listCtrlResults.SetAutoLayout(False)
        self.listCtrlResults.SetConstraints(LayoutAnchors(self.listCtrlResults,
              True, True, True, True))
        self.listCtrlResults.Bind(wx.EVT_LISTBOX, self.OnClicklistCtrlResults,
              id=wxID_PANELSEARCHLISTCTRLRESULTS)

        self.listCtrlResults.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        self.buttonNext = wx.Button(id=wxID_PANELSEARCHBUTTONNEXT,
              label='Show Next', name='buttonNext', parent=self,
              pos=wx.Point(336, 16), size=wx.Size(96, 23), style=0)
        self.buttonNext.SetConstraints(LayoutAnchors(self.buttonNext, False,
              True, True, False))
        self.buttonNext.Bind(wx.EVT_BUTTON, self.OnButtonNext,
              id=wxID_PANELSEARCHBUTTONNEXT)
        self.buttonNext.SetDefault()

        self.checkBoxHighlight = wx.CheckBox(id=wxID_PANELSEARCHCHECKBOXHIGHLIGHT,
              label='Highlight all matches', name='checkBoxHighlight',
              parent=self, pos=wx.Point(8, 128), size=wx.Size(160, 13), style=0)
        self.checkBoxHighlight.SetValue(True)
        self.checkBoxHighlight.Show(False)

        self.buttonCopy = wx.Button(id=wxID_PANELSEARCHBUTTONCOPY,
              label='Copy to Clipboard', name='buttonCopy', parent=self,
              pos=wx.Point(192, 128), size=wx.Size(104, 23), style=0)
        self.buttonCopy.Bind(wx.EVT_BUTTON, self.OnButtonCopy,
              id=wxID_PANELSEARCHBUTTONCOPY)

        self.buttonShowList = wx.ToggleButton(id=wxID_PANELSEARCHBUTTONSHOWLIST,
              label='Show/Hide List >', name='buttonShowList', parent=self,
              pos=wx.Point(320, 128), size=wx.Size(112, 23), style=0)
        self.buttonShowList.SetValue(False)
        self.buttonShowList.SetConstraints(LayoutAnchors(self.buttonShowList,
              False, True, True, False))
        self.buttonShowList.Bind(wx.EVT_TOGGLEBUTTON, self.OnButtonShowList,
              id=wxID_PANELSEARCHBUTTONSHOWLIST)


    def __init__(self, parent, id, pos, size, style, name, strSearch=''):
        self.parent = parent
        self.strSearch = strSearch
        self._init_ctrls(parent)
        self._init_data(parent)

        #connect signals
        wx.py.dispatcher.connect(receiver=self.ShowNext, signal='Next', sender=self.parent)
        wx.py.dispatcher.connect(receiver=self.ShowNext, signal='Prev', sender=self.parent)
        wx.py.dispatcher.connect(receiver=self.OnButtonClose, signal='Close', sender=self.parent)
       
    def _init_data(self, parent):
        self.config = self.GetSearchConfig()
        
    def SetSTC(self, stc):
        self.stc = stc

    def SetLogViewer(self, logviewer):
        self.logviewer = logviewer
        self.logfile = self.logviewer.txt_logfile
        
    def SetSearchWord(self, text):
        index = self.searchWord.FindString(text)
        if index < 0:
            index = self.searchWord.Insert(text, 0)
        self.searchWord.Select(index)
        
    def ShowNext(self, signal):
        text = self.stc.GetSelectedTextUTF8()
        if not text:
            self.SetSearchWord(self.config.SearchWord)
            self.parent.Show(True)
            self.buttonNext.SetFocus()
            return 
        
        curSearchText = self.config.SearchWord
        if not self.config.Case:  
            text = text.lower() 
            curSearchText = curSearchText.lower()
            
        if text != curSearchText:
            self.SetSearchWord(self.stc.GetSelectedTextUTF8())
            self.parent.Show(True)
            self.buttonNext.SetFocus()
            return
        
        if signal == 'Next':
            self.config.CurrentLine += 1
            if self.config.CurrentLine >= self.config.MaxLine:
                self.config.CurrentLine = 0
        elif signal == 'Prev':
            self.config.CurrentLine -= 1
            if self.config.CurrentLine < 0:
                self.config.CurrentLine = self.config.MaxLine - 1
        
        self.listCtrlResults.Select(self.config.CurrentLine)
        self.RefreshSTCView()       

    def RefreshSTCView(self):
        span = self.listCtrlResults.GetClientData(self.config.CurrentLine)

        start, end = span

        if self.logviewer.bigfile_mode:
            wx.py.dispatcher.send(signal='PositionChanged', position=span)

            start -= self.logviewer.base_start_pos
            end -= self.logviewer.base_start_pos

        linenum = self.stc.LineFromPosition(start)
        linestartposition = self.stc.GetLineEndPosition(linenum-1)

        charwidth = self.stc.TextWidth(wx.stc.STC_STYLE_DEFAULT, 'O')
        position = charwidth * (start - linestartposition - 1)
        self.stc.SetXOffset(0)

        if position > self.stc.Size[0]:
            self.stc.SetXOffset(position - self.stc.Size[0] / 2)
        self.stc.ScrollToLine(linenum - 8)
        self.stc.SetSelectionStart(start)
        self.stc.SetSelectionEnd(end)
        self.stc.ShowMe(self.stc)

        if not self.logviewer.bigfile_mode:
            wx.py.dispatcher.send(signal='PositionChanged', position=None)
        
    def RefreshSTCView2(self):
        linenum, span = self.listCtrlResults.GetClientData(self.config.CurrentLine)
        
        charwidth = self.stc.TextWidth(wx.stc.STC_STYLE_DEFAULT, 'O')
        position = charwidth * span[0]
        self.stc.SetXOffset(0)

        if position > self.stc.Size[0]:
            self.stc.SetXOffset( position -  self.stc.Size[0]/2)
        self.stc.ScrollToLine( linenum-8 )
        linestartposition = self.stc.GetLineEndPosition(linenum-2)
        self.stc.SetSelectionStart(linestartposition+1+span[0])
        self.stc.SetSelectionEnd(linestartposition+1+span[1])
    
    def OnKeyDown(self, event):
        """Key down event handler."""
        key = event.GetKeyCode()
        controlDown = event.ControlDown()
        altDown = event.AltDown()
        shiftDown = event.ShiftDown()
        # Let Ctrl-Alt-* get handled normally.
        if controlDown and altDown:
            event.Skip()
        # Increase font size.
        elif controlDown and key in (ord(']'),ord('}')):
            wx.py.dispatcher.send(signal='FontIncrease')
        # Decrease font size.
        elif controlDown and key in (ord('['),ord('{'),):
            wx.py.dispatcher.send(signal='FontDecrease')
        # Default font size.
        elif controlDown and key in (ord('+'),ord('=')):
            wx.py.dispatcher.send(signal='FontDefault')
        # Find text
        elif controlDown and key in (ord('F'),ord('f')):
            self.Show()
        elif key in (342,):
            wx.py.dispatcher.send(signal='Prev', sender = self.parent)
        elif key in (343,):
            wx.py.dispatcher.send(signal='Next', sender = self.parent)
        elif key in (27,):
            wx.py.dispatcher.send(signal='Close', sender = self.parent, event = None)
        else:
            event.Skip()        

    def OnClicklistCtrlResults(self, event):
        event.Skip()
        self.config.CurrentLine = event.GetSelection()
        self.RefreshSTCView()

    def OnButtonCopy(self, event):
        event.Skip()
        result = ''.join(self.listCtrlResults.GetItems())
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(wx.TextDataObject(result))
        wx.TheClipboard.Close() 
        
    def OnButtonShowList(self, event):
        event.Skip()
        self.listCtrlResults.Show(not self.listCtrlResults.Shown)
        if self.listCtrlResults.Shown:
            self.parent.SetClientSize( wx.Size( self.Size[0], self.listCtrlResults.Position[1]+self.listSize[1]) )
        else:
            self.parent.SetClientSize( wx.Size( self.Size[0], self.listCtrlResults.Position[1]) )

    def OnButtonCount(self, event):
        searchword = self.searchWord.GetValue()
        if searchword == '':
            return
        config = self.GetSearchConfig()
        self.listCtrlResults.Clear()
        
        self.config, matches = self.FindAllLines(searchword, config)
        self.RefreshListBox(matches)          
            
        event.Skip()
        
    def OnButtonNext(self, event):
        searchword = self.searchWord.GetValue()
        if searchword == '':
            return
        self.SetSearchWord(searchword)
        
        config = self.GetSearchConfig()
        if config.isEqual(self.config):
            #show next
            if config.Direction == SearchDirection.Forward:
                self.config.CurrentLine += 1
                if self.config.CurrentLine >= self.config.MaxLine:
                    self.config.CurrentLine = 0
            else:
                self.config.CurrentLine -= 1
                if self.config.CurrentLine < 0:
                    self.config.CurrentLine = self.config.MaxLine - 1
                    
        else:
            self.listCtrlResults.Clear()
            #new search
            self.config, matches = self.FindAllLines( searchword, config)
            self.RefreshListBox(matches)

        if self.config.CurrentLine < 0:
            self.config.CurrentLine = 0
        if self.config.CurrentLine >= self.listCtrlResults.Count:
            self.config.CurrentLine = self.listCtrlResults.Count - 1

        if self.listCtrlResults.Count > 0:
            self.listCtrlResults.Select(self.config.CurrentLine)
            self.RefreshSTCView()
            
        #save search word
        self.SaveSearchWord(searchword)
        
        event.Skip()



    def FindAllLines(self, query, config):
        saved_cursor = self.Cursor

        self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))

        engine = searcheng.SearchEngine(query, config.Regular,
                                     True, config.Case, config.Wholeword)

        f = open(self.logfile.FileName, "rb")
        content = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        engine.SetSearchPool(content)

        #matches = engine.FindAllLines(self.stc)
        matches = engine.FindAll()
        if matches:
            count = len(matches)
        else:
            count = 0

        content.close()
        f.close()
        
        config.CurrentLine = 0
        config.MaxLine = count

        self.SetCursor(saved_cursor)

        wxwidgets.MessageBox(self, "%d times found! "% count,
                      ("Find Count"),
                      wx.ICON_INFORMATION|wx.OK)


        self.stc.SetFocus()
        return config, matches
    
    def OnButtonClose(self, event):
        self.parent.Show(False)
        self.stc.SetFocus()
        #event.Skip()
    
    def RefreshListBox(self, matches):
        self.listCtrlResults.Clear()
        cursor = self.GetCursor()
        self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
        self.listCtrlResults.Freeze()
        current_line = self.stc.GetCurrentLine()

        self.config.CurrentLine = 0
        for m in matches:
            span = m.span()
            state_name = self.GetStateNamebyPos(span[0])

            if self.logviewer.bigfile_mode:
                start, end = span
                if end - start > 512:
                    text = self.logfile.GetPartOfFile((start, start + 512))
                else:
                    text = self.logfile.GetPartOfFile(span)
                self.listCtrlResults.Append("[%s] Position(%d - %d): [%s]" %
                                            (state_name, start, end, text),
                                            span)
            else:
                linenum = self.stc.LineFromPosition(span[0])
                try:
                    text = self.stc.GetLineUTF8(linenum)
                    text = text[:512]
                    self.listCtrlResults.Append("[%s] Line %d: %s" % (state_name, linenum+1, text), span)
                except UnicodeDecodeError:
                    self.listCtrlResults.Append("[%s] Line %d: ......" % (state_name, linenum+1), span)
                if linenum < current_line:
                    self.config.CurrentLine += 1

        self.listCtrlResults.Thaw()
        self.SetCursor(cursor)

    def RefreshListBox2(self, matches):
        self.listCtrlResults.Clear()
        cursor = self.GetCursor()
        self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
        self.listCtrlResults.Freeze()
        for m in matches:
            self.listCtrlResults.Append(m[0],m[1])
        self.listCtrlResults.Thaw()
        self.SetCursor(cursor)
        self.config.CurrentLine = 0

    def OnSearchWordKeyDown(self, event):
        key = event.GetKeyCode()
        if key in (27,):
            wx.py.dispatcher.send(signal='Close', sender = self.parent, event = None)
        else:
            event.Skip()

    def OnPanelSearchReSize(self, event):
        event.Skip()
        self.listSize = self.listCtrlResults.Size
        
    def GetSearchConfig(self):
        config = SearchConfig()
        config.Highlight = self.checkBoxHighlight.GetValue()
        config.Case = self.checkBoxCase.GetValue()
        config.Wholeword = self.checkBoxWholeword.GetValue()
        config.Regular = self.checkBoxRegular.GetValue()
        config.SearchWord = self.searchWord.GetValue()
        config.Direction = SearchDirection.Forward
        if self.radioButtonBackward.GetValue():
            config.Direction = SearchDirection.Backward
        return config
    
    def OnTransparentTicks(self, event):
        event.Skip()
        self.parent.SetTransparent(event.GetPosition())

    def GetStateNamebyPos(self, start_pos):
        tree = self.logviewer.tree
        f3log_obj = self.logviewer.tree.GetPyData(tree.RootItem)

        if f3log_obj:
            state, _ = f3log_obj.GetStateByPos(start_pos)
            if state:
                return state.StateName

        return ""

        
class FrameSearch(wx.Frame):
    def __init__(self, prnt, style = wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE):
        wx.Frame.__init__(self, id=-1, name='FrameSearch',
              parent=prnt, pos=wx.Point(348, 230),
              style= style #|wx.THICK_FRAME|wx.SIMPLE_BORDER #| wx.FRAME_FLOAT_ON_PARENT
              , title='Search')
        
        self.panel = create(self)
        self.SetClientSize(self.panel.Size)
        self.Bind( wx.EVT_CLOSE, self.OnCloseWindow)
        self.CenterOnScreen()
        
    def OnCloseWindow(self, event):
        self.Show(False)
        self.GetParent().SetFocus()
        
    def SetSearchWord(self, text):
        self.panel.SetSearchWord(text)
        
    def SetSTC(self, stc):
        self.panel.SetSTC(stc)

    def SetLogViewer(self, logviewer):
        self.panel.SetLogViewer(logviewer)


class FindInFilesThread(threading.Thread):
    def __init__(self, matches, func_update, func_done):
        threading.Thread.__init__(self)
        self.matches = matches
        self.func_update = func_update
        self.func_done = func_done
    
    def run(self):
        try:
            for m in self.matches:  # trigger iterable generators
                wx.CallAfter(self.func_update)
            wx.CallAfter(self.func_done)
        except:
            utils.logger.exception("Find in Files Error:")
            wx.CallAfter(self.func_done)

            
class PanelFindInFiles(wx.Panel):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=wxID_PANELSEARCH, name='PanelSearch',
              parent=prnt, pos=wx.Point(483, 278), size=wx.Size(658, 494),
              style=wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(650, 464))
        self.SetAutoLayout(True)
        prnt.SetMinSize(wx.Size(658, 100))
        self.Bind(wx.EVT_SIZE, self.OnPanelSearchReSize)
        

        self.staticTextSearch = wx.StaticText(label='Search: ', name='staticTextSearch', parent=self,
              pos=wx.Point(8, 22), size=wx.Size(41, 13), style=0)
        self.searchWord = wx.ComboBox( 
              name='searchWord', parent=self, pos=wx.Point(66, 16),
              size=wx.Size(472, 21), style=0)
        self.searchWord.Select(0)
        self.searchWord.SetConstraints(LayoutAnchors(self.searchWord, True,
              True, True, False))
        self.searchWord.Bind(wx.EVT_KEY_DOWN, self.OnSearchWordKeyDown)
        
        
        self.staticTextFilter = wx.StaticText(label='File Filter:', name='staticTextFilter', parent=self,
              pos=wx.Point(8, 46), size=wx.Size(-1, 13), style=0)
        self.searchFilter = wx.ComboBox( 
              name='searchFilter', parent=self, pos=wx.Point(66, 41),
              size=wx.Size(472, 21), style=0)
        self.searchFilter.Select(0)
        self.searchFilter.SetConstraints(LayoutAnchors(self.searchFilter, True,
              True, True, False))
        
        

        self.buttonFind = wx.Button(label='Find in Files', name='buttonFind', parent=self,
              pos=wx.Point(546, 14), size=wx.Size(96, 23), style=0)
        self.buttonFind.SetConstraints(LayoutAnchors(self.buttonFind, False,
              True, True, False))
        self.buttonFind.Bind(wx.EVT_BUTTON, self.OnButtonFind)
        self.buttonFind.SetDefault()

        self.buttonClose = wx.Button(id=wx.ID_CANCEL,
              label='Close', name='buttonClose', parent=self, 
              pos=wx.Point(546,40), size=wx.Size(96, 23), style=0)
        self.buttonClose.SetConstraints(LayoutAnchors(self.buttonClose, False,
              True, True, False))
        self.buttonClose.Bind(wx.EVT_BUTTON, self.OnButtonClose,
              id=wx.ID_CANCEL)
        
        
        self.checkBoxCase = wx.CheckBox(id=wxID_PANELSEARCHCHECKBOXCASE,
              label='Case sensitivity', name='checkBoxCase', parent=self,
              pos=wx.Point(8, 100), size=wx.Size(122, 13), style=0)
        self.checkBoxCase.SetValue(False)

        self.checkBoxWholeword = wx.CheckBox(id=wxID_PANELSEARCHCHECKBOXWHOLEWORD,
              label='Match whole word', name='checkBoxWholeword', parent=self,
              pos=wx.Point(130, 100), size=wx.Size(122, 13), style=0)
        self.checkBoxWholeword.SetValue(False)

        self.checkBoxRegular = wx.CheckBox(id=wxID_PANELSEARCHCHECKBOXREGULAR,
              label='Regular experssion', name='checkBoxRegular', parent=self,
              pos=wx.Point(8, 120), size=wx.Size(122, 13), style=0)
        self.checkBoxRegular.SetValue(False)
        
        self.checkBoxSubdir = wx.CheckBox(id=wxID_PANELSEARCHCHECKBOXREGULAR,
              label='Include Subdir', name='checkBoxSubdir', parent=self,
              pos=wx.Point(130, 120), size=wx.Size(122, 13), style=0)
        self.checkBoxSubdir.SetValue(False)
           

        self.buttonCopy = wx.Button(id=wxID_PANELSEARCHBUTTONCOPY,
              label='Copy to Clipboard', name='buttonCopy', parent=self,
              pos=wx.Point(540, 90), size=wx.Size(104, 23), style=0)
        self.buttonCopy.Bind(wx.EVT_BUTTON, self.OnButtonCopy)

        self.buttonSave = wx.Button(id=-1,
            label='Save to File', name='buttonSave', parent=self,
            pos=wx.Point(540, 120), size=wx.Size(104, 23), style=0)
        self.buttonSave.Bind(wx.EVT_BUTTON, self.OnButtonSave)

        self.gauge = wx.Gauge(self, -1, 2, pos=(0, 142), size=(650, 8))
        self.StopGauge()

        self.listCtrlResults = wx.ListBox(id=wxID_PANELSEARCHLISTCTRLRESULTS,
              name='listCtrlResults', parent=self, pos=wx.Point(0, 150),
              size=wx.Size(650, 314), style=wx.LB_HSCROLL)
        self.listCtrlResults.SetAutoLayout(False)
        self.listCtrlResults.SetConstraints(LayoutAnchors(self.listCtrlResults,
              True, True, True, True))
        self.listCtrlResults.Bind(wx.EVT_LISTBOX, self.OnDClicklistCtrlResults)

    def __init__(self, parent, id, pos, size, style, name):
        self.parent = parent
        self._init_ctrls(parent)
        self.config = None
        self.results_count = 0

    def StartGauge(self):
        self.buttonFind.SetLabel("Searching...")
        self.buttonFind.Disable()
        self.gauge.Show()

    def UpdateGauge(self):
        self.gauge.Pulse()

    def StopGauge(self):
        self.gauge.Hide()

    def SetFindDirectory(self, path):
        self.findDirBrowser.SetValue(path)
        
    def OnPanelSearchReSize(self, event):
        event.Skip()
        self.listSize = self.listCtrlResults.Size
        
    def OnSearchWordKeyDown(self, event):
        event.Skip()

    def OnSearchCompleted(self):
        self.StopGauge()
        wxwidgets.MessageBox(msg="%s items found" % self.results_count)
        self.buttonFind.Enable()
        self.buttonFind.SetLabel("Find in Files")

    def OnButtonFind(self, event):
        searchword = self.searchWord.GetValue()
        if searchword == '':
            wxwidgets.MessageBox(msg="Please input word to search")
            return
        filefilter = self.searchFilter.GetValue()
        self.SetSearchWord(searchword, filefilter)
        
        config = self.GetFindinFilesConfig()
        if config.isEqual(self.config):
            pass
        elif not config.Directory:
            wxwidgets.MessageBox(msg="Please input search directory")
        else:
            #new search
            self.listCtrlResults.Clear()
            # self.SaveSearchConfig(config)
            self.results_count = 0
            self.config, matches = self.FindinFiles( searchword, config)
            self.StartGauge()
            thread = FindInFilesThread(matches, self.UpdateGauge, self.OnSearchCompleted)
            thread.start()
        
        event.Skip()
        
    def OnButtonClose(self, event):
        self.parent.Show(False)
        self.parent.GetParent().SetFocus()
           
    def OnButtonCopy(self, event):
        event.Skip()
        result = ''.join(self.listCtrlResults.GetItems())
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(wx.TextDataObject(result))
        wx.TheClipboard.Close()

    def OnButtonSave(self, event):
        event.Skip()
        result = ''.join(self.listCtrlResults.GetItems())
        if not result:
            wxwidgets.MessageBox(msg="no result to save")
            return

        dlg = wx.FileDialog(
            self, message="Save result as ...", defaultFile="search_result",
            wildcard="Text files (*.txt)|*.txt|All files|*.*", style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            dlg.Destroy()
            if os.path.exists(path):
                if wxwidgets.MessageBox(msg="file existed, replace it?",
                                        title="Warning",
                                        style=wx.YES_NO) != wx.ID_YES:
                    return
            f = open(path, "w")
            f.write(result)
            f.close()
        else:
            dlg.Destroy()

    def OnDClicklistCtrlResults(self, event):
        event.Skip()
        filename, linenum, searchword, span = event.GetClientData()
        self.LogViewer.ShowLogFileLine(filename=filename, linenum=linenum,
                                       searchword=searchword, span=span)
        self.listCtrlResults.SetFocus()
        
    def FindSearchString(self, text):
        for index in xrange(self.searchWord.Count):
            if self.searchWord.GetString(index) == text:
                return index
        return -1
        
    def SetSearchWord(self, text, filefilter):
        index = self.FindSearchString(text)
        if index < 0:
            index = self.searchWord.Insert(text, 0)
        self.searchWord.Select(index)
        
        index = self.searchFilter.FindString(filefilter)
        if index < 0:
            index = self.searchFilter.Insert(filefilter, 0)
        self.searchFilter.Select(index)
        
    def GetFindinFilesConfig(self):
        config = SearchConfig()
        config.Case = self.checkBoxCase.GetValue()
        config.Wholeword = self.checkBoxWholeword.GetValue()
        config.Regular = self.checkBoxRegular.GetValue()
        config.SearchWord = self.searchWord.GetValue()
        config.FileFilter = utils.RemoveNoneInList(self.searchFilter.GetValue().split(','))
        if not config.FileFilter:
            config.FileFilter = ["*.*"]
        config.FileFilter = [f.strip() for f in config.FileFilter]
        config.IncludeSubDir = self.checkBoxSubdir.GetValue()
        config.Directory = self._findDirectory = self.findDirBrowser.GetValue()
        return config
    
    # def SaveSearchConfig(self, config):
    #     utils.setSetting("FIF_dir_history", config.Directory)
        
    #     f = ','.join(config.FileFilter)
    #     filters = utils.getSetting('FIF_filter_history',[])
    #     try:
    #         filters.remove(f)
    #     except:
    #         pass
    #     filters.insert(0, f)
    #     utils.setSetting('FIF_filter_history',filters[:utils.HISTORY_ITEMS])
        
    #     search_his = utils.getSetting('FIF_search_history',[])
    #     try:
    #         search_his.remove(config.SearchWord)
    #     except:
    #         pass
    #     search_his.insert(0, config.SearchWord)
    #     utils.setSetting('FIF_search_history',search_his[:utils.HISTORY_ITEMS])
               
    #     utils.saveSettings()
    
    def FindinFiles(self, searchword, config):
        engine = searcheng.SearchEngine(searchword, config.Regular,
                                     True, config.Case, config.Wholeword)
        engine.SetFileFilters(config.FileFilter)
        engine.SetResultFormatter(self.InsertResult)
        matches = engine.SearchInDirectory(config.Directory, config.IncludeSubDir)

        return config, matches
          
    def InsertResult(self, filename, linenum, matchstr, span):
        showname = filename
        if len(showname) > 60:
            showname = "%s......%s"%(showname[:20],showname[-40:])
        self.listCtrlResults.Append("%s  %d:  %s"%(showname,linenum+1,matchstr), 
                        clientData=(filename, linenum, self.config.SearchWord, span))
        self.UpdateGauge()
        self.results_count += 1

        
class FrameFindInFile(wx.Frame):
    def __init__(self, prnt, style = wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE):
        wx.Frame.__init__(self, id=-1, name='FrameFindInFile',
                        parent=prnt, pos=wx.Point(348, 230),
                        style= style, title='Find in Files')
        # self.SetIcon(images.findinfiles.GetIcon())
        
        self.panel = PanelFindInFiles(self, id=-1,    
                       pos=wx.Point(0, 0), size=wx.Size(-1, -1),
                       style=wx.TAB_TRAVERSAL,name='')
        self.SetClientSize(self.panel.Size)
        
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.CenterOnScreen()
    
    def OnCloseWindow(self, event):
        self.Show(False)    
        self.GetParent().Show()
    
    def SetLogViewer(self, logviewer):
        self.panel.LogViewer = logviewer
        
    def SetFindDirectory(self, path):
        self.panel.SetFindDirectory(path)


class BoaApp(wx.App):
    def OnInit(self):
        self.main = FrameSearch(None)
        self.main.Show()
        self.SetTopWindow(self.main)
        return True


def main():
    application = BoaApp(0)
    application.MainLoop()


if __name__ == '__main__':    
    main()
