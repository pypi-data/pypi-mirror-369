# SPDX-License-Identifier: BSD-2-Clause

from .blackice_ii          import BlackIceIIPlatform
from .blackice             import BlackIcePlatform
from .fomu_hacker          import FomuHackerPlatform
from .fomu_pvt             import FomuPVTPlatform
from .ice40_hx1k_blink_evn import ICE40HX1KBlinkEVNPlatform
from .ice40_hx8k_b_evn     import ICE40HX8KBEVNPlatform
from .ice40_up5k_b_evn     import ICE40UP5KBEVNPlatform
from .icebreaker_bitsy     import ICEBreakerBitsyPlatform
from .icebreaker           import ICEBreakerPlatform
from .icestick             import ICEStickPlatform
from .icesugar_nano        import ICESugarNanoPlatform
from .icesugar             import ICESugarPlatform
from .nandland_go          import NandlandGoPlatform
from .tinyfpga_bx          import TinyFPGABXPlatform
from .upduino_v1           import UpduinoV1Platform
from .upduino_v2           import UpduinoV2Platform
from .upduino_v3           import UpduinoV3Platform

__all__ = (
	'BlackIceIIPlatform',
	'BlackIcePlatform',
	'FomuHackerPlatform',
	'FomuPVTPlatform',
	'ICE40HX1KBlinkEVNPlatform',
	'ICE40HX8KBEVNPlatform',
	'ICE40UP5KBEVNPlatform',
	'ICEBreakerBitsyPlatform',
	'ICEBreakerPlatform',
	'ICEStickPlatform',
	'ICESugarNanoPlatform',
	'ICESugarPlatform',
	'NandlandGoPlatform',
	'TinyFPGABXPlatform',
	'UpduinoV1Platform',
	'UpduinoV2Platform',
	'UpduinoV3Platform',
)
