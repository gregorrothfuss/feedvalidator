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

import feedvalidator
from feedvalidator import compatibility
from gettext import gettext as _

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

class ShouldRejectUnknownContentTypes(Warning):
    text = _('A server should reject content if not given a content-type.')

class MustRejectNonWellFormedAtom(Warning):
    text = _('A server MUST reject non-wellformed content.')

class InternalErrorEncountered(Error):
    text = _('Internal error encountered. It could be non-welllformed XML.')

class EntryCreationMustReturn201(Error):
    text = _('When an entry is successfully created the server MUST return an HTTP status code of 201.')

class EntryCreationMustReturnLocationHeader(Error):
    text = _('When an entry is successfully created the server MUST return a Link: HTTP header.')

class EntryCreationMustBeReflectedInFeed(Error):
    text = _('When an entry is successfully created it must be added to the associated feed.')

class EntryDeletionMustReturn200(Error):
    text = _('When an entry is successfully deleted the status code MUST be 200.')

class EntryDeletionMustBeReflectedInFeed(Error):
    text = _('When an entry is successfully deleted it must be removed from the associated feed.')

class LocationHeaderMustMatchLinkRelEdit(Error):
    text = _('The link/@rel="edit" URI must match the URI returned via the Link: HTTP header during creation.')

class LinkRelEditResourceInvalid(Error):
    text = _('The link/@rel="edit" URI must be dereferencable.')

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
    
