from functools import reduce
from threading import Thread
from bazaarci.runner.product import Product

class Trigger:
    def __init__(self, *args):
        self.items = set(args)

    def add(self, item):
        self.items.add(item)

    def is_set(self):
        raise NotImplementedError(
            "Class `{}` has not implemented a `is_set` method!".format(self.__class__.__name__)
        )

    def wait(self):
        raise NotImplementedError(
            "Class `{}` has not implemented a `wait` method!".format(self.__class__.__name__)
        )

    def causal_products(self):
        raise NotImplementedError(
            "Class `{}` has not implemented a `causal_products` method!".format(self.__class__.__name__)
        )


class AllOf(Trigger):
    def is_set(self):
        return all(item.is_set() for item in self.items)

    def wait(self):
        [item.wait() for item in self.items]

    def causal_products(self):
        cps = set()
        for item in self.items:
            if isinstance(item, Product):
                cps.add(item)
            else:
                cps += item.causal_products()


class AnyOf(Trigger):
    def __init__(self, *args):
        super().__init__(*args)
        self._causal_products = set()

    def is_set(self):
        return any(product.is_set() for product in self.items)

    def wait(self):
        threads = []
        # Define a thread target that waits and adds the first
        # set product or trigger and terminates the other threads
        def wait_handler(product_or_trigger):
            product_or_trigger.wait()
            # Only add the first one
            if len(self._causal_products) == 0:
                self._causal_products.add(product_or_trigger)
                for thread in threads:
                    thread.terminate()
                    thread.join()
        # Set up a thread to wait on each item
        threads = [Thread(target=wait_handler, args=(item,)) for item in self.items]
        [thread.start() for thread in threads]
