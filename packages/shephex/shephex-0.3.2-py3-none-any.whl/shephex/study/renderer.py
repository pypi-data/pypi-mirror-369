from typing import Any

from rich.console import Console
from rich.table import Table

from shephex.study.study import Study


def safe_getattr(obj: Any, attr: str) -> Any:
    try:
        return getattr(obj, attr)
    except AttributeError:
        return None
    
class StudyRenderer:

    def __init__(self, excluded: list[str] = None) -> None:
        self.excluded = ['procedure', 'options_path', 'time_stamp', 'procedure_type', 'procedure_path']
        self.capitalize_fields = ['identifier', 'status']
        if excluded is not None:
            self.excluded += excluded
        self.conditions = {}

    def add_condition(self, **kwargs) -> None:
        self.conditions.update(kwargs)

    def initialize_table(self, study: Study, **kwargs) -> None:
        rich_table = Table(**kwargs)
        for field in study.table.column_names:
            if field in self.excluded:
                continue
            if field in self.capitalize_fields:
                field = field.capitalize()                    

            rich_table.add_column(field, justify='center')
        return rich_table
    
    def get_rows(self, study: Study) -> list:
        # Janky code to sort by time stamp.
        rows = [row for row in study.table.table]
        time_stamps = [row.time_stamp for row in rows]
        sorted_indices = sorted(range(len(time_stamps)), key=lambda k: time_stamps[k])
        rows = [rows[i] for i in sorted_indices]
        return rows

    def get_table(self, study: Study, **kwargs) -> Table:
        style_dict = {
            'pending': 'yellow',
            'running': 'blue',
            'completed': 'green',
            'failed': 'red',
        }

        rich_table = self.initialize_table(study, **kwargs)
        rows = self.get_rows(study)        
        allowed_identifiers = study.table.where(**self.conditions)

        # Add rows to the rich.Table
        for row in rows:
            if row.identifier not in allowed_identifiers:
                continue

            row_data = []
            for name in study.table.column_names:
                if name in self.excluded:
                    continue
                if name == 'status':
                    row_data.append(row.status.capitalize())
                else:
                    row_data.append(str(safe_getattr(row, name)))
            rich_table.add_row(
                *row_data, style=style_dict.get(row.status.lower(), 'white')
            )

        return rich_table

    def render_study(self, study: Study, **kwargs) -> None:
        rich_table = self.get_table(study, **kwargs)

        # Decide whether to return the table or print # noqa
        console = Console()
        console.print(rich_table)