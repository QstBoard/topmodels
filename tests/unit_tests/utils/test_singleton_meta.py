"""
Unit tests for the SingletonMeta metaclass.

This module tests the thread-safety and uniqueness of the SingletonMeta implementation.
"""

import threading
from threading import Thread

import pytest

from topmodels.utils.meta import SingletonMeta


@pytest.fixture(autouse=True)
def reset_singleton_instances() -> None:
    """
    Pytest fixture that automatically resets the SingletonMeta instance cache before each test.

    This fixture clears the `_instances` dictionary of the `SingletonMeta` metaclass,
    ensuring that singleton instances do not persist between tests and each test runs
    with a fresh singleton state.
    """
    SingletonMeta._instances.clear()

class MySingleton(metaclass=SingletonMeta):
    """
    Example singleton class using SingletonMeta.

    Args:
        value (int, optional): Value to store in the singleton instance. Defaults to 0.
    """
    def __init__(self, value=0):
        """
        Initialize the singleton instance.

        Args:
            value (int, optional): Value to store. Defaults to 0.
        """
        self.value = value

def test__singleton_instance_uniqueness():
    """
    Test that only one instance of the singleton is created,
    regardless of how many times the class is instantiated.
    """
    a = MySingleton(1)
    b = MySingleton(2)
    assert a is b
    assert a.value == b.value

def test__singleton_value_persistence():
    """
    Test that the singleton instance retains its value across instantiations.
    """
    instance = MySingleton(42)
    assert instance.value == 42
    instance.value = 100
    new_instance = MySingleton()
    assert new_instance.value == 100

def test__singleton_thread_safety():
    """
    Test that the singleton instance is unique and consistent across multiple threads.
    """
    results = []

    def create_instance(val):
        instance = MySingleton(val)
        results.append(instance)

    threads: list[Thread] = [
        threading.Thread(target=create_instance, args=(i,))
        for i in range(10)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # All threads should have received the same instance
    assert all(inst is results[0] for inst in results)
