import wx
import sealogfile as sealog
import wx.lib.buttons as buttons
from wx.py.editor import EditWindow
import pandas as pd
import re, os, math
from history_frame import history_frame   #from history_frame import history_frame,log_obj_creater
from log_server_process import log_obj_creater
from sealogfile.utils import str_it
# import sealogfile.highlight as HL

class LogViewer(wx.Panel):
    """LogViewer modified to be used inside a tab."""
    
    def __init__(self, parent, logobj:sealog.F3LogFile):
        super(LogViewer, self).__init__(parent)
        with open(logobj.FileName,'rb') as r:
            self.raw_log = r.read()

        # Split window into two panels
        self.splitter = wx.SplitterWindow(self)
        self.left_panel = wx.Panel(self.splitter)
        self.right_panel = wx.Panel(self.splitter)
        self.splitter.SplitVertically(self.left_panel, self.right_panel, sashPosition=int(800 * 0.3))

        # Tree control for the left panel
        self.tree = wx.TreeCtrl(id=-1,
            name='treeLeft', parent=self.left_panel, pos=wx.Point(0, 0),
            size=wx.Size(160, 466), style=wx.TR_DEFAULT_STYLE |
                                          wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_HAS_BUTTONS | wx.BORDER_THEME)
        self.tree.SetSpacing(8)
        self.tree.SetMinSize(wx.Size(10, 200))

        # TextCtrl for the right panel (to display log content)
        self.editor = EditWindow(self, parent=self.right_panel)
        self.editor.SetAutoLayout(True)
        self.editor.SetMinSize(wx.Size(300, 200))
        self.editor.SetLexer(wx.stc.STC_LEX_NULL)
        self.editor.SetEOLMode(wx.stc.STC_EOL_CRLF)
        self.editor.SetEndAtLastLine(True)
        self.editor.SetScrollWidth(4200)
        self.editor.SetText(self.raw_log)
        self.editor.SetLayoutCache(wx.stc.STC_CACHE_PAGE)
        self.editor.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.editor.setDisplayLineNumbers(True)
        self.editor.ReadOnly = True
        
        # Layout management
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(self.tree, 1, wx.EXPAND)
        self.left_panel.SetSizer(left_sizer)

        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(self.editor, 1, wx.EXPAND)
        self.right_panel.SetSizer(right_sizer)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.splitter, 1, wx.EXPAND)
        self.SetSizer(main_sizer)
        
        # Store parsed log data
        self.log_data = logobj
        print(logobj.TestStateList)
        self.build_tree()

        # Bind events
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_tree_selection)

    def build_tree(self):
        """Build tree based on the log data structure."""
        self.tree.DeleteAllItems()
        root = self.tree.AddRoot('%s-%s-%s' % (self.log_data.SerialNo, self.log_data.Oper, self.log_data.ErrorCode))
        self.tree.SetItemData(root, self.log_data)
        self.tree.SetItemBold(root, True)
        for state in self.log_data.TestStateList:
            state_item = self.tree.AppendItem(root, state.StateName)
            self.tree.SetItemData(state_item, state)
            self.tree.SetItemBold(state_item, True)
            #HL.highlight(self.editor, HL.STYLE_STATE, state_item)
            # Highlight(stc_editor, style, f3logobj, base_start=0):
            for st in state.STList:
                name = str_it(st.TestName)
                param = str_it(st.ExecutionParameter)
                try:
                    stitem = f"[{st.TestNum:03}] {name} ({param})"
                except:
                    stitem = f"[{st.TestNum:03}] Unknown Test ({param})"
                st_item = self.tree.AppendItem(state_item, stitem)
                self.tree.SetItemData(st_item, st)
                #HL.highlight(self.editor, HL.STYLE_SELFTEST, st_item)
                for dblog in st.DBLogList:
                    dblog_str = dblog.Name
                    dblog_item = self.tree.AppendItem(st_item, dblog_str)
                    self.tree.SetItemData(dblog_item, dblog)
                   # HL.highlight(self.editor, HL.STYLE_DBLOG, dblog_item)
        self.tree.Expand(root)

    def on_tree_selection(self, event):
        """Handle selection of a tree item and highlight corresponding log text."""
        item = self.tree.GetSelection()
        item_data = self.tree.GetItemData(item)
        start_pos = item_data.Span[0]
        end_pos = item_data.Span[1]
        self.editor.SetSelection(start_pos, end_pos)  # Highlight from start to end
        # Scroll to the highlighted text
        line_start = self.editor.LineFromPosition(start_pos)
        self.editor.ScrollToLine(line_start - 5)
        self.editor.SetFocus()

    def OnKeyDown(self, event):
        """Key down event handler."""
        event.Skip()
        
