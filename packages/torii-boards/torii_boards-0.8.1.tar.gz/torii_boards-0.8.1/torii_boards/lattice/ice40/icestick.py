# SPDX-License-Identifier: BSD-2-Clause

from torii.build                         import Attrs, Clock, Connector, Pins, Resource
from torii.build.run                     import BuildProducts
from torii.platform.resources.interface  import IrDAResource, UARTResource
from torii.platform.resources.memory     import SPIFlashResources
from torii.platform.resources.user       import LEDResources
from torii.platform.vendor.lattice.ice40 import ICE40Platform

__all__ = (
	'ICEStickPlatform',
)

class ICEStickPlatform(ICE40Platform):
	device      = 'iCE40HX1K'
	package     = 'TQ144'
	default_clk = 'clk12'

	pretty_name = 'iCEstick'
	description = 'Lattice iCEstick iCE40-HX1K Evaluation Kit'

	resources   = [
		Resource(
			'clk12', 0, Pins('21', dir = 'i'), Clock(12e6),
			Attrs(GLOBAL = True, IO_STANDARD = 'SB_LVCMOS')
		),
		*LEDResources(pins = '99 98 97 96 95', attrs = Attrs(IO_STANDARD = 'SB_LVCMOS')),
		UARTResource(
			0,
			rx = '9', tx = '8', rts = '7', cts = '4', dtr = '3', dsr = '2', dcd = '1',
			attrs = Attrs(IO_STANDARD = 'SB_LVTTL', PULLUP = 1),
			role = 'dce'
		),
		IrDAResource(
			0,
			rx = '106', tx = '105', sd = '107',
			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS')
		),
		*SPIFlashResources(
			0,
			cs_n = '71', clk = '70', copi = '67', cipo = '68',
			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS')
		),
	]
	connectors  = [
		Connector('pmod', 0, '78 79 80 81 - - 87 88 90 91 - -'), # J2
		Connector('j', 1, '- - 112 113 114 115 116 117 118 119'), # J1
		Connector('j', 3, '- - 62 61 60 56 48 47 45 44'), # J3
	]

	def toolchain_program(self, products: BuildProducts, name: str) -> None:
		from os         import environ
		from subprocess import check_call

		iceprog = environ.get('ICEPROG', 'iceprog')
		with products.extract(f'{name}.bin') as bitstream_filename:
			check_call([iceprog, bitstream_filename])


if __name__ == '__main__':
	from ...test.blinky import Blinky
	ICEStickPlatform().build(Blinky(), do_program = True)
