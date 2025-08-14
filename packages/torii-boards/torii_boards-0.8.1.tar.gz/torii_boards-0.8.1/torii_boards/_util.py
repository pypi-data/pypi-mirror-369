# SPDX-License-Identifier: BSD-2-Clause

import warnings

__all__ = (
	'_deprecated_import',
)

def _deprecated_import(old: str, new: str):
	warnings.warn(
		f'The import from {old} has been deprecated and moved to {new}',
		DeprecationWarning, stacklevel = 3
	)
