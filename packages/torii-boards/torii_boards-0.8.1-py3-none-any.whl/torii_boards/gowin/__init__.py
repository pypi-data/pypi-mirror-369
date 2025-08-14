# SPDX-License-Identifier: BSD-2-Clause

from .._util import _deprecated_import

__all__ = (
	'tang_nano',
)

def __dir__() -> list[str]:
	return list({*globals(), *__all__})

def __getattr__(name: str):
	match name:
		case 'tang_nano':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.gw1n.{name}')
			from .gw1n import tang_nano
			return tang_nano
		case _:
			raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
