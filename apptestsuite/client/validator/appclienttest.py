__author__ = "Joe Gregorio <http://bitworking.org/>"
__version__ = "$Revision: 150 $"
__copyright__ = "Copyright (c) 2006 Joe Gregorio"
__license__ = "MIT"

import os 
import sys
import httplib2
try:
      from xml.etree.ElementTree import fromstring, tostring
except:
      from elementtree.ElementTree import fromstring, tostring

import atompubbase
from atompubbase.model import Entry, Collection, Service, Context, init_event_handlers, ParseException
import urlparse
import cStringIO
import sys
from optparse import OptionParser
import time
import feedvalidator
from feedvalidator import compatibility
from mimeparse import mimeparse
from xml.sax.saxutils import escape
from feedvalidator.formatter.text_plain import Formatter as text_formatter
from urllib import urlencode
import xml.dom.minidom
import random
import base64
import urllib

# By default we'll check the bitworking collection 
INTROSPECTION_URI = "http://bitworking.org/projects/apptestsite/app.cgi/service/;service_document"

parser = OptionParser()
parser.add_option("--credentials", dest="credentials",
                    help="FILE that contains a name and password on separate lines with an optional third line with the authentication type of 'ClientLogin <service>'.",
                    metavar="FILE")
parser.add_option("--output", dest="output",
                    help="FILE to store test results",
                    metavar="FILE")
parser.add_option("--verbose",
                  action="store_true", 
                  dest="verbose",
                  default=False,
                  help="Print extra information while running.")
parser.add_option("--quiet",
                  action="store_true", 
                  dest="quiet",
                  default=False,
                  help="Do not print anything while running.")
parser.add_option("--debug",
                  action="store_true", 
                  dest="debug",
                  default=False,
                  help="Print low level HTTP information while running.")
parser.add_option("--html",
                  action="store_true", 
                  dest="html",
                  default=False,
                  help="Output is formatted in HTML")

options, cmd_line_args = parser.parse_args() 


# Restructure so that we use atompubbase
# Add hooks that do validation of the documents at every step
# Add hooks to specific actions that validate other things (such as response status codes)
# Add hooks that log the requests and responses for later inspection (putting them on the HTML page).
#
# Need an object to keep track of the current state, i.e. the test and
# request/response pair that each error/warning/informational is about.
#
# Need to track the desired output format.
#
# Might have to fix up the anchors that the html formatter produces.
#
# Create an httplib2 instance for atompubbase that has a memory based cache.

atompubbase.model.init_event_handlers()

class ClientLogin:
  """
  Perform ClientLogin up front, save the auth token, and then
  register for all the PRE events so that we can add the auth token
  to all requests.
  """

  def __init__(self, http, name, password, service):
    auth = dict(accountType="HOSTED_OR_GOOGLE", Email=name, Passwd=password, service=service,
                source='AppClientTest-%s' % __version__.split()[1] )
    resp, content = http.request("https://www.google.com/accounts/ClientLogin", method="POST", body=urlencode(auth), headers={'Content-Type': 'application/x-www-form-urlencoded'})
    lines = content.split('\n')
    d = dict([tuple(line.split("=", 1)) for line in lines if line])
    if resp.status == 403:
        self.Auth = ""
    else:
        self.Auth = d['Auth']
    atompubbase.events.register_callback("PRE", self.pre_cb)

  def pre_cb(self, headers, body, filters):
    info("Added ClientLogin: %s" % self.Auth)
    headers['authorization'] = 'GoogleLogin Auth=' + self.Auth 


def get_test_data(filename):
  return unicode(file(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                   filename), "r").read(), "utf-8")

def get_test_data_raw(filename):
  return file(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                   filename), "r").read()

class MemoryCache:
  mem = {}

  def set(self, key, value):
    self.mem[key] = value

  def get(self, key):
    return self.mem.get(key, None)

  def delete(self, key):
    if key in self.mem:
      del self.mem[key]


REPRESENTATION = "Representation"
CREATE_FAILED = "Create Failed"
REMOVE_FAILED = "Remove Failed"
UPDATE_FAILED = "Update Failed"
CRED_FILE_INVALID = "Credentials file"
SERVICE_DOCUMENT = "Service Document"
HTTP = "HTTP"
EXCEPTION = "Exception"
SPECIFICATION = "Specification"

class Recorder:
  """
  Records all the warning, errors, etc. and is able to
  spit the results out as a text or html report.
  """
  transcript = [] # a list of (MSG_TYPE, message, details)
  tests = []
  html = True
  verbosity = 0
  has_errors = False
  has_warnings = False

  def __init__(self):
    atompubbase.events.register_callback("ANY", self.log_request_response)
    atompubbase.events.register_callback("POST_CREATE", self.create_validation_cb)
    atompubbase.events.register_callback("POST_GET", self.get_check_response_cb)
    atompubbase.events.register_callback("POST_GET", self.content_validation_cb)


  def error(self, msg, detail):
    self.has_errors = True
    self.transcript.append(("Error", msg, detail))

  def warning(self, msg, detail):
    self.has_warnings = True    
    self.transcript.append(("Warning", msg, detail))

  def info(self, detail):
    self.transcript.append(("Info", "Info", detail))

  def success(self, detail):
    self.transcript.append(("Success", "", detail))

  def log(self, msg, detail):
    self.transcript.append(("Log", msg, detail))

  def _end_test(self):
    if self.transcript:
      self.tests.append(self.transcript)
      self.transcript = []

  def begin_test(self, msg, detail):
    self._end_test()
    self.transcript.append(("Begin_Test", msg, detail))

  def tostr(self):
    self._end_test()
    if self.html:
      return self._tohtml()
    else:
      return self._totext()

  def _tohtml(self):
    resp = [u"""<!DOCTYPE HTML>
<html>
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <link href="validator/res/base.css" type="text/css" rel="stylesheet">
    <script type="text/javascript" src="validator/res/jquery-1.2.3.js"></script>
    <script type="text/javascript" src="validator/res/report.js" ></script>
    <title>AppClientTest - Results</title>
  </head>
<body>
  <h1>Test Report</h1>
  <dl>
    <dt>Date</dt>
    <dd>%s</dd>
  </dl>
  <div class='legend'>
  <h3>Legend</h3>
  <dl>
     <dt><img src='validator/res/info.gif'> Informational</dt>
     <dd>Information on what was being tested.</dd>
     <dt><img src='validator/res/warning.gif'> Warning</dt>
     <dd>Warnings indicate behavior that, while legal, may cause<br/>
       either performance or interoperability problems in the field.</dd>
     <dt><img src='validator/res/error.gif'> Error</dt>
     <dd>Errors are violations of either the Atom, AtomPub<br/> or HTTP specifications.</dd>
     <dt><img src='validator/res/log.gif'> Log</dt>
     <dd>Detailed information on the transaction to help you<br/> debug your service.</dd>
     <dt><img src='validator/res/success.gif'> Success</dt>
     <dd>A specific sub-test has been passed successfully.</dd>
     
  </div>
  """ % (time.asctime())] 
    for transcript in self.tests:
      (code, msg, detail) = transcript[0]
      transcript = transcript[1:]
      resp.append(u"<h2>%s</h2><p>%s</p>\n" % (msg, detail))
      resp.append(u"<ol>\n")
      resp.extend([u"  <li class='%s'><img src='validator/res/%s.gif'> %s <span class='%s'>%s</span></li>\n" %
                   (code, code.lower(), (msg == 'Info') and ' ' or msg, code, detail) for (code, msg, detail) in transcript])
      resp.append(u"</ol>\n")
    return (u"".join(resp)).encode("utf-8")

  def _totext(self):
    resp = []
    resp.extend(["  %s:%s %s\n" % (code, msg, detail) for (code, msg, detail) in self.transcript])
    resp.append("\n")
    return "".join(resp)

  def _validate(self, headers, body):
    if headers.status in [200, 201]:
      baseuri = headers.get('content-location', '')
      try:
          events = feedvalidator.validateStream(cStringIO.StringIO(body),
                                                firstOccurrenceOnly=1,
                                                base=baseuri)['loggedEvents']
      except feedvalidator.logging.ValidationFailure, vf:
          events = [vf.event]

      errors = [event for event in events if isinstance(event, feedvalidator.logging.Error)]
      if errors:
        self.error(REPRESENTATION, "\n".join(text_formatter(errors)))

      warnings = [event for event in events if isinstance(event, feedvalidator.logging.Warning)]
      if warnings:
        self.warning(REPRESENTATION, "\n".join(text_formatter(warnings)))

      if self.verbosity > 2:
        infos = [event for event in events if isinstance(event, feedvalidator.logging.Info)]
        if infos:
          self.info("\n".join(text_formatter(infos)))

  def content_validation_cb(self, headers, body, filters):
    self._validate(headers, body)

  def create_validation_cb(self, headers, body, filters):
    self._validate(headers, body)

  def get_check_response_cb(self, headers, body, filters):
    """
    For operations that should return 200, like get, put and delete.
    """
    if not headers.has_key('etag'):
      self.warning(HTTP, "No ETag: header was sent with the response.")
      if not headers.has_key('last-modified'):
        self.warning(HTTP, "No Last-Modified: header was sent with the response.")
    if headers.get('content-length', 0) > 0 and not headers.has_key('-content-encoding'):
      self.warning(HTTP, "No Content-Encoding: header was sent with the response indicating that a compressed entity body was not returned.")

  def log_request_response(self, headers, body, filters):
    if "PRE" in filters:
      direction = "Request"
    else:
      direction = "Response"
    if headers:
      headers_str = u"\n".join(["%s: %s" % (k, v) for (k, v) in headers.iteritems()])
    else:
      headers_str = u""
    need_escape = True
    if body == None or len(body) == 0:
      body = u""
    else:
      if 'content-type' in headers:
        mtype, subtype, params = mimeparse.parse_mime_type(headers['content-type'])
        if subtype[-4:] == "+xml":
          try:
            dom = xml.dom.minidom.parseString(body)
            body = dom.toxml()
            if len(body.splitlines()) < 2:
              body = dom.toprettyxml()            
          except xml.parsers.expat.ExpatError:
            try:
              body = unicode(body, params.get('charset', 'utf-8'))
            except UnicodeDecodeError:
              try:
                body = unicode(body, 'iso-8859-1')
              except UnicodeDecodeError:
                body = urllib.quote(body)
        elif 'charset' in params:
          body = unicode(body, params['charset'])
        elif mtype == 'image' and self.html:
          body = "<img src='data:%s/%s;base64,%s'/>" % (mtype, subtype, base64.b64encode(body))
          need_escape = False
        else:          
          body = "Could not safely serialize the body"          
      else:
        body = "Could not safely serialize the body"

    if headers_str or body:
      if self.html and need_escape:
        body = escape(body)
      if self.html:
        log = u"<pre><code>\n" + escape(headers_str) + "\n\n" + body + u"</code></pre>"
      else:
        log = headers_str + "\n\n" + body
      self.log(direction, log)


