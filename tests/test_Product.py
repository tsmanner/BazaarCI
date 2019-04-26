from unittest import TestCase
from unittest import skip
from unittest.mock import MagicMock, patch
from bazaarci.runner import Product, CachedProduct, GraphProduct


class TestProduct(TestCase):
    @skip("Not Implemented Yet")
    def test_Product(self):
        p = Product("test")


class TestCachedProduct(TestCase):
    @skip("Not Implemented Yet")
    def test_Product(self):
        p = CachedProduct("test")


class TestGraphProduct(TestCase):
    # @skip("Not Implemented Yet")
    def test_Product(self):
        mock_Graph = MagicMock()
        p = GraphProduct(mock_Graph, "test")

