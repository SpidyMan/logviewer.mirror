import wx
import wx.grid as gridlib
import pandas as pd
from log_server_process import log_obj_creater

Testing = True

class history_frame(wx.Frame):
    def __init__(self, parent,serial,maxts = 100):
        if Testing == True: self.df = pd.read_csv('./TestingFile/history_query.csv')
        else: 
            import sql_query
            self.df = sql_query.logservice_history_all(serial,maxts,show_query=False)

        self.serial = serial
        self.maxts  =maxts
        # log_selected = None
        wx.Frame.__init__(self, parent, 
                          title=f'{serial} history for latest:{maxts} transeqs', 
                          size=(500, 600))
        
        panel = wx.Panel(self)
        self.grid = gridlib.Grid(panel)
        self.df = self.df.reset_index(drop=True)
        self.df = self.df.fillna('')
        self.grid.SetRowLabelSize(1)
        # Create the grid
        self.grid.CreateGrid(self.df.shape[0], self.df.shape[1],selmode=gridlib.Grid.GridSelectRows)
        self.logfile_values = {}
        # Set the column headers
        for col_idx, col_name in enumerate(self.df.columns):
            self.grid.SetColLabelValue(col_idx, col_name)
        logfile_col = self.df.columns.get_loc('LOGFILE')
        
        for row in range(self.df.shape[0]):
            for col in range(self.df.shape[1]):
                if col == logfile_col and self.df.iloc[row, col]:
                    self.grid.SetCellValue(row, logfile_col, 'View Log')
                else:
                    self.grid.SetCellValue(row, col, str(self.df.iloc[row, col]))
                attr = self.get_cell_attr(row, col, self.df)
                self.grid.SetAttr(row, col, attr)  # Set the attribute for the cell

        self.grid.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.on_row_click)
        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 10, wx.EXPAND)
        self.grid.AutoSizeColumns(True)
        panel.SetSizer(sizer)
        self.Centre()
        self.Show()

    def get_cell_attr(self, row, col, df):
        # Create a GridCellAttr object
        attr = gridlib.GridCellAttr()
        attr.SetReadOnly(True)
        self.logfile_col = df.columns.get_loc('LOGFILE')
        if df['LOGFILE'][row]: 
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
            size = font.GetPointSize()
            attr.SetFont(wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
            if(col == self.logfile_col):
                size = font.GetPointSize()
                attr.SetFont(wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, True))
                attr.SetTextColour(wx.BLUE)
        # Apply background color based on STATUS
        if str(df['STATUS'][row]).strip().upper() == 'START':
            attr.SetTextColour('#777777')
        elif str(df['STATUS'][row]).strip().upper() == 'N/A':
            attr.SetTextColour('#777777')
        elif str(df['STATUS'][row]).strip().upper() not in ('PASS', 'P'):
            attr.SetBackgroundColour('#CC6666')
        # Apply background color based on OP
        if df['OP'][row].strip().upper() in ['DBG', 'ADG']:
            attr.SetBackgroundColour('#FFCC33')
        if df['OP'][row].strip().upper() in ['NTF']:
            attr.SetBackgroundColour('#CC6630')
        return attr
    
    def on_row_click(self, event):
        row = event.GetRow()
        col = event.GetCol()
        if col == self.logfile_col and not pd.isna(self.df.iloc[row,col]):
            # self.log_selected = str(self.df.iloc[row, col])
            self.selected = self.df.iloc[row]
            thisobj = log_obj_creater(serial = self.serial,
                                                  oper = self.selected.OP,
                                                  ts = self.selected.TS,
                                                  code = self.selected.STATUS,
                                                  ftp_zip_path=str(self.df.iloc[row, col]))
            self.Parent.add_log_tab(thisobj.logobj)
        event.Skip()

    
if __name__ == '__main__':
    app = wx.App(False)
    frame = history_frame(None, serial='B04D062F',maxts=10)
    app.MainLoop()
