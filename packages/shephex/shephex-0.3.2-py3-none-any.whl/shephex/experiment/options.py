import json
from pathlib import Path
from typing import Dict, List, Self, Tuple, TypeAlias, Union


class Options:
    base_types: TypeAlias = Union[int, float, str, bool]
    collection_types: TypeAlias = Union[List, Dict, Tuple]

    def __init__(self, *args, **kwargs) -> None:
        self._args = []
        self._kwargs = {}

        for arg in args:
            self.add_arg(arg)

        for key, value in kwargs.items():
            self.add_kwarg(key, value)


    def _check_type(self, value: Union[base_types, collection_types]):
        valid_type = False
        if isinstance(value, self.base_types):
            valid_type = True
        elif isinstance(value, self.collection_types):
            # Check that keys and values are of base types
            valid_type = True
            if isinstance(value, Dict):
                for k, v in value.items():
                    if not isinstance(k, self.base_types) or not isinstance(
                        v, self.base_types
                    ):
                        valid_type = False
                        break
            else:
                for v in value:
                    if not isinstance(v, self.base_types):
                        valid_type = False
                        break

        if not valid_type:
            raise TypeError(f'Invalid type {type(value)}')

    def __repr__(self) -> str:
        return f'ExperimentOptions(args={self._args}, kwargs={self._kwargs})'

    def dump(self, path: Union[str, Path]) -> None:
        if isinstance(path, str):
            path = Path(path)

        all_options = {'kwargs': self._kwargs, 'args': self._args}

        with open(path / self.name, 'w') as f:
            json.dump(all_options, f, indent=4)

    def to_dict(self) -> Dict:
        options_dict = {**self._kwargs}

        if len(self._args) > 0:
            options_dict['args'] = self._args
        return options_dict

    @property
    def name(self) -> str:
        return 'options.json'

    @classmethod
    def load(cls, path: Union[str, Path], name: str = 'options.json') -> Self:
        if isinstance(path, str):
            path = Path(path)

        with open(path / name, 'r') as f:
            all_options = json.load(f)

        args = all_options.pop('args')
        kwargs = all_options.pop('kwargs')

        return cls(*args, **kwargs)

    def __eq__(self, other: Self) -> bool:
        if not isinstance(other, Options):
            return False

        if self._kwargs != other.kwargs:
            return False

        if self._args != other._args:
            return False

        return True

    def items(self) -> List[Tuple[str, Union[base_types, collection_types]]]:
        all_dict = self._kwargs.copy()
        if len(self._args) > 0:
            all_dict['args'] = self._args
        return all_dict.items()

    def keys(self) -> List[str]:
        all_keys = list(self._kwargs.keys())
        if len(self._args) > 0:
            all_keys.append('args')
        return all_keys

    def values(self) -> List[Union[base_types, collection_types]]:
        for key in self.keys():
            if key == 'args':
                yield self._args
            else:
                yield self._kwargs[key]

    def __getitem__(self, key: str) -> Union[base_types, collection_types]:
        if key == 'args':
            return self._args
        return self._kwargs[key]

    @property
    def kwargs(self) -> Dict:
        return self._kwargs

    @property
    def args(self) -> List:
        return self._args

    def add_kwarg(self, key: str, value: Union[base_types, collection_types]) -> None:
        self._check_type(value)
        if key not in self._kwargs.keys():
            self._kwargs[key] = value
        else:
            raise ValueError(f"Keyword argument {key} already exist")
    
    def add_arg(self, value: Union[base_types, collection_types]) -> None:
        self._check_type(value)
        self._args.append(value)

    def copy(self) -> Self:
        return Options(*self.args, **self.kwargs)

