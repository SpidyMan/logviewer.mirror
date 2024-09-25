import wx
import wx.lib.buttons as buttons
from wx.py.editor import EditWindow
# import pandas as pd
from cryptography.hazmat.primitives.kdf import pbkdf2
import encodings.idna
import re, os, sys




class MainFrame(wx.Frame):
    """MainFrame to manage multiple LogViewer instances using tabs."""
    
    def __init__(self, parent, title):
        super(MainFrame, self).__init__(parent, title=title, size=(800, 600))
        # TextCtrl for the right panel (to display log content)
        self.editor = EditWindow(self,parent)
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

# Main application
if __name__ == "__main__":
    if sys.version_info[0] == 3:
        print('This is Python3 .. Lets Rock n Roll!!!')
        app = wx.App(False)
        frame = MainFrame(None,self, "LogViewer ก๊อบเกรด B ( Speed9 Logviewer)")
        frame.Show(True)
        # #ftp_zip_path = "teppinasv001.seagate.com/prod/none/merlin/history/COMET/20/B04D062F.4905113404.r.zip"
        # local_file="B04D062F_COMET_135_PASS.txt"
        # log_process = log_obj_creater('ABCDE','TEST',99,'PASS',ftp_zip_path,local_file)
        # frame.add_log_tab(log_process.logobj)
        app.MainLoop()
    else:
        print('Python2.... You are too old.. please install new python..')
        