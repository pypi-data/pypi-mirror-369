# SPDX-License-Identifier: BSD-2-Clause

from torii.build                               import Connector
from torii.platform.vendor.lattice.machxo_2_3l import MachXO2Platform

__all__ = (
	'TinyFPGAAX1Platform',
)

class TinyFPGAAX1Platform(MachXO2Platform):
	device      = 'LCMXO2-256HC'
	package     = 'SG32'
	speed       = '4'

	pretty_name = 'TinyFPGA AX1'
	description = 'TinyFPGA AX1 Lattice MachXO2-256 Development Board'

	connectors  = [
		Connector(
			'gpio', 0,
			# Left side of the board
			#  1  2  3  4  5  6  7  8  9 10 11
			'13 14 16 17 20 21 23 25 26 27 28 '
			# Right side of the board
			# 12 13 14 15 16 17 18 19 20 21 22
			'-  -  -  -  4  5  8  9  10 11 12 '
		),
	]
	resources = []
	# This board doesn't have an integrated programmer.
