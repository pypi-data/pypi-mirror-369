# SPDX-License-Identifier: BSD-2-Clause

try:
	from importlib import metadata
	__version__ = metadata.version(__package__)
except ImportError:
	__version__ = 'unknown' # :nocov:
