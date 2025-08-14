import importlib.metadata

try:
    __version__ = importlib.metadata.version("hectofinancial-mcp-server")
except importlib.metadata.PackageNotFoundError:
    __version__ = "dev"

__all__ = []
