class main():
    bra bra.....
    def OnButtonGo(self, event):
        event.Skip()
        drivesn = self.comboBoxSN.GetValue().strip().upper()
        m = re.search("([A-Z0-9]{8})", drivesn)
        if len(drivesn) == 8 :

            cursor = self.GetCursor()
            self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
                ### maxts will be edited.
            hist_frame = history_frame(self, drivesn,maxts=100)
            hist_frame.Show()
            self.SetCursor(cursor)


the hist_frame wil showed up... then they will be a selected data from df to be