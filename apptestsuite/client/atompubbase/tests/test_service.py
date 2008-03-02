import unittest
from model import Context, Service 
from mockhttp import MockHttp

HTTP_SRC_DIR = "./tests/"

class Test(unittest.TestCase):
    def test_get(self):
        c = Context()
        c.service = "http://example.org/service.atomsvc"
        c.http = MockHttp(HTTP_SRC_DIR)
        s = Service(c)
        headers, body = s.get()
        self.assertEqual(headers["status"], "200")

    def test_iter(self):
        s = Service(Context(http = MockHttp(HTTP_SRC_DIR), service = "http://example.org/service.atomsvc"))
        self.assertEqual("http://example.org/entry/index.atom", s.iter().next().collection)

    def test_iter_match(self):
        s = Service(Context(http = MockHttp(HTTP_SRC_DIR), service = "http://example.org/service_entry_image.atomsvc"))
        self.assertEqual("http://example.org/images/index.atom", s.iter_match('image/png').next().collection)

    def test_iter_match_fail(self):
        s = Service(Context(http = MockHttp(HTTP_SRC_DIR), service = "http://example.org/service.atomsvc"))
        try:
            s.iter_match('image/png').next()
            self.fail("StopIteration should have been raised.")
        except StopIteration:
            pass



if __name__ == "__main__":
    unittest.main()

