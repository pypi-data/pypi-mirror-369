from abc import ABC


class Callback(ABC):
    """
    This module contains the Callback class, which is a base class for all callbacks
    """

    def on_start(self): ...

    def on_step(self, step, X): ...

    def on_end(self): ...
