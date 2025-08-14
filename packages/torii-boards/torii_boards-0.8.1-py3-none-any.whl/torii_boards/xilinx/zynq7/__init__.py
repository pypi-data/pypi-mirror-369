# SPDX-License-Identifier: BSD-2-Clause

from .arty_z7          import ArtyZ720Platform
from .ebaz4205         import EBAZ4205Platform
from .microzed_z010    import MicroZedZ010Platform
from .microzed_z020    import MicroZedZ020Platform
from .zturn_lite_z007s import ZTurnLiteZ007SPlatform
from .zturn_lite_z010  import ZTurnLiteZ010Platform

__all__ = (
	'ArtyZ720Platform',
	'EBAZ4205Platform',
	'MicroZedZ010Platform',
	'MicroZedZ020Platform',
	'ZTurnLiteZ007SPlatform',
	'ZTurnLiteZ010Platform',
)
