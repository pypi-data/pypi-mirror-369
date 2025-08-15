"""
Defines the ChainableExperimentIterator class, which can be used to define sets of experiments.
"""
from collections.abc import Iterator
from pathlib import Path
from typing import Callable, Self, Union

from shephex.experiment import Experiment, Options
from shephex.study import Study


class ChainableExperimentIterator(Iterator):
    """
    An iterator that can be used to define sets of experiments with a chainable interface.
    """
    def __init__(self, function: Union[Callable, str, Path], directory: Union[Path, str]) -> None:
        """

        Parameters
        ----------
        function : Union[Callable, str, Path]
            The function to be executed
        directory : Union[Path, str]
            The directory where the experiments will be saved.    
        """
        self.function = function
        self.directory = Path(directory)
        self.options = []
        self.index = -1

    def add(self, *args, zipped: bool = False, permute: bool = True, **kwargs) -> Self:
        """
        Add one or more options to the iterator.

        Parameters
        ----------
        args : Iterable
            Positional arguments to be added.
        zipped : bool, optional
            If True, arguments are added in order - no permutation of arguments is done, by default False
            This is analogous to Python's zip function.
        permute : bool, optional
            If True, arguments are permuted with other arguments and previous options to yield 
            all possible combinations, by default True
        kwargs : Dict
            Key-word arguments to be added.        
        """
        if zipped or not permute:
            self._zipped_add(*args, **kwargs)
        else:
            self._permute_add(*args, **kwargs)

        return self
    
    def zip(self, *args, **kwargs) -> Self:
        """
        Add arguments in order. 

        All positional arguments and key-word arguments must have the same number 
        of elements. If some options are already configured, the number of elements 
        must match the number of elements in the previously added options.

        Parameters
        ----------
        args : Iterable
            Positional arguments to be added.
        kwargs : Dict
            Key-word arguments to be added.        
        """
        return self.add(*args, zipped=True, permute=False, **kwargs)
    
    def permute(self, *args, **kwargs) -> Self:
        """
        Add arguments permutationally.

        Arguments are permuted with other arguments and previous options to yield
        all possible combinations.

        Parameters
        ----------
        args : Iterable
            Positional arguments to be added.
        kwargs : Dict 
            Key-word arguments to be added.
        """
        return self.add(*args, zipped=False, permute=True, **kwargs)
    
    def _zipped_add(self, *args, **kwargs):
        """
        Add options 'strictly' meaning that all arguments and keyword arguments 
        must have the same number of elements in their iterables.
        """

        arg_elements = []
        for iterable in args:
            arg_elements.append(len(iterable))

        for iterable in kwargs.values():
            arg_elements.append(len(iterable))

        n_elements = arg_elements[0]
    
        if not all([arg_element == n_elements for arg_element in arg_elements]):
            raise ValueError("Number of elements in passed arguments and key-word arguments is not equal")

        if len(self.options) > 0 and n_elements != len(self.options):
            raise ValueError("When adding strict options the number of values for added options must equal the number for previously added values.")

        if len(self.options) == 0:
            self.options = [Options() for _ in range(n_elements)]

        for kwarg, values in kwargs.items():                
            for options, value in zip(self.options, values):
                options.add_kwarg(kwarg, value)

        for arg_values in args:
            for option, value in zip(self.options, arg_values):
                option.add_arg(value)

    def _permute_add(self, *args, **kwargs):
        """
        Add options permutationally. 
        """

        # Deal with the case where this is the first options added.
        if len(self.options) == 0:
            if len(args) != 0:
                self._zipped_add(args[0])
                args = args[1:]
            else:
                key = list(kwargs.keys())[0]
                self._zipped_add(**{key: kwargs.pop(key)})

        if len(args) == 0 and len(kwargs) == 0:
            return 

        # Make permutations
        new_options = []
        for kwarg, kwarg_values in kwargs.items():
            for value in kwarg_values:
                for option in self.options:
                    option_new = option.copy()
                    option_new.add_kwarg(key=kwarg, value=value)
                    new_options.append(option_new)

        for arg_values in args:
            for value in arg_values:
                for option in self.options:
                    option_new = option.copy()
                    option_new.add_arg(value=value)
                    new_options.append(option_new)

        self.options = new_options

    def __iter__(self) -> Self:
        self.index = 0
        self.study = Study(path=self.directory, refresh=True)
        experiments = []
        for options in self.options:
            experiment = Experiment(*options.args, function=self.function, **options.kwargs, root_path=self.directory)
            self.study.add_experiment(experiment=experiment)
            experiments.append(experiment)
        self._experiments = self.study.get_experiments(status='pending', loaded_experiments=experiments)

        return self

    def __next__(self) -> Experiment:
        if self.index < len(self._experiments):
            experiment = self._experiments[self.index]
            self.index += 1
            return experiment
        else:
            raise StopIteration
        
    def __len__(self) -> int:
        return len(self.options)