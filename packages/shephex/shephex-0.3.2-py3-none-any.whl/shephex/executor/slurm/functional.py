from pathlib import Path
from typing import Iterable, Optional

from shephex import Experiment
from shephex.executor.slurm import SlurmExecutor


def slurm_execute(experiments: Experiment | Iterable[Experiment],
                  directory: Optional[Path | str] = None, 
                  profile: Optional[str] = None,
                  config: Optional[Path | str] = None,
                  **kwargs) -> None:    
    """
    Execute experiments on a Slurm cluster. 

    Parameters
    ----------
    experiments : Experiment | Iterable[Experiment]
        The experiment(s) to execute.
    directory : Path | str, optional
        The directory where the Slurm submission script will be written. If not 
        provided, the script will be written to the `slurm` directory within the
        first experiment's root directory.
    profile : str, optional
        The name of the Slurm profile to use. If provided, the executor will be
        created using the profile configuration.
    config : Path | str, optional
        The path to a Slurm configuration file. If provided, the executor will be
        created using the configuration file.
    **kwargs
        Additional keyword arguments to pass to the SlurmExecutor constructor.
        These will override any values set in the profile or configuration file.
        If no profile or configuration file is provided, these arguments are
        required.
    """
    
    if isinstance(experiments, Experiment):
        experiments = [experiments]
    
    if directory is None:
        directory = experiments[0].root_path / 'slurm'

    if profile is not None:
        executor = SlurmExecutor.from_profile(profile, directory=directory, **kwargs)
    elif config is not None:
        executor = SlurmExecutor.from_config(config, directory=directory, **kwargs)
    else:
        executor = SlurmExecutor(directory=directory, **kwargs)

    executor.execute(experiments)
    