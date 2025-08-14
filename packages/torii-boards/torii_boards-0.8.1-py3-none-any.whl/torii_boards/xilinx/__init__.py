# SPDX-License-Identifier: BSD-2-Clause

from .._util import _deprecated_import

__all__ = (
	'alchitry_au',
	'arty_a7',
	'arty_s7',
	'arty_z7',
	'atlys',
	'cmod_a7',
	'cmod_s7',
	'ebaz4205',
	'genesys2',
	'kc705',
	'kcu105',
	'mega65',
	'mercury',
	'microzed_z010',
	'microzed_z020',
	'nexys4ddr',
	'numato_mimas',
	'sk_xc6slx9',
	'te0714_03_50_2I',
	'zturn_lite_z007s',
	'zturn_lite_z010',
)

def __dir__() -> list[str]:
	return list({*globals(), *__all__})

def __getattr__(name: str):
	match name:
		case 'alchitry_au':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.artix7.{name}')
			from .artix7 import alchitry_au
			return alchitry_au
		case 'arty_a7':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.artix7.{name}')
			from .artix7 import arty_a7
			return arty_a7
		case 'arty_s7':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.spartan7.{name}')
			from .spartan7 import arty_s7
			return arty_s7
		case 'arty_z7':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.zynq7.{name}')
			from .zynq7 import arty_z7
			return arty_z7
		case 'atlys':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.spartan6.{name}')
			from .spartan6 import atlys
			return atlys
		case 'cmod_a7':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.artix7.{name}')
			from .artix7 import cmod_a7
			return cmod_a7
		case 'cmod_s7':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.spartan7.{name}')
			from .spartan7 import cmod_s7
			return cmod_s7
		case 'ebaz4205':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.zynq7.{name}')
			from .zynq7 import ebaz4205
			return ebaz4205
		case 'genesys2':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.kintex7.{name}')
			from .kintex7 import genesys2
			return genesys2
		case 'kc705':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.kintex7.{name}')
			from .kintex7 import kc705
			return kc705
		case 'kcu105':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.kintex_us.{name}')
			from .kintex_us import kcu105
			return kcu105
		case 'mega65':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.artix7.{name}')
			from .artix7 import mega65
			return mega65
		case 'mercury':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.spartan3.{name}')
			from .spartan3 import mercury
			return mercury
		case 'microzed_z010':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.zynq7.{name}')
			from .zynq7 import microzed_z010
			return microzed_z010
		case 'microzed_z020':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.zynq7.{name}')
			from .zynq7 import microzed_z020
			return microzed_z020
		case 'nexys4ddr':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.artix7.{name}')
			from .artix7 import nexys4ddr
			return nexys4ddr
		case 'numato_mimas':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.spartan6.{name}')
			from .spartan6 import numato_mimas
			return numato_mimas
		case 'sk_xc6slx9':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.spartan6.{name}')
			from .spartan6 import sk_xc6slx9
			return sk_xc6slx9
		case 'te0714_03_50_2I':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.artix7.{name}')
			from .artix7 import te0714_03_50_2I
			return te0714_03_50_2I
		case 'zturn_lite_z007s':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.zynq7.{name}')
			from .zynq7 import zturn_lite_z007s
			return zturn_lite_z007s
		case 'zturn_lite_z010':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.zynq7.{name}')
			from .zynq7 import zturn_lite_z010
			return zturn_lite_z010
		case _:
			raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
