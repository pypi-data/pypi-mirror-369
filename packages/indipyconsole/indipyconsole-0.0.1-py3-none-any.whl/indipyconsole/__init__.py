import sys

from .consoleclient import ConsoleClient

__all__ = ["ConsoleClient"]

version = "0.0.1"

if sys.version_info < (3, 10):
    raise ImportError('indipyconsole requires Python >= 3.10')
