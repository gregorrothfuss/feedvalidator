from elementtree.ElementTree import fromstring, tostring, SubElement
import re

ATOM = "{http://www.w3.org/2005/Atom}%s"
APP = "{http://purl.org/atom/app#}%s"

def get_element(name, entry):
    value = ""
    l = entry.findall(ATOM % name)
    if l:
        value = l[0].text
    return {name: value}

def get_text(name, entry):
    value = ""
    texttype = "text"
    l = entry.findall(ATOM % name)
    if l:
        value = l[0].text
        texttype = l[0].get('type', '')
        if texttype in ["text", "html"]:
            pass
        elif texttype == "xhtml":
            div = l[0].findall("{http://www.w3.org/1999/xhtml}div")[0]
            if div:
                value = "".join( [tostring(c) for c in div.getchildren()] )
        else:
            value = ""
    if value == None:
        value = ""
    return {name: value, (name + "__type"): texttype}

def set_text(name, entry, values):
    elements = entry.findall(ATOM % name)
    if not elements:
        element = SubElement(entry, ATOM % name)
    else:
        element = elements[0]
    element.set('type', values[name + "__type"])
    [element.remove(e) for e in element.getchildren()]
    type = values[name + "__type"]
    if type in ["html", "text"]:
        element.text = values[name]
    elif type == "xhtml":
        element.text = ""
        div = fromstring((u"<div xmlns='http://www.w3.org/1999/xhtml'>%s</div>" % values[name]).encode('utf-8'))
        element.append(div)

def parse_atom_entry(entry):
    res = {}
    res.update(get_text('title', entry))
    res.update(get_text('summary', entry))
    res.update(get_text('content', entry))
    return res

def unparse_atom_entry(entry, values):
    set_text('title', entry, values)
    set_text('summary', entry, values)
    set_text('content', entry, values)

def parse_collection_feed(src):
    # loop over the entries and pull out the title, link/@rel="edit", updated and published.
    entries = []
    feed = fromstring(src)
    for e in feed.findall(ATOM % "entry"):
        entry = {}
        edit_links = [l.get('href', '') for l in e.findall(ATOM % "link") if l.get('rel', '') == "edit"]
        #edit_links = [l.get('href', '') for l in e.findall(ATOM % "link") if l.get('rel', '') == "self"]
        entry['edit'] = edit_links and edit_links[0] or ''
        entry.update(get_text('title', e))
        entry.update(get_element('updated', e))
        entry.update(get_element('published', e))
        entries.append(entry)
    next_links = [l.get('href', '') for l in feed.findall(ATOM % "link") if l.get('rel', '') == "next"]
    next = next_links and next_links[0] or ''
    return (entries, next)

def parse_service(src):
    res = []
    service = fromstring(src)
    workspaces = service.findall(APP % "workspace")
    for w in workspaces:
        wsname = w.get('title', '')
        collections = w.findall(APP % "collection")
        for c in collections:
            cp = {}
            cp['title'] = c.get('title', '')
            cp['href'] = c.get('href', '')
            cp['workspace'] = wsname
            accept = c.findall(APP % "accept")
            cp['accept'] = accept and accept[0].text or '' 
            res.append(cp)
    return res

def wrap(text, width):
    l = 0
    ret = []
    for s in text.split(' '):
        ret.append(s)
        l += len(s)
        nl = s.find('\n') >= 0
        if l > width or nl:
            l = 0
            if not nl:
                ret.append('\n')
        else:
            ret.append(' ')
    return "".join(ret) 
    
    
