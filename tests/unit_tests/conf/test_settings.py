"""Test module for LazySettings and Settings classes."""
import importlib
import sys
from collections import ChainMap
from pathlib import Path
from typing import Any

import pytest

from topmodels.conf import LazySettings, Settings


@pytest.fixture(autouse=True)
def set_topmodels_environment_variable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch
) -> None:
    """Sets kind of local environment for all the `settings` tests."""
    # Set up a temporary package structure for local settings
    local_settings_pkg = tmp_path / 'settings'
    local_settings_pkg.mkdir()
    (local_settings_pkg / '__init__.py').write_text('')
    (local_settings_pkg / 'local_settings.py').write_text('FOO = "bar"')
    monkeypatch.syspath_prepend(tmp_path)
    importlib.invalidate_caches()


    # Set the environment variable to point to the local settings module
    # Mandatory for LazeSettings module
    monkeypatch.setenv(
        'TOPMODELS_SETTINGS_MODULE', 
        f'settings.local_settings'
    )

@pytest.fixture(scope='function')
def lazy_settings() -> LazySettings:
    """Fixture that provides a fresh LazySettings instance for each test."""
    return LazySettings()

@pytest.fixture(scope='function')
def settings() -> Settings:
    """Fixture that provides a fresh Settings instance for each test."""
    return Settings('settings.local_settings')

