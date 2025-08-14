from importlib.metadata import version as _version, PackageNotFoundError

try:
    __version__ = _version("luminarycloud_jupyter")
except PackageNotFoundError:
    __version__ = "0.0.0"
