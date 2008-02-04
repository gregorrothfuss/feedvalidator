__author__ = "Joe Gregorio <http://bitworking.org/>"
__version__ = "$Revision: 150 $"
__copyright__ = "Copyright (c) 2006 Joe Gregorio"
__license__ = "MIT"

import os 
import sys

sys.path.append(os.getcwd())

CUR_DIR = os.path.split(os.path.abspath(__file__))[0]
ATOM = "http://www.w3.org/2005/Atom"
ATOM_LINK = "{%s}link" % ATOM
ATOM_ENTRY = "{%s}entry" % ATOM
ATOM_TITLE= "{%s}title" % ATOM

APP = "http://www.w3.org/2007/app"
APP_COLL = "{%s}collection" % APP
APP_MEMBER_TYPE = "{%s}accept" % APP

import httplib2
try:
      from xml.etree.ElementTree import fromstring, tostring
except:
      from elementtree.ElementTree import fromstring, tostring


# By default we'll check the bitworking collection 
INTROSPECTION_URI = "http://bitworking.org/projects/apptestsite/app.cgi/service/;service_document"
import atompubbase
import urlparse
import cStringIO
import sys
import getopt
import time

# Restructure so that we use atompubbase
# Add hooks that do validation of the documents at every step
# Add hooks to specific actions that validate other things (such as response status codes)
# Add hooks that log the requests and responses for later inspection (putting them on the HTML page).
#
# Need an object to keep track of the current state, i.e. the test and
# request/response pair that each error/warning/informational is about.
#
# Create an httplib2 instance for atompubbase that has a memory based cache.


import feedvalidator
from feedvalidator import compatibility
try:
    from atompubbase.ErrorReporting import *
except:
    path = os.path.split(CUR_DIR)[0]
    sys.path.insert(0, path)
    from atompubbase.ErrorReporting import *

try:
    from mimeparse import mimeparse
except:
    import atompubbase.mimeparse.mimeparse as mimeparse


def usage(option=""):
    print """Usage: appclienttest [OPTION] IntrospectionURI

  -h, --help            Display this help message then exit.
      --name=<name>     User name to use for authentication.
      --password=<pw>   Password to use for authentication.
      --debug=<n>       Print debugging information for n > 0.

"""
    if option:
        print """!! %s !!""" % option


def validate_atom(testcase, content, baseuri):
    retval = True
    try:
        events = feedvalidator.validateStream(cStringIO.StringIO(content), firstOccurrenceOnly=1,base=baseuri)['loggedEvents']
    except feedvalidator.logging.ValidationFailure, vf:
        events = [vf.event]

    filterFunc = getattr(compatibility, "A")
    events = filterFunc(events)
    if len(events):
        from feedvalidator.formatter.text_plain import Formatter
        output = Formatter(events)
        testcase.report(MustUseValidAtom("\n".join(output) + content))
        retval = False
    return retval

class Test:
    """Base class for all the tests. Adds basic
    functionality of recording reports as they
    are generated. Also has a 'run' member
    function which runs over all member functions
    that begin with 'test' and executes them.
    """
    def __init__(self):
        self.reports = []
        self.context = ""
        self.collection_uri = ""
        self.entry_uri = ""

    def report(self, r):
        r.context = self.context 
        if self.collection_uri:
            r.context += "\n\n   Collection: %s" % self.collection_uri
        if self.entry_uri:
            r.context += "\n   Entry: %s" % self.entry_uri
        self.reports.append(r)

    def run(self):
        methods = [ method for method in dir(self) if callable(getattr(self, method)) and method.startswith("test")]
        for method in methods:
            print ".",
            sys.stdout.flush()
            test_member_function = getattr(self, method)
            try:
                self.description = str(test_member_function.__doc__)
                self.context = method
                test_member_function() 
            except Exception, e:
                import traceback
                self.report(InternalErrorEncountered(str(e) + traceback.format_exc()))
    

CONTENT_WITH_SRC = """<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom">
  <title>This is a title</title>
  <id>urn:uuid:1225c695-ffb8-4ebb-aaaa-80da354efa6a</id>
  <updated>2005-09-02T10:30:00Z</updated>
  <summary>Hi!</summary>
  <author>
    <name>Joe Gregorio</name>
  </author>
  <content
     type="image/png"
     src="http://bitworking.org/projects/atompubtest/client/helloworld.png" />
</entry>
"""

