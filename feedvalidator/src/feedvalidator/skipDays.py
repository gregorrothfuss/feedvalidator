"""$Id$"""

__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"
__license__ = "Python"

from base import validatorBase
from logging import *

#
# skipDays element
#
class skipDays(validatorBase):
  def prevalidate(self):
    self.log(UseSyndicationModule({"core":self.name, "ext":"syndication module"}))
    
  def validate(self):
    if "day" not in self.children:
      self.log(MissingElement({"parent":self.name, "element":"day"}))
    if len(self.children) > 7:
      self.log(EightDaysAWeek({}))

  def do_day(self):
    return day()

class day(validatorBase):
  def validate(self):
    if self.value not in ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'):
      self.log(InvalidDay({"parent":self.parent.name, "element":self.name, "value":self.value}))
    else:
      self.log(ValidDay({"parent":self.parent.name, "element":self.name, "value":self.value}))

__history__ = """
$Log$
Revision 1.1  2004/02/03 17:33:16  rubys
Initial revision

Revision 1.5  2003/12/11 16:32:08  f8dy
fixed id tags in header

Revision 1.4  2003/07/30 01:54:59  f8dy
tighten test cases, add explicit params

Revision 1.3  2003/07/29 20:57:39  f8dy
tightened up test cases, check for parent element, explicitly test for success

Revision 1.2  2002/10/18 13:06:57  f8dy
added licensing information

"""
