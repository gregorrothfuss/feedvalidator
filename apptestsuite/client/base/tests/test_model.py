import unittest
import urlparse
import httplib2
import base.appmodel as appmodel
import os
from email import message_from_string, message_from_file
import logging

HTTP_SRC_DIR = "./tests/model/"

class MyHttpReplacement:
    """Build a stand-in for httplib2.Http that takes its
    response headers and bodies from files on disk"""
    def __init__(self, cache=None, timeout=None):
        pass

    def request(self, uri, method="GET", body=None, headers=None, redirections=5):
        path = urlparse.urlparse(uri)[2]
        fname = os.path.join(HTTP_SRC_DIR, path[1:])
        if os.path.exists(fname):
            f = file(fname, "r")
            response = message_from_file(f)
            f.close()
            body = response.get_payload()
            headers = httplib2.Response(response)
            return (headers, body)
        else:
            logging.error("Could not find %s" % fname)
            return (httplib2.Response({"status": "404"}), "")


class Test(unittest.TestCase):
    def setUp(self):
        self.old_httplib2 = httplib2.Http
        httplib2.Http = MyHttpReplacement

    def tearDown(self):
        httplib2.Http = self.old_httplib2 

    def test_404_service(self):
        s = appmodel.Service("http://example.org/missing", ".", "", "")
        self.assertEqual(0, len(s.collections()))
        self.assertEqual(0, len(s.workspaces()))

    def test_simple_service(self):
        s = appmodel.Service("http://example.org/service.atomsvc", ".", "", "")
        self.assertEqual(1, len(s.collections()))
        self.assertEqual(1, len(s.workspaces()))

    def test_iter(self):
        s = appmodel.Service("http://example.org/service.atomsvc", ".", "", "")
        coll = s.collections()[0]
        entries = list(coll.iter_entries())
        self.assertEqual(37, len(entries))
        self.assertEqual("Atom-Powered Robots Run Amok", entries[0]['title'])
        self.assertEqual("test post", entries[36]['title'])

    def test_single_entry_from_iter(self):
        s = appmodel.Service("http://example.org/service.atomsvc", ".", "", "")
        coll = s.collections()[0]
        iter = coll.iter_entries()
        entry = iter.next() 
        entry.get()
        self.assertEqual('Some <html:b xmlns:html="http://www.w3.org/1999/xhtml">more</html:b> text.', entry['content'])




if __name__ == "__main__":
    unittest.main()

