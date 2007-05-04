#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# generated by wxGlade 0.4cvs on Mon Aug 14 00:35:15 2006

import wx
import appmodel 
import apptools
try:
    from xml.etree.ElementTree import fromstring, tostring
except:
    from elementtree.ElementTree import fromstring, tostring
import ErrorReporting

class MyFrame1(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame1.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.window_1 = wx.SplitterWindow(self, -1, style=wx.SP_3D|wx.SP_BORDER)
        self.debug_pane = wx.Panel(self.window_1, -1)
        self.tophalf = wx.SplitterWindow(self.window_1, -1, style=wx.SP_3D|wx.SP_BORDER)
        self.entries_pane = wx.Panel(self.tophalf, -1)
        self.window_2 = wx.SplitterWindow(self.entries_pane, -1, style=wx.SP_3D|wx.SP_BORDER)
        self.window_2_pane_2 = wx.Panel(self.window_2, -1)
        self.window_2_pane_1 = wx.Panel(self.window_2, -1)
        self.collections_pane = wx.Panel(self.tophalf, -1)
        self.label_1 = wx.StaticText(self.collections_pane, -1, "Collections")
        self.collections_tree = wx.TreeCtrl(self.collections_pane, -1, style=wx.TR_HAS_BUTTONS|wx.TR_NO_LINES|wx.TR_DEFAULT_STYLE|wx.SUNKEN_BORDER)
        self.collections_add = wx.Button(self.collections_pane, -1, "Add...")
        self.entries_label = wx.StaticText(self.entries_pane, -1, "Entries")
        self.edit_label = wx.StaticText(self.entries_pane, -1, "Edit")
        self.entries_listbox = wx.ListBox(self.entries_pane, -1, choices=[])
        self.title_label = wx.StaticText(self.entries_pane, -1, "Title")
        self.entry_title_text = wx.TextCtrl(self.entries_pane, -1, "")
        self.title_type_combo = wx.ComboBox(self.entries_pane, -1, choices=["text", "html", "xhtml"], style=wx.CB_DROPDOWN|wx.CB_SIMPLE|wx.CB_READONLY)
        self.summary_label = wx.StaticText(self.window_2_pane_1, -1, "Summary")
        self.entry_summary_text = wx.TextCtrl(self.window_2_pane_1, -1, "", style=wx.TE_MULTILINE)
        self.summary_type_combo = wx.ComboBox(self.window_2_pane_1, -1, choices=["text", "html", "xhtml"], style=wx.CB_DROPDOWN|wx.CB_SIMPLE|wx.CB_READONLY)
        self.content_label = wx.StaticText(self.window_2_pane_2, -1, "Content")
        self.entry_content_text = wx.TextCtrl(self.window_2_pane_2, -1, "", style=wx.TE_MULTILINE)
        self.content_type_combo = wx.ComboBox(self.window_2_pane_2, -1, choices=["text", "html", "xhtml"], style=wx.CB_DROPDOWN|wx.CB_SIMPLE|wx.CB_READONLY)
        self.create_save = wx.Button(self.entries_pane, -1, "Create/Save")
        self.delete = wx.Button(self.entries_pane, -1, "Delete")
        self.diagnostics_tree = wx.TreeCtrl(self.debug_pane, -1, style=wx.TR_HAS_BUTTONS|wx.TR_NO_LINES|wx.TR_HAS_VARIABLE_ROW_HEIGHT|wx.TR_DEFAULT_STYLE|wx.SUNKEN_BORDER)
        self.diagnostics_clear = wx.Button(self.debug_pane, -1, "Clear")
        self.diagnostics_export = wx.Button(self.debug_pane, -1, "Export...")
        self.diagnostics_config = wx.Button(self.debug_pane, -1, "Config...")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_coll_sel_changed, self.collections_tree)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_collection_select, self.collections_tree)
        self.Bind(wx.EVT_TREE_SEL_CHANGING, self.on_coll_sel_changing, self.collections_tree)
        self.Bind(wx.EVT_BUTTON, self.on_collections_add, self.collections_add)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.on_entries_dblclk, self.entries_listbox)
        self.Bind(wx.EVT_LISTBOX, self.on_entries_select, self.entries_listbox)
        self.Bind(wx.EVT_BUTTON, self.on_create_save, self.create_save)
        self.Bind(wx.EVT_BUTTON, self.on_delete, self.delete)
        self.Bind(wx.EVT_BUTTON, self.on_diag_clear, self.diagnostics_clear)
        self.Bind(wx.EVT_BUTTON, self.on_diag_export, self.diagnostics_export)
        self.Bind(wx.EVT_BUTTON, self.on_diag_config, self.diagnostics_config)
        # end wxGlade


        isz = (16,16)
        il = wx.ImageList(*isz)
        self.fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        self.fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_OTHER, isz))
        self.fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))
        self.infoidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_INFORMATION, wx.ART_OTHER, isz))
        self.erroridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_ERROR, wx.ART_OTHER, isz))
        self.warningidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_WARNING, wx.ART_OTHER, isz))

        self.diagnostics_tree.SetImageList(il)
        self.il = il


        # Hook up the validator
        appmodel.logger_cb = self.http_logger
        appmodel.error_reporting_cb = self.error_logger

        # Initialize the diagnostics
        self.diagnostics_root = self.diagnostics_tree.AddRoot("Events")
        self.diagnostics_tree.SetPyData(self.diagnostics_root, None)
        self.diagnostics_tree.Expand(self.diagnostics_root)

        self.diagnostics_tree.SetItemImage(self.diagnostics_root, self.fldridx, wx.TreeItemIcon_Normal)
        self.diagnostics_tree.SetItemImage(self.diagnostics_root, self.fldropenidx, wx.TreeItemIcon_Expanded)

        # Populate the collections 
        self.model = appmodel.Model() 
        self.collections_root = self.collections_tree.AddRoot("Workspaces")
        self.collections_tree.SetPyData(self.collections_root, None)
        for ws in self.model.all_workspaces():
            ws_child = self.collections_tree.AppendItem(self.collections_root, ws[0])
            for coll in ws[1]:
                child = self.collections_tree.AppendItem(ws_child, coll.title)
                self.collections_tree.SetPyData(child, coll)
        self.collections_tree.Expand(self.collections_root)

        # Current collection is a dict with 'href', 'accept', 'workspace' and 'title'
        self.current_collection = None

        # Pull all the entry controls together so they can be enabled/disabled. 
        self.entry_controls = [self.entry_title_text, self.title_type_combo, self.title_label, self.entry_summary_text, self.summary_type_combo, self.summary_label, self.content_label, self.entry_content_text, self.content_type_combo, self.create_save, self.delete]
        self._disable_entry_controls()
 

    def __set_properties(self):
        # begin wxGlade: MyFrame1.__set_properties
        self.SetTitle("APP Test Client")
        self.SetSize((1154, 1026))
        self.label_1.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.collections_add.Enable(False)
        self.collections_add.Hide()
        self.entries_label.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.edit_label.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.entries_listbox.SetMinSize((300, 541))
        self.entry_title_text.SetMinSize((438, 27))
        self.title_type_combo.SetSelection(0)
        self.summary_type_combo.SetSelection(0)
        self.content_type_combo.SetSelection(0)
        self.diagnostics_config.Enable(False)
        self.diagnostics_config.Hide()
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame1.__do_layout
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.FlexGridSizer(2, 1, 0, 0)
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_2 = wx.FlexGridSizer(2, 2, 0, 0)
        grid_sizer_3 = wx.FlexGridSizer(11, 1, 0, 0)
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5 = wx.FlexGridSizer(3, 1, 0, 0)
        sizer_3 = wx.FlexGridSizer(3, 1, 0, 0)
        grid_sizer_1 = wx.FlexGridSizer(3, 1, 0, 0)
        grid_sizer_1.Add(self.label_1, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        grid_sizer_1.Add(self.collections_tree, 1, wx.ALL|wx.EXPAND|wx.ADJUST_MINSIZE, 5)
        grid_sizer_1.Add(self.collections_add, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        self.collections_pane.SetAutoLayout(True)
        self.collections_pane.SetSizer(grid_sizer_1)
        grid_sizer_1.Fit(self.collections_pane)
        grid_sizer_1.SetSizeHints(self.collections_pane)
        grid_sizer_1.AddGrowableRow(1)
        grid_sizer_1.AddGrowableCol(0)
        grid_sizer_2.Add(self.entries_label, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        grid_sizer_2.Add(self.edit_label, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_2.Add(self.entries_listbox, 0, wx.ALL|wx.EXPAND|wx.ADJUST_MINSIZE, 5)
        grid_sizer_3.Add(self.title_label, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_3.Add(self.entry_title_text, 0, wx.EXPAND, 5)
        grid_sizer_3.Add(self.title_type_combo, 0, wx.ADJUST_MINSIZE, 0)
        sizer_3.Add(self.summary_label, 0, wx.ADJUST_MINSIZE, 0)
        sizer_3.Add(self.entry_summary_text, 0, wx.EXPAND, 5)
        sizer_3.Add(self.summary_type_combo, 0, wx.ADJUST_MINSIZE, 0)
        self.window_2_pane_1.SetAutoLayout(True)
        self.window_2_pane_1.SetSizer(sizer_3)
        sizer_3.Fit(self.window_2_pane_1)
        sizer_3.SetSizeHints(self.window_2_pane_1)
        sizer_3.AddGrowableRow(1)
        sizer_3.AddGrowableCol(0)
        sizer_5.Add(self.content_label, 0, wx.ADJUST_MINSIZE, 0)
        sizer_5.Add(self.entry_content_text, 0, wx.EXPAND, 0)
        sizer_5.Add(self.content_type_combo, 0, wx.ADJUST_MINSIZE, 0)
        self.window_2_pane_2.SetAutoLayout(True)
        self.window_2_pane_2.SetSizer(sizer_5)
        sizer_5.Fit(self.window_2_pane_2)
        sizer_5.SetSizeHints(self.window_2_pane_2)
        sizer_5.AddGrowableRow(1)
        sizer_5.AddGrowableCol(0)
        self.window_2.SplitHorizontally(self.window_2_pane_1, self.window_2_pane_2)
        grid_sizer_3.Add(self.window_2, 1, wx.EXPAND, 0)
        sizer_6.Add(self.create_save, 0, wx.ADJUST_MINSIZE, 0)
        sizer_6.Add(self.delete, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_3.Add(sizer_6, 1, wx.EXPAND, 0)
        grid_sizer_3.AddGrowableRow(3)
        grid_sizer_3.AddGrowableRow(5)
        grid_sizer_3.AddGrowableCol(0)
        grid_sizer_2.Add(grid_sizer_3, 1, wx.ALL|wx.EXPAND, 5)
        self.entries_pane.SetAutoLayout(True)
        self.entries_pane.SetSizer(grid_sizer_2)
        grid_sizer_2.Fit(self.entries_pane)
        grid_sizer_2.SetSizeHints(self.entries_pane)
        grid_sizer_2.AddGrowableRow(1)
        grid_sizer_2.AddGrowableCol(1)
        self.tophalf.SplitVertically(self.collections_pane, self.entries_pane)
        sizer_4.Add(self.diagnostics_tree, 1, wx.ALL|wx.EXPAND|wx.ADJUST_MINSIZE, 5)
        sizer_1.Add(self.diagnostics_clear, 0, wx.ADJUST_MINSIZE, 0)
        sizer_1.Add(self.diagnostics_export, 0, wx.ADJUST_MINSIZE, 0)
        sizer_1.Add(self.diagnostics_config, 0, wx.ADJUST_MINSIZE, 0)
        sizer_4.Add(sizer_1, 1, wx.ALL|wx.ADJUST_MINSIZE, 5)
        self.debug_pane.SetAutoLayout(True)
        self.debug_pane.SetSizer(sizer_4)
        sizer_4.Fit(self.debug_pane)
        sizer_4.SetSizeHints(self.debug_pane)
        sizer_4.AddGrowableRow(0)
        sizer_4.AddGrowableCol(0)
        self.window_1.SplitHorizontally(self.tophalf, self.debug_pane, 888)
        sizer_2.Add(self.window_1, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_2)
        self.Layout()
        # end wxGlade

    def on_ok(self, event): # wxGlade: MyFrame1.<event_handler>
        event.Skip()

    def on_diag_clear(self, event): # wxGlade: MyFrame1.<event_handler>
        self.diagnostics_tree.DeleteChildren(self.diagnostics_root)

    def on_collection_select(self, event): # wxGlade: MyFrame1.<event_handler>
        event.Skip()

    def on_collections_add(self, event): # wxGlade: MyFrame1.<event_handler>
        event.Skip()

    def on_entries_dblclk(self, event): # wxGlade: MyFrame1.<event_handler>
        event.Skip()


    def _enable_entry_controls(self):
        [ x.Enable(True) for x in self.entry_controls]
            

    def _disable_entry_controls(self):
        [ x.Enable(False) for x in self.entry_controls]

    
    def on_entries_select(self, event): # wxGlade: MyFrame1.<event_handler>
        sel = self.entries_listbox.GetSelection()
        if sel != wx.NOT_FOUND:
            entry = self.entries_listbox.GetClientData(sel)
            entry.get()
            self.entry_title_text.SetValue(entry["title"])
            self.title_type_combo.SetStringSelection(entry["title__type"])
            self.entry_summary_text.SetValue(entry["summary"])
            self.summary_type_combo.SetStringSelection(entry["summary__type"])
            self.entry_content_text.SetValue(entry["content"])
            self.content_type_combo.SetStringSelection(entry["content__type"])
            self._enable_entry_controls()
            if not entry.member_uri:
                self.create_save.SetLabel("Create")
                self.delete.Disable()
            else:
                self.create_save.SetLabel("Save")
        else:
            self._disable_entry_controls()


    def on_entries_new(self, event): # wxGlade: MyFrame1.<event_handler>
        event.Skip()

    def on_entries_edit(self, event): # wxGlade: MyFrame1.<event_handler>
        sel = self.entries_listbox.GetSelection()
        if sel != wx.NOT_FOUND:
            entry = self.entries_listbox.GetClientData(sel)

    def on_entries_delete(self, event): # wxGlade: MyFrame1.<event_handler>
        event.Skip()

    def on_diag_export(self, event): # wxGlade: MyFrame1.<event_handler>
        # Evetually prompt for a filename, for now we'll just 
        # recurse the tree and dump it to a named file.
        f = file("diagnostics.txt", "w")
        def tree_enumerator(tree, node, depth = 0):
            (child, cookie) = tree.GetFirstChild(node)
            while child:
                yield ' ' * depth + tree.GetItemText(child) 
                for l in tree_enumerator(tree, child, depth+1):
                    yield l
                (child, cookie) = tree.GetNextChild(node, cookie)

        for line in tree_enumerator(self.diagnostics_tree, self.diagnostics_root):
            f.write(line)
            f.write("\n")
        f.close()


    def on_diag_config(self, event): # wxGlade: MyFrame1.<event_handler>
        event.Skip()

    def on_coll_sel_changed(self, event): # wxGlade: MyFrame1.<event_handler>
        item = event.GetItem()
        if item:
            self.current_collection = self.collections_tree.GetItemPyData(item)
        # Get a list and stuff it into 'Entries' along with a "more..." item
        self.update_entry_list(True)

    def on_coll_sel_changing(self, event): # wxGlade: MyFrame1.<event_handler>
        event.Skip()

    def on_create_save(self, event): # wxGlade: MyFrame1.<event_handler>
        sel = self.entries_listbox.GetSelection()
        if sel != wx.NOT_FOUND:
            entry = self.entries_listbox.GetClientData(sel)
            entry["title"] = self.entry_title_text.GetValue()
            entry["title__type"] = self.title_type_combo.GetValue()
            entry["summary"] = self.entry_summary_text.GetValue()
            entry["summary__type"] = self.summary_type_combo.GetValue()
            entry["content"] = self.entry_content_text.GetValue()
            entry["content__type"] = self.content_type_combo.GetValue()
            if not entry.member_uri:
                self.current_collection.post(entry)
            else:
                entry.put()
            self.update_entry_list(True)

    def http_logger(self, uri, resp, content, method, body, headers, redirections):
        child = self.diagnostics_tree.AppendItem(self.diagnostics_root, method + ": Status: %d " % resp.status + ": " + uri )
        if resp.status < 400:
            self.diagnostics_tree.SetItemImage(child, self.infoidx, wx.TreeItemIcon_Normal)
        else:
            self.diagnostics_tree.SetItemImage(child, self.erroridx, wx.TreeItemIcon_Normal)

        req_child = self.diagnostics_tree.AppendItem(child, "Request") 

        self.diagnostics_tree.SetItemImage(req_child, self.fldridx, wx.TreeItemIcon_Normal)
        if headers:
            headers_child = self.diagnostics_tree.AppendItem(req_child, "Headers") 

            for k,v in headers.iteritems():
                self.diagnostics_tree.AppendItem(headers_child, "%s: %s" % (k,v))
        if body:
            body_child = self.diagnostics_tree.AppendItem(req_child, "Body") 

            for line in pretty_content(content).split("\n"):
                self.diagnostics_tree.AppendItem(body_child, line)


        resp_child = self.diagnostics_tree.AppendItem(child, "Response") 

        self.diagnostics_tree.SetItemImage(resp_child, self.fldridx, wx.TreeItemIcon_Normal)

        headers_child = self.diagnostics_tree.AppendItem(resp_child, "Headers") 
        self.diagnostics_tree.SetItemImage(headers_child, self.fileidx, wx.TreeItemIcon_Normal)
        #self.diagnostics_tree.AppendItem(headers_child, "\n".join(["%s: %s" % (k,v) for (k,v) in resp.iteritems()]))
        for k,v in resp.iteritems():
            self.diagnostics_tree.AppendItem(headers_child, "%s: %s" % (k,v) )
        if content:
            content_child = self.diagnostics_tree.AppendItem(resp_child, "Body") 
            for line in pretty_content(content).split("\n"):
                self.diagnostics_tree.AppendItem(content_child, line)
            self.diagnostics_tree.SetItemImage(content_child, self.fileidx, wx.TreeItemIcon_Normal)
        self.diagnostics_tree.Expand(self.diagnostics_root)
        self.diagnostics_tree.ScrollTo(child)

        # Add some tests based on the Content-Type of the response
        # And add errors if there is no content-type
        # And add errors if the content-type is wrong.
        # Also need to keep track of atom:id's and Member URIs to make sure they are not changing
        # 
        # Need to add a "Add challenging entries" button/menu item to the GUI...

    def error_logger(self, reportable):
        (severity, image) = ("Suggestion", self.infoidx) 
        if isinstance(reportable, ErrorReporting.Error):
            (severity, image) = ("Error", self.erroridx)
        elif isinstance(reportable, ErrorReporting.Warning):
            (severity, image) = ("Warning", self.warningidx)

        child = self.diagnostics_tree.AppendItem(self.diagnostics_root, severity + " : " + reportable.toshortstring())
        self.diagnostics_tree.SetItemImage(child, image, wx.TreeItemIcon_Normal)

        for line in reportable.tostring().split("\n"):
            detail = self.diagnostics_tree.AppendItem(child, line) 

        self.diagnostics_tree.Expand(self.diagnostics_root)
        self.diagnostics_tree.ScrollTo(child)

    def update_entry_list(self, fresh):
        if fresh:
            self.entries_listbox.Clear()
        # Loop over the feed and pull out the title, updated, published, and "edit" link
        # also keep track of the "next" link
        self.entry_title_text.SetValue("")
        self.title_type_combo.SetStringSelection("text")
        self.entry_summary_text.SetValue("")
        self.summary_type_combo.SetStringSelection("xhtml")
        self.entry_content_text.SetValue("")
        self.content_type_combo.SetStringSelection("xhtml")
        self._disable_entry_controls()

        # Create and empty Entry() here 
        if self.current_collection:
            (entries, next) = self.current_collection.entries()
            for e in entries:
                index = self.entries_listbox.Append(e['title'])       
                self.entries_listbox.SetClientData(index, e)

    def on_delete(self, event): # wxGlade: MyFrame1.<event_handler>
        sel = self.entries_listbox.GetSelection()
        if sel != wx.NOT_FOUND:
            entry = self.entries_listbox.GetClientData(sel)
            entry.delete()
        self.update_entry_list(True)

# end of class MyFrame1

# http://effbot.python-hosting.com/file/stuff/sandbox/elementlib/indent.py 
def indent(elem, level=0):
    i = "\n" + level*"  "
    if not elem.text or not elem.text.strip():
        elem.text = i + "  "
    for elem in elem:
        indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
        elem.tail = i

def pretty_content(content):
    #try:
    #    element = fromstring(content)
    #    indent(element)
    #content = tostring(element)
    #except:
    #    content = apptools.wrap(content, 80)
    return content




if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = MyFrame1(None, -1, "Hello World")
    frame.Show(1)
    app.MainLoop()



