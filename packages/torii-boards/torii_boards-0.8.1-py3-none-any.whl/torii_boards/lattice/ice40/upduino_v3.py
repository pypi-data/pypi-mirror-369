# SPDX-License-Identifier: BSD-2-Clause

import os
import subprocess

from torii.build                         import Attrs, Clock, Connector, Pins, Resource
from torii.platform.resources.memory     import SPIFlashResources
from torii.platform.resources.user       import RGBLEDResource
from torii.platform.vendor.lattice.ice40 import ICE40Platform

__all__ = (
	'UpduinoV3Platform',
)

class UpduinoV3Platform(ICE40Platform):
	device      = 'iCE40UP5K'
	package     = 'SG48'
	default_clk = 'SB_HFOSC'
	hfosc_div   = 0

	pretty_name = 'Upduino V3'
	description = 'TinyVision Upduino V3 Lattice iCE40-UP5K Development Board'

	resources   = [
		# Solder the OSC jumper to connect the onboard oscillator to pin 20.
		# Note that this overlaps with the QSPI pins.
		Resource(
			'clk12', 0, Pins('20', dir = 'i'), Clock(12e6), Attrs(IO_STANDARD = 'SB_LVCMOS')
		),
		RGBLEDResource(
			0,
			r = '41', g = '39', b = '40', invert = True,
			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS')
		),
		# To use QSPI mode, solder the appropriate jumpers.
		*SPIFlashResources(
			0,
			cs_n = '16', clk = '15', cipo = '17', copi = '14', wp_n = '10', hold_n = '20',
			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS')
		),
	]
	connectors  = [
		# 'Left' row of header pins (JP5 on the schematic)
		Connector('j', 0, '41 39 40 - - - 23 25 26 27 32 35 31 37 34 43 36 42 38 28'),
		# 'Right' row of header pins (JP6 on the schematic)
		Connector('j', 1, '20 10 - - 12 21 13 19 18 11 9 6 44 4 3 48 45 47 46 2')
	]

	def toolchain_program(self, products, name):
		iceprog = os.environ.get('ICEPROG', 'iceprog')
		with products.extract(f'{name}.bin') as bitstream_filename:
			subprocess.check_call([iceprog, bitstream_filename])


if __name__ == '__main__':
	from ...test.blinky import Blinky
	UpduinoV3Platform().build(Blinky(), do_program = True)
