"""SLAMLab Python Package."""

from importlib.metadata import version as _version

__all__ = ["__version__", "about"]

try:
    __version__ = _version("slamlab")
except Exception:  # pragma: no cover
    __version__ = "0.0.1"


def about() -> str:
    """Return a short description of this package."""
    return (
        "slamlab: Python package for SLAMLab. "
        "Visit https://github.com/SLAMLabApp/slamlab_python for updates."
    )
