import wx
import re
import copy
import wx.grid
import wx.html
import threading
import wx.lib.platebtn as platebtn


def SetTransparent(window, alpha):
    if wx.Platform == "__WXMSW__":
        import ctypes
        user32 = ctypes.windll.user32
        hwnd = window.GetHandle()
        style = user32.GetWindowLongA(hwnd, -20)
        style |= 0x00080000
        user32.SetWindowLongA(hwnd, -20, style)
        user32.SetLayeredWindowAttributes(hwnd, 0, alpha, 2)
    else:
        window.SetTransparent(alpha)


class TransparentText(wx.StaticText):
    def __init__(self, parent, id=wx.ID_ANY, label='',
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.TRANSPARENT_WINDOW, name='transparenttext'):
        wx.StaticText.__init__(self, parent, id, label, pos, size, style, name)

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_paint(self, event):
        bdc = wx.PaintDC(self)
        dc = wx.GCDC(bdc)

        font_face = self.GetFont()
        font_color = self.GetForegroundColour()

        dc.SetFont(font_face)
        dc.SetTextForeground(font_color)
        dc.DrawText(self.GetLabel(), 0, 0)

    def on_size(self, event):
        self.Refresh()
        event.Skip()


class PromptingComboBox(wx.ComboBox):
    def __init__(self, parent, value, choices=[], choices_ac=[], style=0, **params):
        wx.ComboBox.__init__(self, parent, wx.ID_ANY, value,
            style=style | wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER,
            choices=choices, **params)
        self.choices = choices_ac or choices
        self.Bind(wx.EVT_TEXT, self.EvtText)
        self.Bind(wx.EVT_CHAR, self.EvtChar)
        self.Bind(wx.EVT_COMBOBOX, self.EvtCombobox)
        self.ignoreEvtText = False

    def Clear(self, *args, **kwargs):
        self.choices = []
        wx.ComboBox.Clear(self, *args, **kwargs)

    def EvtCombobox(self, event):
        self.ignoreEvtText = True
        event.Skip()

    def EvtChar(self, event):
        key_code = event.GetKeyCode()
        if key_code in (8,):
            self.ignoreEvtText = True
        if key_code in (9,32):  # tab and blank
            str_len = len(self.GetValue())
            self.SetInsertionPoint(str_len)
            self.SetMark(str_len, str_len)
            self.ignoreEvtText = True

        if key_code not in (9,):
            event.Skip()

    def EvtText(self, event):
        if self.ignoreEvtText:
            self.ignoreEvtText = False
            return
        currentText = event.GetString().lower()
        if not currentText:
            event.Skip()
            return
        found = False
        for choice in self.choices:
            if choice.lower() == currentText:
                event.Skip()
                return
            if choice.lower().startswith(currentText):
                self.SetValue(choice)
                wx.CallAfter(self.SetFocus)
                wx.CallAfter(self.SetInsertionPoint, len(currentText))
                wx.CallAfter(self.SetMark, len(currentText), len(choice))
                found = True
                break
        if not found:
            event.Skip()


