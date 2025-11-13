"""
Algorithm task 1 package: structured-light copper board particle removal.
"""

from .config import TaskConfig
from .pipeline import run_pipeline
from .service import Task1Runner, Task1RunOptions, Task1RunResult

__all__ = ["TaskConfig", "run_pipeline", "Task1Runner", "Task1RunOptions", "Task1RunResult"]
