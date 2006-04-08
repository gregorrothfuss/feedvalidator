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
import time

import feedvalidator
from feedvalidator import compatibility
from gettext import gettext as _

PACES = {'PaperTrail': False}

def usage(option=""):
    print """Usage: appclienttest [OPTION] IntrospectionURI

  -h, --help            Display this help message then exit.
      --name=<name>     User name to use for authentication.
      --password=<pw>   Password to use for authentication. 
      --debug=<n>       Print debugging information for n > 0.

      --<PaceName>      Where PaceName is one of [%s]
""" % ", ".join(PACES.keys())
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
        if getattr(self, 'pace'):
            self.extra = self.extra + ("\n   [Pace%s]" % self.pace)

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
    text = _('Atom entries and feeds MUST be valid. [RFC 4287]')

class MustRejectNonWellFormedAtom(Warning):
    text = _('A server SHOULD reject non-wellformed content. [XML 1.0 Section 5.1 Validating and Non-Validating Processors]')

class InternalErrorEncountered(Error):
    text = _('Internal error encountered. This error can occur if the site returned non-welllformed XML.')

class EntryCreationMustReturn201(Warning):
    text = _('When an entry is successfully created the server SHOULD return an HTTP status code of 201. [RFC 2616 Section 9.5 POST]')

class EntryCreationMustReturnLocationHeader(Error):
    text = _('When an entry is successfully created the server MUST return a Location: HTTP header. [APP-08 Section 8.1 Creating Resource with POST]')

class EntryCreationMustBeReflectedInFeed(Error):
    text = _('When an entry is successfully created it must be added to the associated feed. [APP-08 Section 8.1 Creating Resources.]')

class EntryDeletionFailed(Error):
    text = _('The status returned does not reflect a successful deletion.')

class EntryDeletionMustBeReflectedInFeed(Error):
    text = _('When an entry is successfully deleted, the Member URI MUST be removed from the collection. ')
    pace = 'PaperTrail'

class LocationHeaderMustMatchLinkRelEdit(Error):
    text = _('The link/@rel="edit" URI must match the URI returned via the Location: HTTP header during creation.') 
    pace = 'PaperTrail'

class GetFailedOnMemberResource(Error):
    text = _('Could not dereference the Member URI.')

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
        if r.pace and not PACES[r.pace]:
            pass
        else:
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

    def setUp(self):
        time.sleep(1)

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
        edituri = absolutize(self.entry_coll_uri, response['location'])
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
        edituri = absolutize(self.entry_coll_uri, response['location'])
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
        edituri = absolutize(self.entry_coll_uri, response['location'])
        (response, content) = self.http.request(edituri, "DELETE")
        if response.status >= 400:
            self.report(EntryDeletionFailed("HTTP Status %d" % response.status))

    def testNonWellFormedEntry(self):
        """ POST an invalid Atom Entry 
        """
        (response, content) = self.http.request(self.entry_coll_uri, "POST", body=INVALID_ENTRY, headers={'Content-Type': 'application/atom+xml', 'Accept': '*/*'})
        if response.status < 400:
            self.report(MustRejectNonWellFormedAtom("Actually returned an HTTP status code %d" % response.status))

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
        edituri = absolutize(self.entry_coll_uri, response['location'])

        time.sleep(2)
        (response, content) = self.http.request(self.entry_coll_uri, "POST", body=CONTENT_WITH_SRC, headers={'Content-Type': 'application/atom+xml', 'Accept': '*/*'})
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
        tree = cElementTree.fromstring(content)
        for coll in tree.findall(".//" + APP_COLL):
            coll_type = [t for t in coll.findall(APP_MEMBER_TYPE) if t.text == "entry"] 
            if coll_type:
                test = EntryCollectionTests(coll.get('href'), self.http)
                test.run()
                self.reports.extend(test.reports)

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
    options.extend(PACES.keys())
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", options )
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    name = password = None
    for o, a in opts:
        if o.split("--")[-1] in PACES:
            PACES[o.split("--")[-1]] = True
        if o == "--name":
            name = a
        if o == "--password":
            password = a
        if o == "--debug":
            print "debug level"
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
    enforced_paces = [name for name in PACES.keys() if PACES[name]]
    for target_uri in args:
        print "Atom Client Tests"
        print "-----------------"
        print ""
        print "Testing the service at <%s>" % target_uri
        print ""
        if enforced_paces:
            print "The following Paces are being enforced <%s>" % ", ".join(enforced_paces)
        else:
            print "No Paces are being enforced."
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
