import wx
import wx.grid as gridlib
import pandas as pd



class history_frame(wx.Frame):

    def get_cell_attr(self, row, col, df):
        # Create a GridCellAttr object
        attr = gridlib.GridCellAttr()
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
    
    def __init__(self, parent,df, title):
        log_selected = None
        wx.Frame.__init__(self, parent, title=title, size=(800, 600))
        panel = wx.Panel(self)
        self.grid = gridlib.Grid(panel)
        df = df.reset_index(drop=True)
        df = df.fillna('')
        # Create the grid
        self.grid.CreateGrid(df.shape[0], df.shape[1],selmode=gridlib.Grid.GridSelectRows)
        self.logfile_values = {}
        # Set the column headers
        for col_idx, col_name in enumerate(df.columns):
            self.grid.SetColLabelValue(col_idx, col_name)
        logfile_col = df.columns.get_loc('LOGFILE')

        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                if col == logfile_col and df.iloc[row, col]:
                    self.grid.SetCellValue(row, logfile_col, 'View Log')
                else:
                    self.grid.SetCellValue(row, col, str(df.iloc[row, col]))
                attr = self.get_cell_attr(row, col, df)
                self.grid.SetAttr(row, col, attr)  # Set the attribute for the cell

        self.grid.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.on_row_click)
        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        self.Centre()
        self.Show()
    
    def on_row_click(self, event):
        row = event.GetRow()
        col = event.GetCol()
        if col == self.logfile_col and not pd.isna(df.iloc[row,col]):
            self.log_selected = str(df.iloc[row, col])
        event.Skip()

    def __repr__(self):
            return repr([self.value1, self.value2])

if __name__ == '__main__':
    app = wx.App(False)
    df = pd.read_csv('B04D062F_history.csv')
    frame = history_frame(None, df,'Pandas DataFrame in wxPython')
    app.MainLoop()
