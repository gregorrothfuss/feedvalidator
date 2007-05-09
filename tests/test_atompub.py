import unittest
import urlparse
import httplib2
import atompub 
import os
from email import message_from_string, message_from_file
import logging
import shutil

HTTP_SRC_DIR = "./tests/model/"
CACHE_DIR = "cache"

class MyHttpReplacement:
    """Build a stand-in for httplib2.Http that takes its
    response headers and bodies from files on disk"""
    def __init__(self, cache=None, timeout=None):
        self.hit_counter = {}

    def request(self, uri, method="GET", body=None, headers=None, redirections=5):
        path = urlparse.urlparse(uri)[2]
        fname = os.path.join(HTTP_SRC_DIR, path[1:])
        if not os.path.exists(fname):
            index = self.hit_counter.get(fname, 1)
            if os.path.exists(fname + "." + str(index)):
                self.hit_counter[fname] = index + 1
                fname = fname + "." + str(index)
        if os.path.exists(fname):
            f = file(fname, "r")
            response = message_from_file(f)
            f.close()
            body = response.get_payload()
            headers = httplib2.Response(response)
            return (headers, body)
        else:
            return (httplib2.Response({"status": "404"}), "")

    def add_credentials(self, name, password):
        pass


class Test(unittest.TestCase):
    def setUp(self):
        if os.path.exists(CACHE_DIR):
            shutil.rmtree(CACHE_DIR)
        os.makedirs(CACHE_DIR)
        self.old_httplib2 = httplib2.Http
        httplib2.Http = MyHttpReplacement

    def tearDown(self):
        httplib2.Http = self.old_httplib2 
        if os.path.exists(CACHE_DIR):
            shutil.rmtree(CACHE_DIR)
        os.makedirs(CACHE_DIR)

    def test_404_service(self):
        s = atompub.Service("http://example.org/missing", CACHE_DIR, "", "")
        self.assertEqual(0, len(s.collections()))
        self.assertEqual(0, len(s.workspaces()))

    def test_simple_service(self):
        s = atompub.Service("http://example.org/service.atomsvc", CACHE_DIR, "", "")
        self.assertEqual(1, len(s.collections()))
        self.assertEqual(1, len(s.workspaces()))

    def test_iter(self):
        s = atompub.Service("http://example.org/service.atomsvc", CACHE_DIR, "", "")
        coll = s.collections()[0]
        entries = list(coll.iter_entries())
        self.assertEqual(37, len(entries))
        self.assertEqual("Atom-Powered Robots Run Amok", entries[0]['title'])
        self.assertEqual("test post", entries[36]['title'])

    def test_single_entry_from_iter(self):
        s = atompub.Service("http://example.org/service.atomsvc", CACHE_DIR, "", "")
        coll = s.collections()[0]
        iter = coll.iter_entries()
        entry = iter.next() 
        self.assertEqual('', entry['content'])
        entry.get()
        self.assertEqual('Some <html:b>more</html:b> text.', entry['content'])

    def test_iter_new(self):
        s = atompub.Service("http://example.org/service-sync.atomsvc", "cache", "", "")
        coll = s.collections()[0]
        entries = list(coll.iter_entries())
        self.assertEqual(2, len(entries))
        self.assertEqual("Atom-Powered Robots Run Amok", entries[0]['title'])
        self.assertEqual("The end of the list.", entries[1]['title'])

        entries = list(coll.iter_new_entries())
        self.assertEqual(1, len(entries))
        self.assertEqual("A new entry", entries[0]['title'])

        entries = list(coll.iter_entries())
        self.assertEqual(3, len(entries))
        self.assertEqual("Atom-Powered Robots Run Amok", entries[1]['title'])
        self.assertEqual("The end of the list.", entries[2]['title'])




if __name__ == "__main__":
    unittest.main()