class TestLazySettings:
    """Tests for the LazySettings class."""

    def test_setup_import_error(
        self,
        lazy_settings: LazySettings, 
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        Test that an ImportError is raised if the environment variable for user 
        settings is not set.

        Preconditions:
            - The 'TOPMODELS_ENVIRONMENT_VARIABLE' environment variable is not set, 
              or monkeypatched as deleted.

        Expected result:
            - Calling lazy_settings._setup() raises an ImportError.
        """
        monkeypatch.delenv("TOPMODELS_SETTINGS_MODULE", raising=False)
        with pytest.raises(ImportError):
            lazy_settings._setup()
        
    def test_getattr_returns_value(
        self,
        lazy_settings: LazySettings,
    ) -> None:
        """
        Test that __getattr__ returns the correct value from the wrapped Settings object.

        Preconditions:
            - The 'local' setting is defined and it contains FOO name.

        Expected result:
            - Accessing lazy_settings.FOO returns the expected value.
        """
        assert lazy_settings.FOO == 'bar'

    def test_getattr_attribute_error(
        self,
        lazy_settings: LazySettings,
    ) -> None:
        """
        Test that __getattr__ raises an AttributeError when accessing a non-existent setting.

        Preconditions:
            - The requested attribute does not exist neither in local defined or 
            in default settings. The default settings is set inside the topmodels.conf module.

        Expected result:
            - Accessing a non-existent attribute raises an AttributeError.
        """
        with pytest.raises(AttributeError):
            _: Any = lazy_settings.NON_EXISTENT_ATTRIBUTE

    def test_setattr_sets_value(self, lazy_settings: LazySettings) -> None:
        """
        Test that __setattr__ sets the value in the wrapped Settings object.

        Preconditions:
            - The 'FOO' setting exists in local setting.

        Expected result:
            - Setting lazy_settings.FOO updates its value.
        """
        lazy_settings.FOO = 'new_value'
        assert lazy_settings.FOO == 'new_value'

    def test_delattr_deletes_values(self, lazy_settings: LazySettings) -> None:
        """
        Test that __delattr__ deletes the value from the wrapped Settings object.

        Preconditions:
            - The 'FOO' setting exists in local setting.

        Expected result:
            - After deletion, accessing lazy_settings.FOO raises an AttributeError.
        """
        lazy_settings.FOO = "new_value"
        del lazy_settings.FOO
        with pytest.raises(AttributeError):
            _ = lazy_settings.FOO

    def test_delattr_non_existing_attribute(self, lazy_settings: LazySettings) -> None:
        """
        Test that __delattr__ raises an AttributeError when trying to delete 
        a non-existing attribute.

        Preconditions:
            - The attribute does not exist neither in local nor default settings.

        Expected result:
            - Deleting a non-existing attribute raises an AttributeError.
        """
        with pytest.raises(AttributeError, match="^No local setting with"):
            del lazy_settings.RANDOM_NON_EXISTING_ATTRIBUTE

    def test_protection_against_deletion_of_wrapped(
        self,
        lazy_settings: LazySettings
    ) -> None:
        """
        Test that the _wrapped attribute cannot be deleted.

        Preconditions:
            - The LazySettings instance is initialized.

        Expected result:
            - Attempting to delete lazy_settings._wrapped raises an AttributeError.
        """
        with pytest.raises(AttributeError, match="Cannot delete the '_wrapped' attribute"):
            del lazy_settings._wrapped


class TestSettings:
    """ 
    Unit tests for the Settings class.

    Local settings are defined in the temporary 'settings.local_settings' module, built
    by the `set_topmodels_environment_variable` fixture.
    
    """

    def test_settings_init_contains_parameter(
        self,
        settings: Settings
    ) -> None:
        """
        Test that the Settings object is initialized with the correct parameters.

        Preconditions:
            - The 'FOO' setting is defined in the local setting.

        Expected result:
            - settings._settings is a ChainMap containing 'FOO'.
            - settings.FOO returns the expected value.
        """
        assert isinstance(settings._settings, ChainMap)
        assert 'FOO' in settings._settings
        assert settings.FOO == 'bar'

    def test_accessing_existing_setting(self, settings: Settings) -> None:
        """
        Test that accessing an existing setting returns the correct value.

        Preconditions:
            - 'FOO' is defined in local setting.
            - 'MIDDLEWARES' is defined in default setting (topmodels.conf).

        Expected result:
            - settings.FOO returns the user-defined value.
            - settings.MIDDLEWARES returns the default value.
        """
        assert settings.FOO == 'bar'
        assert settings.MIDDLEWARES == ['ListOfMiddlewaresModules']

    def test_accessing_non_existing_setting(self, settings: Settings) -> None:
        """
        Test that accessing a non-existing setting raises an AttributeError.

        Preconditions:
            - The requested setting does not exist neither in local nor in default settings.

        Expected result:
            - Accessing a non-existent setting raises an AttributeError.
        """
        with pytest.raises(AttributeError):
            _: Any = settings.NON_EXISTING_SETTING

    def test_setting_existing_global_setting(self, settings: Settings) -> None:
        """
        Test that setting an existing default (global) setting overrides its value,
        and that deleting the override restores the default value.

        Preconditions:
            - 'MIDDLEWARES' is defined in default settings.

        Expected result:
            - Setting settings.MIDDLEWARES changes its value.
            - Deleting settings.MIDDLEWARES restores the default value.
        """
        settings.MIDDLEWARES = ['NewMiddlewareModule']
        assert settings.MIDDLEWARES == ['NewMiddlewareModule']
        del settings.MIDDLEWARES
        assert settings.MIDDLEWARES == ['ListOfMiddlewaresModules']

    def test_setting_existing_user_setting(self, settings: Settings) -> None:
        """
        Test that setting an existing local setting overrides its value,
        and that deleting it removes the local value.

        Preconditions:
            - 'FOO' is defined in user settings.

        Expected result:
            - Accessing settings.FOO returns the user-defined value.
            - Setting settings.FOO changes its value.
            - Deleting settings.FOO removes the local value.
            - Accessing settings.FOO after deletion raises an AttributeError.
        """
        assert settings.FOO == 'bar'
        settings.FOO = "new_value"
        assert settings.FOO == "new_value"
        del settings.FOO
        with pytest.raises(AttributeError):
            _: Any = settings.CONFIG


    def test_deleting_existing_settings(self, settings: Settings) -> None:
        """
        Test that deleting an existing user-defined setting removes it from the settings.

        Preconditions:
            - The 'FOO' setting is defined in the local setting.

        Expected result:
            - Accessing 'settings.FOO' after deletion raises an AttributeError.
        """
        del settings.FOO
        with pytest.raises(AttributeError):
            _: Any = settings.FOO

    def test_deleting_non_existing_settings(self, settings: Settings) -> None:
        """
        Test that deleting a non-existing setting raises an AttributeError.

        Preconditions:
            - The 'NON_EXISTING_SETTING' does not exist neither in local nor default settings.

        Expected result:
            - Deleting 'settings.NON_EXISTING_SETTING' raises an AttributeError.
        """
        with pytest.raises(AttributeError):
            del settings.NON_EXISTING_SETTING

    def test_deleting_existing_but_global_settings(self, settings: Settings) -> None:
        """
        Test that deleting a setting defined only in default settings (not overridden by user)
        raises an AttributeError.

        Preconditions:
            - The 'MIDDLEWARES' setting is only present in default settings.

        Expected result:
            - Deleting 'settings.MIDDLEWARES' raises an AttributeError.
        """
        with pytest.raises(AttributeError):
            del settings.MIDDLEWARES

    def test_isoverridden(self, settings: Settings) -> None:
        """
        Test that the isoverridden method returns True for a user-defined setting
        and False for a setting only present in default settings.

        Preconditions:
            - 'FOO' is defined in user settings.
            - 'MIDDLEWARES' is only defined in default settings.

        Expected result:
            - settings.isoverridden("FOO") returns True.
            - settings.isoverridden("MIDDLEWARES") returns False.
            - Setting 'MIDDLEWARES' to a new value returns True for isoverridden.
        """
        assert settings.isoverridden("FOO")
        assert not settings.isoverridden("MIDDLEWARES")
        settings.MIDDLEWARES = ['NewMiddlewareModule']
        assert settings.isoverridden("MIDDLEWARES")