recorder = Recorder()
error    = recorder.error
warning  = recorder.warning
info     = recorder.info
success  = recorder.success
begin_test = recorder.begin_test


class Test:
    """Base class for all the tests. Has a 'run' member
    function which runs over all member functions
    that begin with 'test' and executes them.
    """
    def __init__(self):
        self.reports = []
        self.context = ""
        self.collection_uri = ""
        self.entry_uri = ""

    def run(self):
        methods = [ method for method in dir(self) if callable(getattr(self, method)) and method.startswith("test")]
        for method in methods:
            if not options.quiet:
              print >>sys.stderr, ".",
            sys.stdout.flush()
            test_member_function = getattr(self, method)
            try:
                self.description = str(test_member_function.__doc__)
                self.context = method
                begin_test(method.split("test", 1)[1].replace("_", " "), self.description)
                test_member_function()
            except ParseException, e:
                recorder.log_request_response(e.headers, e.body, set(["POST"]))
                error(REPRESENTATION, "Not well-formed XML")
            except Exception, e:
                import traceback
                info("Internal error occured while running tests: " + str(e) + traceback.format_exc())


def check_order_of_entries(entries, order):       
  info("Check order of entries in the collection document")
  failed = False
  for context, i in zip(entries, order):
    # Need code to extract text from an XHTML title
    title = Entry(context).etree().find(atompubbase.model.ATOM_TITLE)
    if None == title:
      error(REPRESENTATION, "Failed to preserve title")
      failed = True
    else:
      found_i = int(title.text.split()[-1])
      if found_i != i:
        error(SPECIFICATION, "Failed to preserve order of entries, was expecting %d, but found %d" % (i, found_i))
        failed = True
  if not failed:
    success("Order of entries is correct")
  

