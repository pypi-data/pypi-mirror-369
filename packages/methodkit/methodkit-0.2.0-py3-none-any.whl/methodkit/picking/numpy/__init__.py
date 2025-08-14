import importlib.metadata

from methodkit.utils.conditional import package_installed

if not package_installed("numpy"):
    raise importlib.metadata.PackageNotFoundError("numpy is required for this module")

from .roulette_wheel import *  # noqa: F403
