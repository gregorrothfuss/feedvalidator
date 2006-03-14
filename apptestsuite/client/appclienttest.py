__author__ = "Joe Gregorio <http://bitworking.org/>"
__version__ = "$Revision: 150 $"
__copyright__ = "Copyright (c) 2006 Joe Gregorio"
__license__ = "MIT"

ATOM = "http://www.w3.org/2005/Atom"
ATOM_LINK = "{%s}link" % ATOM
ATOM_ENTRY = "{%s}entry" % ATOM

APP = "http://purl.org/atom/app#"
APP_COLL = "{%s}collection" % APP
APP_MEMBER_TYPE = "{%s}member-type" % APP

# By default we'll check the bitworking collection 
INTROSPECTION_URI = "http://bitworking.org/projects/pyapp/collection.cgi?introspection=1"
import httplib2
import unittest
import cElementTree
import urlparse
import cStringIO
import sys
import getopt

import feedvalidator
from feedvalidator import compatibility
from gettext import gettext as _

def usage(option=""):
    print """Usage: appclienttest [OPTION] IntrospectionURI

  -h, --help            Display this help message then exit.
      --name            User name to use for authentication.
      --password        Password to use for authentication. 
"""
    if option:
        print """!! %s !!""" % option


def validate_atom(testcase, content, baseuri):
    retval = True
    try:
        events = feedvalidator.validateStream(cStringIO.StringIO(content), firstOccurrenceOnly=1,base=baseuri)['loggedEvents']
    except feedvalidator.logging.ValidationFailure, vf:
        events = [vf.event]

    filterFunc = getattr(compatibility, "AA")
    events = filterFunc(events)
    if len(events):
        from feedvalidator.formatter.text_plain import Formatter
        output = Formatter(events)
        testcase.report(MustUseValidAtom("\n".join(output)))
        retval = False
    return retval

class Reportable:
    """Base class for all the errors, warnings and suggestions."""
    text = "" 
    def __init__(self, extra = None):
        self.extra = extra
        self.context = ""

    def tostring(self):
        return self.context + ":" + self.text + ":" + self.extra 

# Every report should subclass one of these three classes, 
# which will make filtering of results easy.
class Error(Reportable): pass 
class Warning(Reportable): pass
class Suggestion(Reportable): pass

class ShouldSupportCacheValidators(Suggestion):
    text = _('GET should support the use of ETags and/or Last-Modifed cache validators.')

class ShouldSupportCompression(Suggestion):
    text = _('GET should support the use of compression to speed of transfers.')

class MustUseValidAtom(Error):
    text = _('Atom entries and feeds MUST be valid.')

class InternalErrorEncountered(Error):
    text = _('Internal error encountered. It could be non-welllformed XML.')

class EntryCreationMustReturnLocationHeader(Error):
    text = _('When an entry is successfully created the server MUST return a Location: HTTP header.')

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

    def report(self, r):
        r.context = self.context
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
                self.report(InternalErrorEncountered(str(e)))
    

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
iVBORwoaCgAAAA1JSERSAAAARgAAAAsIAgAAAE2KbGEAAAABc1JHQgCuzhzpAAAABGdBTUEAALGP\nC
/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAABOElEQVRI\nS92
UPQ6DMAyF29tyCI7ACbgAOzsza1dGRjZuQD/1SZblJFDaSlXrARnHdt6Lf67btl3+TIwSStBl\n8SLuh
24KqaoK52VZ0Od5Rh/HEX1dV3RO0/w7N2ZhZDNEfAY6732GUtd1RqPve/S2bUkLMXROv0BJ\nmAyKL45
nbm4B5TRNuDVNQ2Bd11YZLOicYk9jlRl/xN9ItVV2vY6a5aBKfqDsMhIhhixtPGG6PSR9\ne/mr08RE2
QQoG6tTGlVwzVnh2NXDT1EKKTzDlElqyQ6YiiM0Ikbv8Q0VKNW/ZH+LUqjsDrcspWEY\nFKIpEkOE5gn
+2Tf6MCU9J6P8TuNZk2jXaTEgfpBC04YK2K/wEKgRfaXx/OxqxM+uBx9C1/HrB0mn\npfVg3WHoz62H0
ur4UXtxFf4oH2DfAZ+NlVJRKlJLAAAAAElFTkSuQmCC
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
INVALID_ENTRY = """<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom">
  <title>This is a title</title>
  <id>urn:uuid:1225c695-ffb8-4ebb-aaaa-80da354efa6a</id>
  <updated>2005-09-02T10:30:00Z</updated>
  <summary>Hi!</summary>
</entry>
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
        self.http = http

    def enumerate_collection(self):
        relnext = [self.entry_coll_uri]
        retval = {} 
        while relnext:
            uri = absolutize(self.entry_coll_uri, relnext[0])
            (response, content) = self.http.request(uri, "GET", headers = {"Cache-Control": "max-age=0"})
            if not validate_atom(self, content, uri):
                return {}
            tree = cElementTree.fromstring(content)
            for e in tree.findall(ATOM_ENTRY):
                reledit = [l.get('href', '') for l in e.findall(ATOM_LINK) if l.get('rel', '') == 'edit'] 
                for t in reledit:
                    retval[t] = e 
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
        if not response.has_key('content-encoding'):
            self.report(ShouldSupportCompression("No Content-Encoding: header was sent with the response indicating that a compressed entity body was not returned."))

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
        tree = cElementTree.fromstring(content)
        for coll in tree.findall(".//" + APP_COLL):
            coll_type = [t for t in coll.findall(APP_MEMBER_TYPE) if t.text == "entry"] 
            if coll_type:
                test = EntryCollectionTests(coll.get('href'), self.http)
                test.run()
                self.reports.extend(test.reports)

def format(r):
    return """----------------------------------------
     %s: %s
     Context: %s

     Details: %s

""" % (r.__class__.__name__, r.text, r.context, r.extra)

def print_report(reports, reportclass):
    matching = [r for r in reports if isinstance(r, reportclass)]
    if matching:
        print "\n".join([format(r) for r in matching])
    else:
        print "  No problems found."


def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "name=", "password="])
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
