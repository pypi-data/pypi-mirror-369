# SPDX-License-Identifier: BSD-2-Clause

from .._util import _deprecated_import

__all__ = (
	'quickfeather',
)

def __dir__() -> list[str]:
	return list({*globals(), *__all__})

def __getattr__(name: str):
	match name:
		case 'quickfeather':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.eos_s3.{name}')
			from .eos_s3 import quickfeather
			return quickfeather
		case _:
			raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
