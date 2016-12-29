# -*- coding: utf8 -*-
"""API client module for pybossa-analyst."""

import enki


class PyBossaClient(object):
    """A class for interacting with PyBossa."""

    def __init__(self, app=None):
        """Init method."""
        self.app = app
        if app is not None:  # pragma: no cover
            self.init_app(app)

    def init_app(self, app):
        self.api_key = app.config['API_KEY']
        self.endpoint = app.config['ENDPOINT']
        enki.pbclient.set('api_key', self.api_key)
        enki.pbclient.set('endpoint', self.endpoint)

    def _load(self, func, project_id):
        query = dict(project_id=project_id, all=1, limit=100)
        items = func(**query)
        last_fetched = items
        while self._not_exhausted(last_fetched, query):
            query['last_id'] = last_fetched[-1].id
            last_fetched = func(**query)
            items += last_fetched
        return items

    def _not_exhausted(self, last_fetched, query):
        return (len(last_fetched) != 0
                and len(last_fetched) == query['limit']
                and query.get('id') is None)

    def get_results(self, project_id, **kwargs):
        """Return results."""
        return enki.pbclient.find_results(project_id, all=1, **kwargs)

    def get_all_results(self, project_id):
        """Return all results."""
        return self._load(enki.pbclient.find_results, project_id)

    def get_tasks(self, project_id, **kwargs):
        """Return tasks."""
        return enki.pbclient.find_tasks(project_id, all=1, **kwargs)

    def get_task_runs(self, project_id, **kwargs):
        """Return task runs."""
        return enki.pbclient.find_taskruns(project_id, all=1, **kwargs)

    def get_projects(self, **kwargs):
        """Return projects."""
        return enki.pbclient.find_project(all=1, **kwargs)

    def update_result(self, result):
        """Update a result."""
        return enki.pbclient.update_result(result)

    def get_task_run_dataframe(self, project_id, task_id):
        """Return a dataframe containing all task run info for a task."""
        p = self.get_projects(id=project_id, limit=1)[0]
        e = enki.Enki(self.api_key, self.endpoint, p.short_name, all=1)
        e.get_tasks(task_id=task_id)
        e.get_task_runs()
        t = e.tasks[0]
        return e.task_runs_df[t.id]
