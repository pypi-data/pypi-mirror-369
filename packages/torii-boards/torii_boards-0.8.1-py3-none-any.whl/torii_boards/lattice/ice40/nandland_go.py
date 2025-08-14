# SPDX-License-Identifier: BSD-2-Clause

from torii.build                         import Clock, Connector, Pins, Resource
from torii.build.run                     import BuildProducts
from torii.platform.resources.display    import Display7SegResource, VGAResource
from torii.platform.resources.interface  import UARTResource
from torii.platform.resources.memory     import SPIFlashResources
from torii.platform.resources.user       import ButtonResources, LEDResources
from torii.platform.vendor.lattice.ice40 import ICE40Platform

__all__ = (
	'NandlandGoPlatform',
)

class NandlandGoPlatform(ICE40Platform):
	device      = 'iCE40HX1K'
	package     = 'VQ100'
	default_clk = 'clk25'

	pretty_name = 'Nandland Go'
	description = 'Nandland Go Lattice iCE40-HX1K Development Board'

	resources = [
		Resource(
			'clk25', 0, Pins('15', dir = 'i'), Clock(25e6)
		),
		*LEDResources(pins = '56 57 59 60'),
		*ButtonResources(pins = '53 51 54 52'),
		Display7SegResource(
			0,
			a = '3', b = '4', c = '93', d = '91', e = '90', f = '1', g = '2',
			invert = True
		),
		Display7SegResource(
			1,
			a = '100', b = '99', c = '97', d = '95', e = '94', f = '8', g = '96',
			invert = True
		),
		UARTResource(0, rx = '73', tx = '74'),
		*SPIFlashResources(0, cs_n = '49', clk = '48', copi = '45', cipo = '46'),
		VGAResource(
			0,
			r = '36 37 40',
			g = '29 30 33',
			b = '28 41 42',
			hs = '26', vs = '27'
		),
	]
	connectors = [
		Connector('pmod', 0, '65 64 63 62 - - 78 79 80 81 - -'),
	]

	def toolchain_program(self, products: BuildProducts, name: str) -> None:
		from os         import environ
		from subprocess import check_call

		iceprog = environ.get('ICEPROG', 'iceprog')
		with products.extract(f'{name}.bin') as bitstream_filename:
			check_call([iceprog, bitstream_filename])


if __name__ == '__main__':
	from ...test.blinky import Blinky
	NandlandGoPlatform().build(Blinky(), do_program = True)
