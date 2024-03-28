"""
This package contains the Python interface to the task system, which
manages scheduled functions that are executed at designated intervals.

The global task manager object can be imported as a singleton::

   from direct.task.TaskManagerGlobal import taskMgr

For more information about the task system, consult the
:ref:`tasks-and-event-handling` page in the programming manual.
"""

from .Timer import Timer
from .Task import Task
from .MiniTask import MiniTaskManager, MiniTask
from .TaskManagerGlobal import taskMgr
