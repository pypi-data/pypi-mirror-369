# SPDX-License-Identifier: BSD-2-Clause

from pathlib                    import Path
from unittest                   import TestCase

from torii.platform.vendor      import LatticeICE40Platform

from torii_boards.lattice.ice40 import (
	ice40_hx1k_blink_evn, ice40_hx8k_b_evn, ice40_up5k_b_evn, icebreaker, icebreaker_bitsy,
)
from torii_boards.test.blinky   import Blinky

BUILD_DIR = (Path(__file__).parent / '..' / 'build' / 'test_boards').resolve()

class ToriiBoardsICE40Tests(TestCase):
	def _test_platform(platform: LatticeICE40Platform):
		BUILD_DIR.mkdir(exist_ok = True, parents = True)

		def test_platform(self):
			plat_name  = type(platform).__name__
			plat_build = (BUILD_DIR / plat_name)
			platform.build(Blinky(), plat_name, plat_build, do_build = True, do_program = False)
		return test_platform

	test_icebreaker           = _test_platform(icebreaker.ICEBreakerPlatform())
	test_icebreaker_bitsy     = _test_platform(icebreaker_bitsy.ICEBreakerBitsyPlatform())
	test_ice40_up5k_b_evn     = _test_platform(ice40_up5k_b_evn.ICE40UP5KBEVNPlatform())
	test_ice40_hx1k_blink_evn = _test_platform(ice40_hx1k_blink_evn.ICE40HX1KBlinkEVNPlatform())
	test_ice40_hx8k_b_evn     = _test_platform(ice40_hx8k_b_evn.ICE40HX8KBEVNPlatform())
