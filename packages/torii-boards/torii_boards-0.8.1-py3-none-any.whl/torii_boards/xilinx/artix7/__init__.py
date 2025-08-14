# SPDX-License-Identifier: BSD-2-Clause

from .alchitry_au     import AlchitryAuPlatform
from .arty_a7         import ArtyA7_35Platform, ArtyA7_100Platform
from .cmod_a7         import CmodA7_15Platform, CmodA7_35Platform
from .mega65          import Mega65r3Platform
from .nexys4ddr       import Nexys4DDRPlatform
from .te0714_03_50_2I import TE0714_03_50_2IPlatform

__all__ = (
	'AlchitryAuPlatform',
	'ArtyA7_35Platform',
	'ArtyA7_100Platform',
	'CmodA7_15Platform',
	'CmodA7_35Platform',
	'Mega65r3Platform',
	'Nexys4DDRPlatform',
	'TE0714_03_50_2IPlatform',
)
