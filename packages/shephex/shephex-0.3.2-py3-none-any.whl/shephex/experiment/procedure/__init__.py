"""
Procedures wrap functions or script for a consistent interface.
"""
from shephex.experiment.procedure.procedure import Procedure  # noqa
from shephex.experiment.procedure.pickle import PickleProcedure
from shephex.experiment.procedure.script import ScriptProcedure

__all__ = ['Procedure', 'PickleProcedure', 'ScriptProcedure']
