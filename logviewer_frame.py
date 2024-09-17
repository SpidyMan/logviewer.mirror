#import .....
import wx
import sealogfile as sealog
import wx.lib.buttons as buttons
from sealogfile.utils import parse_NRF_file, split_db_table_line, parse_NRF_file_by_Python
from wx.py.editor import EditWindow
#import sql_query
import pandas as pd
import re,os,shutil,math,sys,ftplib
from history_frame import history_frame
from sealogfile.dexer.parse_log import parse_Text_log
#========== FTP Account SETUP ==============
FTP_USERNAME = 'rouser'
FTP_PASSWORD = 'rouser@357'
ConsolePrint = True

logfile = 'processinglog.log'

def write_log(message, log_file):
    with open(log_file, 'a+') as f:
        f.write(message + '\n')
    if ConsolePrint:print(message)

def download_file_from_ftp(host, path, filename, local_dir, log_file = None,SBR_raw_path = ""):
    # SBR_raw_path is optional to seperate zip file by SBR ( not followed FTP path.)
    try:
        if isinstance(host, str): # host just a string means new host.
            if log_file:write_log('connecting......',log_file)
            ftp_server = ftplib.FTP(host, FTP_USERNAME, FTP_PASSWORD)
            ftp_server.host = host

            if ftp_server:
                if log_file:write_log(f'Connected to FTP server {host}', log_file)
            else:
                if log_file:write_log('Failed to connect to FTP server', log_file)
                return None,None
        elif isinstance(host, ftplib.FTP):
            ftp_server = host
        else:
            raise TypeError('Host should be either a string or ftplib.FTP instance.')

        ftp_server.cwd('/'+path)
        path_to_load = os.path.join(path, filename)             # path in FTP server
        
        if SBR_raw_path != "":
            local_path = os.path.join(SBR_raw_path, filename)
        else:
            local_path = os.path.join(local_dir, path, filename)    # path in Local PC

        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        tmp_file = tempfile.NamedTemporaryFile(delete=False) 

        with tmp_file:
            if log_file:write_log(f'Loading: {path_to_load}', log_file)
            ftp_server.retrbinary(f'RETR {filename}', tmp_file.write)

        tmp_local_path = tmp_file.name
        shutil.move(tmp_local_path, local_path)
        
        if log_file:write_log(f'Downloaded {filename} to {local_path}', log_file)
        return local_path,ftp_server

    except Exception as e:
        if log_file:write_log(f'Failed to download {filename}. Error: {e}', log_file)
        try:
            if tmp_local_path:
                os.remove(tmp_local_path)
        except Exception as remove_err:
            if log_file:write_log(f'Failed to remove temporary file {tmp_local_path}. Error: {remove_err}', log_file)
        return None,None

def str_it(value):
    if isinstance(value,bytes):
        return value.decode('utf-8')
    else:
        return value

