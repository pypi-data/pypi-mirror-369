import re
import subprocess
from pathlib import Path

from shephex.executor.slurm import SlurmBody, SlurmHeader


class SlurmScript:
    def __init__(
        self,
        header: SlurmHeader,
        body: SlurmBody,
        directory: Path,
        name: str = 'submit.sh',
    ) -> None:
        """
        Slurm script object, consisting of a header and body.

        Parameters:
        -----------
        header : SlurmHeader
            Header portion of the script
        body : SlurmBody
            Body portion of the script
        directory : Path
            Directory to write the script to.
        """

        self.header = header
        self.body = body
        self.directory = directory
        self.name = name

    def __repr__(self) -> str:
        return str(self.header) + 2 * '\n' + str(self.body) + '\n'

    @property
    def path(self) -> Path:
        return self.directory / self.name

    def write(self) -> bool:
        """
        Write the script to the specified directory.
        """
        self.directory.mkdir(parents=True, exist_ok=True)

        with open(self.path, 'w') as f:
            f.write(str(self))

    def submit(self, command: str = 'sbatch') -> int:
        """
        Submit the script to the Slurm scheduler.

        Parameters:
        -----------
        command : str
            Command to use to submit the script. Default is 'sbatch'.
        Returns:
        --------
        job_id : int
            Job ID of the submitted
        """
        
        if not self.path.exists():
            self.write()

        command = [command, str(self.name)]
        result = subprocess.check_output(command, cwd=self.directory)
        job_id = int(re.search(r'\d+', str(result)).group())

        return job_id
