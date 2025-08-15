"""
A study is a collection of experiments. Used to avoid repeating the same experiment and to keep track of the results.
"""
from shephex.study.study import Study # noqa
from shephex.study.renderer import StudyRenderer 

__all__ = ['Study', 'StudyRenderer']

