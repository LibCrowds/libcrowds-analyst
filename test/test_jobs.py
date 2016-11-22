# -*- coding: utf8 -*-

from redis import Redis
from pybossa_analyst import jobs


class TestJobs(object):
    """Test jobs module."""

    def setup(self):
        Redis().flushall()

    def test_zip_removal_scheduled(self):
        """Test that the zip removal job is scheduled."""
        job = jobs.remove_old_zips()
        assert job._id in jobs.scheduler

    def test_zip_removal_only_scheduled_once(self):
        """Test that the zip removal job is only scheduled once."""
        jobs.remove_old_zips()
        jobs.remove_old_zips()
        n_jobs = len(jobs.scheduler.get_jobs())
        assert n_jobs == 1

    def test_non_scheduled_job_identified(self):
        """Test that a non scheduled job is identified."""
        def func():
            pass
        assert jobs._already_scheduled(func) is False
