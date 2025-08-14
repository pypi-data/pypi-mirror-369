# SPDX-License-Identifier: BSD-2-Clause

from .zturn_lite_z007s import ZTurnLiteZ007SPlatform

__all__ = (
	'ZTurnLiteZ010Platform',
)

class ZTurnLiteZ010Platform(ZTurnLiteZ007SPlatform):
	device = 'xc7z010'

	pretty_name = 'Z-Turn Lite'
	description = 'Myir Z-Turn Lite Xilinx Zynq-7010 SoC Development Board'
