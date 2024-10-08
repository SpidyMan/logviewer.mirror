import wx
import wx.stc as stc
import re

class SearchDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title=f"Search Text in {parent.TabName}", size=(500, 400))
        # Layout setup
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Search field
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        lbl_search = wx.StaticText(panel, label="Search:")
        self.txt_search = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)  # Add TE_PROCESS_ENTER here
        hbox1.Add(lbl_search, flag=wx.RIGHT, border=8)
        hbox1.Add(self.txt_search, proportion=1)
        vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        # Checkboxes
        self.chk_case = wx.CheckBox(panel, label='Case sensitivity')
        self.chk_whole = wx.CheckBox(panel, label='Match whole word')
        self.chk_regex = wx.CheckBox(panel, label='Regular expression', )
        self.chk_whole.Disable()
        self.chk_regex.Disable()

        vbox.Add(self.chk_case, flag=wx.LEFT|wx.TOP, border=10)
        vbox.Add(self.chk_whole, flag=wx.LEFT, border=10)
        vbox.Add(self.chk_regex, flag=wx.LEFT, border=10,)
        
        # Buttons: Show Next, Count, Close
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        btn_next = wx.Button(panel, label="Show Next")
        btn_count = wx.Button(panel, label="Count")
        btn_close = wx.Button(panel, label="Close")
        hbox3.Add(btn_next)
        hbox3.Add(btn_count, flag=wx.LEFT|wx.BOTTOM, border=5)
        hbox3.Add(btn_close, flag=wx.LEFT|wx.BOTTOM, border=5)
        vbox.Add(hbox3, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        # Result List
        self.lst_results = wx.ListBox(panel)
        vbox.Add(self.lst_results, proportion=1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        panel.SetSizer(vbox)

        # Event Bindings
        btn_next.Bind(wx.EVT_BUTTON, self.OnShowNext)
        btn_count.Bind(wx.EVT_BUTTON, self.OnCount)
        btn_close.Bind(wx.EVT_BUTTON, self.OnClose)
        
        # Bind listbox click event
        self.lst_results.Bind(wx.EVT_LISTBOX, self.OnResultSelected)

        # Bind Enter key on the search textbox to OnShowNext
        self.txt_search.Bind(wx.EVT_TEXT_ENTER, self.OnShowNext)
        self.parent = parent
        self.search_results = []
        
    def OnShowNext(self, event):
        search_text = self.txt_search.GetValue()
        
        if not search_text:
            return
        flags = 0
        if not self.chk_case.GetValue():  
            flags |= re.IGNORECASE
        
        if self.chk_whole.GetValue():
            search_text = rf"\b{search_text}\b"

        self.search_results = []
        # Iterate over lines in the editor
        real_pos = 0  #
        for line_no, line in enumerate(self.parent.editor.GetValue().splitlines()):
            if self.chk_regex.GetValue():
                match = re.search(search_text, line, flags) 
                if match:
                    start_pos, end_pos = match.span() 
                    start_pos += real_pos  
                    end_pos += real_pos    # Sa
                    foundState = self.parent.log_data.GetStateByPos(start_pos)[0].StateName
                    self.search_results.append((foundState, line_no, line, start_pos, end_pos))
            else:
                if not self.chk_case.GetValue():
                    lower_line = line.lower()
                    lower_search_text = search_text.lower()
                    pos = lower_line.find(lower_search_text)
                    if pos != -1:
                        pos += real_pos  # Adjust the position with real_pos
                        end_pos = pos + len(lower_search_text)
                        foundState = self.parent.log_data.GetStateByPos(pos)[0].StateName
                        self.search_results.append((foundState, line_no, line, pos, end_pos))
                else:
                    # Case-sensitive search
                    pos = line.find(search_text)
                    if pos != -1:
                        pos += real_pos  # Adjust the position with real_pos
                        end_pos = pos + len(search_text)  # Case-sensitive, so use the original search text length
                        foundState = self.parent.log_data.GetStateByPos(pos)[0].StateName
                        self.search_results.append((foundState, line_no, line, pos, end_pos))
            
            real_pos += len(line) + 1  # Update real_pos after each line (+1 for newline character)

        # Display the results in the list box
        display_results = [f"[{foundState}] Line {line_no}: {line} (Pos: {pos}-{end_pos})"
                   for foundState, line_no, line, pos, end_pos in self.search_results]
        
        if self.search_results:
            self.lst_results.Set(display_results)
            wx.MessageBox(f"{len(self.search_results)} matches found.", "Search Results")
        else:
            wx.MessageBox("No matches found.", "Search Results")

    def OnCount(self, event):
        # Logic to handle 'Count' functionality
        count = len(self.search_results)
        wx.MessageBox(f"{count} matches found.", "Count Results")

    def OnClose(self, event):
        self.Destroy()

    def OnResultSelected(self, event):
        select_index = self.lst_results.GetSelection()

        if select_index != wx.NOT_FOUND:
            select_item = self.search_results[select_index]
            result_text = select_item[2]
            line_number = select_item[1]
            self.parent.Activate_Tab()
            self.parent.editor.SetSelection(select_item[3], select_item[4])  # Highlight from start to end
            self.parent.editor.ScrollToLine(line_number)
