from pathlib import Path
from typing import List

import rich_click as click

from shephex.cli.slurm.slurm import slurm
from shephex.experiment import Experiment, ExperimentContext, Meta


def get_job_id(directory: Path) -> str:
    context = ExperimentContext(directory / Experiment.shep_dir)
    job_id = context.meta.get('job-id', None)
    return job_id

def get_job_status(directory: Path) -> str:
    meta = Meta.from_file(directory / Experiment.shep_dir)
    return meta.get('status')

@slurm.command()
@click.argument("directories", type=click.Path(exists=True, file_okay=False, dir_okay=True), nargs=-1)
@click.option("-p", '--print_only', is_flag=True, help="Print the command without executing it", default=False)
def cancel(directories: List[click.Path], print_only: bool) -> None:
    """
    Cancel a job
    """
    job_ids = []
    for directory in directories:
        directory = Path(directory)
        job_id = get_job_id(directory)
        status = get_job_status(directory)

        print(job_id, status)
        if status != 'running':
            print(f"Job in {directory} is not running")
            continue
        if job_id is not None:
            job_ids.append(job_id)



    if len(job_ids) == 0:
        print("No job-ids found")
        return
    
    job_ids = list(set(job_ids))
    command = ['scancel'] + job_ids
    command = " ".join(command)

    if print_only:
        print(command)
