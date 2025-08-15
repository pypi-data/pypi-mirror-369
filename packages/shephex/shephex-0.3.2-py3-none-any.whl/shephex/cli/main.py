import rich_click as click

from shephex.cli.execute import execute
from shephex.cli.report import report
from shephex.cli.slurm.slurm import slurm
from shephex.cli.study import study_cli


@click.group()
@click.version_option()
def cli() -> None:
    """shephex CLI"""
    ... # pragma: no cover


cli.add_command(report)
cli.add_command(execute)
cli.add_command(slurm)
cli.add_command(study_cli)
