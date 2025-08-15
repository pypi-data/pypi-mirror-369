from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Union

import dill


class ExperimentError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


@dataclass
class ExperimentResult:
    result: Union[Any, ExperimentError]
    status: Literal['completed', 'failed']
    name: str = 'result'
    extension: str = 'pkl'
    info: Any = None

    def __post_init__(self) -> None:
        if self.status not in ['completed', 'failed']:
            raise ValueError(f'Invalid status: {self.status}')

    @staticmethod
    def get_path(
        directory: Union[Path, str], name: str = 'result', extension: str = 'pkl'
    ) -> Path:
        path = Path(directory) / f'{name}.{extension}'
        return path

    def dump(self, directory: Union[str, Path]) -> None:
        path = self.get_path(directory, self.name, self.extension)
        with open(path, 'wb') as f:
            dill.dump(self, f)
        return

    @classmethod
    def load(
        cls, directory: Union[Path, str], name: str = 'result', extension: str = 'pkl'
    ) -> 'ExperimentResult':
        path = cls.get_path(directory, name, extension)
        with open(path, 'rb') as f:
            result = dill.load(f)
        return result


class FutureResult(ExperimentResult):
    
    def __init__(
        self, name: str = 'future', extension: str = 'pkl', info: Any = None
    ) -> None:
        super().__init__(None, 'pending', name, extension, info)

    def __post_init__(self) -> None:
        pass

    

class DryResult(ExperimentResult):
    def __init__(
        self, name: str = 'dry', extension: str = 'pkl', info: Any = None
    ) -> None:
        super().__init__(None, 'dry', name, extension, info)

    def __post_init__(self) -> None:
        pass