CONTENT_WITH_OTHER = """<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom">
   <title>This should not be blank</title>
   <id>urn:uuid:1225c695-ffb8-4ebb-aaaa-80da354efa6a</id>
   <updated>2005-09-02T10:30:00Z</updated>
   <author>
     <name>Joe Gregorio</name>
   </author>
   <summary>Hi!</summary>
   <content type="image/png" >
iVBORw0KGgoAAAANSUhEUgAAAEYAAAALCAIAAABNimxhAAAAAXNSR0IArs4c6QAAAARnQU1BAACx
jwv8YQUAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAAThJREFU
SEvdlD0OgzAMhdvbcgiOwAm4ADs7M2tXRkY2bkA/9UmW5SRQ2kpV6wEZx3bei3+u27Zd/kyMEkrQ
ZfEi7oduCqmqCudlWdDneUYfxxF9XVd0TtP8OzdmYWQzRHwGOu99hlLXdUaj73v0tm1JCzF0Tr9A
SZgMii+OZ25uAeU0Tbg1TUNgXddWGSzonGJPY5UZf8TfSLVVdr2OmuWgSn6g7DISIYYsbTxhuj0k
fXv5q9PERNkEKBurUxpVcM1Z4djVw09RCik8w5RJaskOmIojNCJG7/ENFSjVv2R/i1Ko7A63LKVh
GBSiKRJDhOYJ/tk3+jAlPSej/E7jWZNo12kxIH6QQtOGCtiv8BCoEX2l8fzsasTPrgcfQtfx6wdJ
p6X1YN1h6M+th9Lq+FF7cRX+KB9g3wGfjZVSUSpSSwAAAABJRU5ErkJggg==
</content>
</entry>
"""

MIXED_TEXT_TYPES = """<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom">
   <title type="html">
      This &lt;b>is&lt;/b> a title.
   </title>
   <id>urn:uuid:1225c695-ffb8-4ebb-aaaa-80da354efa6a</id>
   <updated>2005-09-02T10:30:00Z</updated>
   <author>
     <name>Joe Gregorio</name>
   </author>
   <summary type="xhtml">
      <div xmlns="http://www.w3.org/1999/xhtml">
         Hello <b>World</b>!
      </div>
   </summary>
   <content type="text" >This is just plain text content.
   </content>
</entry>
"""

# A missing Author makes this entry invalid
NON_WELL_FORMED_ENTRY = """<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom">
  <title>This is a title</title>
  <id>urn:uuid:1225c695-ffb8-4ebb-aaaa-80da354efa6a</id>
  <updated>2005-09-02T10:30:00Z</updated>
  <summary>Hi!</summary>
"""

def absolutize(baseuri, uri):
    (scheme, authority, path, query, fragment) = httplib2.parse_uri(uri)
    if authority == None:
        uri = urlparse.urljoin(baseuri, uri)
    return uri