class EntryCollectionTests(Test):
    def __init__(self, collection):
        Test.__init__(self)
        self.collection = collection 

    def testBasic_Entry_Manipulation(self):
        """Add and remove three entries to the collection"""
        info("Service Document: %s" % self.collection.context().collection)
        info("Count the entries in the collection")
        num_entries = len(list(self.collection.iter()))
        body = get_test_data("i18n.atom").encode("utf-8")

        # Add in a slug and category if allowed.
        slugs = []

        
        for i in range(3):
          info("Create new entry #%d" % (i+1))
          slugs.append("".join([random.choice("abcdefghijkl") for x in range(10)]))
          h, b = self.collection.create(headers = {
            'content-type': 'application/atom+xml',
            'slug': slugs[i]
            },
            body = body % (i+1, repr(time.time())))
          if h.status != 201:
            error(CREATE_FAILED, "Entry creation failed with status: %d %s" % (h.status, h.reason))
            return
          if 'location' not in h:
            error(SPECIFICATION, "Location: not returned in response headers.")            
          if 'content-location' not in h:
            warning(SPECIFICATION, "Content-Location: not returned in response headers.")
          if len(body) == 0:
            warning(SPECIFICATION, "Atom Entry not returned on member creation.")            
        info("Count the entries in the collection after adding three.")
        entries = list(self.collection.iter())
        num_entries_after = len(entries)
        if num_entries_after != num_entries + 3:
          warning(CREATE_FAILED, "All three entries did not appear in the collection.")
          return
        else:
          success("Added three entries.")

        # Confirm the order
        check_order_of_entries(entries, [3,2,1])
        
        # Retrieve an entry
        entry = Entry(entries[1])
        e = entry.etree()

        # Check the slug
        slugified = [link for link in e.findall("{%s}link" % atompubbase.model.ATOM)
                       if ('rel' not in link.attrib or link.attrib['rel'] == "alternate") and slugs[1] in link.attrib['href']]
        if not slugified:
          warning("SPECIFICATION", "Slug was ignored")
        else:
          success("Slug was honored")

        # Check the edit link
        editlink = [link for link in e.findall("{%s}link" % atompubbase.model.ATOM)
                       if ("edit" == link.attrib.get('rel', None))]
        if not editlink:
          warning("SPECIFICATION", "Member Entry did not contain an atom:link element with a relation of 'edit'")
        else:
          success("Member contained an 'edit' link")

          
        
        e.find(atompubbase.model.ATOM_TITLE).text = "Internationalization - 2"
        info("Update entry #2 and write back to the collection")
        h, b = entry.put(headers={'content-type': 'application/atom+xml'}, body = tostring(e))
        if h.status != 200:
          error(UPDATE_FAILED, "Failed to accept updated entry")
        else:
          success("Updated entry #2")

        
        # Confirm new order
        check_order_of_entries(self.collection.iter(), [2,3,1])

        # Remove Entries
        for context in entries[0:3]:
          info("Remove entry")
          h, b = Entry(context).delete()
          if h.status != 200:
            error(REMOVE_FAILED, "Entry removal failed with status: %d %s" % (h.status, h.reason))
            return
        success("Removed three entries.")



