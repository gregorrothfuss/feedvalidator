from elementtree.ElementTree import fromstring, tostring, SubElement
import re
from urlparse import urljoin
import feedparser
from StringIO import StringIO

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
        texttype = l[0].get('type', 'text')
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

def parse_atom_entry(uri, entry_src):
    f = StringIO(entry_src)
    f.url = uri
    feed = feedparser.parse(f)
    entry = feed.entries[0]
    res = {}
    res['title'] = entry.title
    res['title__type'] = 'text'
    if 'summary_detail' in entry:
        res['summary'] = entry.summary_detail.value
        res['summary__type'] = entry.summary_detail.type
    else:
        res['summary'] = ""
        res['summary__type'] = "text"
    res['content'] = entry.content[0].value
    res['content__type'] = entry.content[0].type
    return res

def unparse_atom_entry(entry, values):
    set_text('title', entry, values)
    set_text('summary', entry, values)
    set_text('content', entry, values)

def parse_collection_feed(uri, src):
    # loop over the entries and pull out the title, link/@rel="edit", updated and published.
    entries = []
    f = StringIO(src)
    f.url = uri
    feed = feedparser.parse(f)
    for e in feed.entries:
        entry = {}
        edit_links = [l.href for l in e.links if l.rel == "edit"]
        entry['edit'] = edit_links and edit_links[0] or ''
        entry['title'] = e.title
        entry['updated'] = e.updated
        entries.append(entry)
        print entry
    if 'links' in feed:
        next_links = [l.href for l in feed.links if l.rel == "next"]
    else:
        next_links = []
        next = next_links and next_links[0] or ''

    return (entries, next)

def parse_service(uri, src):
    res = []
    service = fromstring(src)
    workspaces = service.findall(APP % "workspace")
    for w in workspaces:
        wsname = w.find(ATOM % "title").text
        collections = w.findall(APP % "collection")
        for c in collections:
            cp = {}
            cp['title'] = wsname = c.find(ATOM % "title").text
            cp['href'] = urljoin(uri, c.get('href', ''))
            print "---------------"
            print uri
            print c.get('href', '')
            print cp['href']
            print
            cp['workspace'] = wsname
            accept = c.findall(APP % "accept")
            cp['accept'] = accept and accept[0].text or '' 
            print cp
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
    
    
