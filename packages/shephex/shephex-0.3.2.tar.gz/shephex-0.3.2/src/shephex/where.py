"""
This module provides functions to find experiments that match certain conditions.
"""
from pathlib import Path
from typing import Any, List, Tuple, Union

from shephex import Study
from shephex.experiment import Experiment, ExperimentResult, Options


def id_where(*args, directory: Union[Path, str], **kwargs) -> Tuple[List[int], List[Options]]:
    """
    Get the ids of the experiments that match the conditions.

    Parameters
    ----------
    directory : Union[Path, str]
        The directory where the experiments are stored.
    args : Any
        Positional arguments for the experiments to find. 
    kwargs : Any
        Keyword arguments for the experiments to find.
    
    Returns
    -------
    Tuple[List[int], List[Options]]
        The ids and options of the experiments that match the conditions.
    """
    study = Study(directory, avoid_duplicates=False)
    ids, options = study.where(*args, **kwargs, load_shephex_options=True)
    return ids, options

def path_where(*args, directory: Union[Path, str], **kwargs) -> Tuple[List[Path], List[Options]]:
    """
    Get the paths of the experiments that match the conditions.

    Parameters
    ----------
    directory : Union[Path, str]
        The directory where the experiments are stored.
    args : Any
        Positional arguments for the experiments to find.
    kwargs : Any
        Keyword arguments for the experiments to find.

    Returns
    -------
    Tuple[List[Path], List[Options]]
        The paths and options of the experiments that match the conditions.
    """
    ids, options = id_where(*args, directory=directory, **kwargs)
    paths = [Path(directory) / f"{id_}-{Experiment.extension}" for id_ in ids]
    return paths, options

def result_where(*args, directory: Union[Path, str], result_object: bool = False, **kwargs) -> Tuple[List[Any], List[Options]]:
    """
    Get the results of the experiments that match the conditions.

    Parameters
    ----------
    directory : Union[Path, str]
        The directory where the experiments are stored.
    result_object : bool
        Whether to return the ExperimentResult object or the result object.
    args : Any
        Positional arguments for the experiments to find.

    Returns
    -------
    Tuple[List[Any], List[Options]]
        The results and options of the experiments that match the conditions
    """
    paths, options = path_where(*args, directory=directory, **kwargs)
    results = [ExperimentResult.load(path / "shephex") for path in paths]
    if not result_object:
        results = [result.result for result in results]
    return results, options





