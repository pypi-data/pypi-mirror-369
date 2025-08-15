# ruff: noqa
class DecoratorState:

    def __init__(self):
        self._active = True

    def disable(self):
        self._active = False
    
    def enable(self):
        self._active = True
    
    @property
    def active(self):
        return self._active

global decorator_state
decorator_state = None

def get_decorator_state():
    global decorator_state
    if decorator_state is None:
        decorator_state = DecoratorState()
    return decorator_state

from contextlib import AbstractContextManager

class disable_decorators(AbstractContextManager):

    def __enter__(self):
        get_decorator_state().disable()
    
    def __exit__(self, *exc):
        get_decorator_state().enable()


from shephex.decorators.chain import chain
from shephex.decorators.hexperiment import hexperiment

__all__ = ['chain', 'hexperiment']