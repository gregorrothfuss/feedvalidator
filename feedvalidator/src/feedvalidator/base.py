"""$Id$"""

__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"
__license__ = "Python"

from xml.sax.handler import ContentHandler
from xml.sax.xmlreader import Locator

# references:
# http://web.resource.org/rss/1.0/modules/standard.html
# http://web.resource.org/rss/1.0/modules/proposed.html
# http://dmoz.org/Reference/Libraries/Library_and_Information_Science/Technical_Services/Cataloguing/Metadata/RDF/Applications/RSS/Specifications/RSS1.0_Modules/
namespaces = {
  "http://webns.net/mvcb/":                         "admin",
  "http://purl.org/rss/1.0/modules/aggregation/":   "ag",
  "http://purl.org/rss/1.0/modules/annotate/":      "annotate",
  "http://media.tangent.org/rss/1.0/":              "audio",
  "http://backend.userland.com/blogChannelModule":  "blogChannel",
  "http://web.resource.org/cc/":                    "cc",
  "http://backend.userland.com/creativeCommonsRssModule": "creativeCommons",
  "http://purl.org/rss/1.0/modules/company":        "company",
  "http://purl.org/rss/1.0/modules/content/":       "content",
  "http://my.theinfo.org/changed/1.0/rss/":         "cp",
  "http://purl.org/dc/elements/1.1/":               "dc",
  "http://purl.org/dc/terms/":                      "dcterms",
  "http://purl.org/rss/1.0/modules/email/":         "email",
  "http://purl.org/rss/1.0/modules/event/":         "ev",
  "http://purl.org/rss/1.0/modules/image/":         "image",
  "http://xmlns.com/foaf/0.1/":                     "foaf",
  "http://purl.org/rss/1.0/modules/link/":          "l",
  "http://www.w3.org/1999/02/22-rdf-syntax-ns#":    "rdf",
  "http://www.w3.org/2000/01/rdf-schema#":          "rdfs",
  "http://purl.org/rss/1.0/modules/reference/":     "ref",
  "http://purl.org/rss/1.0/modules/richequiv/":     "reqv",
  "http://purl.org/rss/1.0/modules/rss091#":        "rss091",
  "http://purl.org/rss/1.0/modules/search/":        "search",
  "http://purl.org/rss/1.0/modules/slash/":         "slash",
  "http://purl.org/rss/1.0/modules/servicestatus/": "ss",
  "http://hacks.benhammersley.com/rss/streaming/":  "str",
  "http://purl.org/rss/1.0/modules/subscription/":  "sub",
  "http://purl.org/rss/1.0/modules/syndication/":   "sy",
  "http://purl.org/rss/1.0/modules/taxonomy/":      "taxo",
  "http://purl.org/rss/1.0/modules/threading/":     "thr",
  "http://purl.org/rss/1.0/modules/wiki/":          "wiki",
  "http://schemas.xmlsoap.org/soap/envelope/":      "soap",
  "http://purl.org/atom/ns#":                       "atom",
  "http://www.w3.org/1999/xhtml":                   "xhtml",
}

