import logging

try:
    from xml.etree.ElementTree import fromstring, tostring, SubElement
except:
    from elementtree.ElementTree import fromstring, tostring, SubElement
import re
from urlparse import urljoin
import feedparser
import appmodel
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
        texttype = mime2atom(l[0].get('type', 'text'))
        if texttype in ["text", "html"]:
            pass
        elif texttype == "xhtml":
            div = l[0].findall("{http://www.w3.org/1999/xhtml}div")[0]
            if div != None:
                if div.text:
                    value = div.text
                value = value + "".join( [tostring(c) for c in div.getchildren()] )

        else:
            value = ""
    if value == None:
        value = ""
    return {name: value, (name + "__type"): texttype}

def set_text(name, entry, values):
    logging.warn(values[name + "__type"])
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
        try:
            # For now if we don't have valid XHTML then just push it up 
            # as html. In the future we can use the 1812 normalization
            # code to convert it into xhtml.
            logging.warn(tostring(entry))
            div = fromstring((u"<div xmlns='http://www.w3.org/1999/xhtml'>%s</div>" % values[name]).encode('utf-8'))
            element.append(div)
            logging.warn(tostring(element))
            logging.warn(tostring(entry))
        except:
            element.text = values[name]
            element.set('type', 'html')


mime_to_atom = {
        "application/xhtml+xml": "xhtml",
        "text/html": "html",
        "text/plain": "text"
        }

def mime2atom(t):
    if t in mime_to_atom:
        return mime_to_atom[t]
    else:
        return t

def parse_atom_entry(uri, entry):
    res = {}
    res.update(get_text('content', entry))
    res.update(get_text('title', entry))
    res.update(get_text('summary', entry))
    return res

def unparse_atom_entry(entry, values):
    set_text('title', entry, values)
    set_text('summary', entry, values)
    set_text('content', entry, values)

def parse_collection_feed(uri, src):
    # loop over the entries and pull out the title, link/@rel="edit", updated and published.
    entries = []
    feed = fromstring(src)
    for e in feed.findall(ATOM % "entry"):
        entry = {}
        try:
            edit_links = [l.attrib['href'] for l in e.findall(ATOM % "link") if 'rel' in l.attrib and l.attrib['rel'] == "edit"]
        except:
            edit_links = []
        entry['edit'] = urljoin(uri, edit_links and edit_links[0] or '')
        entry['title'] = e.find(ATOM % "title").text
        entry['updated'] = e.find(ATOM % "updated").text 
        entries.append(entry)
    next_links = [l.attrib['href'] for l in feed.findall(ATOM % "link") if 'rel' in l.attrib and l.attrib['rel'] == "next"]
    if next_links:
        next = urljoin(uri, next_links[0])
    else:
        next = ''

    return (entries, next)


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
    
    
