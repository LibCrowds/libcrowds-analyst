# -*- coding: utf8 -*-
"""Main module for libcrowds-analyst."""

import settings
from flask import Flask, request
from flask_wtf.csrf import CsrfProtect
from libcrowds_analyst import view, auth


def create_app():
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(settings)
    app.config.from_envvar('LIBCROWDS_ANALYST_SETTINGS', silent=True)
    setup_csrf(app)
    setup_url_rules(app)
    setup_auth(app)
    return app


def setup_csrf(app):
    """Setup csrf protection."""
    csrf = CsrfProtect(app)
    csrf.exempt(view.index)


def setup_url_rules(app):
    """Setup URL rules"""
    rules = {'/': view.index,
             '/<short_name>': view.analyse_empty_result,
             '/<short_name>/<int:result_id>/edit': view.edit_result,
             '/<short_name>/reanalyse': view.reanalyse}
    for route, func in rules.items():
        app.add_url_rule(route, view_func=func, methods=['GET', 'POST'])


def setup_auth(app):
    """Setup basic auth for all requests."""
    @app.before_request
    def requires_auth():
        if request.endpoint != 'index' and request.method != 'POST':
            cred = request.authorization
            if not cred or not auth.check_auth(cred.username, cred.password):
                return auth.authenticate()
