# -*- coding: utf8 -*-
"""Main module for pybossa-analyst."""

import os
from flask import Flask, request
from pybossa_analyst import default_settings
from pybossa_analyst.extensions import *


def create_app():
    """Application factory."""
    app = Flask(__name__)
    configure_app(app)
    setup_url_rules(app)
    setup_auth(app)
    setup_csrf(app)
    setup_z3950_manager(app)
    zip_builder.init_app(app)
    pybossa_client.init_app(app)
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
    from pybossa_analyst.view import blueprint as bp
    app.register_blueprint(bp, url_prefix='')


def setup_auth(app):
    """Setup basic auth for all requests."""
    from pybossa_analyst import auth

    @app.before_request
    def requires_auth():
        if request.endpoint != 'analyse.index':
            cred = request.authorization
            if not cred or not auth.check_auth(cred.username, cred.password):
                return auth.authenticate()


def setup_csrf(app):
    """Setup csrf protection."""
    from pybossa_analyst.view import index
    csrf.init_app(app)
    csrf.exempt(index)


def setup_z3950_manager(app):
    """Setup Flask-Z3950."""
    z3950_manager.init_app(app)
    z3950_manager.register_blueprint(url_prefix='/z3950')
