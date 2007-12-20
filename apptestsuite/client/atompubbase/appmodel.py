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
    (service, collection, entry) = context.restore((Service, Collection, Entry))

    # You don't have to use the context, Entries
    # and Collections can be instantiated from URIs instead
    # of Context instances.
    entry = Entry(entry_edit_uri)


Each atompub object also has a 'to str' function
to output the representation.

"""



class Context(object):
    """
    Encapsulates the current service documents,
    the current collection and the current 
    entry. Can be picked and un-pickled to
    achieve persistence of context.
    """

    def __init__(self, http):
        self.service = None
        self.collection = None 
        self.entry = None
        self.collection_stack = []
        self.http = http 

    def __setattr__(self, name, value):
        if name == "service_document":
            self.__dict__[name] = value 
            self.__dict__["collection"] = None 
            self.__dict__["collection_stack"] = [] 
            self.__dict__["entry"] = None 
        elif name == "collection":
            self.__dict__[name] = [value] 
            self.__dict__["collection_stack"] = [] 
            self.__dict__["entry"] = None 
            pass
        elif name == "entry":
            self.__dict__[name] = [value] 
            pass
        else:
            raise AttributeError("Attribute '%s' not found" % name)

    def collpush(self, uri):
        pass

    def collpop(self, uri):
        pass
    
class Entry(object):
    def __init__(self, context_or_uri):
        pass

    def get(self, body=None, headers={}):
        pass

    def put(self, body, headers={}):
        pass

    def delete(self, body=None, headers={}):
        pass

    def context(self):
        pass


class Collection(object):
    def __init__(self, context_or_uri):
        pass

    def get(self, body=None, headers={}):
        pass

    def get_next(self, body=None, headers={}):
        pass

    def post(self, body, headers={}):
        pass

    def iter(self):
        pass

class Service(object):
    def __init__(self, context_or_uri):
        pass

    def get(self, body=None, headers={}):
        pass

    def iter(self):
        pass

    def iter_match(self, mimetype):
        pass


