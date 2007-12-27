import unittest
from model import Context, Service, Collection
from mockhttp import MockHttp

class Test(unittest.TestCase):
    def test_iter(self):
        context = Context(http = MockHttp(), collection = "http://example.org/entry/index.atom")
        collection = Collection(context)
        entry_contexts = list(collection.iter())
        self.assertEqual(4, len(entry_contexts))
    
        # Now test rewinding, starting the iteration over again.
        context = collection.iter().next()
        self.assertEqual(context.entry, "http://example.org/entry/67")
        self.assertEqual(context.collection, "http://example.org/entry/index.atom")

    def test_iter_empty(self):
        context = Context(http = MockHttp(), collection = "http://example.org/empty/index.atom")
        collection = Collection(context)
        entry_contexts = list(collection.iter())
        self.assertEqual(0, len(entry_contexts))


if __name__ == "__main__":
    unittest.main()

