import wx

class ResultDialog(wx.Dialog):
    def __init__(self, parent, title, results):
        super().__init__(parent, title=title, size=(300, 400))

        self.results = results
        self.listbox = wx.ListBox(self, choices=results, style=wx.LB_SINGLE)

        self.ok_button = wx.Button(self, wx.ID_OK, "Select")
        self.cancel_button = wx.Button(self, wx.ID_CANCEL, "Cancel")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 10)
        sizer.Add(self.ok_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer.Add(self.cancel_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.on_select, self.ok_button)

    def on_select(self, event):
        # Get selected line index
        selection = self.listbox.GetSelection()
        if selection != wx.NOT_FOUND:
            # Send selected line index back to parent
            self.EndModal(selection)

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.tc = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE|wx.TE_RICH2)
        self.bt_find_all = wx.Button(self, -1, "Find All")

        self.Bind(wx.EVT_BUTTON, self.on_button_find_all, self.bt_find_all)
        
        self.pos = 0
        self.size = 0

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tc, 1, wx.EXPAND, 0)
        sizer.Add(self.bt_find_all, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()

    def on_button_find_all(self, event):
        self.txt = self.tc.GetValue()
        dlg = wx.TextEntryDialog(self, "Enter search term:", "Find All")
        if dlg.ShowModal() == wx.ID_OK:
            search_term = dlg.GetValue()
            self.find_all(search_term)

    def find_all(self, search_term):
        lines = self.txt.splitlines()
        matching_lines = [f"Line {i+1}" for i, line in enumerate(lines) if search_term in line]

        if matching_lines:
            dlg = ResultDialog(self, "Find All Results", matching_lines)
            if dlg.ShowModal() != wx.ID_CANCEL:
                selected_index = dlg.GetReturnCode()  # Get selected line index
                self.highlight_selected_line(selected_index, search_term)
        else:
            wx.MessageBox(f"'{search_term}' not found.", "Find All Results", wx.OK | wx.ICON_WARNING)

    def highlight_selected_line(self, index, search_term):
        lines = self.txt.splitlines()
        selected_line = lines[index]

        # Find the position of the selected line in the full text
        pos = self.txt.find(selected_line)
        size = len(selected_line)

        # Highlight the entire line containing the search term
        self.tc.SetStyle(pos, pos + size, wx.TextAttr("blue", "yellow"))

if __name__ == "__main__":
    app = wx.App(False)
    frame_1 = MyFrame(None, wx.ID_ANY, "")
    frame_1.Show()
    app.MainLoop()
