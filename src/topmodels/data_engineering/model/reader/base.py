from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from typing_extensions import Self


class ModelDefinitionBase(ABC):

    def __init__(self, path: str|Path) -> None:
        self._data_model_fpath = path
        self._data_model = self.data_model

    @abstractmethod
    def read(self) -> Self: ...

    @property
    def data_model(self) -> dict[str, Any]:
        self.read()
        return self._data_model
