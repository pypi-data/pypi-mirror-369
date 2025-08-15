import json
import shutil
from pathlib import Path


class SlurmProfileManager:

    def __init__(self) -> None:
        self.settings_directory = Path.home() / '.shephex/'
        self.settings_directory.mkdir(exist_ok=True)
        self.settings_path = self.settings_directory / 'slurm_profile_manager.json'
                
        self.settings = self.load_settings()
        self.profile_directory = Path(self.settings['profile_directory'])
        self.profile_directory.mkdir(exist_ok=True)

    def load_settings(self) -> dict:
        if self.settings_path.exists():
            with open(self.settings_path) as f:
                settings = json.load(f)
        else:
            settings = {"profile_directory": str(self.settings_directory / 'slurm_profiles')}
            with open(self.settings_path, 'w') as f:
                json.dump(settings, f, indent=4)

        return settings
    
    def get_profile_directory(self) -> Path:
        return self.profile_directory
    
    def get_all_profiles(self) -> list[Path]:
        return list(self.profile_directory.glob('*.json'))
    
    def get_profile_path(self, name: str) -> Path:
        if not name.endswith('.json'):
            name = name + '.json'

        path = self.profile_directory / name
        if not path.exists():
            raise FileNotFoundError(f'Profile {name} not found in {self.profile_directory}')
        
        return path
    
    def get_profile(self, name: str) -> dict:
        path = self.get_profile_path(name)
        with open(path) as f:
            return json.load(f)

    def add_profile(self, file: Path, name: str, overwrite: bool) -> None:
        directory = self.get_profile_directory()

        if not file.suffix == '.json':
            raise ValueError('Profile file must be a json file.')
    
        if name is None:
            name = Path(file).stem

        new_path = (directory / name).with_suffix('.json')

        if new_path.exists() and not overwrite:
            raise FileExistsError(f'Profile {name} already exists in {directory}')
        else:
            shutil.copy(file, new_path)