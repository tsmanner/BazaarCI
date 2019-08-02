import os
from unittest import TestCase
from unittest.mock import MagicMock
from bazaarci.dsl.loader import load


class TestGrammar(TestCase):
    def test_load(self):
        graph = load("docs/mockups/dsl/SimpleGraph.bc")
        print(graph)
        print(graph.subgraphs)
        print(graph.steps)
        for step in graph.steps:
            print(step)
            print({attr.key: attr.value for attr in step.attributes})
            if step.consumes: print("<-", {product for product in step.consumes})
            if step.produces: print("->", {product for product in step.produces})
        for product in graph.products:
            print(product)
            print('   ', {attr.key: attr.value for attr in product.attributes})
        for product in graph.uses:
            print(product)
            print('   ', product.subgraph)
            print('   ', product.name)
