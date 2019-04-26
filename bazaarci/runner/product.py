from functools import lru_cache
from threading import Event

__all__ = [
    "Product",
    "CachedProduct",
    "GraphProduct",
]


class Product(Event):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __str__(self):
        return "Product({})".format(self.name)


class CachedProduct(Product):
    _cache = {}

    def __new__(cls, name, *args, **kwargs):
        if name not in cls._cache:
            cls._cache[name] = cls(name, *args, **kwargs)
        return cls._cache[name]

    def __init__(self, name):
        super().__init__(name)


class GraphProduct(Product):
    def __init__(self, graph, name):
        super().__init__(name)
        self.graph = graph

    def fullname(self):
        return '.'.join((self.graph.fullname, self.name))
