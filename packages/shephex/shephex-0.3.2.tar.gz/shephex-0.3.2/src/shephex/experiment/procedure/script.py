import importlib.util
import inspect
from pathlib import Path
from typing import Callable, Optional, Union

from shephex.experiment.context import ExperimentContext
from shephex.experiment.options import Options
from shephex.experiment.result import ExperimentResult

from .pickle import PickleProcedure
from .procedure import Procedure


class ScriptProcedure(Procedure):
    """
    A procedure wrapping a script.
    """

    def __init__(
        self,
        function: Optional[Callable] = None,
        path: Optional[Path | str] = None,
        function_name: Optional[str] = None,
        code: Optional[str] = None,
        context: bool = False,
    ) -> None:
        super().__init__(name='procedure.py', context=context)
        if function is not None:
            self.function_name = function.__name__
            self.script_code = Path(inspect.getsourcefile(function)).read_text()
        elif path is not None and function_name is not None:
            if not isinstance(path, Path):
                path = Path(path)
            self.function_name = function_name
            self.script_code = path.read_text()
        elif code is not None and function_name is not None:
            self.function_name = function_name
            self.script_code = code
        else:
            raise ValueError(
                'ScriptProcedure requires one of following sets of arguments: function, path and function_name, or code and function_name.'
            )

    def dump(self, directory: Union[Path, str]) -> None:
        directory = Path(directory)
        with open(directory / self.name, 'w') as f:
            f.write(self.script_code)

    def _execute(
        self,
        options: Options,
        directory: Optional[Union[Path, str]] = None,
        shephex_directory: Optional[Union[Path, str]] = None,
        context: Optional[ExperimentContext] = None,
    ) -> ExperimentResult:
        """
        Execute the procedure by running the script on a subprocess.

        Parameters
        ----------
        directory : Optional[Union[Path, str]], optional
        """
        # Directory handling
        if directory is None:
            directory = Path.cwd()  # pragma: no cover

        # Basic command
        path = (shephex_directory / self.name).resolve()

        assert (
            shephex_directory.exists()
        ), f'Directory {shephex_directory} does not exist.'
        assert path.exists(), f'File {path} does not exist.'
        assert Path(directory).exists(), f'Directory {directory} does not exist.'

        func_function = self.get_function_from_script(path, self.function_name)
        if hasattr(func_function, '__wrapped__'):  # check if decorated
            func = func_function()
        else:
            func = func_function

        func_procedure = PickleProcedure(func, context=self.context)

        return func_procedure._execute(options, directory, shephex_directory, context)

    def hash(self) -> int:
        return self.script_code.__hash__()

    def get_function_from_script(self, script_path: Path, func_name: str) -> None:
        """Dynamically imports a function from a Python script given its path."""
        script_path = Path(script_path).resolve()  # Ensure absolute path
        module_name = script_path.stem  # Extract filename without .py

        # Create a module spec
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        if spec is None:
            raise ImportError(f'Could not load spec for {script_path}')

        # Create a module from the spec
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # Execute the module

        # Retrieve the function
        if not hasattr(module, func_name):
            raise AttributeError(f"Module {module_name} has no function '{func_name}'")

        return getattr(module, func_name)

    def get_metadata(self) -> dict:
        metadata = super().get_metadata()
        metadata['type'] = 'ScriptProcedure'
        metadata['function_name'] = self.function_name
        return metadata

    @classmethod
    def from_metadata(cls, metadata: dict) -> 'ScriptProcedure':
        return cls(
            function_name=metadata['function_name'],
            context=metadata['context'],
            path=metadata['path'],
        )
