from importlib import metadata

from schema_automator.annotators import *
from schema_automator.importers import *
from schema_automator.generalizers import *

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # package is not installed
    __version__ = "0.0.0"  # pragma: no cover
