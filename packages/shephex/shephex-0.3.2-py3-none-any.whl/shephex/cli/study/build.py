from pathlib import Path

import rich_click as click

from shephex.cli.study.main import study_cli
from shephex.study import Study


@study_cli.command("build")
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--avoid-duplicates",
    is_flag=True,
    default=False,
    help="Avoid duplicates in the study.",
)
@click.option('dump_path', '--dump-path', type=click.Path(), default=None, help="Path to dump the study.")
def build_study(
    directory: Path,
    avoid_duplicates: bool,
    dump_path: Path | None,
) -> None:
    """
    Build a study from the given directory.
    """
    study = Study(directory, refresh=False, avoid_duplicates=avoid_duplicates)
    study.refresh(clear_table=True, progress_bar=True)
    study.dump(path=dump_path)