class MainFrame(wx.Frame):
    """MainFrame to manage multiple LogViewer instances using tabs."""
    
    def __init__(self, parent, title):
        super(MainFrame, self).__init__(parent, title=title, size=(800, 600))
        
        self.toolbar = self.CreateToolBar()
        self.toolbar.SetToolBitmapSize((24, 24))
        
        self.toolbar.AddControl(wx.StaticText(self.toolbar, -1, " DriveSN: "))
        self.toolbar.AddSeparator()
        #self.snlist = utils.getSetting("DriveSN_history", [])
        self.snlist = ['B04D062F']
        self.comboBoxSN = wx.ComboBox(parent=self.toolbar, id=-1, value="", size=wx.Size(90, 20), choices=self.snlist)
        self.comboBoxSN.Select(0)
        self.toolbar.AddControl(self.comboBoxSN)
        self.toolbar.AddSeparator()
        btnGo = buttons.ThemedGenBitmapTextButton(self.toolbar, -1, None, 'Show Logfile', size=wx.Size(100, 26))
        self.toolbar.AddSeparator()
        self.Bind(wx.EVT_BUTTON, self.OnButtonGo, btnGo)
        self.toolbar.AddControl(btnGo)
        self.toolbar.Realize() 

        # Create a notebook (tab control)
        self.notebook = wx.Notebook(self)

        # # Add menu or other UI elements if necessary (e.g., to open new logs)
        # self.menu_bar = wx.MenuBar()
        # file_menu = wx.Menu()
        # open_menu_item = file_menu.Append(wx.ID_OPEN, "&Open Log\tCtrl+O", "Open a log file")
        # self.Bind(wx.EVT_MENU, self.on_open_log, open_menu_item)
        # self.menu_bar.Append(file_menu, "&File")
        # self.SetMenuBar(self.menu_bar)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def on_open_log(self, event):
        """Event handler for opening new log files."""
        with wx.FileDialog(self, "Open Log File", wildcard="Log files (*.txt)|*.txt",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return  # The user canceled the dialog

            # Proceed to open the file
            path = file_dialog.GetPath()
            self.open_log_file(path)

    def OnButtonGo(self, event):
        event.Skip()
        drivesn = self.comboBoxSN.GetValue().strip().upper()
        m = re.search("([A-Z0-9]{8})", drivesn)
        if len(drivesn) == 8 :

            cursor = self.GetCursor()
            self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            if self.hist_frame is None or not self.hist_frame.IsShown():
                self.hist_frame = history_frame(self, drivesn, maxts=100)
                self.hist_frame.Show()
            else:
                self.hist_frame.Raise()  # Bring the existing frame to the front

            self.SetCursor(cursor)
        else:
            wx.MessageBox("Pls input valid Drive SN!")

    def open_log_file(self, filepath):
        """Open and parse a log file, then create a new LogViewer tab."""
        try:
            log = sealog.F3LogFile(filepath)
            with open(filepath, 'rb') as raw_logf:
                raw_log = raw_logf.read()
            log.Process(skip_header_footer=True)
            log_viewer = LogViewer(self.notebook, log, raw_log)
            self.notebook.AddPage(log_viewer, os.path.basename(filepath))
        except Exception as e:
            wx.MessageBox(f"Failed to open log file: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
    def add_log_tab(self,logobj:sealog.F3LogFile):
        logobj.Process(skip_header_footer=False)
        log_viewer = LogViewer(self.notebook,logobj)
        self.notebook.AddPage(log_viewer,os.path.basename(logobj.FileName),select = True)
            



# Main application
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame(None, "Multiple Log Viewer")
    frame.Show(True)
    #def __init__(self,serial,oper,ts,code,ftp_zip_path):
    serial = "ABCDE"
    oper = 'TEST'
    ts = 99
    code= 'PASS'
    #ftp_zip_path = "teppinasv001.seagate.com/prod/none/merlin/history/COMET/20/B04D062F.4905113404.r.zip"
    ftp_zip_path = "teppinasv001.seagate.com/prod/none/merlin/history/COMET/20/B04D062F.4905113404.r.zip"
    local_file="B04D062F_COMET_135_PASS.txt"
    log_process = log_obj_creater(serial,oper,ts,code,ftp_zip_path,local_file)

    frame.add_log_tab(log_process.logobj)
    app.MainLoop()
