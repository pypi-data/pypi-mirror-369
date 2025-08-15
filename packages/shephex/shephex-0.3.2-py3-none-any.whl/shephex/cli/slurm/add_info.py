from pathlib import Path

import rich_click as click

from shephex.cli.slurm.slurm import slurm
from shephex.experiment import Experiment, ExperimentContext


@slurm.command()
@click.option("-j", "--job-id", type=str, required=True)
@click.option("-d", "--directory", type=click.Path(exists=True, file_okay=False, dir_okay=True), required=True)
def add_info(job_id: str, directory: click.Path) -> None:
    """
    Add information to a job
    """
    directory = Path(directory)
    context = ExperimentContext(directory / Experiment.shep_dir)
    try:
        context.meta.load(directory / Experiment.shep_dir)
    except FileNotFoundError:
        pass
    context.add('job-id', job_id)