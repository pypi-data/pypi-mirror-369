"""
Experiment class definition.
"""

import json
import pickle as pkl
from pathlib import Path
from time import time
from typing import Any, Callable, Optional, TypeAlias, Union

import shortuuid

from shephex.experiment.context import ExperimentContext
from shephex.experiment.meta import Meta
from shephex.experiment.options import Options
from shephex.experiment.procedure import PickleProcedure, ScriptProcedure
from shephex.experiment.result import ExperimentResult
from shephex.experiment.status import Status

ProcedureType: TypeAlias = Union[PickleProcedure, ScriptProcedure]


class Experiment:
    """
    Experiment class definition, shephex's central object.
    """

    extension = 'exp'
    shep_dir = 'shephex'

    def __init__(
        self,
        *args,
        function: Optional[Union[Callable, str, Path]] = None,
        procedure: Optional[ProcedureType] = None,
        root_path: Optional[Union[Path, str]] = None,
        identifier: Optional[str] = None,
        status: Optional[Status] = None,
        meta: Optional[Meta] = None,
        **kwargs,
    ) -> None:
        """
        An experiment object containing the procedure, options, and metadata.

        Parameters
        ----------
        *args
            Positional arguments to be passed to the function or script.
        function : Optional[Union[Callable, str, Path]], optional
            A callable function or path to a script, by default None
        procedure : Optional[ProcedureType], optional
            A procedure object, by default None
        root_path : Union[Path, str], optional
            The root path for the experiment, by default None
        identifier : Optional[str], optional
            The identifier for the experiment, by default None. When None
            a random identifier is generated using shortuuid.
        status : Optional[str], optional
            The status of the experiment, by default None (pending).
        meta : Optional[Meta], optional
            A shephex.experiment.meta object, by default None. If supplied,
            identifier and status are ignored.
        """

        # Root path
        self.root_path = Path(root_path).resolve() if root_path else Path.cwd()

        # Set the procedure
        if function is not None:
            self.procedure = function
        elif procedure is not None:
            self._procedure = procedure
        else:
            raise ValueError("Either 'func' or 'procedure' must be provided.")

        # Set the options
        args = args if args else []
        kwargs = kwargs if kwargs else {}
        self.options = Options(*args, **kwargs)

        # Meta
        if meta is None:
            identifier = identifier if identifier is not None else shortuuid.uuid()
            status = status if status is not None else Status.pending()

            self.meta = Meta(
                status=status,
                identifier=identifier,
                procedure=self.procedure.get_metadata(),
                options_path=f'{self.shep_dir}/{self.options.name}',
                time_stamp=time(),
            )
        else:
            self.meta = meta

    ############################################################################
    # Properties
    ############################################################################

    @property
    def root_path(self) -> Path:
        """
        The root path for the experiment.

        Returns
        -------
        Path
            The root path for the experiment
        """
        return self._root_path

    @root_path.setter
    def root_path(self, root_path: Path) -> None:
        self._root_path = Path(root_path)

    @property
    def identifier(self) -> str:
        """
        The identifier for the experiment.

        Returns
        -------
        str
            The identifier for the experiment.
        """
        return self.meta['identifier']

    @property
    def procedure(self) -> ProcedureType:
        """
        The procedure for the experiment.

        Returns
        -------
        ProcedureType
            The procedure for the experiment.
        """
        return self._procedure

    @procedure.setter
    def procedure(self, procedure: ProcedureType):
        """
        Set the procedure for the experiment.

        Parameters
        ----------
        procedure : ProcedureType
                The procedure for the experiment. This can be a callable function,
                a path to a script, or a Procedure object.
                If path or str is provided, a ScriptProcedure object is created.
                If callable is provided, a PickleProcedure object is created.

        Raises
        ------
        ValueError
                If the procedure type is not a valid type.
        """

        procedure_type = type(procedure)
        if isinstance(procedure, (ScriptProcedure, PickleProcedure)):
            pass
        elif procedure_type is str or procedure_type is Path:
            procedure = ScriptProcedure(procedure)
        elif callable(procedure):
            procedure = PickleProcedure(procedure)
        else:
            raise ValueError(f'Invalid procedure type: {procedure_type}')

        self._procedure = procedure

    @property
    def status(self) -> Status:
        """
        The status of the experiment.

        Returns
        -------
        str
                The status of the experiment.
        """
        return self.meta['status']

    @status.setter
    def status(self, status: Union[str, Status]) -> None:
        """
        Set the status of the experiment.

        Parameters
        ----------
        status : str
            The status of the experiment. Valid statuses are:
            'pending', 'submitted', 'running', 'completed', 'failed'.

        Raises
        ------
        ValueError
            If the status is not a valid status.
        """
        if isinstance(status, str):
            status = Status(status)
        self.meta['status'] = status

    @property
    def directory(self) -> Path:
        """
        The directory for the experiment.

        Created as root_path/identifier-extension/

        Returns
        -------
        Path
                The directory for the experiment.
        """
        if not self.root_path.exists():
            self.root_path.mkdir(parents=True)

        directory = self.root_path / Path(f'{self.identifier}-{self.extension}/')
        return directory

    @property
    def shephex_directory(self) -> Path:
        return self.directory / self.shep_dir

    ############################################################################
    # Methods
    ############################################################################

    def dump(self) -> None:
        """
        Dump all the experiment data to the experiment directory, including
        the options, meta, and procedure.
        """
        path = self.directory
        if not path.exists():
            path.mkdir(parents=True)

        self.shephex_directory.mkdir(parents=True, exist_ok=True)

        self._dump_options()
        self._dump_meta()
        self._dump_procedure()

    def _dump_options(self) -> None:
        self.options.dump(self.shephex_directory)

    def _dump_procedure(self) -> None:
        self.procedure.dump(self.shephex_directory)

    def _dump_meta(self) -> None:
        self.meta.dump(self.shephex_directory)

    @classmethod
    def load(
        cls,
        path: Union[str, Path],
        override_procedure: Optional[ProcedureType] = None,
        load_procedure: bool = True,
    ) -> 'Experiment':
        """
        Load an experiment from a directory.

        Parameters
        ----------
        path : Union[str, Path]
                The path to the experiment directory.
        override_procedure : Optional[ProcedureType], optional
                Override the procedure object, by default None
        load_procedure : bool, optional
                Load the procedure object, by default True

        Returns
        -------
        Experiment
                An experiment object loaded from the directory.
        """

        path = Path(path)

        # Load the meta file
        meta = Meta.from_file(path / cls.shep_dir)
        meta['status'] = Status(meta['status'])

        # Load the options
        with open(path / meta['options_path'], 'rb') as f:
            options = json.load(f)

        # Load the procedure
        procedure = cls.load_procedure(path / cls.shep_dir, meta['procedure'], override_procedure, load_procedure)

        # Create the experiment
        experiment = cls(
            *options['args'],
            **options['kwargs'],
            procedure=procedure,
            root_path=path.parent,
            meta=meta,
        )

        return experiment

    @staticmethod
    def load_procedure(
        path: Path,
        meta: dict,
        override_procedure: Optional[ProcedureType] = None,
        load_procedure: bool = True,
    ) -> ProcedureType:
        # Load the procedure
        procedure_path = path / meta['name']
        procedure_type = meta['type']

        if override_procedure:
            return override_procedure
        elif not load_procedure:
            return PickleProcedure(lambda: None)

        if procedure_type == 'ScriptProcedure':
            meta['path'] = str(procedure_path)
            procedure = ScriptProcedure.from_metadata(meta)

        elif procedure_type == 'PickleProcedure':
            with open(procedure_path, 'rb') as f:
                procedure = pkl.load(f)

        return procedure

    def _execute(
        self, execution_directory: Optional[Union[Path, str]] = None
    ) -> ExperimentResult:
        """
        Execute the experiment procedure.

        Parameters
        ----------
        execution_directory : Optional[Union[Path, str]], optional
                The directory where the experiment will be executed, defaults to
                the experiment directory.
        """
        self.update_status(Status.running())
        if self.procedure.context:
            context = ExperimentContext(self.shephex_directory.resolve())
        else:
            context = None

        if execution_directory is None:
            execution_directory = self.directory

        result = self.procedure._execute(
            options=self.options,
            directory=execution_directory,
            shephex_directory=self.shephex_directory,
            context=context,
        )
        self.meta.load(self.shephex_directory)  # Reload the meta file
        self.update_status(result.status)
        return result

    def update_status(self, status: Union[Status, str]) -> None:
        """
        Update the status of the experiment.
        """
        self.status = status
        self._dump_meta()

    def to_dict(self) -> dict:
        """
        Return a dictionary representation of the experiment. Used for printing
        not for saving or comparing experiments.

        Returns
        -------
        dict
            A dictionary representation of the experiment.
        """
        experiment_dict = self.meta.get_dict()
        experiment_dict.update(self.options.to_dict())
        return experiment_dict

    ############################################################################
    # Magic Methods
    ############################################################################

    def __eq__(self, experiment: Any) -> bool:
        """
        Compare two experiments based on their options.

        Parameters
        ----------
        experiment : Any
            The experiment to compare.

        Returns
        -------
        bool
            True if the experiments have the same options, False otherwise.
        """
        if not isinstance(experiment, Experiment):
            return False

        if self.procedure != experiment.procedure:
            return False

        return experiment.options == self.options

    def __repr__(self) -> str:
        """
        Return a string representation of the experiment.

        Returns
        -------
        str
            A string representation of the experiment.
        """
        rep_str = f'Experiment {self.identifier}'
        for key, value in self.options.items():
            rep_str += f'\n\t{key}: {value}'
        rep_str += f'\n\tStatus: {self.status}'
        rep_str += f'\n\tProcedure: {self.procedure.name}'
        return rep_str
