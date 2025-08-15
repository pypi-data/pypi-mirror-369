import subprocess
from pathlib import Path
from typing import Union

import rich_click as click

from shephex.cli.slurm.slurm import slurm


def check_job_status(job_id: int) -> Union[str, None]: # pragma: no cover
    """
    Return the status of a given job id.
    """
    output = subprocess.check_output(['sacct', '-j', job_id, '--format', 'state, JobName', '--noheader']).decode('utf-8')
    output = output.split()

    if len(output) == 0:
        return None
    
    return output[0]

def find_output_file(job_id: int) -> str: # pragma: no cover
    """
    Return the path of the output file for a given job id.
    """
    status = check_job_status(job_id)

    if status is None:
        print(f"Job id {job_id} not found.")
        exit()
    elif status == "RUNNING":
        command = ["scontrol", "show", "job", job_id]
        output = subprocess.check_output(command).decode('utf-8')
        output = output.split()

        output_file = None
        for info in output:
            if 'StdOut' in info:
                output_file = info.split('=')[1]
                break    
    else:
        # We need to use sacct to find the output file
        # First determine the working directory
        command = ['sacct', '-j', job_id, '--format', 'workdir%-1000', '--noheader']
        output = subprocess.check_output(command).decode('utf-8')
        workdir = output.strip()

        # Now we need to read the submission script to find the output file
        command = ['sacct', '-B', '-j', job_id]
        output = subprocess.check_output(command).decode('utf-8')

        output = output.split('\n')

        found=False
        for line in output:

            if '#SBATCH --output' in line or 'SBATCH -o' in line:
                file_name = line.split('--output=')[1]

                if '_' in job_id:
                    job_id, arr_id = job_id.split('_')            
                    file_name = file_name.replace(r'%A', f'{job_id}')
                    file_name = file_name.replace(r'%a', f'{arr_id}')
                else:
                    file_name = file_name.replace(r'%A', f'{job_id}')
                found=True
                break

        if not found:
            # Then we assume that thee job was submitted with the default output file
            file_name=f"slurm-{job_id}.out"

        output_file = f"{workdir}/{file_name}"

        # CHeck if the file exists
        if not Path(output_file).exists():
            print(f"File {output_file} does not exist - Might be I wasn't able to find it correctly.")
            exit()

    return output_file

@slurm.command(name='open')
@click.argument("job_id", type=str)
@click.option("-c", "--command_call", type=str, help="Command to open file with", default="code")
@click.option("-p", "--print_path", help="Print the path of the file and exit.", is_flag=True)
def open_slurm(job_id: int, 
               command_call: str, 
               print_path: bool) -> None:
    """
    Open slurm output file for a given job id.
    """
    file_name = find_output_file(job_id)

    if print_path:
        print(file_name)
    else: # pragma: no cover
        command = [command_call, file_name]
        subprocess.call(command)