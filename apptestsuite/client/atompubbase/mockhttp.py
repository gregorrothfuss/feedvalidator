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
        self.hit_counter = {}

    def request(self, uri, method="GET", body=None, headers=None, redirections=5):
        counter = self.hit_counter.get(uri, 0)
        counter += 1
        self.hit_counter[uri] = counter
        path = urlparse.urlparse(uri)[2]
        fname = os.path.join(HTTP_SRC_DIR, method, path.strip("/") + ".file")
        fname_next = fname + "." + str(counter)
        if os.path.exists(fname_next):
            fname = fname_next
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


class MockRecorder(httplib2.Http):
    def __init__(self, h, directory):
        self.h = h
        self.directory = directory
        self.hit_counter = {}
        
    def request(self, uri, method="GET", body=None, headers=None, redirections=5):
        counter = self.hit_counter.get(uri, 0)
        counter += 1
        self.hit_counter[uri] = counter
        headers, body = self.h.request(uri, method, body, headers, redirections)
        path = urlparse.urlparse(uri)[2]
        fname = os.path.join(self.directory, method, path.strip("/") + ".file")
        if counter >= 2:
            fname = fname + "." + str(counter)
        dirname = os.path.dirname(fname)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        f = file(fname, "w")
        f.write(
            "\r\n".join(["%s: %s" % (key, value) for key, value in headers.iteritems()])
            )
        f.write("\r\n\r\n")
        f.write(body)
        f.close()
        return (headers, body)

    def add_credentials(self, name, password):
        h.add_credentials(name, password)
