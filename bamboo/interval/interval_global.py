"""
This module imports all of the other interval modules, to provide a
single convenient module from which all interval types can be imported.
"""

# In this unusual case, I'm not going to declare __all__,
# since the purpose of this module is to add up the contributions
# of a number of other modules.

from .interval import *
from .actor_interval import *
from .function_interval import *
from .lerp_interval import *
from .indirect_interval import *
from .mopath_interval import *
try:
    import panda3d.physics
    # Some people may have the particle system compiled out
    if hasattr(panda3d.physics, 'ParticleSystem'):
        from .particle_interval import *
        if __debug__:
            from .test_interval import *
except ImportError:
    pass
from .sound_interval import *
from .projectile_interval import *
from .meta_interval import *
from .interval_manager import *
from panda3d.direct import WaitInterval
