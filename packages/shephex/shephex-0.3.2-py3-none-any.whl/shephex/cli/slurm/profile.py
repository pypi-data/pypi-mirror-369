from pathlib import Path

import rich
import rich_click as click
from rich.table import Table

from shephex.cli.slurm.slurm import slurm
from shephex.executor.slurm import SlurmExecutor, SlurmProfileManager


@slurm.group()
def profile() -> None:
    """
    Manage SLURM profiles.
    """
    ... # pragma: no cover


@profile.command()
@click.argument(
    'path', required=False, type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
def directory(path: click.Path) -> None:
    """
    Set the default directory for Slurm profiles. If no path is provided, the current default directory is printed.
    """
    if path is None:
        spm = SlurmProfileManager()
        click.echo(spm.get_profile_directory())
        return


@profile.command()
@click.argument(
    'file_name',
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
)
@click.option(
    '--name',
    '-n',
    help='Name of the profile. If not provided, the name of the file will be used.',
    default=None,
)
@click.option(
    '--overwrite',
    '-o',
    is_flag=True,
    help='Overwrite the profile if it already exists.',
    default=False,
)
def add(file_name: Path, name: str, overwrite: bool) -> None:
    """
    Add a new SLURM profile.
    """
    spm = SlurmProfileManager()
    spm.add_profile(file_name, name, overwrite)


@profile.command(name='list')
def list_profiles() -> None:
    """
    List all available SLURM profiles.
    """
    spm = SlurmProfileManager()
    profiles = spm.get_all_profiles()

    table = Table(title='SLURM Profiles')
    table.add_column('Name')
    table.add_column('Full Path')

    for profile in profiles:
        table.add_row(profile.stem, str(profile))

    rich.print(table)


@profile.command(name='print')
@click.argument('name')
@click.option(
    'as_dict',
    '--dict',
    is_flag=True,
    help='Print the profile as a dictionary.',
    default=False,
)
def print_profile(name: str, as_dict: bool) -> None:
    """
    Print the contents of a SLURM profile.
    """
    spm = SlurmProfileManager()
    profile = spm.get_profile(name)
    if as_dict:
        rich.print(profile)
        return

    executor = SlurmExecutor.from_profile(name, safety_check=False)
    rich.print(executor.header)
    rich.print(executor._make_slurm_body([]))


@profile.command()
@click.argument('name')
def delete(name: str) -> None:
    """
    Delete a SLURM profile.
    """
    spm = SlurmProfileManager()
    profile = spm.get_profile_path(name)
    profile.unlink()
    click.echo(f'Profile {name} deleted.')
