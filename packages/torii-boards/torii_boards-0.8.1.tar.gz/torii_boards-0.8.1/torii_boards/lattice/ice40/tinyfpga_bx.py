# SPDX-License-Identifier: BSD-2-Clause

from torii.build                         import Attrs, Clock, Connector, Pins, Resource
from torii.build.run                     import BuildProducts
from torii.platform.resources.interface  import DirectUSBResource
from torii.platform.resources.memory     import SPIFlashResources
from torii.platform.resources.user       import LEDResources
from torii.platform.vendor.lattice.ice40 import ICE40Platform

__all__ = (
	'TinyFPGABXPlatform',
)

class TinyFPGABXPlatform(ICE40Platform):
	device      = 'iCE40LP8K'
	package     = 'CM81'
	default_clk = 'clk16'

	pretty_name = 'TinyFPGA BX'
	description = 'TinyFPGA BX Lattice iCE40-LP8K Development Board'

	resources   = [
		Resource(
			'clk16', 0, Pins('B2', dir = 'i'), Clock(16e6), Attrs(IO_STANDARD = 'SB_LVCMOS')
		),
		*LEDResources(pins = 'B3', attrs = Attrs(IO_STANDARD = 'SB_LVCMOS')),
		DirectUSBResource(
			0,
			d_p = 'B4', d_n = 'A4', pullup = 'A3',
			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS')
		),
		*SPIFlashResources(
			0,
			cs_n = 'F7', clk = 'G7', copi = 'G6', cipo = 'H7', wp_n = 'H4', hold_n = 'J8',
			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS')
		),
	]
	connectors  = [
		Connector(
			'gpio', 0,
			# Left side of the board
			# 1  2  3  4  5  6  7  8  9  10 11 12 13
			' A2 A1 B1 C2 C1 D2 D1 E2 E1 G2 H1 J1 H2 '
			# Right side of the board
			# 14 15 16 17 18 19 20 21 22 23 24
			' H9 D9 D8 C9 A9 B8 A8 B7 A7 B6 A6 '
			# Bottom of the board
			# 25 26 27 28 29 30 31
			' G1 J3 J4 G9 J9 E8 J2'
		),
	]

	def toolchain_program(self, products: BuildProducts, name: str) -> None:
		from os         import environ
		from subprocess import check_call

		tinyprog = environ.get('TINYPROG', 'tinyprog')
		with products.extract(f'{name}.bin') as bitstream_filename:
			check_call([tinyprog, '-p', bitstream_filename])


if __name__ == '__main__':
	from ...test.blinky import Blinky
	TinyFPGABXPlatform().build(Blinky(), do_program = True)
