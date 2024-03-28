"""
This package contains the Python implementation of the interval system,
which is a mechanism for playing back scripted actions.  A range of
interval types has been defined to automate motion, animation, sounds,
color, function calls, as well as other intervals and arbitrary
properties.

All interval types can be conveniently imported from the
:mod:`.IntervalGlobal` module::

   from bamboo.interval.IntervalGlobal import *

For more information about intervals, see the :ref:`intervals` manual page.
"""

from bamboo.interval.actor_interval import ActorInterval
from bamboo.interval.anim_control_interval import AnimControlInterval
from bamboo.interval.function_interval import FunctionInterval
from bamboo.interval.lerp_interval import (LerpPosInterval, LerpHprInterval, LerpColorInterval, LerpFunc,
                                           LerpFuncNS, LerpScaleInterval, LerpShearInterval, LerpQuatInterval,
                                           LerpFunctionInterval, LerpPosHprInterval, LerpTexScaleInterval,
                                           LerpTexOffsetInterval, LerpPosQuatInterval, LerpPosQuatScaleInterval,
                                           LerpPosQuatScaleShearInterval, LerpHprScaleInterval,
                                           LerpPosHprScaleShearInterval, LerpTexRotateInterval, LerpQuatScaleInterval,
                                           LerpColorScaleInterval, LerpPosHprScaleInterval, LerpFunctionNoStateInterval,
                                           LerpNodePathInterval)
from bamboo.interval.indirect_interval import IndirectInterval
from bamboo.interval.interval import Interval
from bamboo.interval.interval_global import *

if __name__ == "__main__":
    from bamboo import Window, DirectObject
    def pr():
        print("HI")
    j = Sequence(AcceptInterval(DirectObject(), "w",     pr), Func(lambda: print("NO")))
    j.start()
    Window().run()