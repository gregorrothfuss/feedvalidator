"""$Id$"""

__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"
__license__ = "Python"

from base import validatorBase
from validators import *

#
# Atom link element
#
class link(nonblank,xmlbase,iso639,nonhtml,positiveInteger,nonblank):
  validRelations = ['alternate', 'enclosure', 'related', 'self', 'via',
    "previous", "next", "first", "last", "current", "payment"]
    # http://www.imc.org/atom-protocol/mail-archive/msg04095.html

  def getExpectedAttrNames(self):
    return [(None, u'type'), (None, u'title'), (None, u'rel'), (None, u'href'), (None, u'length'), (None, u'hreflang'), (u'http://www.w3.org/1999/02/22-rdf-syntax-ns#', u'type'), (u'http://www.w3.org/1999/02/22-rdf-syntax-ns#', u'resource')]
	      
  def validate(self):
    self.type = ""
    self.rel = "alternate"
    self.hreflang = ""
    self.title = ""

    if self.attrs.has_key((None, "rel")):
      self.value = self.rel = self.attrs.getValue((None, "rel"))
      if self.rel in self.validRelations: 
        self.log(ValidAtomLinkRel({"parent":self.parent.name, "element":self.name, "attr":"rel", "value":self.rel}))
      elif rfc2396_full.rfc2396_re.match(self.rel.encode('idna')):
        self.log(ValidAtomLinkRel({"parent":self.parent.name, "element":self.name, "attr":"rel", "value":self.rel}))
      else:
        self.log(UnregisteredAtomLinkRel({"parent":self.parent.name, "element":self.name, "attr":"rel", "value":self.rel}))
      nonblank.validate(self, errorClass=AttrNotBlank, extraParams={"attr": "rel"})

    if self.attrs.has_key((None, "type")):
      self.value = self.type = self.attrs.getValue((None, "type"))
      if not mime_re.match(self.type):
        self.log(InvalidMIMEType({"parent":self.parent.name, "element":self.name, "attr":"type", "value":self.type}))
      elif self.rel == "self" and self.type not in ["application/atom+xml", "application/rss+xml", "application/rdf+xml"]:
        self.log(SelfNotAtom({"parent":self.parent.name, "element":self.name, "attr":"type", "value":self.type}))
      else:
        self.log(ValidMIMEAttribute({"parent":self.parent.name, "element":self.name, "attr":"type", "value":self.type}))

    if self.attrs.has_key((None, "title")):
      self.log(ValidTitle({"parent":self.parent.name, "element":self.name, "attr":"title"}))
      self.value = self.title = self.attrs.getValue((None, "title"))
      nonblank.validate(self, errorClass=AttrNotBlank, extraParams={"attr": "title"})
      nonhtml.validate(self)

    if self.attrs.has_key((None, "length")):
      self.value = self.hreflang = self.attrs.getValue((None, "length"))
      positiveInteger.validate(self)
      nonblank.validate(self)

    if self.attrs.has_key((None, "hreflang")):
      self.value = self.hreflang = self.attrs.getValue((None, "hreflang"))
      iso639.validate(self)

    if self.attrs.has_key((None, "href")):
      self.value = self.attrs.getValue((None, "href"))
      xmlbase.validate(self, extraParams={"attr": "href"})

      if self.rel == "self" and self.parent.name == "feed":
        from urlparse import urljoin
        if urljoin(self.xmlBase,self.value) not in self.dispatcher.selfURIs:
          if urljoin(self.xmlBase,self.value).split('#')[0] != self.xmlBase.split('#')[0]:
            self.log(SelfDoesntMatchLocation({"parent":self.parent.name, "element":self.name}))

    else:
      self.log(MissingHref({"parent":self.parent.name, "element":self.name, "attr":"href"}))

  def startElementNS(self, name, qname, attrs):
    self.push(eater(), name, attrs)

  def characters(self, text):
    if text.strip():
      self.log(AtomLinkNotEmpty({"parent":self.parent.name, "element":self.name}))
