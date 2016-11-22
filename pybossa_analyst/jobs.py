# -*- coding: utf8 -*-
"""Jobs module for pybossa-analyst."""

from datetime import datetime
from redis import Redis
from rq_scheduler import Scheduler
from pybossa_analyst.core import zip_builder


scheduler = Scheduler('pybossa_analyst', connection=Redis())
ONE_HOUR = 60*60


def _already_scheduled(func):
    """Return True if a job has already been scheduled, False otherwise."""
    scheduled = [j.func_name for j in scheduler.get_jobs()]
    return func.__name__ in scheduled


def remove_old_zips():
    """Schedule the removal of all old zip files."""
    if not _already_scheduled(zip_builder.remove_old_zips):
        return scheduler.schedule(scheduled_time=datetime.utcnow(),
                                  func=zip_builder.remove_old_zips,
                                  interval=ONE_HOUR,
                                  repeat=None)
