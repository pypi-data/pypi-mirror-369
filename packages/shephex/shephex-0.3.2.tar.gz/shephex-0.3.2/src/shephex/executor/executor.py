"""
Executor base class.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Sequence, Union

from rich.progress import track

from shephex.decorators import disable_decorators
from shephex.experiment import DryResult, Experiment, ExperimentResult
from shephex.experiment.chain_iterator import ChainableExperimentIterator
from shephex.experiment.status import Pending, Status


class Executor(ABC):
    """
    Executor base class.
    """
    def __init__(self) -> None:
        pass

    def execute(
        self,
        experiments: Union[Experiment, Sequence[Experiment]],
        dry: bool = False,
        execution_directory: Optional[Union[Path, str]] = None,
        valid_statuses: Optional[Sequence[Status]] = None,
    ) -> Union[ExperimentResult, List[ExperimentResult]]:
        """
        Execute a set of experiments.

        Parameters
        -----------
        experiments: Experiment or Sequence[Experiment]
            The experiments to be executed.
        dry: bool
            If True, the experiments will not be executed, only information about
            them will be printed.
        """
        if isinstance(experiments, Experiment):
            experiments = [experiments]
        elif isinstance(experiments, ChainableExperimentIterator):
            experiments = list(experiments)

        if valid_statuses is None:
            valid_statuses = [Pending()]

        valid_experiments = []
        for experiment in experiments:
            if experiment.status in valid_statuses:
                valid_experiments.append(experiment)
            else:
                print(f"Experiment {experiment.identifier} has status {experiment.status}, skipping.")

        for experiment in track(valid_experiments, description="Preparing experiments"):
            if not experiment.shephex_directory.exists():
                experiment.dump()

        results = self._sequence_execute(
            valid_experiments, dry=dry, execution_directory=execution_directory
        )

        return results

    def _sequence_execute(
        self,
        experiments: Sequence[Experiment],
        dry: bool = False,
        execution_directory: Optional[Union[Path, str]] = None,
    ) -> Sequence[ExperimentResult]:
        results = []
        for experiment in experiments:
            result = self._execute(
                experiment, dry=dry, execution_directory=execution_directory
            )
            results.append(result)
        return results

    @abstractmethod
    def _single_execute(
        self,
        experiment: Experiment,
        dry: bool = False,
        execution_directory: Optional[Union[Path, str]] = None,
    ) -> ExperimentResult:
        raise NotImplementedError  # pragma: no cover

    def _execute(
        self,
        experiment: Experiment,
        dry: bool = False,
        execution_directory: Optional[Union[Path, str]] = None,
    ) -> ExperimentResult:
        result = self._single_execute(
            experiment, dry=dry, execution_directory=execution_directory
        )
        return result


class LocalExecutor(Executor):
    """
    Executor that runs the experiment locally, in the current process (or subprocess),
    without any parallelization.
    """

    def __init__(self) -> None:
        super().__init__()

    def _single_execute(
        self,
        experiment: Experiment,
        dry: bool = False,
        execution_directory: Optional[Union[Path, str]] = None,
    ) -> ExperimentResult:
        
        if dry:
            print(f'Experiment {experiment.identifier} to be executed locally.')
            return DryResult()

        with disable_decorators():
            result = experiment._execute(execution_directory=execution_directory)
            
        return result