class LogViewer(wx.Frame):

    def OnKeyDown(self, event):
        """Key down event handler."""
        key = event.GetKeyCode()
        controlDown = event.ControlDown()
        altDown = event.AltDown()

        if controlDown and altDown:
            event.Skip()
        # Increase font size.
        elif controlDown and key in (ord(']'), ord('}')):
            wx.py.dispatcher.send(signal='FontIncrease')
        # Decrease font size.
        elif controlDown and key in (ord('['), ord('{'),):
            wx.py.dispatcher.send(signal='FontDecrease')
        # Default font size.
        elif controlDown and key in (ord('+'), ord('=')):
            wx.py.dispatcher.send(signal='FontDefault')
        # Find text
        elif controlDown and key in (ord('F'), ord('f')):
            search_dialog = sealog.SearchDialog(self)
            search_dialog.Show()
        else:
            event.Skip()

    def __init__(self, parent, title, log,raw_log):
        super(LogViewer, self).__init__(parent, title=title, size=(800,600))


        self.toolbar = self.CreateToolBar()
        self.toolbar.SetToolBitmapSize((24, 24))
        
        self.toolbar.AddControl(wx.StaticText(self.toolbar, -1, " DriveSN: "))
        self.toolbar.AddSeparator()
        #self.snlist = utils.getSetting("DriveSN_history", [])
        self.snlist = ['aaa','bbb']
        self.comboBoxSN = wx.ComboBox(parent=self.toolbar, id=-1, value="", size=wx.Size(90, 20), choices=self.snlist)
        # self.comboBoxSN.Bind(wx.EVT_KEY_DOWN, self.OnSNKeyDown)
        # self.comboBoxSN.Bind(wx.EVT_COMBOBOX, self.OnSNComboBox)
        self.comboBoxSN.Select(0)
        self.toolbar.AddControl(self.comboBoxSN)
        self.toolbar.AddSeparator()
        btnGo = buttons.ThemedGenBitmapTextButton(self.toolbar, -1, None, 'Show Logfile', size=wx.Size(100, 26))
        self.toolbar.AddSeparator()
        self.Bind(wx.EVT_BUTTON, self.OnButtonGo, btnGo)
        self.toolbar.AddControl(btnGo)
        self.toolbar.Realize() 

        self.panel = wx.Panel(self)
        # Split window into two panels
        self.splitter = wx.SplitterWindow(self.panel)
        self.left_panel = wx.Panel(self.splitter)
        self.right_panel = wx.Panel(self.splitter)
        self.splitter.SplitVertically(self.left_panel, self.right_panel, sashPosition=int(800 * 0.3))
        self._searchframe = None
        self.raw_log = raw_log
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
        self.editor.SetText(raw_log)
        self.editor.SetLayoutCache(wx.stc.STC_CACHE_PAGE)
        self.editor.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.editor.setDisplayLineNumbers(True)
        # Layout management
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(self.tree, 1, wx.EXPAND)
        self.left_panel.SetSizer(left_sizer)

        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(self.editor, 1, wx.EXPAND)
        self.right_panel.SetSizer(right_sizer)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.splitter, 1, wx.EXPAND)
        self.panel.SetSizer(main_sizer)
        
        # Store parsed log data
        self.log_data = log
        #self.logfile = log
        self.build_tree()

        # Bind events
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_tree_selection)
    
    def OnButtonGo(self, event):
        event.Skip()
        drivesn = self.comboBoxSN.GetValue().strip().upper()
        m = re.search("([A-Z0-9]{8})", drivesn)
        if len(drivesn) == 8 :

            cursor = self.GetCursor()
            self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            local_file = True
            if local_file:
                history = pd.read_csv('B04D062F_history.csv')
            else:
                history = sql_query.logservice_history_all(drivesn,100)
            print(history)
            if len(history.index)>0:
                ###TODO: let put this sn into sn history list ....
                historyfile = f'{drivesn}_history.csv'
                history.to_csv(historyfile,index=False)

                hist_frame = history_frame(self, history,'Pandas DataFrame in wxPython')
                hist_frame.Show()
            self.SetCursor(cursor)
        else:
            wx.MessageBox("Pls input valid Drive SN!")

    def build_tree(self):
        """Build tree based on the log data structure."""
        self.tree.DeleteAllItems()
        root = self.tree.AddRoot('%s-%s-%s' % (log.SerialNo, log.Oper, log.ErrorCode))
        
        for state in self.log_data.TestStateList:
            state_item = self.tree.AppendItem(root, state.StateName)
            self.tree.SetItemData(state_item,state)
            for st in state.STList:
                name = str_it(st.TestName)
                param = str_it(st.ExecutionParameter)
                try:
                    stitem = f"[{st.TestNum:03}] {name} ({param})" 
                except:
                    stitem = f"[{st.TestNum:03}] Unknown Test ({param})"
                if isinstance(stitem,bytes):stitem = stitem.decode("utf-8")

                st_item = self.tree.AppendItem(state_item,stitem)
                self.tree.SetItemData(st_item,st)

                for dblog in st.DBLogList:
                    dblog_str = (dblog.Name).decode("utf-8")
                    dblog_item = self.tree.AppendItem(st_item, dblog_str)
                    self.tree.SetItemData(dblog_item,dblog)
        self.tree.Expand(root)
    
    
    def ShowEditorLineNum(self):
        maxline = self.stc.GetLineCount()
        dc = wx.ClientDC(self.stc)
        fontwidth = dc.GetCharWidth()
        width = (math.floor(math.log10(maxline)) + 2) * fontwidth
        #width = self.stc.TextWidth(wx.stc.STC_STYLE_LINENUMBER, 'O'*(maxline+1))
        self.stc.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.stc.SetMarginWidth(1, width)

    def on_tree_selection(self, event):
        """Handle selection of a tree item and highlight corresponding log text."""
        item = self.tree.GetSelection()
        item_data = self.tree.GetItemData(item)
        start_pos = item_data.Span[0]
        end_pos = item_data.Span[1]
        self.editor.SetSelection(start_pos, end_pos)  # Highlight from start to end
        # Calculate line position from start_pos
        line_start = self.editor.LineFromPosition(start_pos)
        self.editor.ScrollToLine(line_start-5)
        self.editor.SetFocus() 
    
    def OnKeyDown(self, event):
        """Key down event handler."""
        key = event.GetKeyCode()
        controlDown = event.ControlDown()
        altDown = event.AltDown()

        if controlDown and altDown:
            event.Skip()
        # Increase font size.
        elif controlDown and key in (ord(']'), ord('}')):
            wx.py.dispatcher.send(signal='FontIncrease')
        # Decrease font size.
        elif controlDown and key in (ord('['), ord('{'),):
            wx.py.dispatcher.send(signal='FontDecrease')
        # Default font size.
        elif controlDown and key in (ord('+'), ord('=')):
            wx.py.dispatcher.send(signal='FontDefault')
        # Find text
        elif controlDown and key in (ord('F'), ord('f')):
            search_dialog = sealog.SearchDialog(self)
            search_dialog.Show()
        else:
            event.Skip()

    def process_logfile(self,logfile_path:str):
        # download and parsing logfile.
        if logfile_path:
            # download log from ftp server...
            # WHEN  fl.FILE_NAME IS not NULL THEN fl.HOST||'/' || fl."PATH" || fl.FILE_NAME  
            host,ftp_path,filename = logfile_path.split() 
            local_fullpath,host = download_file_from_ftp(host, ftp_path, filename, local_dir, log_file,SBR_raw_path)  
            return 0

# Main application
if __name__ == "__main__":
    txt_logfile = "B04D062F_COMET_135_PASS.txt"

    log = sealog.F3LogFile(txt_logfile)
    with open(txt_logfile,'rb') as raw_logf:
        raw_log = raw_logf.read()
    log.Process(skip_header_footer=True)
    logclass = log#Log(raw_log,log.TestStateList)
    app = wx.App(False)
    frame = LogViewer(None, "Log Viewer", logclass,raw_log)
    frame.Show(True)
    app.MainLoop()
