from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union

from shephex.experiment.context import ExperimentContext
from shephex.experiment.options import Options
from shephex.experiment.result import ExperimentResult


class Procedure(ABC):
    """
    Procedure base-class.
    """
    def __init__(self, name: str, context: bool = False) -> None:
        self.name = name
        self.context = context

    @abstractmethod
    def dump(self, directory: Union[Path, str]) -> None:
        pass  # pragma: no cover

    @classmethod
    @abstractmethod
    def from_metadata(cls, metadata: dict) -> 'Procedure':
        return cls._from_metadata(metadata)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @abstractmethod
    def _execute(
        self,
        options: Options,
        directory: Optional[Union[Path, str]] = None,
        context: Optional[ExperimentContext] = None,
    ) -> ExperimentResult:
        pass  # pragma: no cover

    @abstractmethod
    def hash(self) -> int:
        pass  # pragma: no cover

    def __hash__(self) -> int:
        return self.hash()

    def __eq__(self, other: 'Procedure') -> bool:
        return self.hash() == other.hash()
    
    def get_metadata(self) -> dict:
        return {
            'name': self.name,
            'context': self.context,
        }
