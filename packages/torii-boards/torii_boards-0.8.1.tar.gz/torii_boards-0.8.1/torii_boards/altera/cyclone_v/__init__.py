# SPDX-License-Identifier: BSD-2-Clause

from .chameleon96 import Chameleon96Platform
from .de0_cv      import DE0CVPlatform
from .de1_soc     import DE1SoCPlatform
from .de10_nano   import DE10NanoPlatform
from .mister      import MisterPlatform

__all__ = (
	'Chameleon96Platform',
	'DE0CVPlatform',
	'DE1SoCPlatform',
	'DE10NanoPlatform',
	'MisterPlatform',
)
