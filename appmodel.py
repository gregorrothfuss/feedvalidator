#!/usr/bin/env python2.4
import httplib2
import apptools
import logging
try:
    from xml.etree.ElementTree import fromstring, tostring
except:
    from elementtree.ElementTree import fromstring, tostring
import cPickle
import md5
import feedvalidator
from feedvalidator import compatibility
import cStringIO
from ErrorReporting import *
from urlparse import urljoin
from ConfigParser import SafeConfigParser
import os
import anydbm

httplib2.debuglevel=100

ATOM = "{http://www.w3.org/2005/Atom}%s"
APP = "{http://purl.org/atom/app#}%s"

# Called as logger_cb(uri, resp, content, method, body, headers, redirections)
logger_cb = None

# Called with a ErrorReporting.Reportable
# e.g. error_reporting_cb(EntryCreationMustReturn201())
error_reporting_cb = None


# Monkey patch httplib2 to enable logging/validation
#
httplib2.Http.request_not_instrumented = httplib2.Http.request

def instrumented_request(self, uri, method="GET", body=None, headers=None, redirections=httplib2.DEFAULT_MAX_REDIRECTS):
    (resp, content) = httplib2.Http.request_not_instrumented(self, uri, method, body, headers, redirections)
    # trigger a validation callback with the request and response info
    if logger_cb:
        logger_cb(uri, resp, content, method, body, headers, redirections)
    return (resp, content)

httplib2.Http.request = instrumented_request

ENTRY_ELEMENTS = ["title", "title__type", "summary", "summary__type", "content", "content__type"]
DEFAULT_ENTRY = """<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom">
  <title type="text">Title goes here.</title>
  <id>http://bitworking.org/foo/app/main/third</id>
  <author>
     <name>anonymous</name>
  </author>
  <updated>2006-08-04T15:52:00-05:00</updated>
  <summary type="xhtml">
    <div xmlns="http://www.w3.org/1999/xhtml">
    </div>
  </summary>
  <content type="xhtml">
    <div xmlns="http://www.w3.org/1999/xhtml">
    </div>
  </content>
</entry>

"""

def report(reportable):
    if error_reporting_cb:
        error_reporting_cb(reportable)

def validate_atom(content, baseuri):
    try:
        events = feedvalidator.validateStream(cStringIO.StringIO(content), firstOccurrenceOnly=1,base=baseuri)['loggedEvents']
    except feedvalidator.logging.ValidationFailure, vf:
        events = [vf.event]

    filterFunc = getattr(compatibility, "A")
    err_events = filterFunc(events)
    if len(err_events):
        from feedvalidator.formatter.text_plain import Formatter
        output = Formatter(err_events)
        report(MustUseValidAtom("\n".join(output)))

    warn_events = [event for event in events if compatibility._should(event)]
    if len(warn_events):
        from feedvalidator.formatter.text_plain import Formatter
        output = Formatter(warn_events)
        report(AtomShouldViolation("\n".join(output)))


class Entry(object):
    def __init__(self, h, edit, title="", title__type="text", updated="", published=""):
        self.h = h
        self.member_uri = edit 

        # Will be filled in with an ElementTree of the entry
        # once self.get() is called.
        self.element = None

        self._values = {
            "title" : title,
            "title__type" : title__type,
            "updated" : updated,
            "published" : published,
            "summary": "",
            "summary__type": "text",
            "content": "",
            "content__type": "text"
        }

    # def get/set text element (takes both text and it's type)
    # def get/set link (rel and optional type).

    def __getitem__(self, name):
        return self._values.get(name, name.endswith("__type") and 'text' or '')

    def __setitem__(self, name, value):
        if name in self._values:
            self._values[name] = value
        else:
            raise IndexError, "index '%s' not found" % name

    def get(self):
        if self.member_uri:
            (resp, content) = self.h.request(self.member_uri)
        else:
            content = DEFAULT_ENTRY
        validate_atom(content, self.member_uri)
        self.element = fromstring(content)
        d = apptools.parse_atom_entry(self.member_uri, content)
        self._values.update(d)

    def put(self):
        # loop over the values in sef._values, update self.element
        # then serialize the element into a PUT
        self.h.request(self.member_uri, method="PUT", body=self.tostring(), headers={
                'content-type': 'application/atom+xml'
                }
            )

    def delete(self):
        self.h.request(self.member_uri, method="DELETE")

    def tostring(self):
        apptools.unparse_atom_entry(self.element, self._values)

        logging.error(tostring(self.element))
        return tostring(self.element)

