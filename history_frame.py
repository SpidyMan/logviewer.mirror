import wx
import wx.grid as gridlib
import pandas as pd



class history_frame(wx.Frame):
    
    def GetsAttr(self, row, col,df):
        self._data= df
        attr = gridlib.GridCellAttr()
        if self._data['LOGFILE'][row]:
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
            size = font.GetPointSize()
            attr.SetFont(wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD, False))
            if df.iloc[0, col] == 'LOGFILE':
               attr.SetTextColour(wx.BLUE)
               attr.SetFont(wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD, True))

        if self._data['STATUS'][row].strip().upper() in ('START', 'S'):
            attr.SetTextColour('#777777')
        elif self._data['STATUS'][row].strip().upper() in ('N/A',):
            attr.SetTextColour('#777777')
        elif self._data['STATUS'][row].strip().upper() not in ('PASS', 'P'):
            attr.SetBackgroundColour('#CC6666')
        # elif self._data['STATUS_DESC'][row]:
        #     attr.SetBackgroundColour('#669966')

        if self._data['OP'][row].strip().upper() in ['DBG', 'ADG']:
            attr.SetBackgroundColour('#FFCC33')
        if self._data['OP'][row].strip().upper() in ['NTF']:
            attr.SetBackgroundColour('#CC6630')

        return attr
    def __init__(self, parent,df, title):

        wx.Frame.__init__(self, parent, title=title, size=(1000, 600))

        panel = wx.Panel(self)
        self.grid = gridlib.Grid(panel)

        # Create the grid
        self.grid.CreateGrid(df.shape[0], df.shape[1])
        self.logfile_values = {}

        for col_idx, col_name in enumerate(df.columns):
            self.grid.SetColLabelValue(col_idx, col_name)
            for row in range(df.shape[0]):
                self.GetsAttr(row,col_idx,df)

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
        # Check if the clicked cell is in the 'logfile' column
        if (row, col) in self.logfile_values:
            real_value = self.logfile_values[(row, col)]
            print(f"Real value: {real_value}")
            # Optionally, update the cell to show the real value
            self.grid.SetCellValue(row, col, real_value)
        event.Skip()

if __name__ == '__main__':
    app = wx.App(False)
    df = pd.read_csv('historyfile.csv')
    frame = history_frame(None, df,'Pandas DataFrame in wxPython')
    app.MainLoop()
