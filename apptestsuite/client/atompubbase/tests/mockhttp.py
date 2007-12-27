import urlparse
import httplib2
from email import message_from_string, message_from_file
import os

HTTP_SRC_DIR = "./tests/"

class MockHttp:
    """
    A mock for httplib2.Http that takes its
    response headers and bodies from files on disk
    """
    def __init__(self, cache=None, timeout=None):
        pass

    def request(self, uri, method="GET", body=None, headers=None, redirections=5):
        path = urlparse.urlparse(uri)[2]
        fname = os.path.join(HTTP_SRC_DIR, method, path[1:])
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


