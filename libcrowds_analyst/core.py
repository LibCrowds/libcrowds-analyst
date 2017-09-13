# -*- coding: utf8 -*-
"""Main module for libcrowds-analyst."""

import os
import json
from flask import Flask, make_response
from libcrowds_analyst import default_settings
from werkzeug.http import HTTP_STATUS_CODES


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
    """Setup error handlers."""
    def error_response(status_code, description):  # pragma: no cover
        response = make_response(
            json.dumps({
                "message": HTTP_STATUS_CODES.get(status_code),
                "status": status_code,
                "description": description
            })
        )
        response.mimetype = 'application/json'
        response.status_code = status_code
        return response

    @app.errorhandler(400)
    def _400_error(e):  # pragma: no cover
        return error_response(405, e.description)

    @app.errorhandler(404)
    def _404_error(e):  # pragma: no cover
        return error_response(404, e.description)

    @app.errorhandler(405)
    def _405_error(e):  # pragma: no cover
        return error_response(405, e.description)

    @app.errorhandler(500)
    def _500_error(e):  # pragma: no cover
        return error_response(500, e.description)
