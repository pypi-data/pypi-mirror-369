# SPDX-License-Identifier: BSD-2-Clause

from torii.build                        import Attrs, Clock, DiffPairs, Resource
from torii.build.run                    import BuildProducts
from torii.platform.resources.interface import UARTResource
from torii.platform.resources.user      import LEDResources
from torii.platform.vendor.xilinx       import XilinxPlatform

__all__ = (
	'KC705Platform',
)

class KC705Platform(XilinxPlatform):
	device      = 'xc7k325t'
	package     = 'ffg900'
	speed       = '2'
	default_clk = 'clk156'

	pretty_name = 'KC705'
	description = 'Xilinx KC705 Kintex7-325T Evaluation Board'

	resources   = [
		Resource(
			'clk156', 0, DiffPairs('K28', 'K29', dir = 'i'), Clock(156e6), Attrs(IOSTANDARD = 'LVDS_25')
		),
		*LEDResources(
			pins = 'AB8 AA8 AC9 AB9 AE26 G19 E18 F16',
			attrs = Attrs(IOSTANDARD = 'LVCMOS15')
		),
		UARTResource(
			0,
			rx = 'M19', tx = 'K24',
			attrs = Attrs(IOSTANDARD = 'LVCMOS33')
		),
	]

	def toolchain_program(self, products: BuildProducts, name: str) -> None:
		from os         import environ
		from subprocess import check_call

		openocd = environ.get('OPENOCD', 'openocd')
		with products.extract(f'{name}.bit') as bitstream_filename:
			check_call([
				openocd, '-c', f'source [find board/kc705.cfg]; init; pld load 0 {bitstream_filename}; exit'
			])


if __name__ == '__main__':
	from ...test.blinky import Blinky
	KC705Platform().build(Blinky(), do_program = True)
