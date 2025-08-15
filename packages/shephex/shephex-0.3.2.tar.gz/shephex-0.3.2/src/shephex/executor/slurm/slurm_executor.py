import inspect
import json
from pathlib import Path
from typing import List, Literal, Optional, Union

from shephex.executor.executor import Executor
from shephex.executor.slurm import (
    SlurmBody,
    SlurmHeader,
    SlurmProfileManager,
    SlurmScript,
)
from shephex.experiment import FutureResult
from shephex.experiment.experiment import Experiment


class SlurmSafetyError(Exception):    
    pass

class SlurmExecutor(Executor):
    """
    Shephex SLURM executor for executing experiments on a SLURM cluster.
    """
    def __init__(
        self, directory: Union[str, Path] = None, 
        scratch: bool = False, 
        ulimit: Union[int, Literal['default']] = 8000,
        move_output_file: bool = True,
        safety_check: bool = True,
        array_limit: int | None = None,
        **kwargs
    ) -> None:
        """
        shephex SLURM executor.

        Parameters
        ----------
        directory : Union[str, Path], optional
            Directory where the SLURM script and output files will be stored,
            defaults to /slurm.
        scratch : bool, optional
            If True, the executor will use the /scratch directory for the
            execution of the experiments. Defaults to False. When true
            files will automatically be copied back to the original directory
            once the job is finished.
        **kwargs
            Additional keyword arguments to be passed to the SlurmHeader,
            these are the SLURM parameters for the job. Supports all the 
            arguments for sbatch, see https://slurm.schedmd.com/sbatch.html.
        """
        if safety_check:
            self.safety_check(frame_index=2)

        self.header = SlurmHeader()
        for key, value in kwargs.items():
            self.header.add(key, value)

        if directory is None:
            directory = 'slurm'
        self.directory = Path(directory)

        # Containers for commands to be executed before and after the main execution
        self._commands_pre_execution = []
        self._commands_post_execution = []

        # Special options
        self.ulimit = ulimit
        self.move_output_file = move_output_file
        self.scratch = scratch
        self.array_limit = array_limit

        # To kepe track of the special options for saving the config
        self.special_options = {
            'scratch': scratch,
            'ulimit': ulimit,
            'move_output_file': move_output_file,
            'array_limit': array_limit,
        }


    @classmethod
    def from_config(cls, path: Path, safety_check: bool = True, **kwargs) -> 'SlurmExecutor':

        if safety_check:
            cls.safety_check(frame_index=1)

        if not isinstance(path, Path):
            path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f'File {path} does not exist')
        if not path.suffix == '.json':
            raise ValueError(f'File {path} is not a json file')

        with open(path) as f:
            config = json.load(f)
        config.update(kwargs)

        pre_commands = config.pop('commands_pre_execution', list())
        post_commands = config.pop('commands_post_execution', list())

        instance = cls(**config, safety_check=False)
        instance._commands_pre_execution = pre_commands
        instance._commands_post_execution = post_commands
        return instance
        
    def to_config(self, path: Path | str) -> None:
        if not isinstance(path, Path):
            path = Path(path)
        config = self.header.to_dict()
        config.update(self.special_options)

        config['commands_pre_execution'] = self._commands_pre_execution
        config['commands_post_execution'] = self._commands_post_execution

        with open(path, 'w') as f:
            json.dump(config, f, indent=4)

    @classmethod
    def from_profile(cls, name: str, safety_check: bool = True, **kwargs) -> 'SlurmExecutor':
        """
        Create a new SlurmExecutor from a profile.

        Parameters
        ----------
        name : str
            Name of the profile.
        safety_check : bool, optional
            If True, a safety check will be performed to ensure that the executor
            is not instantiated on a script that is not the main script. Defaults to True.
        **kwargs
            Additional keyword arguments to be passed to the SlurmExecutor.
        """
        if safety_check:
            cls.safety_check(frame_index=2)            
            kwargs.pop("safety_check", None)

        spm = SlurmProfileManager()
        profile = spm.get_profile_path(name)
        return cls.from_config(profile, **kwargs, safety_check=False)

    def _single_execute(self) -> None:
        raise NotImplementedError('Single execution is not supported for SLURM Executor, everything is executed with _sequence execute.')
        
    def _sequence_execute(
        self,
        experiments: List[Experiment],
        dry: bool = False,
        execution_directory: Union[Path, str] = None,
    ) -> List[FutureResult]:
        """
        Execute a sequence of experiments as an array job.

        Parameters
        ----------
        experiments : List[Experiment]
                List of experiments to be executed.
        dry : bool, optional
                If True, the script will be printed instead of executed.
        execution_directory : Union[Path, str], optional
                Directory where the experiments will be executed.

        Returns
        -------
        List[FutureResult]
                List of FutureResult objects.
        """

        if len(experiments) == 0:
            return []
        
        # Dump config:
        self.directory.mkdir(parents=True, exist_ok=True)
        index = len(list(self.directory.glob('config*.json')))
        path = self.directory / f'config_{index}.json'
        self.to_config(path)

        header = self.header.copy()
        if self.array_limit is not None:
            array_limit = min(self.array_limit, len(experiments))
        else:
            array_limit = len(experiments)

        header.add('array', f'0-{len(experiments)-1}%{array_limit}')

        body = self._make_slurm_body(experiments)

        count = len(list(self.directory.glob('submit*.sh')))
        script = SlurmScript(header, body, directory=self.directory, name=f'submit_{count}.sh')
        if dry:
            print(script)
            return [FutureResult() for _ in experiments]

        script.write()

        job_id = script.submit()
        for experiment in experiments:
            experiment.update_status('submitted')

        return [FutureResult(info={'job_id': job_id}) for _ in experiments]

    def _bash_array_str(self, strings: List[str]) -> str:
        """
        Convert a list of strings into a nicely formatted bash array of string.

        Parameters
        ----------
        strings : List[str]
            List of strings to be converted.

        Returns
        -------
        str
            A python string representing a bash array of strings.
        """
        bash_str = ' \n\t'.join(strings)
        return f'(\n\t{bash_str}\n)'

    def _body_add(self, command: str, when: Optional[Literal['pre', 'post']] = None) -> None:
        """
        Add a command to the body of the SLURM script.

        Parameters
        ----------
        command : str
            Command to be added to the body.
        """
        if when is None:
            when = 'pre'

        if when == 'pre':
            self._commands_pre_execution.append(command)
        
        elif when == 'post':
            self._commands_post_execution.append(command)

    def _make_slurm_body(self, experiments: List[Experiment]) -> SlurmBody:
        """
        Make a new SlurmBody object.

        Returns
        -------
        SlurmBody
            A new SlurmBody object.
        """

        identifiers = [str(experiment.identifier) for experiment in experiments]
        directories = [str(experiment.directory.resolve()) for experiment in experiments]

        body = SlurmBody()

        body.add(f'directories={self._bash_array_str(directories)}')
        body.add(f'identifiers={self._bash_array_str(identifiers)}')

        if self.move_output_file:
            self._body_add(r"mv slurm-${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}.out ${directories[$SLURM_ARRAY_TASK_ID]}", when='pre')
        if self.ulimit != 'default':
            self._body_add(f'ulimit -Su {self.ulimit}', when='pre')

        for command in self._commands_pre_execution:
            body.add(command)

        # Slurm info command:
        command = r'hex slurm add-info -d ${directories[$SLURM_ARRAY_TASK_ID]} -j "${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"'
        body.add(command)

        # Execution command
        command = r'hex execute ${directories[$SLURM_ARRAY_TASK_ID]}'

        if self.scratch:
            command += ' -e /scratch/$SLURM_JOB_ID'

        body.add(command)

        for command in self._commands_post_execution:
            body.add(command)

        if self.scratch:
            body.add(
                r'cp -r /scratch/$SLURM_JOB_ID/* ${directories[$SLURM_ARRAY_TASK_ID]}'
            )

        return body

    @staticmethod
    def safety_check(frame_index: int = 2) -> None:
        """
        Check if the executor is being called from the main script.

        Parameters
        ----------
        frame_index : int, optional
            Index of the frame to be checked. Defaults to 2.
        
        Raises
        ------
        SlurmSafetyError
            If the executor is not being called from the main script.

        Frame index depends on which creation method is used:
        - from_profile: 2
        - from_config: 1
        - __init__: 0
        """

        caller_frames = inspect.stack()
        caller_frame = caller_frames[frame_index]
        caller_module = inspect.getmodule(caller_frame[0])

        if caller_module and caller_module.__name__ != "__main__" or caller_module is None:
            raise SlurmSafetyError("""SlurmExecutor should only be called from the main script.
            If the you really want, you can disable this check. This error may be caused by not having
            a 'if __name__ == "__main__":' block in the main script.""")