h = httplib2.Http(".cache")


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
    def __init__(self, entry_coll_uri):
        Test.__init__(self)
        self.entry_coll_uri = entry_coll_uri


    def enumerate_collection(self):
        relnext = [self.entry_coll_uri]
        retval = {} 
        while relnext:
            uri = absolutize(self.entry_coll_uri, relnext[0])
            (response, content) = h.request(uri, "GET", headers = {"Cache-Control": "max-age=0"})
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
        (response, content) = h.request(self.entry_coll_uri)
        if not response.has_key('etag'):
            self.report(ShouldSupportCacheValidators("No ETag: header was sent with the response."))
            if not response.has_key('last-modified'):
                self.report(ShouldSupportCacheValidators("No Last-Modified: header was sent with the response."))
        if not response.has_key('content-encoding'):
            self.report(ShouldSupportCompression("No Content-Encoding: header was sent with the response indicating that a compressed entity body was not returned."))

    def testMissingContentType(self):
        """POST an entry with no Content-Type header.
It MUST fail since entry collections 
only accept Atom Entries.
"""
        toc = self.enumerate_collection()
        startnum = len(toc)
        (response, content) = h.request(self.entry_coll_uri, "POST", body=CONTENT_WITH_SRC)
        toc = self.enumerate_collection()
        if response.status < 400:
            self.report(ShouldRejectUnknownContentTypes("Expected failure but instead received a %d status code." % response.status))
            return
        # Make sure an entry was not added 
        if startnum < len(toc):
            self.report(ShouldRejectUnknownContentTypes("The size of the table of contents changed from %d to %d." % (startnum, len(toc))))

    def testContentWithSrc(self):
        """POST a good Atom Entry with a content/@src
        attribute set and with the right mime-type.
        Ensure that the entry is added to the collection.
        """
        toc = self.enumerate_collection()
        startnum = len(toc)
        # Add a new entry
        (response, content) = h.request(self.entry_coll_uri, "POST", body=CONTENT_WITH_SRC, headers={'Content-Type': 'application/atom+xml', 'Accept': '*/*'})

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
        edituri = absolutize(self.entry_coll_uri, response['location'])
        if edituri not in toc:
            self.report(LocationHeaderMustMatchLinkRelEdit("The Location: header value %s can't be found in %s" % (response['location'], str(toc))))

        (response, content) = h.request(edituri, "GET", headers = {"Cache-Control": "max-age=0"})
        if response.status != 200:
            self.report(LinkRelEditResourceInvalid("Expected an HTTP status code of 200 but instead received %d" % response.status))
        validate_atom(self, content, edituri)

        # Cleanup
        (response, content) = h.request(edituri, "DELETE")
        if response.status != 200:
            self.report(EntryDeletionMustReturn200("Expected an HTTP status code of 200 on sending a DELETE but instead received %d" % response.status))
        toc = self.enumerate_collection()
        if startnum != len(toc):
            self.report(EntryDeletionMustBeReflectedInFeed("Number of entries went from %d before to %d entries after the entry was deleted." % (startnum, len(toc))))
        if edituri in toc:
            self.report(EntryDeletionMustBeReflectedInFeed("The URI for the entry just deleted <%s> must not appear in the feed after the entry is deleted." % edituri))

    def testContentWithBase64Content(self):
        """ POST a good Atom Entry with an entry 
        whose atom:content is a base64 encoded png.
        """
        (response, content) = h.request(self.entry_coll_uri, "POST", body=CONTENT_WITH_OTHER, headers={'Content-Type': 'application/atom+xml', 'Accept': '*/*'})
        if response.status != 201:
            self.report(EntryCreationMustReturn201("Actually returned an HTTP status code %d" % response.status))
        edituri = absolutize(self.entry_coll_uri, response['location'])
        (response, content) = h.request(edituri, "DELETE")
        if response.status != 200:
            self.report(EntryDeletionMustReturn200("Expected an HTTP status code of 200 on sending a DELETE but instead received %d" % response.status))

    def testMixedTextConstructs(self):
        """ POST a good Atom Entry with an entry 
        whose Text Constructs contain a mix of types.
        """
        (response, content) = h.request(self.entry_coll_uri, "POST", body=MIXED_TEXT_TYPES, headers={'Content-Type': 'application/atom+xml', 'Accept': '*/*'})
        if response.status != 201:
            self.report(EntryCreationMustReturn201("Actually returned an HTTP status code %d" % response.status))
        edituri = absolutize(self.entry_coll_uri, response['location'])
        (response, content) = h.request(edituri, "DELETE")
        if response.status != 200:
            self.report(EntryDeletionMustReturn200("Expected an HTTP status code of 200 on sending a DELETE but instead received %d" % response.status))

    def testInvalidEntry(self):
        """ POST an invalid Atom Entry 
        """
        (response, content) = h.request(self.entry_coll_uri, "POST", body=INVALID_ENTRY, headers={'Content-Type': 'application/atom+xml', 'Accept': '*/*'})
        if response.status < 400:
            self.report(MustRejectNonWellFormedAtom("Actually returned an HTTP status code %d" % response.status))


    def testDoubleAddWithSameAtomId(self):
        """POST two Atom entries with the same atom:id 
        to the collection. The response for both MUST be
        201 and two new entries must be created."""
        toc = self.enumerate_collection()
        startnum = len(toc)
        # Add a new entry
        (response, content) = h.request(self.entry_coll_uri, "POST", body=CONTENT_WITH_SRC, headers={'Content-Type': 'application/atom+xml', 'Accept': '*/*'})
        if response.status != 201:
            self.report(EntryCreationMustReturn201("Actually returned an HTTP status code %d" % response.status))
            return
        toc = self.enumerate_collection()
        # Make sure it was added to the collection
        if startnum >= len(toc):
            self.report(EntryCreationMustBeReflectedInFeed("Number of entries went from %d before to %d entries after the entry was created." % (startnum, len(toc))))
            return
        # The location header should match the link/@rel="edit"
        edituri = absolutize(self.entry_coll_uri, response['location'])

        (response, content) = h.request(self.entry_coll_uri, "POST", body=CONTENT_WITH_SRC, headers={'Content-Type': 'application/atom+xml', 'Accept': '*/*'})
        if response.status != 201:
            self.report(EntryCreationMustReturn201("When POSTing a second entry with the same atom:id of an entry we just POSTed the server returned an HTTP status code %d" % response.status))
            return

        toc = self.enumerate_collection()
        # Make sure it was added to the collection
        if startnum+1 >= len(toc):
            self.report(EntryCreationMustBeReflectedInFeed("Number of entries went from %d before to %d entries after the entry was created." % (startnum+1, len(toc))))
        edituri2 = absolutize(self.entry_coll_uri, response['location'])

        if edituri == edituri2:
            self.report(EntryCreationMustReturnLocationHeader("Non unique Location: header value returned in a 201 response. <%s>" % edituri))

        # Cleanup
        (response, content) = h.request(edituri, "DELETE")
        if response.status != 200:
            self.report(EntryDeletionMustReturn200("Expected an HTTP status code of 200 on sending a DELETE but instead received %d" % response.status))
        (response, content) = h.request(edituri2, "DELETE")
        if response.status != 200:
            self.report(EntryDeletionMustReturn200("Expected an HTTP status code of 200 on sending a DELETE but instead received %d" % response.status))

class TestIntrospection(Test):
    def __init__(self, uri):
        Test.__init__(self)
        self.introspection_uri  = uri

    def testEachEntryCollection(self):
        """Run over each entry collection listed
in an Introspection document and
run the Entry collection tests
against it."""
        response, content = h.request(self.introspection_uri)
        tree = cElementTree.fromstring(content)
        for coll in tree.findall(".//" + APP_COLL):
            coll_type = [t for t in coll.findall(APP_MEMBER_TYPE) if t.text == "entry"] 
            if coll_type:
                test = EntryCollectionTests(coll.get('href'))
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

if __name__ == '__main__':
    target_uri = (len(sys.argv) > 1) and sys.argv[1] or INTROSPECTION_URI
    print "Atom Client Tests"
    print "-----------------"
    print ""
    print "Testing the service at <%s>" % target_uri
    print "Running: ",
    test = TestIntrospection(target_uri)
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


