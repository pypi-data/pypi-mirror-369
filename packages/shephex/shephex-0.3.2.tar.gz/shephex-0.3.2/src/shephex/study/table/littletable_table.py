from typing import Any, Dict, List

from littletable import Table


def safe_getattr(obj: Any, attr: str) -> Any:
    try:
        return getattr(obj, attr)
    except AttributeError:
        return None


class LittleTable:
    def __init__(self) -> None:
        self.table = Table()
        self.table.add_field('identifier', fn=None, default=None)
        self.table.add_field('status', fn=None, default=None)
        self.table.create_index('identifier')

        self.column_names = ['identifier', 'status']

    def add_column(self, name: str) -> None:
        """
        Add a new column to the table. The column will be filled with None values.
        """
        self.table.add_field(name, fn=None, default=None)
        self.column_names.append(name)

    def add_row(self, row_data: Dict, add_columns: bool = False) -> None:
        for key in row_data.keys():
            if key not in self.column_names:
                self.add_column(key)

        self.table.insert(row_data)

    def contains_row(self, row_data: Dict) -> bool:
        """
        Check if the table contains a row with the same data.
        """
        # Check for the identifier
        contains_id = len(self.table.where(identifier=row_data['identifier'])) > 0
        if contains_id:
            return True

        # Check if any row contains the same data
        unchecked_keys = [
            'identifier',
            'status',
            'time_stamp',
            'procedure_path',
            'options_path',
            'procedure'
        ]
        checked_row = {
            key: row_data[key] for key in row_data if key not in unchecked_keys
        }
        contains_data = len(self.table.where(**checked_row)) > 0
        
        if contains_data:
            return True

        return False

    def get_row_match(self, identifier: str) -> Dict:
        # First find the corresponding row with the identifier
        match_list = self.table.where(identifier=identifier)
        if len(match_list) > 1 or len(match_list) == 0:
            raise ValueError(
                f'Found {len(match_list)} rows with the identifier {identifier}.'
            )

        match = match_list[0]
        return match

    def update_row(self, row_data: Dict) -> None:
        """
        Update the row in the table.
        """
        match = self.get_row_match(row_data['identifier'])
        self.table.remove(match)
        self.add_row(row_data)

    def update_row_partially(self, row_data: Dict) -> None:
        match = self.get_row_match(row_data['identifier'])
        for key in self.column_names:
            if key not in row_data.keys():
                row_data[key] = safe_getattr(match, key)

        self.table.remove(match)
        self.add_row(row_data)

    def where(self, *args, **kwargs) -> List[Dict]:
        """
        Return identifiers of rows that match the query.
        """
        return [row.identifier for row in self.table.where(*args, **kwargs)]