class RMGridTable(wx.grid.PyGridTableBase):
    RE_FILTER = re.compile(r'''(?P<name>\w+)\b\s*(?P<op>[<>=!|&^]+| in | not in )\s*(?P<val>\S+)''')

    def __init__(self, name, data, colnames,grid):
        wx.grid.PyGridTableBase.__init__(self)
        self.dataOrg = data
        self.grid = grid
        self.name = name
        self.restData = []
        self.filter = []
        self.lengthLimit = 500
        self.IsDivided = False
        self.filterFlag = False
        self.firstLoading = True
        self.DivideData(data)
        self.colnames = colnames
        for col in range(len(colnames), len(self.data[-1])):
            self.colnames.append(self.GetColLabelValue(col))

        self.sort_reverse = False

    def GetAllData(self):
        return [self.dataOrg, self.filter][self.filterFlag]

    def DivideData(self, data, filterFlag=False):
        self.filterFlag = filterFlag
        self.restData = []
        if len(data) > self.lengthLimit:
            dataLength = len(data)
            start = 0
            for i in range(int(dataLength / self.lengthLimit) + 1):
                self.restData.append(data[start:start + self.lengthLimit])
                start += self.lengthLimit
            self.data = self.restData.pop(0)
            self.IsDivided = True
        else:
            self.IsDivided = False
            if filterFlag:
                self.data = data
            else:
                self.data = self.dataOrg

    def Reset(self, grid):
        old_numrows = self.GetNumberRows()
        self.DivideData(self.dataOrg)
        new_numrows = self.GetNumberRows()
        count = new_numrows - old_numrows
        self.RefreshView(grid, count)


    def AppendRestData(self, grid):
        if self.IsDivided:
            restData = self.restData.pop(0)
            count = len(restData)
            self.data.extend(restData)
            self.RefreshView(grid, count)
            if len(self.restData)==0:
                 self.IsDivided = False

    def RefreshView(self, grid, count=0):
        grid.BeginBatch()
        if count > 0:
            msg = wx.grid.GridTableMessage(self,
                wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED,
                count, -1)
        elif count < 0:
            msg = wx.grid.GridTableMessage(self,
                wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED,
                self.GetNumberRows(), abs(count))
        if count != 0:
            grid.ProcessTableMessage(msg)

        msg = wx.grid.GridTableMessage(self,
            wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        grid.ProcessTableMessage(msg)

        grid.AdjustScrollbars()
        grid.EndBatch()
        grid.Refresh()

    def Filter(self, filter_string, grid):
        def evalFilter(line, index, op, val):
            try:
                data = line[index]
            except:
                return False
            op = op.strip()
            if op == "=":
                op = "=="
            try:
                val = eval(val)
                if op in ("in", "not in"):
                    data_type = type(val[0])
                else:
                    data_type = type(val)

                if data_type in (int, long):
                    if data.find(".") > -1:
                        data = float(data)
                    else:
                        data = int(data)
                else:
                    data = data_type(data)
            except:
                pass

            exp = "data %s val" % (op)
            return eval(exp)

        old_numrows = self.GetNumberRows()
        filter_string = filter_string and filter_string.replace('==', '=')
        matches = filter_string and self.RE_FILTER.finditer(filter_string)
        if not matches:
            return False

        filters = []
        new_filterstring = filter_string
        for match in matches:
            name = match.group('name').lower()
            op = match.group('op')
            val = match.group('val')

            index = 0
            for desc in self.colnames:
                if desc.lower() == name:
                    name_index = index
                    break
                index += 1
                name_index = index

            if index >= len(self.colnames):
                raise Exception("no '%s' in this table" % name)
            filters.append((name_index, op, val))

            new_filterstring = new_filterstring.replace(match.group(0), '%s')

        filter_data = []
        for line in self.dataOrg:
            results = []
            for f in filters:
                results.append(evalFilter(line, f[0], f[1], f[2]))

            result_string = new_filterstring % tuple(results)
            if eval(result_string):
                filter_data.append(line)

        self.filter = filter_data
        self.DivideData(filter_data, True)
        new_numrows = self.GetNumberRows()
        self.RefreshView(grid, new_numrows - old_numrows)

        return True

    def GetNumberCols(self):
        return max(len(self.colnames), len(self.data[-1]))

    def GetNumberRows(self):
        return len(self.data)

    def GetColLabelValue(self, col):
        if col < len(self.colnames):
            return self.colnames[col]
        col_name = []
        while True:
            col_name.append(chr(ord('A') + col % 26))
            col = col / 26
            if col <= 0:
                break
        col_name.reverse()
        return ''.join(col_name)

    def GetRowLabelValue(self, row):
        if row == self.GetNumberRows()-1:
            if not self.firstLoading:
                self.AppendRestData(self.grid)
            else:
                self.firstLoading = False
        return "%s" % (row)

    def GetValue(self, row, col):
        try:
            return self.data[row][col]
        except:
            return ""

    def SetValue(self, row, col, value):
        pass

    def SortColumn(self, col):
        def sort_key(line):
            if col >= len(line):
                return ""
            try:
                return float(line[col])
            except:
                return line[col]

        self.data.sort(key=sort_key, reverse=self.sort_reverse)
        self.sort_reverse = not self.sort_reverse


import wx.lib.sized_controls as sc


class HtmlDialog(sc.SizedDialog):
    def __init__(self, parent, title, html_source, pos=wx.DefaultPosition, size=(550, 190)):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        wx.Dialog.__init__(self, parent, -1, title, style=style, pos=pos)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        html = wx.html.HtmlWindow(self, size=size)
        if "gtk2" in wx.PlatformInfo:
            html.SetStandardFonts()
        html.SetPage(html_source)
        sizer.Add(html, 0, wx.EXPAND | wx.ALL)
        self.SetSizerAndFit(sizer)


class MultilineTextEntryDialog(wx.Dialog):
    def __init__(self, parent, caption, title, pos=wx.DefaultPosition, size=(100, 300),
                 choices=None, selection=0):
        style = wx.RESIZE_BORDER | wx.NO_BORDER
        super(MultilineTextEntryDialog, self).__init__(parent, -1, title, style=style, pos=pos)
        text = wx.StaticText(self, -1, caption)
        input = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
        input.SetInitialSize(size)
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, 0, wx.ALL, 5)
        sizer.Add(input, 1, wx.EXPAND | wx.ALL, 5)

        self.cb_sbr = wx.CheckBox(self, -1, "Load from SBR#")
        self.cb_sbr.Bind(wx.EVT_CHECKBOX, self.OnSBRChecked)
        sizer.Add(self.cb_sbr, 0, wx.EXPAND | wx.ALL, 5)

        self.comboBoxServer = wx.ComboBox(parent=self, id=-1, value="", style=wx.CB_READONLY,
                                          size=(80, 20), choices=choices or [])
        self.comboBoxServer.SetSelection(selection)

        sizer.Add(self.comboBoxServer, 0, wx.EXPAND | wx.ALL, 5)

        self.comboBoxServer.Hide()

        sizer.Add(buttons, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizerAndFit(sizer)
        self.input = input

    def ShowModal(self, pos=None, *args, **kwargs):
        if pos:
            self.SetPosition(pos)
        self.input.SetFocus()
        return super(MultilineTextEntryDialog, self).ShowModal(*args, **kwargs)

    def SetValue(self, value):
        self.input.SetValue(value)

    def GetValue(self):
        return self.input.GetValue()

    def OnSBRChecked(self, evt):
        import logservice
        evt.Skip()
        if self.IsSBRChecked:
            site_name = logservice.LogServiceSite.GetSiteNameFromSBR(self.GetValue().strip())
            self.comboBoxServer.SetStringSelection(site_name)

        self.comboBoxServer.Show(self.IsSBRChecked)
        self.Layout()

    @property
    def IsSBRChecked(self):
        return self.cb_sbr.IsChecked()

    @property
    def Site(self):
        return self.comboBoxServer.GetStringSelection()


#
# MenuItem
#
try:
    from agw import flatmenu as FM
except ImportError:  # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.flatmenu as FM


class ReportMenuItem(FM.FlatMenuItem):

    def __init__(self, parent, id=wx.ID_SEPARATOR, text="", helpString="",
                 kind=wx.ITEM_NORMAL, subMenu=None, normalBmp=wx.NullBitmap,
                 disabledBmp=wx.NullBitmap,
                 hotBmp=wx.NullBitmap, report=None):
        FM.FlatMenuItem.__init__(
            self, parent, id, text, helpString, kind, subMenu, normalBmp, disabledBmp, hotBmp)
        self.report = report

    def SetReport(self, report):
        self.report = report

    def GetReport(self):
        return self.report
    Report = property(GetReport, SetReport, None, "Report bind to this menu")


#
# CreateReportMenu
#
def CreateReportMenu(parent, reportlist, onSelectedHandler, icon=wx.NullBitmap):
    reportmenu = FM.FlatMenu()
    for rep in reportlist:
        id = wx.NewId()
        if rep.Name == "--":
            reportmenu.AppendSeparator()
        else:
            menuItem = ReportMenuItem(
                reportmenu, id, rep.Name, "", wx.ITEM_NORMAL)
            reportmenu.AppendItem(menuItem)
            menuItem.Report = rep
            parent.Bind(FM.EVT_FLAT_MENU_SELECTED, onSelectedHandler, id=id)
            menuItem.SetNormalBitmap(icon)
    return reportmenu


def CreateFlatMenu(parent, items, onSelectedHandler, icon=wx.NullBitmap):
    menu = FM.FlatMenu()
    for item in items:
        id = wx.NewId()
        menuItem = FM.FlatMenuItem(menu, id, item, "", wx.ITEM_NORMAL)
        menu.AppendItem(menuItem)
        parent.Bind(FM.EVT_FLAT_MENU_SELECTED, onSelectedHandler, id=id)
        menuItem.SetNormalBitmap(icon)
    return menu


def CreateMenu(parent, items, onSelectedHandler):
    menu = wx.Menu()
    for item in items:
        id = wx.NewId()
        menu.Append(id, item)
        parent.Bind(wx.EVT_MENU, onSelectedHandler, id=id)
    return menu

#
# LogProcessThread
#


class LogProcessThread(threading.Thread):

    def __init__(self, logfile, **kwargs):
        threading.Thread.__init__(self)
        self.logfile = logfile
        self.param = kwargs

    def stop(self):
        pass

    def run(self):
        self.logfile._isProcess = True
        self.logfile.ReProcess()
        wx.CallAfter(self.param["callback"], self.logfile)


def MessageBox(parent=None, msg="", title="", style=wx.OK | wx.ICON_INFORMATION):
    dlg = wx.MessageDialog(parent, msg,
                           title,
                           style)
    result = dlg.ShowModal()
    dlg.Destroy()
    return result


class PlateButton(platebtn.PlateButton):
    def _SetState(self, state):
        self._state['pre'] = self._state['cur']
        self._state['cur'] = state
        self.Parent.Refresh()
