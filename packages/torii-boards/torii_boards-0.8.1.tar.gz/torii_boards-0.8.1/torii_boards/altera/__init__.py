# SPDX-License-Identifier: BSD-2-Clause

from .._util import _deprecated_import

__all__ = (
	'arrow_deca',
	'chameleon96',
	'de0_cv',
	'de0',
	'de1_soc',
	'de10_lite',
	'de10_nano',
	'mister',
	'rz_easyfpga_a2_2',
)

def __dir__() -> list[str]:
	return list({*globals(), *__all__})

def __getattr__(name: str):
	match name:
		case 'arrow_deca':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.max10.{name}')
			from .max10 import arrow_deca
			return arrow_deca
		case 'chameleon96':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.cyclone_v.{name}')
			from .cyclone_v import chameleon96
			return chameleon96
		case 'de0_cv':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.cyclone_v.{name}')
			from .cyclone_v import de0_cv
			return de0_cv
		case 'de0':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.cyclone_iii.{name}')
			from .cyclone_iii import de0
			return de0
		case 'de1_soc':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.cyclone_v.{name}')
			from .cyclone_v import de1_soc
			return de1_soc
		case 'de10_lite':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.max10.{name}')
			from .max10 import de10_lite
			return de10_lite
		case 'de10_nano':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.cyclone_v.{name}')
			from .cyclone_v import de10_nano
			return de10_nano
		case 'mister':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.cyclone_v.{name}')
			from .cyclone_v import mister
			return mister
		case 'rz_easyfpga_a2_2':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.cyclone_iv.{name}')
			from .cyclone_iv import rz_easyfpga_a2_2
			return rz_easyfpga_a2_2
		case _:
			raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
