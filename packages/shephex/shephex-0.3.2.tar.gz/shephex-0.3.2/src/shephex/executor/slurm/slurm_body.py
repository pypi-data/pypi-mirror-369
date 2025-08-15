from typing import List, Self, Union


class SlurmBody:
    def __init__(self, commands: Union[List, str] = None) -> None:
        """
        Body portion of a Slurm script. That is the commands that will be executed,
        e.g.
            "python my_script.py"

        Note these are generally not checked for correctness.

        Parameters
        ----------
        commands : Union[List, str], optional
            List of commands to be executed, by default None
        """
        self.commands = []

        if commands is not None:
            self.add(commands)

    def add(self, command: Union[List[str], str]) -> None:
        """
        Add a command to the body

        Parameters
        ----------
        command : Union[List, str]
            Command to be added
        """
        if isinstance(command, list):
            if not all(isinstance(c, str) for c in command):
                raise TypeError('All commands must be strings')
            self.commands.extend(command)
        else:
            if not isinstance(command, str):
                raise TypeError('Command must be a string')
            self.commands.append(command)

    def __repr__(self) -> str:
        return '\n'.join(self.commands)

    def __add__(self, other: Self) -> Self:
        """
        Concatenate two SlurmBody objects. Order of operations matters!

        Parameters
        ----------
        other : Self
            SlurmBody object to concatenate with.
        """
        body = SlurmBody()
        body.commands = self.commands + other.commands
        return body