import wx
import wx.grid as gridlib
import pandas as pd



class history_frame(wx.Frame):
    

    def get_cell_attr(self, row, col, df):
        # Create a GridCellAttr object
        attr = gridlib.GridCellAttr()

        # Example of applying styles based on LOGFILE column
        if col == 0 and df['LOGFILE'][row]:  # Assuming 'LOGFILE' is the first column
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
            size = font.GetPointSize()
            attr.SetFont(wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
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

        wx.Frame.__init__(self, parent, title=title, size=(1000, 600))

        panel = wx.Panel(self)
        self.grid = gridlib.Grid(panel)

        # Create the grid
        self.grid.CreateGrid(df.shape[0], df.shape[1])
        self.logfile_values = {}

        # Set cell values and attributes
        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
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
        # Check if the clicked cell is in the 'logfile' column
        if (row, col) in self.logfile_values:
            real_value = self.logfile_values[(row, col)]
            print(f"Real value: {real_value}")
            # Optionally, update the cell to show the real value
            self.grid.SetCellValue(row, col, real_value)
        event.Skip()

if __name__ == '__main__':
    app = wx.App(False)
    df = pd.read_csv('B04D062F_history.csv')
    frame = history_frame(None, df,'Pandas DataFrame in wxPython')
    app.MainLoop()
