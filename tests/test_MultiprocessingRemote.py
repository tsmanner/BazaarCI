from os import getpid
from unittest import TestCase
from unittest.mock import Mock
from bazaarci.runner.step import skip_if_redundant, wait_for_producers
from bazaarci.runner.remote import MultiprocessingRemote


class TestMultiprocessingRemote(TestCase):
    def test___call__(self):
        r = MultiprocessingRemote()
        mock_Step = Mock()
        r(mock_Step)
        mock_Step.set_run_behavior.assert_called_once_with(
            mock_Step,
            skip_if_redundant,
            wait_for_producers,
            r.execute_in_process
        )

    def test_execute_in_process(self):
        """ Execute the `os.getpid` function in a new process.  It must be different
            than the result of `os.getpid` of the calling process.
        """
        r = MultiprocessingRemote()
        wrapped = r.execute_in_process(getpid)
        remote_pid = wrapped(None)
        self.assertIsInstance(remote_pid, int)
        self.assertNotEqual(remote_pid, getpid())
