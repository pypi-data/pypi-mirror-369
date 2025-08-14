# SPDX-License-Identifier: BSD-2-Clause

from .colorlight_5a75b_r7_0 import Colorlight_5A75B_R70Platform
from .ecp5_5g_evn           import ECP55GEVNPlatform
from .ecpix5                import ECPIX545Platform, ECPIX585Platform
from .logicbone             import LogicbonePlatform, Logicbone85FPlatform
from .orangecrab_r0_1       import OrangeCrabR0_1Platform
from .orangecrab_r0_2       import OrangeCrabR0_2_25FPlatform, OrangeCrabR0_2_85FPlatform
from .supercon19badge       import Supercon19BadgePlatform
from .ulx3s                 import ULX3S_12F_Platform, ULX3S_25F_Platform, ULX3S_45F_Platform, ULX3S_85F_Platform
from .versa_ecp5_5g         import VersaECP55GPlatform
from .versa_ecp5            import VersaECP5Platform

__all__ = (
	'Colorlight_5A75B_R70Platform',
	'ECP55GEVNPlatform',
	'ECPIX545Platform',
	'ECPIX585Platform',
	'LogicbonePlatform',
	'Logicbone85FPlatform',
	'OrangeCrabR0_1Platform',
	'OrangeCrabR0_2_25FPlatform',
	'OrangeCrabR0_2_85FPlatform',
	'Supercon19BadgePlatform',
	'ULX3S_12F_Platform',
	'ULX3S_25F_Platform',
	'ULX3S_45F_Platform',
	'ULX3S_85F_Platform',
	'VersaECP55GPlatform',
	'VersaECP5Platform',
)