#
# From the SAX parser's point of view, this class is the one responsible for
# handling SAX events.  In actuality, all this class does is maintain a
# pushdown stack of the *real* content handlers, and delegates sax events
# to the current one.
#
class SAXDispatcher(ContentHandler):

  firstOccurrenceOnly = 0

  def __init__(self):
    from root import root
    ContentHandler.__init__(self)
    self.lastKnownLine = 1
    self.lastKnownColumn = 0
    self.loggedEvents = []
    self.feedType = 0
    self.handler_stack=[[root(self)]]

  def setDocumentLocator(self, locator):
    self.locator = locator
    ContentHandler.setDocumentLocator(self, self.locator)

  def setFirstOccurrenceOnly(self, firstOccurrenceOnly=1):
    self.firstOccurrenceOnly = firstOccurrenceOnly

  def startPrefixMapping(self, prefix, uri):
    if namespaces.has_key(uri):
      if not namespaces[uri] == prefix and prefix:
        from logging import NonstdPrefix
        self.log(NonstdPrefix({'preferred':namespaces[uri], 'ns':uri}))
    elif prefix in namespaces.values():
      from logging import ReservedPrefix
      preferredURI = [key for key, value in namespaces.items() if value == prefix][0]
      self.log(ReservedPrefix({'prefix':prefix, 'ns':preferredURI}))

  def startElementNS(self, name, qname, attrs):
    self.lastKnownLine = self.locator.getLineNumber()
    self.lastKnownColumn = self.locator.getColumnNumber()
    qname, name = name
    for handler in iter(self.handler_stack[-1]):
      handler.startElementNS(name, qname, attrs)

  def resolveEntity(self, publicId, systemId):
    if (publicId=='-//Netscape Communications//DTD RSS 0.91//EN' and
        systemId=='http://my.netscape.com/publish/formats/rss-0.91.dtd'):
      from logging import ValidDoctype
      self.log(ValidDoctype({}))
    else:
      from logging import ContainsSystemEntity
      self.lastKnownLine = self.locator.getLineNumber()
      self.lastKnownColumn = self.locator.getColumnNumber()
      self.log(ContainsSystemEntity({}))
    from StringIO import StringIO
    return StringIO()

  def characters(self, string):
    self.lastKnownLine = self.locator.getLineNumber()
    self.lastKnownColumn = self.locator.getColumnNumber()
    for handler in iter(self.handler_stack[-1]):
      handler.characters(string)

  def endElementNS(self, name, qname):
    self.lastKnownLine = self.locator.getLineNumber()
    self.lastKnownColumn = self.locator.getColumnNumber()
    qname, name = name
    for handler in iter(self.handler_stack[-1]):
      handler.endElementNS(name, qname)
    del self.handler_stack[-1]

  def push(self, handler):
    try:
      iter(handler)
    except:
      handler = [handler]
    self.handler_stack.append(handler)

  def log(self, event):
    def findDuplicate(self, event):
      duplicates = [e for e in self.loggedEvents if e.__class__ == event.__class__]
      for dup in duplicates:
        for k, v in event.params.items():
          if k != 'value':
            if not k in dup.params or dup.params[k] != v: break
	else:
         return dup
          
    if event.params.has_key('element') and event.params['element']:
      event.params['element'] = event.params['element'].replace('_', ':')
    if self.firstOccurrenceOnly:
      dup = findDuplicate(self, event)
      if dup:
        dup.params['msgcount'] = dup.params['msgcount'] + 1
        return
      event.params['msgcount'] = 1
    try:
      line = self.locator.getLineNumber()
      backupline = self.lastKnownLine
      column = self.locator.getColumnNumber()
      backupcolumn = self.lastKnownColumn
    except AttributeError:
      line = backupline = column = backupcolumn = 1
    event.params['line'] = line
    event.params['backupline'] = backupline
    event.params['column'] = column
    event.params['backupcolumn'] = backupcolumn
    self.loggedEvents.append(event)

  def error(self, exception):
    from logging import SAXError
    self.log(SAXError({'exception':str(exception)}))
    raise exception
  fatalError=error
  warning=error

  def setFeedType(self, feedType):
    self.feedType = feedType

  def getFeedType(self):
    return self.feedType
    
#
# This base class for content handlers keeps track of such administrative
# details as the parent of the current element, and delegating both log
# and push events back up the stack.  It will also concatenate up all of
# the SAX events associated with character data into a value, handing such
# things as CDATA and entities.
#
# Subclasses are expected to declare "do_name" methods for every
# element that they support.  These methods are expected to return the
# appropriate handler for the element.
#
# The name of the element and the names of the children processed so
# far are also maintained.
#
# Hooks are also provided for subclasses to do "prevalidation" and
# "validation".
#
class validatorBase(ContentHandler):
  defaultNamespaces = []
  
  def __init__(self):
    ContentHandler.__init__(self)
    self.value = ""
    self.attrs = None
    self.children = []
    self.isValid = 1
    self.name = None

  def unknown_starttag(self, name, qname, attrs):
    from validators import eater
    return eater()

  def startElementNS(self, name, qname, attrs):
    from validators import eater
    if qname in self.defaultNamespaces: qname=None
    hasNS = (qname<>None)

    if namespaces.has_key(qname):
      qname, name = None, namespaces[qname] + "_" + name

    # ensure all attribute namespaces are properly defined
    for (namespace,attr) in attrs.keys():
      if ':' in attr and not namespace:
        from logging import MissingNamespace
        self.log(MissingNamespace({"parent":self.name, "element":attr}))

    if qname:
      handler = self.unknown_starttag(name, qname, attrs)
    else:
      try:
        handler = getattr(self, "do_" + name)()
      except AttributeError:
        if name.find(':') != -1:
          from logging import MissingNamespace
          self.log(MissingNamespace({"parent":self.name, "element":name}))
          handler = eater()
        elif not hasNS:
          from logging import UndefinedElement
          self.log(UndefinedElement({"parent":self.name, "element":name}))
          handler = eater()
	else:
          handler = self.unknown_starttag(name, qname, attrs)

    try:
      iter(handler)
    except TypeError:
      handler = [handler]
    for aHandler in iter(handler):
      aHandler.parent = self
      aHandler.dispatcher = self.dispatcher
      aHandler.value = ""
      aHandler.name = name
      aHandler.attrs = attrs
      aHandler.prevalidate()

     # MAP - always append name, even if already exists (we need this to
     # check for too many hour elements in skipHours, and it doesn't
     # hurt anything else)
    self.children.append(name)
    self.push(handler)

  def endElementNS(self, name, qname):
    self.value=self.value.strip()
    self.validate()
    if self.isValid and self.name: 
      from validators import ValidElement
      self.log(ValidElement({"parent":self.parent.name, "element":name}))

  def characters(self, string):
    for c in string:
      if 0x80 <= ord(c) <= 0x9F:
        from validators import BadCharacters
        self.log(BadCharacters({"parent":self.parent.name, "element":self.name}))

    self.value = self.value + string

  def log(self, event):
    self.dispatcher.log(event)
    self.isValid = 0

  def setFeedType(self, feedType):
    self.dispatcher.setFeedType(feedType)
    
  def push(self, handler):
    self.dispatcher.push(handler)

  def leaf(self):
    from validators import text
    return text()

  def prevalidate(self):
    pass
  
  def validate(self):
    pass

