"""
meta.py

This module provides a thread-safe Singleton metaclass implementation.
"""

from threading import Lock
from typing import Any, Dict, TypeVar

T = TypeVar("T", bound="SingletonMeta")

class SingletonMeta(type):
    """
    Thread-safe Singleton metaclass.

    Ensures that only one instance of a class using this metaclass exists.
    """

    _instances: Dict[Any, Any] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> T:
        """
        Returns the singleton instance of the class.

        If the instance does not exist, it is created in a thread-safe manner.
        """
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
