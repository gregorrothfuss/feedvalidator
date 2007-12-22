import unittest
from model import Context, Service 
import pickle
from StringIO import StringIO 
from email import message_from_string, message_from_file
import os
import urlparse
import httplib2

HTTP_SRC_DIR = "./tests/model/"

class MockHttp:
    """
    A mock for httplib2.Http that takes its
    response headers and bodies from files on disk
    """
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
            return (httplib2.Response({"status": "404"}), "")

    def add_credentials(self, name, password):
        pass

class Test(unittest.TestCase):
    def test_get(self):
        c = Context()
        c.service = "http://example.org/service.atomsvc"
        c.http = MockHttp()
        s = Service(c)
        headers, body = s.get()
        self.assertEqual(headers["status"], "200")

    def test_iter(self):
        s = Service(Context(http = MockHttp(), service = "http://example.org/service.atomsvc"))
        self.assertEqual("http://example.org/entry/index.atom", s.iter().next().collection)

    def test_iter_match(self):
        s = Service(Context(http = MockHttp(), service = "http://example.org/service_entry_image.atomsvc"))
        self.assertEqual("http://example.org/images/index.atom", s.iter_match('image/png').next().collection)

    def test_iter_match_fail(self):
        s = Service(Context(http = MockHttp(), service = "http://example.org/service.atomsvc"))
        try:
            s.iter_match('image/png').next()
            self.fail("StopIteration should have been raised.")
        except StopIteration:
            pass



if __name__ == "__main__":
    unittest.main()

