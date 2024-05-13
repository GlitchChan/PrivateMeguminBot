import pathlib
from os import getenv

__all__ = ("DEBUG", "ROOT")

DEBUG = getenv("DEBUG", "False") in {"True", "1", "true"}
ROOT = pathlib.Path(__file__).parent.resolve()
