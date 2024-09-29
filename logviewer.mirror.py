import wx
import sealogfile as sealog
import wx.lib.buttons as buttons
from wx.py.editor import EditWindow
import wx.lib.agw.aui as aui
# import pandas as pd
from cryptography.hazmat.primitives.kdf import pbkdf2
import encodings.idna
import re, os, sys
from history_frame import history_frame
from sealogfile.utils import str_it
import sealogfile.highlight as HL
import configparser


config = configparser.ConfigParser()
config.read('config.ini')
try:
    max_history_count = config['SETUP'].getint('MAX_HISTORY')
except:
    max_history_count = 100

class LogViewer(wx.Panel):
    """LogViewer modified to be used inside a tab."""
    def __init__(self, parent, logobj:sealog.F3LogFile):
        super(LogViewer, self).__init__(parent)
        self.parent = parent
        with open(logobj.FileName,'rb') as r:
            self.raw_log = r.read()
        self.TabName = None
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
        self.build_tree()
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_tree_selection)
        HL.initStyles(self.editor)
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
            HL.highlight(self.editor, HL.STYLE_STATE, state)

            for st in state.STList:
                name = str_it(st.TestName)
                param = str_it(st.ExecutionParameter)
                try:
                    stitem = f"[{st.TestNum:03}] {name} ({param})"
                except:
                    stitem = f"[{st.TestNum:03}] Unknown Test ({param})"
                
                st_item = self.tree.AppendItem(state_item, stitem)
                self.tree.SetItemData(st_item, st)

                if st.TestNum > 0:
                    HL.highlight(self.editor, HL.STYLE_SELFTEST, st)

                for dblog in st.DBLogList:
                    dblog_str = dblog.Name
                    dblog_item = self.tree.AppendItem(st_item, dblog_str)
                    self.tree.SetItemData(dblog_item, dblog)
                    if st.TestNum > 0:
                        HL.highlight(self.editor, HL.STYLE_DBLOG, dblog)
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
        key = event.GetKeyCode()
        controlDown = event.ControlDown()
        altDown = event.AltDown()

        if controlDown and altDown:
            event.Skip()
        # # Increase font size.
        # elif controlDown and key in (ord(']'), ord('}')):
        #     wx.py.dispatcher.send(signal='FontIncrease')
        # # Decrease font size.
        # elif controlDown and key in (ord('['), ord('{'),):
        #     wx.py.dispatcher.send(signal='FontDecrease')
        # # Default font size.
        # elif controlDown and key in (ord('+'), ord('=')):
        #     wx.py.dispatcher.send(signal='FontDefault')
        # # Find text
        elif controlDown and key in (ord('F'), ord('f')):
            search_dialog = sealog.SearchDialog(self)
            search_dialog.Show()
        elif controlDown and key in (ord('U'), ord('u')):
            search_dialog = HL.highlight(self.editor,)
            search_dialog.Show()
        else:
            event.Skip()

    def Activate_Tab(self):
        for i in range(self.parent.GetPageCount()):
            if self.parent.GetPageText(i) == self.TabName:
                self.parent.SetSelection(i)
                return

class MainFrame(wx.Frame):
    """MainFrame to manage multiple LogViewer instances using tabs."""
    
    def __init__(self, parent, title):
        super(MainFrame, self).__init__(parent, title=title, size=(800, 600))
        self.hist_frame = None  # Initialize the history frame reference
        self.toolbar = self.CreateToolBar()
        self.toolbar.SetToolBitmapSize((24, 24))
        
        self.toolbar.AddControl(wx.StaticText(self.toolbar, -1, " DriveSN: "))
        self.toolbar.AddSeparator()
        #self.snlist = utils.getSetting("DriveSN_history", [])
        self.snlist = ['']
        self.comboBoxSN = wx.ComboBox(parent=self.toolbar, id=-1, value="", size=wx.Size(90, 20), choices=self.snlist)
        self.comboBoxSN.Select(0)
        self.toolbar.AddControl(self.comboBoxSN)
        self.toolbar.AddSeparator()
        btnGo = buttons.ThemedGenBitmapTextButton(self.toolbar, -1, None, 'View History', size=wx.Size(100, 26))
        self.toolbar.AddSeparator()
        self.Bind(wx.EVT_BUTTON, self.OnButtonGo, btnGo)
        self.toolbar.AddControl(btnGo)
        self.toolbar.Realize() 

        # Create a notebook (tab control)
        #self.notebook = wx.Notebook(self)
        self.notebook  = aui.AuiNotebook(self)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def OnButtonGo(self, event):
        event.Skip()
        drivesn = self.comboBoxSN.GetValue().strip().upper()
        m = re.search("([A-Z0-9]{8})", drivesn)
        if len(drivesn) == 8 :
            cursor = self.GetCursor()
            self.SetCursor(wx.Cursor(wx.CURSOR_WAIT))
            if self.hist_frame is None or not self.hist_frame.IsShown():
                self.hist_frame = history_frame(self, drivesn, max_history_count)
                self.hist_frame.Bind(wx.EVT_CLOSE, self.on_hist_frame_close)
                self.hist_frame.Show()
            else:
                self.hist_frame.Raise()  # Bring the existing frame to the front

            self.SetCursor(cursor)
        else:
            wx.MessageBox("Pls input valid Drive SN!")


    def on_hist_frame_close(self, event):
        # Set the reference to None when the frame is closed
        self.hist_frame = None
        event.Skip()  # Let the default close event happen

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

    def add_log_tab(self, logobj: sealog.F3LogFile):
        log_filename = os.path.basename(logobj.FileName)
        for i in range(self.notebook.GetPageCount()):
            if self.notebook.GetPageText(i) == log_filename:
                self.notebook.SetSelection(i)
                return
        logobj.Process(skip_header_footer=False)
        log_viewer = LogViewer(self.notebook, logobj)
        self.notebook.AddPage(log_viewer, log_filename, select=True)
        log_viewer.TabName = log_filename
# Main application
if __name__ == "__main__":
    if sys.version_info[0] == 3:
        print('This is Python3 .. Lets Rock n Roll!!!')
        app = wx.App(False)
        frame = MainFrame(None, "LogViewer ก๊อบเกรด B ( Speed9 Logviewer)")
        frame.Show(True)
        # #ftp_zip_path = "teppinasv001.seagate.com/prod/none/merlin/history/COMET/20/B04D062F.4905113404.r.zip"
        # local_file="B04D062F_COMET_135_PASS.txt"
        # log_process = log_obj_creater('ABCDE','TEST',99,'PASS',ftp_zip_path,local_file)
        # frame.add_log_tab(log_process.logobj)
        app.MainLoop()
    else:
        print('Python2.... You are too old.. please install new python..')

