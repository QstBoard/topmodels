import yaml
from typing_extensions import Self

from topmodels.data_engineering.model.reader.base import ModelDefinitionBase


def read_yaml(file_path):
    try:
        with open(file_path, encoding="utf-8") as f:
            content = yaml.safe_load(f)
    except UnicodeDecodeError:
        with open(file_path, encoding="cp1252") as f:
            content = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(file_path) from e
    except FileNotFoundError as e:
        raise FileNotFoundError(file_path) from e
    return content

class LocalModelDefinition(ModelDefinitionBase):
    def read(self) -> Self:
        self._data_model = read_yaml(self._data_model_fpath)
        return self


class RemoteModelDefinition(ModelDefinitionBase):
    # TODO: Implement remote reading logic
    def read(self) -> Self:
        return self