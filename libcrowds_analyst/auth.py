# -*- coding: utf8 -*-
"""Basic auth module for libcrowds-analyst."""

from flask import current_app
from flask import Response


def check_auth(username, password):
    """Check if a username password combination is valid."""
    pw = current_app.config['PASSWORD']
    un = current_app.config['USERNAME']
    return username == un and password == pw


def authenticate():
    """Sends a 401 response that enables basic auth."""
    return Response(
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})
