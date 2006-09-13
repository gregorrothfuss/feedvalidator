SERVICE1 = """<?xml version="1.0" encoding='utf-8'?>
<service xmlns="http://purl.org/atom/app#">
  <workspace title="Main Site" > 
    <collection 
      title="My Blog Entries" 
      href="http://example.org/reilly/main" />
    <collection 
      title="Pictures" 
      href="http://example.org/reilly/pic" >
      <accept>image/*</accept>
    </collection>
  </workspace>
  <workspace title="Side Bar Blog">
    <collection title="Remaindered Links" 
      href="http://example.org/reilly/list" />
  </workspace>
</service>"""


ENTRY1 = """<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom">
  <title type="text">third</title>
  <id>http://bitworking.org/foo/app/main/third</id>
  <author>
     <name>Joe Gregorio</name>
  </author>
  <updated>2006-08-04T15:52:00-05:00</updated>
  <summary type="html">&lt;p>not much&lt;/p></summary>
  <content type="xhtml">
    <div xmlns="http://www.w3.org/1999/xhtml"><p>Some stuff</p>

      <p><i>[Update: The Atom draft is finished.]</i></p>
      outside a child element.

      <p>More stuff.</p></div>
  </content>
</entry>
"""

import apptools
import unittest
from elementtree.ElementTree import fromstring, tostring
class parseAtomTest(unittest.TestCase):

    def testSimple(self):
        res = apptools.parse_atom_entry(fromstring(ENTRY1))
        self.assertEqual(res['title'], "third")
        self.assertEqual(res['summary'], "<p>not much</p>")

        self.assertEqual(res['content'][:18], """<html:p xmlns:html""")

class parseServiceTest(unittest.TestCase):

    def testSimple(self):
        res = apptools.parse_service(SERVICE1)
        self.assertEqual(3, len(res))
        self.assertEqual("Main Site", res[0]['workspace'])
        self.assertEqual("My Blog Entries", res[0]['title'])
        self.assertEqual("http://example.org/reilly/main", res[0]['href'])
        self.assertEqual("", res[0]['accept'])

        self.assertEqual("Main Site", res[1]['workspace'])
        self.assertEqual("Pictures", res[1]['title'])
        self.assertEqual("http://example.org/reilly/pic", res[1]['href'])
        self.assertEqual("image/*", res[1]['accept'])

        self.assertEqual("Side Bar Blog", res[2]['workspace'])
        self.assertEqual("Remaindered Links", res[2]['title'])
        self.assertEqual("http://example.org/reilly/list", res[2]['href'])
        self.assertEqual("", res[2]['accept'])

class unparseServiceTest(unittest.TestCase):

    def testEntry(self):
        element = fromstring(ENTRY1)
        d = apptools.parse_atom_entry(element)
        d['content'] = "This is text"
        d['content__type'] = 'text'
        d['summary'] = "<p>This is text</p>"
        d['summary__type'] = 'xhtml'
        apptools.unparse_atom_entry(element, d)
        d = apptools.parse_atom_entry(element)
        self.assertEqual("This is text", d['content'])
        self.assertEqual('<html:p xmlns:html="http://www.w3.org/1999/xhtml">This is text</html:p>', d['summary'])

class wrapTest(unittest.TestCase):

    def testWrap(self):
        self.assertEqual("This\nis", apptools.wrap("This\nis", 80))
        self.assertEqual("This is ", apptools.wrap("This is", 80))
        self.assertEqual("This\nis ", apptools.wrap("This is", 3))
        self.assertEqual("This\nis\n", apptools.wrap("This is\n", 3))

unittest.main()

