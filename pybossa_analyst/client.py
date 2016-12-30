# -*- coding: utf8 -*-
"""API client module for pybossa-analyst."""

import enki


def _configure_client(self, api_key, endpoint):
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
    return (len(last_fetched) != 0 and len(last_fetched) == query['limit'])

def get_results(self, api_key, endpoint, project_id, **kwargs):
    """Return results."""
    self._configure_client(api_key, endpoint)
    return enki.pbclient.find_results(project_id, all=1, **kwargs)

def get_all_results(self, api_key, endpoint, project_id):
    """Return all results."""
    self._configure_client(api_key, endpoint)
    return self._load(enki.pbclient.find_results, project_id)

def get_tasks(self, api_key, endpoint, project_id, **kwargs):
    """Return tasks."""
    self._configure_client(api_key, endpoint)
    return enki.pbclient.find_tasks(project_id, all=1, **kwargs)

def get_task_runs(self, api_key, endpoint, project_id, **kwargs):
    """Return task runs."""
    self._configure_client(api_key, endpoint)
    return enki.pbclient.find_taskruns(project_id, all=1, **kwargs)

def get_projects(self, api_key, endpoint, **kwargs):
    """Return projects."""
    self._configure_client(api_key, endpoint)
    return enki.pbclient.find_project(all=1, **kwargs)

def update_result(self, api_key, endpoint, result):
    """Update a result."""
    self._configure_client(api_key, endpoint)
    return enki.pbclient.update_result(result)

def get_task_run_dataframe(self, api_key, endpoint, project_id, task_id):
    """Return a dataframe containing all task run info for a task."""
    self._configure_client(api_key, endpoint)
    p = self.get_projects(id=project_id, limit=1)[0]
    e = enki.Enki(api_key, endpoint, p.short_name, all=1)
    e.get_tasks(task_id=task_id)
    e.get_task_runs()
    t = e.tasks[0]
    return e.task_runs_df[t.id]