class EntryCollectionTests(Test):
    def __init__(self, entry_coll_uri, http):
        Test.__init__(self)
        self.entry_coll_uri = entry_coll_uri
        self.collection_uri = entry_coll_uri
        self.http = http
        print "Testing: %s\n" % entry_coll_uri

    def setUp(self):
        time.sleep(1)

    def enumerate_collection(self):
        relnext = [self.entry_coll_uri]
        retval = {} 
        while relnext:
            uri = absolutize(self.entry_coll_uri, relnext[0])
            self.entry_uri = uri
            (response, content) = self.http.request(uri, "GET", headers = {"Cache-Control": "max-age=0"})
            if not validate_atom(self, content, uri):
                return {}
            tree = fromstring(content)
            for e in tree.findall(ATOM_ENTRY):
                reledit = [l.get('href', '') for l in e.findall(ATOM_LINK) if l.get('rel', '') == 'edit'] 
                for t in reledit:
                    retval[absolutize(self.entry_coll_uri, t)] = e 
            relnext = [l.get('href', '') for l in tree.findall(ATOM_LINK) if l.get('rel', '') == 'next'] 
        return retval

    def testHttpConformance(self):
        """Do a simple GET on a collection
        feed and look for suggested HTTP
        practice."""
        (response, content) = self.http.request(self.entry_coll_uri)
        if not response.has_key('etag'):
            self.report(ShouldSupportCacheValidators("No ETag: header was sent with the response."))
            if not response.has_key('last-modified'):
                self.report(ShouldSupportCacheValidators("No Last-Modified: header was sent with the response."))
        if not response.has_key('-content-encoding'):
            self.report(ShouldSupportCompression("No Content-Encoding: header was sent with the response indicating that a compressed entity body was not returned."))

    def testContentWithSrc(self):
        """POST a good Atom Entry with a content/@src
        attribute set and with the right mime-type.
        Ensure that the entry is added to the collection.
        """
        toc = self.enumerate_collection()
        startnum = len(toc)
        # Add a new entry
        (response, content) = self.http.request(self.entry_coll_uri, "POST", body=CONTENT_WITH_SRC, headers={'Content-Type': 'application/atom+xml', 'Accept': '*/*'})

        if response.status != 201:
            self.report(EntryCreationMustReturn201("Actually returned an HTTP status code %d" % response.status))
        if not response.has_key('location'):
            self.report(EntryCreationMustReturnLocationHeader("Header is completely missing"))
            return

        toc = self.enumerate_collection()
        # Make sure it was added to the collection
        if startnum >= len(toc):
            self.report(EntryCreationMustBeReflectedInFeed("Number of entries went from %d before to %d entries after the entry was created." % (startnum, len(toc))))

        # The location header should match the link/@rel="edit"
        edituri = response['location']
        if edituri not in toc:
            self.report(LocationHeaderMustMatchLinkRelEdit("The Location: header value %s can't be found in %s" % (response['location'], str(toc))))

        (response, content) = self.http.request(edituri, "GET", headers = {"Cache-Control": "max-age=0"})
        if response.status != 200:
            self.report(GetFailedOnMemberResource("Expected an HTTP status code of 200 but instead received %d" % response.status))
        validate_atom(self, content, edituri)

        # Cleanup
        (response, content) = self.http.request(edituri, "DELETE")
        if response.status >= 400:
            self.report(EntryDeletionFailed("HTTP Status %d" % response.status))
        toc = self.enumerate_collection()

        if startnum != len(toc):
            self.report(EntryDeletionMustBeReflectedInFeed("Number of entries went from %d before to %d entries after the entry was deleted." % (startnum, len(toc))))
        if edituri in toc:
            self.report(EntryDeletionMustBeReflectedInFeed("The URI for the entry just deleted <%s> must not appear in the feed after the entry is deleted." % edituri))

    def testContentWithBase64Content(self):
        """ POST a good Atom Entry with an entry 
        whose atom:content is a base64 encoded png.
        """
        (response, content) = self.http.request(self.entry_coll_uri, "POST", body=CONTENT_WITH_OTHER, headers={'Content-Type': 'application/atom+xml', 'Accept': '*/*'})
        if response.status != 201:
            self.report(EntryCreationMustReturn201("Actually returned an HTTP status code %d" % response.status))
        else:
            edituri = response['location']
            (response, content) = self.http.request(edituri, "DELETE")
            if response.status >= 400:
                self.report(EntryDeletionFailed("HTTP Status %d" % response.status))

    def testMixedTextConstructs(self):
        """ POST a good Atom Entry with an entry 
        whose Text Constructs contain a mix of types.
        """
        (response, content) = self.http.request(self.entry_coll_uri, "POST", body=MIXED_TEXT_TYPES, headers={'Content-Type': 'application/atom+xml', 'Accept': '*/*'})
        if response.status != 201:
            self.report(EntryCreationMustReturn201("Actually returned an HTTP status code %d" % response.status))
        edituri = response['location']
        (response, content) = self.http.request(edituri, "DELETE")
        if response.status >= 400:
            self.report(EntryDeletionFailed("HTTP Status %d" % response.status))

    def testNonWellFormedEntry(self):
        """ POST an invalid Atom Entry 
        """
        (response, content) = self.http.request(self.entry_coll_uri, "POST", body=NON_WELL_FORMED_ENTRY, headers={'Content-Type': 'application/atom+xml', 'Accept': '*/*'})
        if response.status < 400:
            self.report(MustRejectNonWellFormedAtom("Actually returned an HTTP status code %d" % response.status))

    def testI18n(self):
        """ POST a fully utf-8 Atom Entry 
        """
        i18n = file(os.path.join(CUR_DIR, "i18n.atom"), "r").read()
        tree = fromstring(i18n)
        title_sent = tree.findall(".//" + ATOM_TITLE)[0].text
        (response, content) = self.http.request(self.entry_coll_uri, "POST", body=i18n, headers={'Content-Type': 'application/atom+xml', 'Content-Length' : str(len(i18n)), 'Accept': '*/*'})
        if response.status >= 400:
            self.report(ServerShouldHandleI18NContent("Actually returned an HTTP status code %d" % response.status))
        if response.status != 201:
            self.report(EntryCreationMustReturn201("Actually returned an HTTP status code %d" % response.status))
        location = response['location']
        (response, content) = self.http.request(location, "GET")
        tree = fromstring(content)
        title_received = tree.findall(".//" + ATOM_TITLE)[0].text
        tree.findall(".//" + ATOM_TITLE)[0].text = "Non Internationalized"
        if title_sent != title_received:
            self.report(ServerShouldHandleI18NContent(u"%s != %s" % (title_sent, title_received)))
        ni18n = tostring(tree)
        (response, content) = self.http.request(location, "PUT", body=ni18n, headers={'Content-Length' : str(len(ni18n)), 'Content-Type' : 'application/atom+xml'})
        if response.status != 200:
            self.report(EntryUpdateFailed("Actually returned an HTTP status code %d" % response.status))

        (response, content) = self.http.request(location, "GET")
        tree = fromstring(content)
        title_received = tree.findall(".//" + ATOM_TITLE)[0].text
        if title_received != "Non Internationalized":
            self.report(EntryUpdateFailed("Title not updated. %s != %s" % (title_received, "Non Internationalized")))


        (response, content) = self.http.request(location, "DELETE")

    def testDoubleAddWithSameAtomId(self):
        """POST two Atom entries with the same atom:id 
        to the collection. The response for both MUST be
        201 and two new entries must be created."""
        toc = self.enumerate_collection()
        startnum = len(toc)
        # Add a new entry
        (response, content) = self.http.request(self.entry_coll_uri, "POST", body=CONTENT_WITH_SRC, headers={'Content-Type': 'application/atom+xml', 'Accept': '*/*'})
        if response.status != 201:
            self.report(EntryCreationMustReturn201("Actually returned an HTTP status code %d" % response.status))
            return
        toc = self.enumerate_collection()
        # Make sure it was added to the collection
        if startnum >= len(toc):
            self.report(EntryCreationMustBeReflectedInFeed("Number of entries went from %d before to %d entries after the entry was created." % (startnum, len(toc))))
            return
        # The location header should match the link/@rel="edit"
        edituri = response['location']

        time.sleep(2)
        (response, content) = self.http.request(self.entry_coll_uri, "POST", body=CONTENT_WITH_SRC, headers={'Content-Type': 'application/atom+xml', 'Accept': '*/*'})
        if response.status != 201:
            self.report(EntryCreationMustReturn201("When POSTing a second entry with the same atom:id of an entry we just POSTed the server returned an HTTP status code %d" % response.status))
            return

        toc = self.enumerate_collection()
        # Make sure it was added to the collection
        if startnum+1 >= len(toc):
            self.report(EntryCreationMustBeReflectedInFeed("Number of entries went from %d before to %d entries after the entry was created." % (startnum+1, len(toc))))
        edituri2 = response['location']

        if edituri == edituri2:
            self.report(EntryCreationMustReturnLocationHeader("Non unique Location: header value returned in a 201 response. <%s>" % edituri))

        # Cleanup
        (response, content) = self.http.request(edituri, "DELETE")
        if response.status >= 400:
            self.report(EntryDeletionFailed("HTTP Status %d" % response.status))
        (response, content) = self.http.request(edituri2, "DELETE")
        if response.status >= 400:
            self.report(EntryDeletionFailed("HTTP Status %d" % response.status))

