"""
Entry point for the TopModels package.

When the package is run as a script (e.g., with `python -m topmodels`), 
this module imports and executes the `main` function from the CLI module.

The CLI (`topmodels.cli`) dispatches commands to available actions:
- "scaffold": generates a new machine learning project structure using customizable templates.
TODO. To be implemented:
- "train": trains a machine learning model with the specified configuration and dataset.
- "evaluate": evaluates a trained model on a given dataset and outputs performance metrics.
- "predict": runs inference using a trained model on new input data.
"""

from .cli import main

if __name__ == "__main__":
    main()
