import wx
import wx.grid as gridlib
import pandas as pd

# Sample data
# data = {'Name': ['Alice', 'Bob', 'Charlie', 'David'],
#         'Age': [24, 27, 22, 32],
#         'Occupation': ['Engineer', 'Doctor', 'Artist', 'Lawyer']}

#df = pd.DataFrame(data)

usecols= ['TRANS_SEQ','SERIAL_NUM','START_DATE','EVENT_DATE','EQUIP_TYPE','EQUIP_ID',\
          'LOC_ID','SLOT','OPERATION','RUN_TYPE','EVENT_STATUS','BUILD_GROUP','FISCAL_DATE','SETUP_FILE']
df = pd.read_csv('history_direct_sql.csv',usecols = usecols)
#df = pd.read_csv('some_data.csv', usecols = ['col1','col2'], low_memory = True)
class DataFrameGrid(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1000, 600))

        panel = wx.Panel(self)
        self.grid = gridlib.Grid(panel)

        # Create the grid
        self.grid.CreateGrid(df.shape[0], df.shape[1])

        # Set the column headers
        for col_idx, col_name in enumerate(df.columns):
            self.grid.SetColLabelValue(col_idx, col_name)

        # Set the data in the grid
        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                self.grid.SetCellValue(row, col, str(df.iloc[row, col]))

        # Bind the cell click event
        self.grid.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.on_row_click)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        self.Centre()
        self.Show()

    def on_row_click(self, event):
        # Get the row and column where the click happened
        row = event.GetRow()
        col = event.GetCol()

        # Retrieve the entire row information from the DataFrame
        row_data = df.iloc[row]
        
        # Display the selected row data in the console (you can handle it differently)
        print(f"Row {row} clicked: {row_data.to_dict()}")

        # You can also access a specific cell value if needed
        cell_value = self.grid.GetCellValue(row, col)
        print(f"Cell ({row}, {col}) clicked: {cell_value}")

        # Continue processing other events
        event.Skip()

if __name__ == '__main__':
    app = wx.App(False)
    frame = DataFrameGrid(None, 'Pandas DataFrame in wxPython')
    app.MainLoop()
