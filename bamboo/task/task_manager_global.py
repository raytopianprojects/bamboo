"""Contains the global :class:`~.Task.TaskManager` object."""

__all__ = ['taskMgr']

from bamboo.task import task

#: The global task manager.
taskMgr = task.TaskManager()
