SERVICE1 = """<?xml version="1.0" encoding='utf-8'?>
<service xmlns="http://www.w3.org/2007/app"
         xmlns:atom="http://www.w3.org/2005/Atom"   >
  <workspace>
    <atom:title>Main Site</atom:title>
    <collection
      href="http://example.org/reilly/main" />
      <atom:title>My Blog Entries</title>
    </collection>
    <collection   href="http://example.org/reilly/pic" >
      <atom:title>Pictures</atom:title>
      <accept>image/*</accept>
    </collection>
  </workspace>
  <workspace>
    <atom:title>Side Bar Blog</atom:title>
    <collection href="http://example.org/reilly/list" />
       <atom:title>Remaindered Links</atom:title>
    </collection>
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
  <div xmlns="http://www.w3.org/1999/xhtml"><p style="color:red" other="&amp; and &lt; and &quot;">Some stuff</p><i>&lt;</i>.</div>
  </content>
</entry>
"""


ENTRY2 = """<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom">
  <title type="text">third</title>
  <summary type="html">&lt;p>not much&lt;/p></summary>
</entry>
"""


import util
import unittest
try:
    from xml.etree.ElementTree import fromstring, tostring
except:
    from elementtree.ElementTree import fromstring, tostring

class parseAtomTest(unittest.TestCase):

    def testSimple(self):
        etree = fromstring(ENTRY1)
        self.assertEqual(("text", "third"), util.get_text('title', etree))
        self.assertEqual(("html", "<p>not much</p>"), util.get_text('summary', etree))
        self.assertEqual(("xhtml", u'<p style="color:red" other=\'&amp; and &lt; and "\'>Some stuff</p><i>&lt;</i>.\n  '), util.get_text('content', etree))


class unparseAtomEntryTest(unittest.TestCase):

    def testEntry(self):
        etree = fromstring(ENTRY2)
        util.set_text(etree, 'content', 'html', '<p>hello</p>')
        self.assertEqual(("html", "<p>hello</p>"), util.get_text('content', etree))

        util.set_text(etree, 'title', 'xhtml', '<p>hello</p>')
        self.assertEqual(("xhtml", "<p>hello</p>"), util.get_text('title', etree))

        util.set_text(etree, 'summary', 'text', '<p>hello</p>')
        self.assertEqual(("text", "<p>hello</p>"), util.get_text('summary', etree))


class wrapTest(unittest.TestCase):

    def testWrap(self):
        self.assertEqual("This\nis", util.wrap("This\nis", 80))
        self.assertEqual("This is ", util.wrap("This is", 80))
        self.assertEqual("This\nis ", util.wrap("This is", 3))
        self.assertEqual("This\nis\n", util.wrap("This is\n", 3))

