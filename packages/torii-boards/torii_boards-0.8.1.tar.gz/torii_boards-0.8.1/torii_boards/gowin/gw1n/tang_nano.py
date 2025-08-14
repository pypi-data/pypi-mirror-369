# SPDX-License-Identifier: BSD-2-Clause

import subprocess

from torii.build                        import Attrs, Clock, Pins, Resource, Subsignal
from torii.platform.resources.interface import UARTResource
from torii.platform.resources.memory    import SPIFlashResources
from torii.platform.resources.user      import ButtonResources, RGBLEDResource
from torii.platform.vendor.gowin        import GowinPlatform

__all__ = (
	'TangNanoPlatform',
)

class TangNanoPlatform(GowinPlatform):
	part        = 'GW1N-LV1QN48C6/I5'
	family      = 'GW1N-1'
	default_clk = 'OSC'
	osc_frequency = 24_000_000

	pretty_name = 'Tang Nano'
	description = 'Sipeed Tang Nano Gowin GW1N-1 Development Board'

	resources   = [
		# This clock is shared with the USB-JTAG MCU and stops when the USB bus is suspended.
		# It probably should not be used, but is included for completeness.
		Resource(
			'clk24', 0, Pins('35', dir = 'i'), Clock(24_000_000), Attrs(IO_TYPE = 'LVCMOS33')
		),
		RGBLEDResource(0, r = '18', g = '16', b = '17', attrs = Attrs(IO_TYPE = 'LVCMOS33')),
		*ButtonResources(pins = '15 14', invert = True, attrs = Attrs(IO_TYPE = 'LVCMOS33')),
		UARTResource(0, tx = '9', rx = '8', attrs = Attrs(IO_TYPE = 'LVCMOS33', PULL_MODE = 'UP')),
		*SPIFlashResources(
			0,
			cs_n = '19', clk = '20', copi = '22', cipo = '23', wp_n = '24', hold_n = '25',
			attrs = Attrs(IO_TYPE = 'LVCMOS33')
		),
		# TODO(aki): Replace with `LCDResource` when in Torii
		Resource(
			'lcd', 0,
			Subsignal('clk', Pins('11', dir = 'o')),
			Subsignal('hs', Pins('10', dir = 'o')),
			Subsignal('vs', Pins('46', dir = 'o')),
			Subsignal('de', Pins('5', dir = 'o')),
			Subsignal('r', Pins('27 28 29 30 31', dir = 'o')),
			Subsignal('g', Pins('32 33 34 38 39 40', dir = 'o')),
			Subsignal('b', Pins('41 42 43 44 45', dir = 'o')),
			Attrs(IO_TYPE = 'LVCMOS33')
		),
		Resource('lcd_backlight', 0, Pins('47', dir = 'o'), Attrs(IO_TYPE = 'LVCMOS33')),
	]

	def toolchain_prepare(self, fragment, name, **kwargs):
		overrides = {
			'add_options': 'set_option -use_mspi_as_gpio 1 -use_sspi_as_gpio 1',
			'gowin_pack_opts': '--sspi_as_gpio --mspi_as_gpio'
		}
		return super().toolchain_prepare(fragment, name, **overrides, **kwargs)

	def toolchain_program(self, products, name):
		with products.extract(f'{name}.fs') as bitstream_filename:
			subprocess.check_call([
				'openFPGALoader', '-b', 'tangnano', bitstream_filename
			])


if __name__ == '__main__':
	from ...test.blinky import Blinky
	TangNanoPlatform().build(Blinky(), do_program = True)
