# SPDX-License-Identifier: BSD-2-Clause

from pathlib                   import Path
from unittest                  import TestCase

from torii.platform.vendor     import LatticeECP5Platform

from torii_boards.lattice.ecp5 import (
	orangecrab_r0_1, orangecrab_r0_2, versa_ecp5, versa_ecp5_5g
)
from torii_boards.test.blinky  import Blinky

BUILD_DIR = (Path(__file__).parent / '..' / 'build' / 'test_boards').resolve()

class ToriiBoardsECP5Tests(TestCase):
	def _test_platform(platform: LatticeECP5Platform):
		BUILD_DIR.mkdir(exist_ok = True, parents = True)

		def test_platform(self):
			plat_name  = type(platform).__name__
			plat_build = (BUILD_DIR / plat_name)
			platform.build(Blinky(), plat_name, plat_build, do_build = True, do_program = False)
		return test_platform

	test_versa_ecp5        = _test_platform(versa_ecp5.VersaECP5Platform())
	test_versa_ecp5_5g     = _test_platform(versa_ecp5_5g.VersaECP55GPlatform())
	test_orangecrab_r0_1   = _test_platform(orangecrab_r0_1.OrangeCrabR0_1Platform())
	test_orangecrab_r0_225 = _test_platform(orangecrab_r0_2.OrangeCrabR0_2_25FPlatform())
	test_orangecrab_r0_285 = _test_platform(orangecrab_r0_2.OrangeCrabR0_2_85FPlatform())
