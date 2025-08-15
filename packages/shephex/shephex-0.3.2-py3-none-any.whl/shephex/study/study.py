from pathlib import Path
from typing import List, Optional, Self, Tuple, Union

import dill
from rich.progress import track

from shephex.experiment.experiment import Experiment
from shephex.experiment.options import Options
from shephex.study.table import LittleTable as Table


class Study:
    """
    A study is a series of related experiments. The role of the study object is
    to manage experiments and provide a common interface for interacting with
    them.
    """

    def __init__(self, path: Union[Path, str], refresh: bool = True, avoid_duplicates: bool = True) -> None:
        self.path = Path(path)
        self.avoid_duplicates = avoid_duplicates
        if refresh:
            self.refresh(clear_table=True)

    def add_experiment(
        self, experiment: Experiment, verbose: bool = True, check_contain: bool = True
    ) -> bool:
        """
        Add an experiment to the study.
        """
        if check_contain:
            contained = self.contains_experiment(experiment)
        elif not check_contain:
            contained = False

        if not contained:
            self.table.add_row(experiment.to_dict(), add_columns=True)
            if not experiment.directory.exists():
                experiment.dump()

    def update_experiment(self, experiment: Experiment) -> None:
        """
        Update the experiment in the study.
        """
        self.table.update_row(experiment.to_dict())

    def contains_experiment(self, experiment: Experiment) -> bool:
        """
        Check if the experiment is already in the study.

        Returns
        --------
        contains: bool
                True if the experiment is in the study, False otherwise.
        """
        if not self.avoid_duplicates:
            return False

        contains = self.table.contains_row(experiment.to_dict())
        return contains

    def discover_experiments(self) -> List[Path]:
        return self.path.glob(f'*-{Experiment.extension}')

    def refresh(self, clear_table: bool = False, progress_bar: bool = False) -> None:
        # Check if the study directory exists
        if not self.path.exists():
            self.path.mkdir(parents=True)  # pragma: no cover

        if clear_table:
            self.table = Table()

        # Get the list of experiments
        experiments_paths = list(self.discover_experiments())

        # Add the experiments to the table
        for experiment_path in track(experiments_paths, description="Loading experiments", disable=not progress_bar, show_speed=True):
            experiment = Experiment.load(experiment_path, load_procedure=False)
            if not self.contains_experiment(experiment):
                self.add_experiment(experiment, verbose=True, check_contain=True)
            else:
                self.update_experiment(experiment)

    def report(self) -> None:
        from shephex.study.renderer import StudyRenderer
        StudyRenderer().render_study(self)

    def get_experiments(
        self,
        status: str = None,
        load_procedure: bool = True,
        loaded_experiments: Optional[List[Experiment]] = None,
    ) -> List[Experiment]:
        """
        Get the experiments in the study.

        Todo: This is probably quite inefficient, so should be improved.
        """
        experiments = []

        if status != 'all' or status is None:
            identifiers = self.table.where(status=status)
        else:
            identifiers = [row.identifier for row in self.table.table]

        if loaded_experiments is not None:
            loaded_ids = [experiment.identifier for experiment in loaded_experiments]
        else:
            loaded_ids = []

        for identifier in identifiers:
            if identifier in loaded_ids:
                experiment = loaded_experiments[loaded_ids.index(identifier)]
            else:
                path = self.path / f'{identifier}-{Experiment.extension}'
                experiment = Experiment.load(path, load_procedure=load_procedure)
                
            experiments.append(experiment)
        return experiments

    def where(self, load_shephex_options: bool = True, *args, **kwargs) -> Union[List[str], Tuple[List[str], List[Options]]]:
        identifiers = self.table.where(*args, **kwargs)
        if load_shephex_options:
            paths = [Path(self.path) / f"{id_}-{Experiment.extension}" for id_ in identifiers]
            options = [Options.load(path / "shephex") for path in paths]
            return identifiers, options
        
        return identifiers
    
    def dump(self, path: str | Path | None = None) -> None:
        if path is None:
            path = self.path / "study.pckl"

        with open(path, "wb") as f:
            dill.dump(self, f)

    @classmethod
    def load(cls, path: str | Path | None = None) -> Self:
        if path is None:
            path = Path.cwd() / "study.pckl"

        with open(path, "rb") as f:
            study = dill.load(f)
        return study


