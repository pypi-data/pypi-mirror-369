from importlib.metadata import version
from .gitlab import Gitlab
from .logger import Logger

__version__ = version("GitlabParser")
__all__ = ['Gitlab', 'Logger']

Gitlab = Gitlab
Logger = Logger