class MediaCollectionTests(Test):
    def __init__(self, collection):
        Test.__init__(self)
        self.collection = collection 

    def testBasic_Media_Manipulation(self):
        """Add and remove an image in the collection"""
        info("Service Document: %s" % self.collection.context().collection)
        info("Count the entries in the collection")
        num_entries = len(list(self.collection.iter()))
        
        body = get_test_data_raw("success.gif")
        
        info("Create new media entry")
        slug = "".join([random.choice("abcdefghijkl") for x in range(10)])
        h, b = self.collection.create(headers = {
          'content-type': 'image/gif',
          'slug': slug
          },
          body = body)
        if h.status != 201:
          error(CREATE_FAILED, "Entry creation failed with status: %d %s" % (h.status, h.reason))
          return
        if 'location' not in h:
          error(SPECIFICATION, "Location: not returned in response headers.")            
        if 'content-location' not in h:
          warning(SPECIFICATION, "Content-Location: not returned in response headers.")
        if len(body) == 0:
          warning(SPECIFICATION, "Atom Entry not returned on member creation.")            

        info("Count the entries in the collection after adding three.")
        entries = list(self.collection.iter())
        num_entries_after = len(entries)
        if num_entries_after != num_entries + 1:
          warning(CREATE_FAILED, "New media entry did not appear in the collection.")
          return
        else:
          success("Added Media Entry")

        entry = Entry(entries[0])
        e = entry.etree()

        # Check the slug
        slugified = [link for link in e.findall("{%s}link" % atompubbase.model.ATOM)
                       if ('rel' not in link.attrib or link.attrib['rel'] == "alternate") and slug in link.attrib['href']]
        if not slugified:
          warning("SPECIFICATION", "Slug was ignored")
        else:
          success("Slug was honored")


        # Check the edit link
        editlink = [link for link in e.findall("{%s}link" % atompubbase.model.ATOM)
                       if ("edit" == link.attrib.get('rel', None))]
        if not editlink:
          warning("SPECIFICATION", "Member Entry did not contain an atom:link element with a relation of 'edit'")
        else:
          success("Member contained an 'edit' link")
          

        # Check the edit-media link
        editmedialink = [link for link in e.findall("{%s}link" % atompubbase.model.ATOM)
                       if ("edit-media" == link.attrib.get('rel', None))]
        if not editmedialink:
          warning("SPECIFICATION", "Member Entry did not contain an atom:link element with a relation of 'edit-media'")
        else:
          success("Member contained an 'edit-media' link")
          

        
        e.find(atompubbase.model.ATOM_TITLE).text = "Success"
        info("Update Media Link Entry and write back to the collection")
        h, b = entry.put(headers={'content-type': 'application/atom+xml'}, body = tostring(e))
        if h.status != 200:
          error(UPDATE_FAILED, "Failed to accept updated entry")
        else:
          success("Updated Media Link Entry")

        
        # Remove Entry
        info("Remove entry")
        h, b = entry.delete()
        if h.status != 200:
          error(REMOVE_FAILED, "Entry removal failed with status: %d %s" % (h.status, h.reason))
          return
        success("Removed Media Entry")



class TestIntrospection(Test):
    def __init__(self, uri, http):
        Test.__init__(self)
        self.http = http
        self.introspection_uri  = uri

    def testEntry_Collection(self):
        """Find the first entry collection listed in an Introspection document and run the Entry collection tests against it."""
        context = Context(self.http, self.introspection_uri)
        service = Service(context)
        entry_collections = list(service.iter_match("application/atom+xml;type=entry"))
          
        if 0 == len(entry_collections):
            warning(SERVICE_DOCUMENT, "Didn't find any entry collections to test")
        else:
          test = EntryCollectionTests(Collection(entry_collections[0]))
          test.run()

        media_collections = list(service.iter_match("image/gif"))
          
        if 0 == len(media_collections):
            warning(SERVICE_DOCUMENT, "Didn't find any media collections that would accept GIF images")
        else:
          test = MediaCollectionTests(Collection(media_collections[0]))
          test.run()

def main(options, cmd_line_args):
    if options.debug:
        httplib2.debuglevel = 5
    if options.verbose:
        recorder.verbosity = 3
    if options.html:
        recorder.html = True

    http = httplib2.Http(MemoryCache())
    http.force_exception_to_status_code = False

    if options.credentials:
      parts = file(options.credentials, "r").read().splitlines()
      if len(parts) == 2:
        name, password = parts
        http.add_credentials(name, password)
      elif len(parts) == 3:
        name, password, authtype = parts 
        authname, service = authtype.split()
        if authname != "ClientLogin":
          error(CRED_FILE, "Unknown type of authentication: %s ['ClientLogin' is the only good value at this time.]" % cl)
          return
        cl = ClientLogin(http, name, password, service)
      else:
        error(CRED_FILE, "Wrong format for credentials file")

    #from atompubbase.mockhttp import MockRecorder
    #http = MockRecorder(http, "./validator/rawtestdata/")

    if not cmd_line_args:
      cmd_line_args = [INTROSPECTION_URI]
    for target_uri in cmd_line_args:
      if not options.quiet:
        print >>sys.stderr, "Testing the service at <%s>" % target_uri
        print >>sys.stderr, "Running: ",
      test = TestIntrospection(target_uri, http)
      test.run()
    
    outfile = sys.stdout
    if options.output:
      outfile = file(options.output, "w")

    print >>outfile, recorder.tostr()
    status = 0
    if recorder.has_warnings:
      status = 1
    if recorder.has_errors:
      status = 2

    return status

if __name__ == '__main__':
    sys.exit(main(options, cmd_line_args))
