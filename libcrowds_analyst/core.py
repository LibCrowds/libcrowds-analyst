# -*- coding: utf8 -*-
"""Main module for libcrowds-analyst."""

import os
from flask import Flask, jsonify
from libcrowds_analyst import default_settings


def create_app():
    """Application factory."""
    app = Flask(__name__)
    configure_app(app)
    setup_url_rules(app)
    setup_error_handler(app)
    return app


def configure_app(app):
    """Configure the app."""
    app.config.from_object(default_settings)
    app.config.from_envvar('LIBCROWDS_ANALYST_SETTINGS', silent=True)
    if not os.environ.get('LIBCROWDS_ANALYST_SETTINGS'):  # pragma: no cover
        here = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(os.path.dirname(here), 'settings.py')
        if os.path.exists(config_path):
            app.config.from_pyfile(config_path)


def setup_url_rules(app):
    """Setup URL rules."""
    from libcrowds_analyst.api import BP as api_bp
    app.register_blueprint(api_bp, url_prefix='/')


def setup_error_handler(app):
    """Setup error handler."""
    @app.errorhandler(Exception)
    def _handle_error(error):  # pragma: no cover
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
