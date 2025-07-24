"""
Default configuration settings for the TopModels project.

This module defines default middleware and other settings used throughout the application.
"""
from typing import Literal

MODEL_MODULE: str = "model"
CONTROLLER_MODULE: str = "controller"
MIDDLEWARES: list[str] = [
    "ListOfMiddlewaresModules",
]
DATA_ENGINE: Literal["local_spark", "databricks_spark"] = "local_spark"
DATA_READER: Literal["local", "remote"] = "local"