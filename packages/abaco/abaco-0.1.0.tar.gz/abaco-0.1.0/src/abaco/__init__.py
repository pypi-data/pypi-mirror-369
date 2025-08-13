# The __init__.py file is loaded when the package is loaded.
# It is used to indicate that the directory in which it resides is a Python package
from importlib import metadata

__version__ = metadata.version("abaco")

# from abaco.ABaCo import abaco_run

# The __all__ variable is a list of variables which are imported
# when a user does "from example import *"
# __all__ = ["abaco_run", "abaco_recon"]
