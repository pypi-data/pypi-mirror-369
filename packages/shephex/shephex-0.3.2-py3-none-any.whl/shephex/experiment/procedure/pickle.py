import os
import pickle
import traceback
from inspect import getsource, getsourcefile, signature
from pathlib import Path
from typing import Callable, Optional, Union

import dill

from shephex.experiment.context import ExperimentContext
from shephex.experiment.options import Options
from shephex.experiment.result import ExperimentError, ExperimentResult
from shephex.experiment.status import Status

from .procedure import Procedure


class PickleProcedure(Procedure):
    """
    A procedure wrapping a function.
    """
    def __init__(self, func: Callable, context: bool = False) -> None:
        super().__init__(name='procedure.pkl', context=context)
        self.func = func
        self.signature = signature(func)
        self.script_code = Path(getsourcefile(func)).read_text()


    def dump(self, directory: Union[Path, str]) -> None:
        directory = Path(directory)
        with open(directory / self.name, 'wb') as f:
            dill.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL, recurse=True)

        name = self.name.replace('.pkl', '.py')
        with open(directory / name, 'w') as f:
            f.write(self.script_code)
    
    def _execute(
        self,
        options: Options,
        directory: Optional[Union[Path, str]] = None,
        shephex_directory: Optional[Union[Path, str]] = None,
        context: Optional[ExperimentContext] = None,
    ) -> ExperimentResult:
        # Directory handling
        """
        Execute the procedure by calling the function.

        Parameters
        ----------
        options : Options
                The options for the procedure.
        directory : Optional[Union[Path, str]], optional
                Directory where the procedure will be executed, by default None.
        shephex_directory : Optional[Union[Path, str]], optional
                Directory where the procedure is saved, by default None.
        context : Optional[ExperimentContext], optional
                The context for the experiment, by default None.

        Returns
        -------
        ExperimentResult
                The result of the experiment.
        """

        cwd = Path.cwd()
        if directory is not None:
            directory = Path(directory)
            directory.mkdir(parents=True, exist_ok=True)
            os.chdir(directory)

        if context is None: # Execution without context
            try:
                result = self.func(*options.args, **options.kwargs)
                status = Status.completed()
            except Exception as e:
                print(traceback.format_exc())
                result = ExperimentError(e)
                status = Status.failed()
        else: # Execution with context
            if 'context' in options.kwargs.keys():
                raise ValueError(
                    '"context" is a reserved keyword if shephex context is enabled.'
                )

            try:
                result = self.func(*options.args, **options.kwargs, context=context)
                status = Status.completed()

            except Exception as e:
                print(traceback.format_exc())
                result = ExperimentError(e)
                status = Status.failed()

        result = ExperimentResult(result=result, status=status)
        result.dump(shephex_directory)
        # Directory handling
        os.chdir(cwd)
        return result

    def hash(self) -> int:
        return hash(getsource(self.func))

    def get_metadata(self) -> dict:
        metadata = super().get_metadata()
        metadata['type'] = 'PickleProcedure'
        return metadata

    @classmethod
    def from_metadata(cls, metadata: dict):
        raise NotImplementedError('PickleProcedure cannot be created from metadata - currently.')
