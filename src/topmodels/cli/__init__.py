"""
This module serves as the entry point for the TopModels CLI.

It parses command-line arguments to determine which CLI action to execute.
Supported actions are defined in the ACTIONS dictionary and are dynamically
imported from the 'topmodels.cli.actions' package. If an invalid or missing
action is provided, a ValueError is raised. The selected action module must
implement a 'run' function, which is called with the remaining command-line
arguments.

Example usage:
    python -m topmodels.cli scaffold [options]
"""
import importlib
import sys

COMMAND_PACKAGE = "topmodels.cli.actions"
ACTIONS = {
    "scaffold": "scaffold",
}


def main():
    """
    Entry point for the TopModels CLI.

    Parses command-line arguments to determine the requested action.
    Dynamically imports and executes the corresponding action module's `run` function,
    passing any additional arguments.

    Raises:
        ValueError: If the action is missing or invalid.
        ImportError: If the action module cannot be imported.
    """
    actions_name = sys.argv[1] if len(sys.argv) > 1 else None
    if not actions_name or actions_name not in ACTIONS:
        raise ValueError(
            f"Invalid action '{actions_name}'. Available actions are: {', '.join(ACTIONS.keys())}"
        )

    module_name = f"{COMMAND_PACKAGE}.{ACTIONS[actions_name]}"
    try:
        action_module = importlib.import_module(module_name)
    except ImportError as e:
        raise ImportError(
            f"Failed to import action module '{module_name}'. "
            f"Ensure the module exists and is correctly named."
        ) from e

    action_module.run(sys.argv[2:])
