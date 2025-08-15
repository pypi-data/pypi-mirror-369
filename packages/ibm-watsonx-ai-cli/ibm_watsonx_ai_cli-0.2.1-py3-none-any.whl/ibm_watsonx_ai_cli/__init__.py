#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2025.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from importlib.metadata import version

pkg_name = __name__.replace("_", "-")
__version__ = version(pkg_name)
