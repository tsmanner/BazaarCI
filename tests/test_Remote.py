from unittest import TestCase
from bazaarci.runner.remote.remote import Remote


class TestRemote(TestCase):
    def test___call__(self):
        r = Remote()
        with self.assertRaises(NotImplementedError):
            r(None)
