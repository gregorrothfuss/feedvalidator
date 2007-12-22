"""
There are four classes that make up the core
of the atompub model.

class Context
class Service
class Collection
class Entry

Context represents the current state, as represented
by a service document, a collection and an entry.

Each atompub object (Service, Collection, or Entry) 
is just instantiated with a URI (or with a Context)
that it then uses to perform its work. Each object can produce
a list of URIs (actually Context objects) (possibly filtered) 
for the next level down. The only parsing done will be xpaths to
pick out URIs, e.g. collections from service documents. 
Here is an example of how the classes are used together:

    # Note that httplib2.Http is passed in so you 
    # can pass in your own instrumented version, etc.
    from httplib2 import Http
    h = httplib2.Http()
    c = Context(h, service_document_uri)
    service = Service(c)

    collection = Collection(service.iter()[0]) 
    entry = Entry(collection.iter()[0])
    (headers, body) = entry.get()
    body = "<entry>...some updated stuff </entry>"
    entry.put(body)

    # saving and restoring is a matter of pickling/unpickling the Context.
    import pickle
    f = file("somefile", "w")
    pickle.dump(entry.context(), f)

    import pickle
    f = file("somefile", "r")
    context = pickle.load(f)
    # You pass the class names into restore() for it to use to restore the context.
    (service, collection, entry) = context.restore(Service, Collection, Entry)

    # You don't have to use the context, Entries
    # and Collections can be instantiated from URIs instead
    # of Context instances.
    entry = Entry(entry_edit_uri)

"""
import events
from mimeparse import mimeparse
import urlparse

def absolutize(baseuri, uri):
    """
    Given a baseuri, return the absolute
    version of the given uri. Works whether
    uri is relative or absolute.
    """
    (scheme, authority, path, query, fragment) = urlparse.urlsplit(uri)
    if not authority:
        uri = urlparse.urljoin(baseuri, uri)
    return uri


class Context(object):
    """
    Encapsulates the current service documents,
    the current collection and the current 
    entry. Can be picked and un-pickled to
    achieve persistence of context.
    """
    _service = None
    _collection = None 
    _entry = None
    _http = None
    _collection_stack = []

    def __init__(self, http = None, service=None, collection=None, entry=None):
        self._collection_stack = []
        self.http = http
        self._service = service
        self._collection = collection
        self._entry = entry

    def _get_service(self):
        return self._service

    def _set_service(self, service):
        self._service = service
        self._collection = None 
        self._collection_stack = [] 
        self._entry = None 

    service = property(_get_service, _set_service, None, "The URI of the Service Document. None if not set yet.")

    def _get_collection(self):
        return self._collection

    def _set_collection(self, collection):
        self._collection = collection
        self._collection_stack = []
        self._entry = None 

    collection = property(_get_collection, _set_collection, None, "The URI of the collection. None if not set yet.")

    def _get_entry(self):
        return self._entry

    def _set_entry(self, entry):
        self._entry = entry

    entry = property(_get_entry, _set_entry, None, "The URI of the entry. None if not set yet.")

    def restore(self, service_type, collection_type, entry_type):
        """
        Restore the state from a Context. The types of the objects
        to be instantiate for the service, collection and entry 
        are passed in. If no URI is set for a specific level 
        then None is returned for that instance.
        """
        service = self._service and service_type(self) or None
        collection = self._collection and collection_type(self) or None
        entry = self._entry and entry_type(self) or None
        return (service, collection, entry)

    def collpush(self, uri):
        self._collection_stack.append((self._collection, self._entry))
        self._collection = uri
        self._entry = None 

    def collpop(self):
        self._collection, self._entry = self._collection_stack.pop()


APP = "http://www.w3.org/2007/app"
APP_COLL = "{%s}collection" % APP
APP_MEMBER_TYPE = "{%s}accept" % APP
import copy
try:
    from xml.etree.ElementTree import fromstring, tostring
except:
    from elementtree.ElementTree import fromstring, tostring



class Service(object):
    def __init__(self, context_or_uri):
        self.context = isinstance(context_or_uri, Context) and context_or_uri or Context(service=context_or_uri) 
        self.representation = None

    def context(self):
        return self.context

    def get(self, headers=None, body=None):
        headers, body = self.context.http.request(self.context.service, headers=headers)
        if headers.status == 200:
            self.representation = body
        return (headers, body)

    def iter_match(self, mimerange):
        if not self.representation:
            headers, body = self.get()
        service_tree = fromstring(body)
        for coll in service_tree.findall(".//" + APP_COLL):
            coll_type = [t for t in coll.findall(APP_MEMBER_TYPE) if mimeparse.best_match([t.text], mimerange)] 
            if coll_type:
                context = copy.copy(self.context)
                context.collection = absolutize(self.context.service, coll.get('href')) 
                yield context

    def iter(self):
        return self.iter_match("*/*")


events.add_event_handlers(Service)

