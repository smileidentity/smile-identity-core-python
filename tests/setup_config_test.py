"""Checks if importlib_metadata.version(__package__) was defined.

This test suite contains different test around testing different setup
configurations for the core library.
"""

from smile_id_core import __version__


def test_version_exists() -> None:
    """Assertion check on version()."""
    assert (__version__, "Package version is not defined.") is not None
