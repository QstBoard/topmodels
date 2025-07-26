"""
Configuration management for the topmodels package.

This module provides a lazy-loading settings interface that loads user-defined
settings from a module specified by the `TOPMODELS_SETTINGS_MODULE` environment variable,
falling back to default settings where necessary.

Example:
    Set the environment variable and access your settings:

        >>> import os
        >>> from topmodels.conf import settings
        >>> os.environ["TOPMODELS_SETTINGS_MODULE"] = "myproject.settings"
        # now you can access your settings
"""

import importlib
import os
from collections import ChainMap
from types import ModuleType
from typing import Any

import topmodels.conf.default_settings as default_settings_module
from topmodels.core import SETTINGS_MODULE_VARIABLE

_NOT_SET = object()

class LazySettings:
    """
    Lazily loads the settings object when an attribute is first accessed.

    Attributes:
        _wrapped (Settings | object): The actual Settings instance, loaded on demand.
    """

    def __init__(self):
        """
        Initializes the LazySettings instance with no wrapped Settings object.
        """
        self._wrapped: Settings|object = _NOT_SET

    def _setup(self):
        """
        Loads the user settings module specified by the `SETTINGS_MODULE_VARIABLE` environment variable
        and wraps it in a Settings object.

        Raises:
            ImportError: If the `SETTINGS_MODULE_VARIABLE` environment variable is not set.
        """
        user_settings_module = os.environ.get(SETTINGS_MODULE_VARIABLE)
        if not user_settings_module:
            raise ImportError(f'{SETTINGS_MODULE_VARIABLE} environment variable not set.')
        self._wrapped = Settings(user_settings_module)

    def __getattr__(self, name: str) -> Any:
        """
        Proxies attribute access to the wrapped Settings object.
        Loads the Settings on first request.

        Args:
            name (str): The attribute name.

        Returns:
            Any: The value of the requested setting.
        """
        if self._wrapped is _NOT_SET:
            self._setup()
        val: Any = getattr(self._wrapped, name)
        self.__dict__[name] = val
        return val

    def __setattr__(self, name: str, value: Any):
        """
        Proxies attribute setting to the wrapped Settings object.
        Loads the Settings on first request.

        Args:
            name (str): The attribute name.
            value (Any): The value to set.
        """
        if name == '_wrapped':
            self.__dict__.clear()
            self.__dict__["_wrapped"] = value
        else:
            self.__dict__.pop(name, None)
            if self._wrapped is _NOT_SET:
                self._setup()
            setattr(self._wrapped, name, value)

    def __delattr__(self, name: str) -> None:
        """
        Deletes an attribute from the wrapped Settings object.

        Args:
            name (str): The attribute name.
        """
        if name == '_wrapped':
            raise AttributeError("Cannot delete the '_wrapped' attribute")
        if self._wrapped is _NOT_SET:
            self._setup()
        delattr(self._wrapped, name)
        self.__dict__.pop(name, None)


def extract_settings(module, *, prefix:str ="") -> dict[str, Any]:
    """
    Extracts all uppercase attributes from a module as settings.

    Args:
        module (ModuleType): The module to extract settings from.

    Returns:
        dict[str, Any]: A dictionary of setting names and values.

    Example:
        >>> import types
        >>> mod = types.SimpleNamespace(MY_SETTING=1, not_a_setting=2)
        >>> extract_settings(mod)
        {'MY_SETTING': 1}
    """
    if not isinstance(prefix, str):
        raise TypeError("Prefix must be a string")

    settings_dict: dict[str, Any] = {}
    for setting in dir(module):
        if setting.isupper():
            settings_dict[prefix.upper()+setting] = getattr(module, setting)
    return settings_dict

class Settings:
    """
    Manages user and default settings, providing attribute-style access.

    Attributes:
        _settings (ChainMap): ChainMap of user and default settings.
    """

    def __init__(self, user_settings_module: str) -> None:
        """
        Initializes the Settings object by loading user and default settings.

        Args:
            user_settings_module (str): The module path for user settings.
                The user settings take precedence over default settings.
        """
        user_mod: ModuleType = importlib.import_module(user_settings_module)

        user_settings: dict[str, Any] = extract_settings(user_mod)
        default_settings: dict[str, Any] = extract_settings(default_settings_module)

        self._settings = ChainMap(user_settings, default_settings)

    def __getattr__(self, name: str) -> Any:
        """
        Retrieves a setting value by attribute name.

        Args:
            name (str): The setting name.

        Returns:
            Any: The value of the setting.

        Raises:
            AttributeError: If the setting does not exist.
        """
        try:
            val = self._settings[name]
        except KeyError as e:
            raise AttributeError(f"'Settings' object has no attribute '{name}'") from e
        self.__dict__[name] = val
        return val

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Sets an attribute on the Settings object.

        Args:
            name (str): The attribute name.
            value (Any): The value to set.
        """
        if name != '_settings':
            self._settings[name] = value
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        """
        Deletes an attribute from the Settings object.
        With the ChainMap mechanism, it is only possible to delete user settings.

        Args:
            name (str): The attribute name to delete.

        Notes:
            - We choose to use __dict__.pop instead of super().__delattr__(name) 
              in the case in which the attribute was not yet accessed by __getattr__ 
              and therefore do not exist as instance attribute. 
              This prevents an AttributeError from being raised.

        Raises:
            AttributeError: If the attribute does not exist.
        """
        try:
            del self._settings[name]
        except KeyError as e:
            raise AttributeError(f"No local setting with name '{name}'") from e
        self.__dict__.pop(name, None)

    def isoverridden(self, setting: str) -> bool:
        """
        Checks if a setting is overridden in the user settings.

        Args:
            setting (str): The name of the setting.

        Returns:
            bool: True if the setting is overridden by user settings, False otherwise.
        """
        return setting in self._settings.maps[0]

settings = LazySettings()
