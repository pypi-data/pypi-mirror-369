from pathlib import Path

import rich_click as click

from shephex import Experiment
from shephex.executor import LocalExecutor
from shephex.experiment.status import Pending, Submitted


@click.command(name='execute')
@click.argument(
    'directory', type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.option(
    '-e',
    '--execution-directory',
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=None,
)
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose output.', default=False)
def execute(directory: click.Path, execution_directory: click.Path, verbose: bool) -> None:
    """
    Execute an experiment.
    """
    directory = Path(directory)

    if verbose:
        print(f'Loading experiment from {directory}')

    experiment = Experiment.load(directory)
    executor = LocalExecutor()

    if execution_directory is not None:
        execution_directory = Path(execution_directory)

    executor.execute(experiment, execution_directory=execution_directory, 
                     valid_statuses=[Pending(), Submitted()])
