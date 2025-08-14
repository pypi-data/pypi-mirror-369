# SPDX-License-Identifier: BSD-2-Clause

from .versa_ecp5 import VersaECP5Platform

__all__ = (
	'VersaECP55GPlatform',
)

class VersaECP55GPlatform(VersaECP5Platform):
	device      = 'LFE5UM5G-45F'

	pretty_name = 'Versa 5G'
	description = 'Lattice Versa 5G ECP5-5G-45F Evaluation Board'

	# Everything else is identical between 3G and 5G Versa boards.


if __name__ == '__main__':
	from ...test.blinky import Blinky
	VersaECP55GPlatform().build(Blinky(), do_program = True)
