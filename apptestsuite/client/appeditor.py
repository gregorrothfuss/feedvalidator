#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# generated by wxGlade 0.4cvs on Mon Aug 14 00:35:15 2006

import wx
import appmodel 
import apptools
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
        self.collections_pane = wx.Panel(self.tophalf, -1)
        self.label_1 = wx.StaticText(self.collections_pane, -1, "Collections")
        self.collections_tree = wx.TreeCtrl(self.collections_pane, -1, style=wx.TR_HAS_BUTTONS|wx.TR_NO_LINES|wx.TR_DEFAULT_STYLE|wx.SUNKEN_BORDER)
        self.collections_add = wx.Button(self.collections_pane, -1, "Add...")
        self.entries_label = wx.StaticText(self.entries_pane, -1, "Entries")
        self.edit_label = wx.StaticText(self.entries_pane, -1, "Edit")
        self.entries_listbox = wx.ListBox(self.entries_pane, -1, choices=[])
        self.label_2 = wx.StaticText(self.entries_pane, -1, "Title")
        self.entry_title_text = wx.TextCtrl(self.entries_pane, -1, "")
        self.title_type_combo = wx.ComboBox(self.entries_pane, -1, choices=["text", "html", "xhtml"], style=wx.CB_DROPDOWN|wx.CB_SIMPLE|wx.CB_READONLY)
        self.label_3 = wx.StaticText(self.entries_pane, -1, "Summary")
        self.entry_summary_text = wx.TextCtrl(self.entries_pane, -1, "", style=wx.TE_MULTILINE)
        self.summary_type_combo = wx.ComboBox(self.entries_pane, -1, choices=["text", "html", "xhtml"], style=wx.CB_DROPDOWN|wx.CB_SIMPLE|wx.CB_READONLY)
        self.label_4 = wx.StaticText(self.entries_pane, -1, "Content")
        self.entry_content_text = wx.TextCtrl(self.entries_pane, -1, "", style=wx.TE_MULTILINE)
        self.content_type_combo = wx.ComboBox(self.entries_pane, -1, choices=["text", "html", "xhtml"], style=wx.CB_DROPDOWN|wx.CB_SIMPLE|wx.CB_READONLY)
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
        self.collections_root = self.collections_tree.AddRoot("Collections")
        self.collections_tree.SetPyData(self.collections_root, None)
        for coll in self.model.all_collections():
            child = self.collections_tree.AppendItem(self.collections_root, coll.title)
            self.collections_tree.SetPyData(child, coll)
        self.collections_tree.Expand(self.collections_root)

        # Current collection is a dict with 'href', 'accept', 'workspace' and 'title'
        self.current_collection = None


    def __set_properties(self):
        # begin wxGlade: MyFrame1.__set_properties
        self.SetTitle("APP Test Client")
        self.SetSize((1154, 809))
        self.label_1.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.entries_label.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.edit_label.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.entries_listbox.SetMinSize((300, 541))
        self.entry_title_text.SetMinSize((438, 27))
        self.title_type_combo.SetSelection(0)
        self.entry_summary_text.SetMinSize((438, 208))
        self.summary_type_combo.SetSelection(0)
        self.entry_content_text.SetMinSize((438, 156))
        self.content_type_combo.SetSelection(0)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame1.__do_layout
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.FlexGridSizer(2, 1, 0, 0)
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_2 = wx.FlexGridSizer(2, 2, 0, 0)
        grid_sizer_3 = wx.FlexGridSizer(11, 1, 0, 0)
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
        grid_sizer_3.Add(self.label_2, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_3.Add(self.entry_title_text, 0, wx.EXPAND, 5)
        grid_sizer_3.Add(self.title_type_combo, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_3.Add(self.label_3, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_3.Add(self.entry_summary_text, 0, wx.EXPAND, 5)
        grid_sizer_3.Add(self.summary_type_combo, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_3.Add(self.label_4, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_3.Add(self.entry_content_text, 0, wx.EXPAND, 0)
        grid_sizer_3.Add(self.content_type_combo, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_3.Add(self.create_save, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_3.Add(self.delete, 0, wx.ADJUST_MINSIZE, 0)
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
        self.tophalf.SplitVertically(self.collections_pane, self.entries_pane, 200)
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
        self.window_1.SplitHorizontally(self.tophalf, self.debug_pane, 627)
        sizer_2.Add(self.window_1, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_2)
        self.Layout()
        # end wxGlade

    def on_ok(self, event): # wxGlade: MyFrame1.<event_handler>
        print "Event handler `on_ok' not implemented"
        event.Skip()

    def on_diag_clear(self, event): # wxGlade: MyFrame1.<event_handler>
        self.diagnostics_tree.DeleteChildren(self.diagnostics_root)

    def on_collection_select(self, event): # wxGlade: MyFrame1.<event_handler>
        print "Event handler `on_collection_select' not implemented"
        event.Skip()

    def on_collections_add(self, event): # wxGlade: MyFrame1.<event_handler>
        print "Event handler `on_collections_add' not implemented"
        event.Skip()

    def on_entries_dblclk(self, event): # wxGlade: MyFrame1.<event_handler>
        print "Event handler `on_entries_dblclk' not implemented"
        event.Skip()

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

    def on_entries_new(self, event): # wxGlade: MyFrame1.<event_handler>
        print "Event handler `on_entries_new' not implemented"
        event.Skip()

    def on_entries_edit(self, event): # wxGlade: MyFrame1.<event_handler>
        sel = self.entries_listbox.GetSelection()
        if sel != wx.NOT_FOUND:
            entry = self.entries_listbox.GetClientData(sel)
            print entry

    def on_entries_delete(self, event): # wxGlade: MyFrame1.<event_handler>
        print "Event handler `on_entries_delete' not implemented"
        event.Skip()

    def on_diag_export(self, event): # wxGlade: MyFrame1.<event_handler>
        print "Event handler `on_diag_export' not implemented"
        event.Skip()

    def on_diag_config(self, event): # wxGlade: MyFrame1.<event_handler>
        print "Event handler `on_diag_config' not implemented"
        event.Skip()

    def on_coll_sel_changed(self, event): # wxGlade: MyFrame1.<event_handler>
        print "Event handler `on_coll_sel_changed' not implemented"
        item = event.GetItem()
        if item:
            self.current_collection = self.collections_tree.GetItemPyData(item)
        # Get a list and stuff it into 'Entries' along with a "more..." item
        self.update_entry_list(True)

    def on_coll_sel_changing(self, event): # wxGlade: MyFrame1.<event_handler>
        print "Event handler `on_coll_sel_changing' not implemented"
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
                self.update_entry_list(True)
            else:
                entry.put()

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
            self.diagnostics_tree.AppendItem(headers_child, "\n".join(["%s: %s" % (k,v) for (k,v) in headers.iteritems()]))
        if body:
            body_child = self.diagnostics_tree.AppendItem(req_child, "Body") 
            self.diagnostics_tree.AppendItem(body_child, pretty_content(body))


        resp_child = self.diagnostics_tree.AppendItem(child, "Response") 

        self.diagnostics_tree.SetItemImage(resp_child, self.fldridx, wx.TreeItemIcon_Normal)

        headers_child = self.diagnostics_tree.AppendItem(resp_child, "Headers") 
        self.diagnostics_tree.SetItemImage(headers_child, self.fileidx, wx.TreeItemIcon_Normal)
        self.diagnostics_tree.AppendItem(headers_child, "\n".join(["%s: %s" % (k,v) for (k,v) in resp.iteritems()]))
        if content:
            content_child = self.diagnostics_tree.AppendItem(resp_child, "Body") 
            self.diagnostics_tree.AppendItem(content_child, pretty_content(content))
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

        detail = self.diagnostics_tree.AppendItem(child, reportable.tostring()) 
        self.diagnostics_tree.Expand(self.diagnostics_root)
        self.diagnostics_tree.ScrollTo(child)

    def update_entry_list(self, fresh):
        if fresh:
            self.entries_listbox.Clear()
        # Loop over the feed and pull out the title, updated, published, and "edit" link
        # also keep track of the "next" link

        # Create and empty Entry() here 
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
    try:
        element = fromstring(content)
        indent(element)
        content = tostring(element)
    except:
        content = apptools.wrap(content, 80)
    return content




if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = MyFrame1(None, -1, "Hello World")
    frame.Show(1)
    app.MainLoop()



