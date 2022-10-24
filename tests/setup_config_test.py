"""
This test suite contains different test around testing different setup configurations
for the core library.
"""
import unittest
from smile_id_core import __version__


class SetupConfigTest(
    unittest.TestCase,
):
    def test_version_exists(self):
        self.assertIsNotNone(__version__, "Package version is not defined.")
