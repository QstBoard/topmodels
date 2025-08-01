from __future__ import annotations

from abc import ABC
from pathlib import Path
from typing import Type

from typing_extensions import TYPE_CHECKING, Self

from topmodels.conf import settings
from topmodels.data_engineering.model.reader.definition import (
    LocalModelDefinition, RemoteModelDefinition)
from topmodels.data_engineering.model.reader.type import ReaderType

if TYPE_CHECKING:
    from topmodels.data_engineering.model.reader.base import \
        ModelDefinitionBase


class ModelDefinitionFactory(ABC):
    __STRATEGIES: dict[ReaderType|str, Type[ModelDefinitionBase]] = {
        ReaderType.LOCAL: LocalModelDefinition,
        ReaderType.REMOTE: RemoteModelDefinition,
    }
    
    def __new__(cls) -> Self:
        raise TypeError(
            f"{cls.__name__} is a static class and cannot be instantiated."
        )

    @staticmethod
    def get_definition(
        path: str | Path,
        strategy: ReaderType | str = '',
    ) -> ModelDefinitionBase:
        if not strategy:
            strategy = settings.DATA_READER
        if strategy not in ModelDefinitionFactory.__STRATEGIES:
            raise ValueError(f"Data reader {strategy} not supported")
        reader_class: type[ModelDefinitionBase] = (
            ModelDefinitionFactory
            .__STRATEGIES[strategy]
        )
        return reader_class(path)
        