class _EntryIterator(object):
    def __init__(self, h, collection_uri, hit_map):
        self.h = h
        self.collection_uri = collection_uri
        self.local_hit_map = {}
        self.page_uri = collection_uri
        self.hit_map = hit_map
        self.entries = [] 
        self.next = None

    def __iter__(self):
        return self

    def next(self):
        if None == self.entries:
            (resp, content) = self.h.request(self.page_uri)
            (self.entries, self.page_uri) = apptools.parse_collection_feed(self.page_uri, content)
        if len(entries):
            entry = entries[0]
            del entries[0]
            # Compute the hit hash from the "edit" URI and the app:edited/atom:updated
            # Do we skip entries that do not have an "edit" URI?!?
            return Entry(self.h, **entry)
        else:
            raise StopIterator


class Collection(object):
    def __init__(self, h, cachedir, href, title, workspace, accept):
        self.h = h
        self.cachedir = os.path.join(cachedir, httplib2.safename(href))
        if not os.path.exists(self.cachedir):
            os.makedirs(self.cachedir)
        self.hitmap = anydbm.open(os.path.join(self.cachedir, "hitmap.db"), "c")
        self.href = href 
        self.title = title 
        self.workspace = workspace 
        self.accept = accept 

    def post(self, entry):
        (resp, content) = self.h.request(self.href, method="POST", body=entry.tostring(), headers={
                'content-type': 'application/atom+xml;type=entry'
                }
            )

    def iter_entries(self):
        pass

    def iter_new_entries(self):
        pass

    def entries(self):
        (resp, content) = self.h.request(self.href)
        retval = [Entry(self.h, "", "(new...)")]
        if resp['status'] == 304 and self.entry_info:
            return (self.entry_info['entries'], self.entry_info['next'])
        elif resp.status < 300:
            validate_atom(content, self.href)
            retval.extend([Entry(self.h, **e) for e in self.entry_info['entries']])
            self.entry_info_cache.set(self.cachekey, cPickle.dumps(self.entry_info))
            return (retval,  self.entry_info['next'])
        else:
            return (retval, None)

# Need to save and restore service URIs along with
# names and passwords.

# TODO convert the service list to use ConfigParser
# TODO rename Model to Service
# Convert Service to use not use ConfigParser, instead have it take 
# a uri, name, and password. One Service object per Service document.
class Service:
    def __init__(self, service_uri, cachedir, username, password):
        self.h = httplib2.Http(os.path.join(cachedir, ".httplib2_cache"))
        self.h.follow_all_redirects = True
        # A list of tuples, each a name and a list of Collection objects.
        self._workspaces = [] 
        (resp, content) = self.h.request(service_uri)
        if resp.status == 200:
            try:
                self._parse_service(service_uri, content, name, password)
            except:
                logging.error("Failed to parse service document at %s" % service_uri)
            service = fromstring(content)
            workspaces = service.findall(APP % "workspace")
            for w in workspaces:
                wstitle = w.find(ATOM % "title")
                wsname = (wstitle != None) and wstitle.text or "No title"
                collections = []
                collection_elements = w.findall(APP % "collection")
                for c in collection_elements:
                    cp = {}
                    title = c.find(ATOM % "title")
                    cp['title'] = (title != None) and title.text or "No title"
                    cp['href'] = urljoin(service_uri, c.get('href', ''))
                    cp['workspace'] = wsname
                    accepts = c.findall(APP % "accept")
                    cp['accept'] = [node.text for node in accepts]
                    collections.append(Collection(self.h, cachedir, **cp))
                self._workspaces.append( (wsname, collections) )

    def collections(self):
        return sum([collections for (wsname, collections) in self._workspaces], [])

    def workspaces(self):
        """Returns a list of tuples, (workspacename, collections), where
        collections is a list of Collection objects, and workspacename is the
        name of the workspace"""
        return self._workspaces
    

#    def load_service_list(self):
#        config = SafeConfigParser()
#        config.read(['config.ini'])
#
#        self.service_list = []
#        for service in config.sections():
#            uri = config.get(service, 'uri')
#            if config.has_option(service, 'name'):
#                name = config.get(service, 'name')
#                password = config.get(service, 'password')
#            else:
#                name = password = None
#            self.service_list.append((uri, name, password))



