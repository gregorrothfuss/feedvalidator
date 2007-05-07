import unittest
import urlparse
import httplib2
import appmodel
import os
from email import message_from_string, message_from_file

HTTP_SRC_DIR = "./tests/model/"

def a404():
    return (
            httplib2.Response({
                "status": "404",
                }),
            ""
            )

class MyHttpReplacement:
    """Build a stand-in for httplib2.Http that takes its
    response headers and bodies from files on disk"""
    def __init__(self, cache=None, timeout=None):
        pass

    def request(self, uri, method="GET", body=None, headers=None, redirections=5):
        path = urlparse.urlparse(uri)[2]
        fname = os.path.join(HTTP_SRC_DIR, path[1:])
        print fname
        if os.path.exists(fname):
            f = file(fname, "r")
            response = message_from_file(f)
            f.close()
            body = response.get_payload()
            headers = httplib2.Response(response)
            return (headers, body)
        else:
            return a404()




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

if __name__ == "__main__":
    unittest.main()

