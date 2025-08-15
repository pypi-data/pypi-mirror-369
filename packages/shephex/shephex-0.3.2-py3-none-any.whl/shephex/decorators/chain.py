import functools
from pathlib import Path
from typing import Callable, Literal, Optional

from shephex.decorators import get_decorator_state
from shephex.experiment import ChainableExperimentIterator
from shephex.experiment.procedure import PickleProcedure, ScriptProcedure


def chain(
    context: bool = False,
    hex_directory: str | Path = 'experiments/',
    procedure_type: Literal['ScriptProcedure', 'PickleProcedure'] = 'PickleProcedure',
) -> Callable:
    """
    Decorator to create a ChainableExperimentIterator for the function it is applied to.

    Parameters
    -----------
    context (bool):
        Whether to pass the experiment context to the function. If this is activated
        the function will need to take an additional keyword argument `context` that
        will be passed the experiment context. This offers limited access to
        writing to the context, e.g. to track progress.
    """

    def decorator(function: Callable):

        @functools.wraps(function)
        def wrapper(*args, directory: Optional[str | Path] = None, **kwargs):

            # If the decorator is not active, return the function
            if not get_decorator_state().active:
                return function
            
            if procedure_type == 'ScriptProcedure':
                procedure = ScriptProcedure(function, context=context)
            elif procedure_type == 'PickleProcedure':
                procedure = PickleProcedure(function, context=context)

            if directory is None:
                directory = hex_directory

            return ChainableExperimentIterator(procedure, directory)

        return wrapper

    return decorator
