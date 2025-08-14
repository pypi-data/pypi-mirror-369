# SPDX-License-Identifier: BSD-2-Clause

from .._util import _deprecated_import

__all__ = (
	'blackice_ii',
	'blackice',
	'colorlight_5a75b_r7_0',
	'ecp5_5g_evn',
	'ecpix5',
	'fomu_hacker',
	'fomu_pvt',
	'ice40_hx1k_blink_evn',
	'ice40_hx8k_b_evn',
	'ice40_up5k_b_evn',
	'icebreaker_bitsy',
	'icebreaker',
	'icestick',
	'icesugar',
	'icesugar_nano',
	'logicbone',
	'machxo3_sk',
	'nandlang_go',
	'orangecrab_r0_1',
	'orangecrab_r0_2',
	'supercon19badge',
	'tinyfpga_ax1',
	'tinyfpga_ax2',
	'tinyfpga_bx',
	'ulx3s',
	'upduino_v1',
	'upduino_v2',
	'upduino_v3',
	'versa_ecp5_5g',
	'versa_ecp5',
)

def __dir__() -> list[str]:
	return list({*globals(), *__all__})

def __getattr__(name: str):
	match name:
		case 'blackice_ii':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ice40.{name}')
			from .ice40 import blackice_ii
			return blackice_ii
		case 'blackice':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ice40.{name}')
			from .ice40 import blackice
			return blackice
		case 'colorlight_5a75b_r7_0':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ecp5.{name}')
			from .ecp5 import colorlight_5a75b_r7_0
			return colorlight_5a75b_r7_0
		case 'ecp5_5g_evn':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ecp5.{name}')
			from .ecp5 import ecp5_5g_evn
			return ecp5_5g_evn
		case 'ecpix5':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ecp5.{name}')
			from .ecp5 import ecpix5
			return ecpix5
		case 'fomu_hacker':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ice40.{name}')
			from .ice40 import fomu_hacker
			return fomu_hacker
		case 'fomu_pvt':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ice40.{name}')
			from .ice40 import fomu_pvt
			return fomu_pvt
		case 'ice40_hx1k_blink_evn':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ice40.{name}')
			from .ice40 import ice40_hx1k_blink_evn
			return ice40_hx1k_blink_evn
		case 'ice40_hx8k_b_evn':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ice40.{name}')
			from .ice40 import ice40_hx8k_b_evn
			return ice40_hx8k_b_evn
		case 'ice40_up5k_b_evn':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ice40.{name}')
			from .ice40 import ice40_up5k_b_evn
			return ice40_up5k_b_evn
		case 'icebreaker_bitsy':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ice40.{name}')
			from .ice40 import icebreaker_bitsy
			return icebreaker_bitsy
		case 'icebreaker':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ice40.{name}')
			from .ice40 import icebreaker
			return icebreaker
		case 'icestick':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ice40.{name}')
			from .ice40 import icestick
			return icestick
		case 'icesugar':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ice40.{name}')
			from .ice40 import icesugar
			return icesugar
		case 'icesugar_nano':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ice40.{name}')
			from .ice40 import icesugar_nano
			return icesugar_nano
		case 'logicbone':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ecp5.{name}')
			from .ecp5 import logicbone
			return logicbone
		case 'machxo3_sk':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.machxo3.{name}')
			from .machxo3 import machxo3_sk
			return machxo3_sk
		case 'nandlang_go':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ice40.{name}')
			from .ice40 import nandland_go
			return nandland_go
		case 'orangecrab_r0_1':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ecp5.{name}')
			from .ecp5 import orangecrab_r0_1
			return orangecrab_r0_1
		case 'orangecrab_r0_2':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ecp5.{name}')
			from .ecp5 import orangecrab_r0_2
			return orangecrab_r0_2
		case 'supercon19badge':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ecp5.{name}')
			from .ecp5 import supercon19badge
			return supercon19badge
		case 'tinyfpga_ax1':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.machxo2.{name}')
			from .machxo2 import tinyfpga_ax1
			return tinyfpga_ax1
		case 'tinyfpga_ax2':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.machxo2.{name}')
			from .machxo2 import tinyfpga_ax2
			return tinyfpga_ax2
		case 'tinyfpga_bx':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ice40.{name}')
			from .ice40 import tinyfpga_bx
			return tinyfpga_bx
		case 'ulx3s':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ecp5.{name}')
			from .ecp5 import ulx3s
			return ulx3s
		case 'upduino_v1':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ice40.{name}')
			from .ice40 import upduino_v1
			return upduino_v1
		case 'upduino_v2':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ice40.{name}')
			from .ice40 import upduino_v2
			return upduino_v2
		case 'upduino_v3':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ice40.{name}')
			from .ice40 import upduino_v3
			return upduino_v3
		case 'versa_ecp5_5g':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ecp5.{name}')
			from .ecp5 import versa_ecp5_5g
			return versa_ecp5_5g
		case 'versa_ecp5':
			_deprecated_import(f'{__name__}.{name}', f'{__name__}.ecp5.{name}')
			from .ecp5 import versa_ecp5
			return versa_ecp5
		case _:
			raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
