from functools import reduce
from threading import Event, Thread

class Trigger(Event):
    def __init__(self, *args, return_when):
        super().__init__(self)
        self.products = set(args)

    def add(self, item):
        self.products.add(item)

    def causal_products(self):
        raise NotImplementedError(
            "Class `{}` has not implemented a `causal_products` method!".format(
                self.__class__.__name__
            )
        )


class AllOf(Trigger):
    def wait(self):
        [item.wait() for item in self.products]
        self.set()

    def causal_products(self):
        cps = set()
        for item in self.products:
            cps += item.causal_products()


class AnyOf(Trigger):
    def __init__(self, *args):
        super().__init__(*args)
        self._causal_products = set()

    def wait(self):
        threads = []

        # Define a thread target that waits and adds the first
        # set product or trigger and terminates the other threads
        def wait_handler(product_or_trigger):
            product_or_trigger.wait()
            # Only add the first one
            if not self.is_set():
                self.set()
                self._causal_products = product_or_trigger.causal_products()
                # Join all the threads, we don't care anymore
                # when/which complete
                [thread.join() for thread in threads]

        # Set up a thread to wait on each item
        threads = [Thread(target=wait_handler, args=(item,)) for item in self.products]
        [thread.start() for thread in threads]
