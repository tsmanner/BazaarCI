import hashlib
import multiprocessing
import os
import random
from functools import wraps
from multiprocessing.managers import BaseManager, SyncManager

from bazaarci.runner import Step
from bazaarci.runner.remote.remote import Remote
from bazaarci.runner.step import skip_if_redundant, wait_for_producers


class OutputManager(BaseManager): pass
output_dict = dict()
OutputManager.register("get_output", callable=lambda: output_dict)


def cache_return_value(func, address, key):
    remote_manager = OutputManager(address=address)
    remote_manager.connect()
    remote_manager.get_output().update([(key, func())])


class MultiprocessingRemote(Remote):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager = OutputManager()
        self.manager.start()

    def execute_in_process(self, func):
        """ Write a function that uses a Queue or Proxy to map the
            function output onto a process-safe value that can be
            captured in `Step.output` so the user can get at the
            return value
        """
        @wraps(func)
        def wrapped(step):
            # Calculate a unique ID to use for the output lookup
            wrapper_hash = hashlib.sha256(bytes(str(random.random()), "utf-8")).hexdigest()
            # Multiprocessing Setup
            process = multiprocessing.Process(target=cache_return_value, args=(func, self.manager.address, wrapper_hash))
            # Execution
            process.start()
            # Teardown
            process.join()
            # Free up this key
            return self.manager.get_output().pop(wrapper_hash)
        return wrapped

    def __call__(self, step: Step):
        step.set_run_behavior(step, skip_if_redundant, wait_for_producers, self.execute_in_process)
