import functools
import hashlib
import multiprocessing
import os
import subprocess
import random
import time
from multiprocessing.managers import SyncManager

from bazaarci.runner import Step
from bazaarci.runner.remote.remote import Remote
from bazaarci.runner.step import skip_if_redundant, wait_for_producers


ENCODING = "utf-8"


class OutputManager(SyncManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.function_dict = None
        self.output_dict = None

    def _setup(self):
        self.function_dict = self.dict()
        self.output_dict = self.dict()
        self.register("get_function", callable=self.get_function_method)
        self.register("set_function", callable=self.set_function_method)
        self.register("has_output", callable=self.has_output_method)
        self.register("get_output", callable=self.get_output_method)
        self.register("pop_output", callable=self.pop_output_method)
        self.register("set_output", callable=self.set_output_method)

    def start(self, *args, **kwargs):
        super().start(*args, **kwargs)
        self._setup()

    def connect(self, *args, **kwargs):
        super().connect(*args, **kwargs)
        self._setup()

    def get_function_method(self, key):
        return self.function_dict[key]

    def set_function_method(self, key, func):
        self.function_dict[key] = func

    def has_output_method(self, key):
        return key in self.output_dict

    def get_output_method(self, key):
        return self.output_dict[key]

    def pop_output_method(self, key):
        return self.output_dict.pop(key)

    def set_output_method(self, key, value):
        self.output_dict[key] = value



def execute_cached_function(address, key, authkey):
    time.sleep(2)
    remote_manager = OutputManager(address=address, authkey=authkey.encode(ENCODING))
    remote_manager.connect()
    func = remote_manager.get_function(key)._getvalue()
    remote_manager.set_output(key, func())


class MultiprocessingRemote(Remote):
    def __init__(self, *args, timeout=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.authkey = hashlib.sha256(bytes(str(random.random()), ENCODING)).hexdigest()
        self.manager = OutputManager(authkey=self.authkey.encode(ENCODING))
        self.timeout = timeout
        self.manager.start()

    def _wait_for_result(self, key):
        """ Blocks until an optional timeout is reached, or
            the output dictionary has the result for this key
        """
        start_time = time.time()
        while not self.manager.has_output(key)._getvalue() and (self.timeout == 0 or time.time() < (start_time + self.timeout)):
            pass

    def execute_in_process(self, func):
        """ Write a function that uses a Queue or Proxy to map the
            function output onto a process-safe value that can be
            captured in `Step.output` so the user can get at the
            return value
        """
        @functools.wraps(func)
        def wrapped(step):
            # Calculate a unique ID to use for the output lookup
            wrapper_hash = hashlib.sha256(bytes(str(random.random()), ENCODING)).hexdigest()
            # Multiprocessing Setup
            self.manager.set_function(wrapper_hash, func)
            remote_process_command = 'python3 -m bazaarci.runner.remote.multiprocessingremote'
            sp_env = os.environ.copy()
            sp_env.update(
                BAZAARCI_GRAPH_ADDRESS=self.manager.address,
                BAZAARCI_STEP_HASH=wrapper_hash,
                BAZAARCI_AUTHKEY=self.authkey,
            )
            # Execution
            subprocess.Popen(remote_process_command, env=sp_env, shell=True)
            self._wait_for_result(wrapper_hash)
            # Free up this key
            return self.manager.pop_output(wrapper_hash)._getvalue()
        return wrapped

    def __call__(self, step: Step):
        step.set_run_behavior(step, skip_if_redundant, wait_for_producers, self.execute_in_process)


if __name__ == "__main__":
    execute_cached_function(
        os.getenv("BAZAARCI_GRAPH_ADDRESS"),
        os.getenv("BAZAARCI_STEP_HASH"),
        os.getenv("BAZAARCI_AUTHKEY"),
    )
