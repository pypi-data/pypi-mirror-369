from beartype.claw import beartype_this_package

beartype_this_package()

import importlib.metadata

from .ingenia import Ingenia
from .modules.agent import Agent
from .modules.chat import Chat
from .modules.chunk import Chunk
from .modules.dataset import DataSet
from .modules.document import Document
from .modules.session import Session

# Try to get version from metadata, fallback to local version for development
try:
    __version__ = importlib.metadata.version("ingenia")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.1.0-dev"  # Local development version

__all__ = ["Ingenia", "DataSet", "Chat", "Session", "Document", "Chunk", "Agent"]
