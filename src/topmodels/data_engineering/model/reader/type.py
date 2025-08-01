from enum import Enum


class ReaderType(str, Enum):
    LOCAL= 'local'
    REMOTE = 'remote'
