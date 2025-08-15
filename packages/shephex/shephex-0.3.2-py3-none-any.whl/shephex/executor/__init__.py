"""
Executors define the ways in which experiments are executed. 
"""

from shephex.executor.executor import Executor, LocalExecutor
from shephex.executor.slurm import SlurmExecutor

__all__ = ['Executor', 'LocalExecutor', 'SlurmExecutor']
