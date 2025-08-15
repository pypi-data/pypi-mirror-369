from pathlib import Path
from time import sleep

import rich_click as click
from littletable import Table as LittleTable
from rich import print
from rich.console import group
from rich.live import Live
from rich.table import Table

from shephex.experiment.context import ExperimentContext
from shephex.study import Study, StudyRenderer


class LiveReport:
    def __init__(self, directory: Path) -> None:
        self.study = Study(directory, avoid_duplicates=False)
        self.experiments = self.study.get_experiments(
            status='all', load_procedure=False
        )

    def update_table(self, **kwargs) -> Table:
        for experiment in self.experiments:
            try:
                update_dict = {'identifier': experiment.identifier}
                # Update from meta file
                context = ExperimentContext(experiment.shephex_directory)
                update_dict.update(context.meta)

                # Update from meta file
                experiment.meta.load(experiment.shephex_directory)
                update_dict.update({'status': experiment.meta['status']})

                self.study.table.update_row_partially(update_dict)
            except Exception:  # pragma: no cover
                """
                Ignore exceptions for now.
                """
                pass


class ConditionParser:

    def __init__(self) -> None:
        self.types = {'int': int, 'float': float, 'str': str}

    def comma_seperated(self, value: str, val_type: str) -> list:
        values = value.split(',')
        return [self.types[val_type](value) for value in values]
    
    def dash_seperated(self, value: str, val_type: str) -> list:
        start, end = value.split('-')
        start = self.types[val_type](start)
        end = self.types[val_type](end)
        return start, end

    def parse_conditions(self, renderer: StudyRenderer, filters: list[tuple]) -> None:
        condition_attrs = [filt[0] for filt in filters]
        conditions = {attr: [] for attr in condition_attrs}
        condition_types = {attr: LittleTable.is_in for attr in condition_attrs}

        for key, value, ftype in filters:
            if ',' in value: # comma seperated
                conditions[key].extend(self.comma_seperated(value, ftype))
            elif '-' in value: # dash seperated
                start, end = self.dash_seperated(value, ftype)
                conditions[key] = [start, end]
                condition_types[key] = LittleTable.within
            else: 
                conditions[key].append(self.types[ftype](value))
                
        for key, values in conditions.items():
            if condition_types[key] == LittleTable.is_in:
                conditions[key] = condition_types[key](values)
            elif condition_types[key] == LittleTable.within:
                conditions[key] = condition_types[key](*values)


        renderer.add_condition(**conditions)

@click.command()
@click.argument('directories', type=click.Path(exists=True), nargs=-1)
@click.option('-rr', '--refresh-rate', type=float, default=1)
@click.option('--total-time', type=float, default=-1)
@click.option('-l', '--live', is_flag=True, default=True)
@click.option('-f', '--filters', nargs=3, multiple=True)
@click.option('-fr', '--filter-range', type=click.Tuple([str, float, float]), multiple=True, nargs=3)
def report(
    directories: list[Path], 
    refresh_rate: int, 
    total_time: int, 
    live: bool, 
    filters: tuple,
    filter_range: tuple[str, float, float]
) -> None:
    """
    Display a live report of the experiments in a directory.
    """
    if total_time > 0:
        iterator = range(int(total_time * refresh_rate))
    else:
        iterator = iter(int, 1)

    reports = {directory: LiveReport(directory) for directory in directories}
    renderer = StudyRenderer()

    condition_parser = ConditionParser()

    for filt in filter_range:
        converted = (filt[0], f"{filt[1]}-{filt[2]}", 'float')
        filters += (converted,)

    condition_parser.parse_conditions(renderer, filters)

    @group()
    def get_render_group():
        for directory, live_report in reports.items():
            kwargs = {'title': directory}
            live_report.update_table()
            yield renderer.get_table(live_report.study, **kwargs)

    if live:
        with Live(get_render_group(), refresh_per_second=refresh_rate) as live:
            for _ in iterator:                
                sleep(1 / refresh_rate)
                live.update(get_render_group())

    else:
        print(get_render_group())
