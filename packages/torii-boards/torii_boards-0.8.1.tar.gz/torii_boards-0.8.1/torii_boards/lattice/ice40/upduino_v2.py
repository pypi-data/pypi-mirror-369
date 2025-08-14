# SPDX-License-Identifier: BSD-2-Clause

from torii.build     import Attrs, Clock, Pins, Resource
from torii.build.run import BuildProducts

from .upduino_v1     import UpduinoV1Platform

__all__ = (
	'UpduinoV2Platform',
)

class UpduinoV2Platform(UpduinoV1Platform):
	pretty_name = 'Upduino V2'
	description = 'TinyVision Upduino V2 Lattice iCE40-UP5K Development Board'

	# Mostly identical to the V1 board, but it has an integrated
	# programmer and a 12MHz oscillator which is NC by default.
	resources = UpduinoV1Platform.resources + [
		# Solder pin 12 to the adjacent 'J8' osc_out pin to enable.
		Resource(
			'clk12', 0, Pins('12', dir = 'i'), Clock(12e6), Attrs(IO_STANDARD = 'SB_LVCMOS')
		),
	]

	def toolchain_program(self, products: BuildProducts, name: str) -> None:
		from os         import environ
		from subprocess import check_call

		iceprog = environ.get('ICEPROG', 'iceprog')
		with products.extract(f'{name}.bin') as bitstream_filename:
			check_call([iceprog, bitstream_filename])


if __name__ == '__main__':
	from ...test.blinky import Blinky
	UpduinoV2Platform().build(Blinky(), do_program = True)