class TestIntrospection(Test):
    def __init__(self, uri, http):
        Test.__init__(self)
        self.http = http
        self.introspection_uri  = uri

    def testEachEntryCollection(self):
        """Run over each entry collection listed
in an Introspection document and
run the Entry collection tests
against it."""
        response, content = self.http.request(self.introspection_uri)
        # Add a validation step for the introspection document itself.
        tree = fromstring(content)
        collections = list(tree.findall(".//" + APP_COLL))
        for coll in collections:
            coll_type = [t for t in coll.findall(APP_MEMBER_TYPE) if mimeparse.best_match([t.text], 'application/atom+xml;type=entry')] 
            if coll_type:
                test = EntryCollectionTests(absolutize(self.introspection_uri, coll.get('href')), self.http)
                test.run()
                self.reports.extend(test.reports)
                break
        if 0 == len(collections):
            print "Didn't find any collections"

def format(r):
    return """----------------------------------------
%s:
   %s

Context: 
   %s

Details: 
   %s

""" % (r.__class__.__name__, r.text, r.context, r.extra)

def print_report(reports, reportclass):
    matching = [r for r in reports if isinstance(r, reportclass)]
    if matching:
        print "\n".join([format(r) for r in matching])
    else:
        print "  No problems found."


def main():

    options = ["help", "name=", "password=", "debug="]
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", options )
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    name = password = None
    for o, a in opts:
        if o == "--name":
            name = a
        if o == "--password":
            password = a
        if o == "--debug":
            httplib2.debuglevel = int(a)
        if o in ["h", "--help"]:
            usage()
            sys.exit()
            

    http = httplib2.Http(".cache")

    if name:
        print "%s: %s" % (name, password)
        http.add_credentials(name, password)
    if not args:
        args = [INTROSPECTION_URI]
    for target_uri in args:
        print "Atom Client Tests"
        print "-----------------"
        print ""
        print "Testing the service at <%s>" % target_uri
        print ""
        print ""
        print "Running: ",
        test = TestIntrospection(target_uri, http)
        test.run()
        reports = test.reports
        print ""
        print "== Errors =="
        print_report(reports, Error)
        print "== Warnings =="
        print_report(reports, Warning)
        print "== Suggestions =="
        print_report(reports, Suggestion)
        if not reports:
            print "Success!"


if __name__ == '__main__':
    main()
