"""$Id$"""

__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"
__license__ = "Python"

from base import validatorBase
from logging import *
from validators import rdfAbout, noduplicates
from root import rss11_namespace as rss11_ns

rdfNS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

#
# rdf:RDF element.  The valid children include "channel", "item", "textinput", "image"
#
class rdf(validatorBase,object):

  def do_rss090_channel(self):
    from channel import channel
    self.defaultNamespaces.append("http://my.netscape.com/rdf/simple/0.9/")
    return channel(), noduplicates()

  def do_channel(self):
    from channel import channel
    return rdfAbout(), channel(), noduplicates()

  def do_item(self):
    from item import item
    if "http://my.netscape.com/rdf/simple/0.9/" in self.defaultNamespaces:
      return item()
    else:
      return rdfAbout(), item()

  def do_textinput(self):
    from textInput import textInput
    return textInput()

  def do_image(self):
    from image import image
    return image()
  
  def prevalidate(self):
    self.setFeedType(TYPE_RSS1)
    
  def validate(self):
    if not "channel" in self.children and not "rss090_channel" in self.children:
      self.log(MissingChannel({"parent":self.name, "element":"channel"}))

#
# This class is intended to validate that the element is syntatically valid
# RDF, but doesn't otherwise process the element.
#
class rdfProperty(validatorBase):
  def __init__(self, parent, name, qname, attrs):
    validatorBase.__init__(self)
    self.name=name
    self.parent=parent
    self.dispatcher=parent.dispatcher
    self.attrs=attrs

    # ensure no rss11 children
    if qname==rss11_ns:
      from logging import UndefinedElement
      self.log(UndefinedElement({"parent":parent.name, "element":name}))

    # no duplicate rdf:abouts
    if attrs.has_key((rdfNS,"about")):
      about = attrs[(rdfNS,"about")]
      if not "abouts" in self.dispatcher.__dict__:
        self.dispatcher.__dict__["abouts"] = []
      if about in self.dispatcher.__dict__["abouts"]:
        self.log(DuplicateValue({"parent":parent.name, "element":"rdf:about", "value":about}))
      else:
        self.dispatcher.__dict__["abouts"].append(about)

  def getExpectedAttrNames(self):
    if not self.attrs: return self.attrs
    attrs = []
    for ns,n in self.attrs.keys():
      if ns==rdfNS and n=="resource": continue
      if ns==rss11_ns: continue
      attrs.append((ns,n))   
    return attrs

  def startElementNS(self, name, qname, attrs):
    # ensure element is "namespace well formed"
    if name.find(':') != -1:
      from logging import MissingNamespace
      self.log(MissingNamespace({"parent":self.name, "element":name}))

    # ensure all attribute namespaces are properly defined
    for (namespace,attr) in attrs.keys():
      if ':' in attr and not namespace:
        from logging import MissingNamespace
        self.log(MissingNamespace({"parent":self.name, "element":attr}))

    # no mixed content
    if self.value.strip():
      self.log(InvalidRDF({"parent":self.name, "element":name}))

    # eat children
    self.push(rdfProperty(self, name, qname, attrs))

__history__ = """
$Log$
Revision 1.5  2005/01/22 23:45:36  rubys
pass last rss11 test case (neg-ext-notrdf.xml)

Revision 1.4  2005/01/21 13:52:54  rubys
Better fix for Mozilla bug 279202

Revision 1.2  2004/06/28 23:34:46  rubys
Support RSS 0.90

Revision 1.1.1.1  2004/02/03 17:33:16  rubys
Initial import.

Revision 1.10  2003/12/11 16:32:08  f8dy
fixed id tags in header

Revision 1.9  2003/10/16 15:54:41  rubys
Detect duplicate channels

Revision 1.8  2003/08/12 00:26:30  rubys
Misleading error message if a channel is missing in an RSS 1.0 feed

Revision 1.7  2003/08/10 13:49:14  rubys
Add support for chanel and item level rdf:about.  Ensure that http and
ftp URLs have exactly two slashes after the scheme.

Revision 1.6  2003/07/29 19:38:07  f8dy
changed test cases to explicitly test for success (rather than the absence of failure)

Revision 1.5  2003/07/09 16:24:30  f8dy
added global feed type support

Revision 1.4  2002/10/22 14:11:36  f8dy
initial attempts to handle RSS 1.0 vs. 2.0 images and textinputs; test
cases still fail

Revision 1.3  2002/10/22 13:16:03  f8dy
passed lowercase textinput test

Revision 1.2  2002/10/18 13:06:57  f8dy
added licensing information

"""
