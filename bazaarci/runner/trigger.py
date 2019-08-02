import asyncio
from concurrent.futures import FIRST_COMPLETED, ALL_COMPLETED
from threading import Event, Thread

class Trigger(Event, asyncio.Future):
    def __init__(self, *args, return_when):
        super().__init__(self)
        self.products = set(args)
        self.return_when = return_when
        self.causal_products = None
        self.pending_products = None
        self.waiting = False

    def add(self, item):
        self.products.add(item)

    def wait(self):
        if (not self.waiting) and (not self.is_set()):
            self.waiting = True
            self.causal_products, self.pending_products = yield from asyncio.wait(
                self.products,
                return_when=self.return_when
            )
            [pending.cancel() for pending in self.pending_products]
            self.set()
            self.waiting = False
        return Event.wait(self)


class AllOf(Trigger):
    def __init__(self, *args):
        super().__init__(*args, ALL_COMPLETED)


class AnyOf(Trigger):
    def __init__(self, *args):
        super().__init__(*args, FIRST_COMPLETED)


class ExactlyN(Trigger):
    def __init__(self, n, *args):
        super().__init__(*args, FIRST_COMPLETED)
        self.n = n

    def wait(self):
        if (not self.waiting) and (not self.is_set()):
            self.waiting = True
            pending_products = self.products
            for _ in range(self.n):
                complete, pending_products =  yield from asyncio.wait(
                    pending_products,
                    return_when=self.return_when
                )
                causal_products += complete
            [product.cancel() for product in pending_products]
            self.pending_products = pending_products
            self.causal_products = causal_products
            self.set()
            self.waiting = False
        return Event.wait(self)
