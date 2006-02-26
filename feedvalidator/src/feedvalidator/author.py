"""$Id$"""

__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"
__license__ = "Python"

from base import validatorBase
from validators import *

#
# author element.
#
class author(validatorBase):
  def getExpectedAttrNames(self):
    return [(u'http://www.w3.org/1999/02/22-rdf-syntax-ns#', u'parseType')]

  def validate(self):
    if not "name" in self.children and not "atom_name" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"name"}))

  def do_name(self):
    return nonhtml(), nonemail(), nonblank(), noduplicates()

  def do_email(self):
    return addr_spec(), noduplicates()

  def do_uri(self):
    return nonblank(), rfc3987(), nows(), noduplicates()

  def do_foaf_workplaceHomepage(self):
    return eater()

  def do_foaf_homepage(self):
    return eater()

  def do_foaf_weblog(self):
    return eater()
  
  # RSS/Atom support
  do_atom_name = do_name
  do_atom_email = do_email
  do_atom_uri = do_uri

__history__ = """
$Log$
Revision 1.10  2006/02/26 01:56:59  rubys
IRI support

Revision 1.9  2006/01/02 01:26:18  rubys
Remove vestigial Atom 0.3 support

Revision 1.8  2005/10/12 08:57:44  rubys
Issue warnings on names containing email addresses.

Revision 1.7  2005/08/20 03:58:58  rubys
white-space + xml:base

Revision 1.6  2005/08/08 00:52:04  rubys
email MUST conform to the "addr-spec" production

Revision 1.5  2005/07/28 09:54:14  rubys
RDF extensions

Revision 1.4  2005/07/26 18:18:19  rubys
Update RSS+Atom support

Revision 1.3  2005/07/15 11:17:23  rubys
Baby steps towards Atom 1.0 support

Revision 1.2  2004/02/20 15:35:46  rubys
Feature 900555: RSS+Atom support

Revision 1.1.1.1  2004/02/03 17:33:14  rubys
Initial import.

Revision 1.5  2003/12/11 16:32:08  f8dy
fixed id tags in header

Revision 1.4  2003/09/01 21:27:48  f8dy
remove weblog, homepage

Revision 1.3  2003/08/03 18:46:04  rubys
support author(url,email) and feed(author,copyright,generator)

Revision 1.2  2003/07/09 16:24:30  f8dy
added global feed type support

Revision 1.1  2003/07/07 00:54:00  rubys
Rough in some pie/echo support

"""
