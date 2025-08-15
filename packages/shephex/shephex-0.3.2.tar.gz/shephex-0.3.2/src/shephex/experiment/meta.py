import json
from pathlib import Path
from typing import Self


class Meta(dict):
    def __init__(self, name: str ='meta.json', **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = name

    def dump(self, directory: Path) -> None:
        with open(directory / self.name, 'w') as f:
            json.dump(self, f, indent=4)

    def load(self, directory: Path) -> None:
        with open(directory / self.name, 'r') as f:
            data = json.load(f)
            for key, value in data.items():
                self.update(key, value)

    def update(self, key: str, value: str) -> None:
        self[key] = value

    @classmethod
    def from_file(cls, directory: Path, retries: int = 0) -> Self:
        meta = cls()
        try:
            meta.load(directory)
        except: # noqa: E722 - should fix but..
            print(f"Directory: {directory} was unreadable, check the job. Exiting")
            raise ValueError()
        return meta

    def get_dict(self) -> dict:
        return dict(self.copy())
