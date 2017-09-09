# -*- coding: utf8 -*-
"""Auth module for libcrowds-analyst."""

import pbclient
from werkzeug.exceptions import Unauthorized


def ensure_authorized_to_update(short_name):
    """Ensure that a result can be updated using the current API key."""
    p = pbclient.find_project(short_name=short_name, all=1)[0]
    r = pbclient.find_results(p.id, limit=1, all=1)[0]
    resp = pbclient.update_result(r)
    if isinstance(resp, dict) and resp.get('status_code') == 401:
        err_msg = ("You are not authorised to update results for this project",
                   "using the API key provided.")
        raise Unauthorized(err_msg)
