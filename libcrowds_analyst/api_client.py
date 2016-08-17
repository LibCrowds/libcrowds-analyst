# -*- coding: utf8 -*-
"""API client module for libcrowds-analyst."""

import pbclient
from flask import abort


class APIClient(object):
    """A class for interacting with the PyBossa API."""

    def __init__(self, app=None):
        """Init method."""
        self.app = app
        if app is not None:  # pragma: no cover
            self.init_app(app)

    def init_app(self, app):
        pbclient.set('api_key', app.config['API_KEY'])
        pbclient.set('endpoint', app.config['ENDPOINT'])

    def get_first_result(self, project_id, **kwargs):
        """Return the first result or abort an exception is thrown."""
        res = pbclient.find_results(project_id, limit=1, all=1, **kwargs)
        if isinstance(res, dict) and 'status_code' in res:  # pragma: no cover
            abort(res['status_code'])
        return res[0] if res else None

    def update_result(self, result):
        """Update a result or abort if an exception is thrown."""
        res = pbclient.update_result(result)
        if isinstance(res, dict) and 'status_code' in res:  # pragma: no cover
            abort(res['status_code'])

    def get_project(self, short_name):
        """Return a project or abort an exception is thrown."""
        res = pbclient.find_project(short_name=short_name, all=1)
        if isinstance(res, dict) and 'status_code' in res:  # pragma: no cover
            abort(res['status_code'])
        return res[0] if res else None
