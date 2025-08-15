from pathlib import Path
from typing import Any, Union

from shephex.experiment.meta import Meta


class ExperimentContext:
    def __init__(self, directory: Union[Path, str], refresh: bool = True) -> None:
        self._directory = Path(directory)
        self.meta = Meta(name='context.json')
        if refresh:
            self.refresh()

    def __repr__(self) -> str:
        return 'ExperimentContext()'
    
    def refresh(self) -> None:
        try:
            self.meta.load(self.shephex_directory)
        except FileNotFoundError:
            pass

    @property
    def directory(self) -> Path:
        return self._directory.parent

    @property    
    def shephex_directory(self) -> Path:
        return self._directory

    def update_progress(self, progress: Union[str, Any]) -> None:
        if not isinstance(progress, str):
            progress = str(progress)

        self.meta.update('progress', progress)
        self.meta.dump(self.shephex_directory)

    def add(self, key: str, value: Any) -> None:
        self.meta.update(key, value)
        self.meta.dump(self.shephex_directory)
