# -*- coding: utf8 -*-
"""Main module for pybossa-analyst."""

import os
from flask import Flask, request, render_template
from werkzeug.exceptions import HTTPException, InternalServerError
from requests.exceptions import RequestException
from pybossa_analyst import default_settings
from pybossa_analyst.extensions import *


def create_app():
    """Application factory."""
    app = Flask(__name__)
    configure_app(app)
    setup_url_rules(app)
    setup_csrf(app)
    setup_error_handler(app)
    setup_hooks(app)
    setup_z3950_manager(app)
    return app


def configure_app(app):
    """Configure the app."""
    app.config.from_object(default_settings)
    app.config.from_envvar('PYBOSSA_ANALYST_SETTINGS', silent=True)
    if not os.environ.get('PYBOSSA_ANALYST_SETTINGS'):  # pragma: no cover
        here = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(os.path.dirname(here), 'settings.py')
        if os.path.exists(config_path):
            app.config.from_pyfile(config_path)


def setup_url_rules(app):
    """Setup URL rules."""
    from pybossa_analyst.view.home import blueprint as home
    from pybossa_analyst.view.analysis import blueprint as analyse
    from pybossa_analyst.view.download import blueprint as download
    app.register_blueprint(home, url_prefix='/')
    app.register_blueprint(analyse, url_prefix='/analysis')
    app.register_blueprint(download, url_prefix='/download')


def setup_csrf(app):
    """Setup csrf protection."""
    from pybossa_analyst.view.home import index
    csrf.init_app(app)
    csrf.exempt(index)


def setup_error_handler(app):
    """Setup error handler."""
    @app.errorhandler(Exception)
    def _handle_error(e):
        if app.debug:
            raise
        if isinstance(e, RequestException):
            endpoint = app.config['ENDPOINT']
            e.code = 500
            e.description = "Could not connect to {0}.".format(endpoint)
        elif not isinstance(e, HTTPException):
            e = InternalServerError()
        return render_template('error.html', exception=e), e.code


def setup_hooks(app):
    """Setup hooks."""
    @app.context_processor
    def _global_template_context():
        return dict(
            brand=app.config['BRAND'],
            github_url=app.config['GITHUB_URL']
        )


def setup_z3950_manager(app):
    """Setup Flask-Z3950."""
    z3950_manager.init_app(app)
    z3950_manager.register_blueprint(url_prefix='/z3950')
