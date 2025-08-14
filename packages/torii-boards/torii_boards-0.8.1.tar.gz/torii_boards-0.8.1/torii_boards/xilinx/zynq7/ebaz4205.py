# SPDX-License-Identifier: BSD-2-Clause

from torii.build                        import Attrs, Clock, Pins, Resource
from torii.build.run                    import BuildProducts
from torii.platform.resources.interface import UARTResource
from torii.platform.resources.user      import LEDResources
from torii.platform.vendor.xilinx       import XilinxPlatform

__all__ = (
	'EBAZ4205Platform',
)

class EBAZ4205Platform(XilinxPlatform):
	device      = 'xc7z010'
	package     = 'clg400'
	speed       = '1'
	default_clk = 'clk33_333'

	pretty_name = 'EBAZ4205'
	description = 'EBAZ4205 Ebit E9+ Xilinx Zynq-7010 Board'

	resources   = [
		Resource(
			'clk33_333', 0, Pins('N18', dir = 'i'), Clock(33.333e6), Attrs(IOSTANDARD = 'LVCMOS33')
		),
		*LEDResources(
			pins = 'W14 W13',
			attrs = Attrs(IOSTANDARD = 'LVCMOS33')
		),
		UARTResource(
			0,
			rx = 'B19', tx = 'B20',
			attrs = Attrs(IOSTANDARD = 'LVCMOS33')
		),
	]

	connectors = []

	def toolchain_program(self, products: BuildProducts, name: str, **kwargs) -> None:
		from os         import environ
		from subprocess import run

		xc3sprog = environ.get('XC3SPROG', 'xc3sprog')
		with products.extract(f'{name}.bit') as bitstream_filename:
			run([xc3sprog, '-c', 'jtaghs1_fast', '-p', '1', bitstream_filename], check = True)


if __name__ == '__main__':
	from ...test.blinky import Blinky
	EBAZ4205Platform().build(Blinky(), do_program = True)
