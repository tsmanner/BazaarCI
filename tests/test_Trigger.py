from unittest import TestCase
from unittest.mock import MagicMock, patch
from bazaarci.runner import Trigger


class TestTrigger(TestCase):
    def test_produces(self):
        t = Trigger()
        self.assertIn()
