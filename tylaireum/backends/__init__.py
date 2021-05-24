import importlib
from pathlib import Path


def get_backend(backend: str = "cpp"):
    return importlib.import_module(f"tylaireum.api.backends.{backend}")
