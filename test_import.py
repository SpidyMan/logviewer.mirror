#import .....
import wx
import sealogfile as sealog
import sys
from sealogfile.utils import parse_NRF_file, split_db_table_line, parse_NRF_file_by_Python
from wx.py.editor import EditWindow
import math
class LogViewer(wx.Frame):
    def __init__(self, parent, title, log,raw_text):
        super(LogViewer, self).__init__(parent, title=title, size=(800,600))
        self.panel = wx.Panel(self)
    
        # Split window into two panels
        self.splitter = wx.SplitterWindow(self.panel)
        self.left_panel = wx.Panel(self.splitter)
        self.right_panel = wx.Panel(self.splitter)
        self.splitter.SplitVertically(self.left_panel, self.right_panel, sashPosition=int(800 * 0.2))
        
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
        self.build_tree()

        # Bind events
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_tree_selection)

    def build_tree(self):
        """Build tree based on the log data structure."""
        self.tree.DeleteAllItems()
        root = self.tree.AddRoot('%s-%s-%s' % (log.SerialNo, log.Oper, log.ErrorCode))
        
        for state in self.log_data.TestStateList:
            state_item = self.tree.AppendItem(root, state.StateName)
            self.tree.SetItemData(state_item,state)
            for st in state.STList:
                st_vir_name = st.DBLogList[0].Name if st.TestNum == -1 else st.TestName
                if isinstance(st_vir_name,bytes):st_vir_name = st_vir_name.decode("utf-8")

                st_item = self.tree.AppendItem(state_item, f'[{st.TestNum:03}]({st_vir_name})')
                
                self.tree.SetItemData(st_item,st)
                for dblog in st.DBLogList:
                    dblog_item = self.tree.AppendItem(st_item, f'{str(dblog.Name)}')
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



# Main application
if __name__ == "__main__":

    log = sealog.F3LogFile("B04N3613_COMET_307_PASS.txt")
    raw_log = ''
    with open("B04N3613_COMET_307_PASS.txt",'r') as raw_logf:
        raw_log = raw_logf.read()
    log.Process(skip_header_footer=True)
    logclass = log#Log(raw_log,log.TestStateList)
    app = wx.App(False)
    frame = LogViewer(None, "Log Viewer", logclass,raw_log)
    frame.Show(True)
    app.MainLoop()
