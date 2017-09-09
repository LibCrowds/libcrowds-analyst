# -*- coding: utf8 -*-
"""Main module for libcrowds-analyst."""

import os
from flask import Flask
from werkzeug.exceptions import HTTPException, InternalServerError
from requests.exceptions import RequestException
from libcrowds_analyst import default_settings
from libcrowds_analyst.extensions import z3950_manager


def create_app():
    """Application factory."""
    app = Flask(__name__)
    configure_app(app)
    setup_error_handler(app)
    setup_z3950_manager(app)
    return app


def configure_app(app):
    """Configure the app."""
    app.config.from_object(default_settings)
    app.config.from_envvar('libcrowds_analyst_SETTINGS', silent=True)
    if not os.environ.get('libcrowds_analyst_SETTINGS'):  # pragma: no cover
        here = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(os.path.dirname(here), 'settings.py')
        if os.path.exists(config_path):
            app.config.from_pyfile(config_path)


def setup_url_rules(app):
    """Setup URL rules."""
    from libcrowds_analyst.api import blueprint as api
    app.register_blueprint(api, url_prefix='/')


def setup_error_handler(app):
    """Setup error handler."""
    @app.errorhandler(Exception)
    def _handle_error(e):  # pragma: no cover
        if app.debug:
            raise
        if isinstance(e, RequestException):
            endpoint = app.config['ENDPOINT']
            e.code = 500
            e.description = "Could not connect to {0}.".format(endpoint)
        elif not isinstance(e, HTTPException):
            e = InternalServerError()
        return render_template('error.html', exception=e), e.code


def setup_z3950_manager(app):
    """Setup Flask-Z3950."""
    z3950_manager.init_app(app)
    z3950_manager.register_blueprint(url_prefix='/z3950')
