from copy import deepcopy
from typing import Tuple

from shephex.executor.slurm.slurm_options import valid_options

flags = [str(option[0]).replace('-', '') for option in valid_options]
long_flags = [option[1].replace('--', '') for option in valid_options]


class HeaderOption:
    def __init__(self, key: str, value: str) -> None:
        """
        A single header option for a Slurm script
        Slurm script, e.g.
            #SBATCH --partition=<partition>

        Checked for correctness against 'valid_options'.

        Parameters
        ----------
        key : str
            Option key, such as 'partition'
        value : str
            Option value, such as 'gpu'
        """

        self.key, self.option_index = self.get_name_and_index(key)
        self.value = value

    def __repr__(self) -> str:
        return f'#SBATCH --{self.key}={self.value}'

    def __str__(self) -> str:
        return self.__repr__()

    @staticmethod
    def get_name_and_index(item: str) -> Tuple[str, int]:
        item = item.replace('_', '-')
        if item in flags:
            index = flags.index(item)
            return long_flags[index], index
        elif item in long_flags:
            index = long_flags.index(item)
            return item, index
        else:
            raise ValueError(f'Invalid option: {item}')


class SlurmHeader:
    def __init__(self) -> None:
        """
        Header portion of a Slurm script, consisting of a list of header options.
        """
        self.options = []

    def add(self, key: str, value: str) -> None:
        """
        Add a header option to the header.
        Raises an error if the option already exists.

        Parameters
        ----------
        key : str
            Option key, such as 'partition'
        """
        option = HeaderOption(key, value)

        for i, existing_option in enumerate(self.options):
            if option.option_index == existing_option.option_index:
                raise ValueError(
                    f"Option '{key}' already exists in header options ({existing_option.key})"
                )

        self.options.append(option)

    def __repr__(self) -> str:
        s = '#!/bin/sh'
        for option in self.options:
            s += '\n' + str(option)
        return s

    def copy(self) -> 'SlurmHeader':
        return deepcopy(self)
    
    def to_dict(self) -> dict:
        return {option.key: option.value for option in self.options}
