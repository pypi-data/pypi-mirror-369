"""
Defines the Experiment class and related classes.
"""

from .experiment import Experiment  # noqa
from .options import Options
from .procedure import PickleProcedure, Procedure, ScriptProcedure
from .result import ExperimentError, ExperimentResult, FutureResult, DryResult
from .context import ExperimentContext
from .meta import Meta
from .chain_iterator import ChainableExperimentIterator

__all__ = [
    'Experiment',
    'Options',
    'ExperimentError',
    'ExperimentResult',
    'DryResult',
    'Procedure',
    'PickleProcedure',
    'ScriptProcedure',
    'FutureResult',
    'ExperimentContext',
    'Meta',
    'ChainableExperimentIterator'
]