__history__ = """
$Log$
Revision 1.4  2004/02/16 01:41:05  rubys
Fix for 893709: Detected an unknown type feed reported by Les Orchard

Revision 1.3  2004/02/07 14:23:19  rubys
Fix for bug 892178: must reject xml 1.1

Revision 1.2  2004/02/06 18:43:18  rubys
Apply patch 886675 from Joseph Walton:
"Warn about windows-1252 presented as ISO-8859-1"

Revision 1.1.1.1  2004/02/03 17:33:15  rubys
Initial import.

Revision 1.41  2003/12/11 16:32:08  f8dy
fixed id tags in header

Revision 1.40  2003/08/23 23:25:14  rubys
Allow unprefixed elements (like xhtml) to pass through without warning

Revision 1.39  2003/08/23 21:01:00  rubys
Validate that content, content:encoded, and xhtml:body are safe

Revision 1.38  2003/08/12 02:02:26  rubys
Detect unknown elements even if they have underscores.  Reported by
Brent Simmons.

Revision 1.37  2003/08/09 18:18:03  rubys
Permit NetScape's 0.91 DOCTYPE

Revision 1.36  2003/08/05 05:32:35  f8dy
0.2 snapshot - change version number and default namespace

Revision 1.35  2003/08/04 00:54:35  rubys
Log every valid element (for better self validation in test cases)

Revision 1.34  2003/07/28 21:56:52  rubys
Check attributes for valid namespaces

Revision 1.33  2003/07/09 16:24:30  f8dy
added global feed type support

Revision 1.32  2003/07/07 00:54:00  rubys
Rough in some pie/echo support

Revision 1.31  2003/06/26 18:03:04  f8dy
add workaround for case where SAX throws UnicodeError but locator.getLineNumber() is screwy

Revision 1.30  2003/04/07 19:49:22  rubys
Handle ignorable whitespace in elements such as comments

Revision 1.29  2003/03/01 13:53:22  rubys
Improved duplicate checking

Revision 1.28  2002/12/20 13:26:00  rubys
CreativeCommons support

Revision 1.27  2002/10/31 00:52:21  rubys
Convert from regular expressions to EntityResolver for detecting
system entity references

Revision 1.26  2002/10/30 23:03:01  f8dy
security fix: external (SYSTEM) entities

Revision 1.25  2002/10/24 14:47:33  f8dy
decoupled "no duplicates" check from individual validator classes,
allow handlers to return multiple validator classes

Revision 1.24  2002/10/24 13:55:58  f8dy
added rdfs namespace

Revision 1.23  2002/10/22 19:20:54  f8dy
passed testcase for foaf:person within dc:creator (or any other text
element)

Revision 1.22  2002/10/22 12:57:35  f8dy
fixed bug setting parameters for ReservedPrefix error

Revision 1.21  2002/10/18 20:31:28  f8dy
fixed namespace for mod_aggregation

Revision 1.20  2002/10/18 13:06:57  f8dy
added licensing information

"""