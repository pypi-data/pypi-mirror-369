# SPDX-License-Identifier: BSD-2-Clause

from torii.build                         import Attrs, Clock, Connector, Pins, PinsN, Resource
from torii.build.run                     import BuildProducts
from torii.platform.resources.interface  import DirectUSBResource, UARTResource
from torii.platform.resources.memory     import SPIFlashResources
from torii.platform.resources.user       import LEDResources, SwitchResources
from torii.platform.vendor.lattice.ice40 import ICE40Platform

__all__ = (
	'ICESugarPlatform',
)

class ICESugarPlatform(ICE40Platform):
	device      = 'iCE40UP5K'
	package     = 'SG48'
	default_clk = 'clk12'

	pretty_name = 'iCESugar'
	description = 'iCESugar Lattice iCE40-UP5K Development Board'

	resources   = [
		Resource(
			'clk12', 0, Pins('35', dir = 'i'), Clock(12e6),
			Attrs(GLOBAL = True, IO_STANDARD = 'LVCMOS33')
		),
		*LEDResources(pins = '40 41 39', invert = True, attrs = Attrs(IO_STANDARD = 'LVCMOS33')),
		# Semantic aliases
		Resource('led_r', 0, PinsN('40', dir = 'o'), Attrs(IO_STANDARD = 'LVCMOS33')),
		Resource('led_g', 0, PinsN('41', dir = 'o'), Attrs(IO_STANDARD = 'LVCMOS33')),
		Resource('led_b', 0, PinsN('39', dir = 'o'), Attrs(IO_STANDARD = 'LVCMOS33')),
		*SwitchResources(
			pins = '18 19 20 21',
			attrs = Attrs(IO_STANDARD = 'LVCMOS33')
		),
		UARTResource(
			0,
			rx = '4', tx = '6',
			attrs = Attrs(IO_STANDARD = 'LVTTL33', PULLUP = 1)
		),
		*SPIFlashResources(
			0,
			cs_n = '16', clk = '15', copi = '14', cipo = '17', wp_n = '12', hold_n = '13',
			attrs = Attrs(IO_STANDARD = 'LVCMOS33')
		),
		DirectUSBResource(
			0,
			d_p = '10', d_n = '9', pullup = '11', attrs = Attrs(IO_STANDARD = 'LVCMOS33')
		),
	]

	connectors = [
		Connector('pmod', 0, '10 6 3 48 - -  9 4 2 47 - -'), # PMOD1 - IO pins shared by USB
		Connector('pmod', 1, '46 44 42 37 - - 45 43 38 36 - -'), # PMOD2
		Connector('pmod', 2, '34 31 27 25 - - 32 28 26 23 - -'), # PMOD3
		Connector('pmod', 3, '21 20 19 18 - - - - - - - -'), # PMOD4 - IO pins used for switches via jumpers
	]

	def toolchain_program(self, products: BuildProducts, name: str) -> None:
		from os         import environ
		from subprocess import check_call

		iceprog = environ.get('ICEPROG', 'iceprog')
		with products.extract(f'{name}.bin') as bitstream_filename:
			check_call([iceprog, bitstream_filename])


if __name__ == '__main__':
	from ...test.blinky import Blinky
	ICESugarPlatform().build(Blinky(), do_program = True)
