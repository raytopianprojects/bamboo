__all__ = ['jobMgr']

from . import job_manager

#: Contains the global :class:`~.JobManager.JobManager` object.
jobMgr = job_manager.JobManager()
