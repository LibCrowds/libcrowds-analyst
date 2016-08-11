# -*- coding: utf8 -*-
"""Main module for libcrowds-analyst."""

import os
from flask import Flask, request
from libcrowds_analyst import default_settings
from libcrowds_analyst.extensions import zip_builder, csrf, z3950_manager
from libcrowds_analyst import view, auth


def create_app():
    """Application factory."""
    app = Flask(__name__)
    configure_app(app)
    setup_url_rules(app)
    setup_auth(app)
    setup_csrf(app)
    setup_z3950_manager(app)
    zip_builder.init_app(app)
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
    rules = {'/': view.index,
             '/<short_name>/': view.analyse_next_empty_result,
             '/<short_name>/<int:result_id>/': view.analyse_result,
             '/<short_name>/<int:result_id>/edit/': view.edit_result,
             '/<short_name>/reanalyse/': view.reanalyse,
             '/<short_name>/download/': view.prepare_zip,
             '/<short_name>/download/<path:filename>/check': view.check_zip,
             '/<short_name>/download/<path:filename>': view.download_zip}
    for route, func in rules.items():
        app.add_url_rule(route, view_func=func, methods=['GET', 'POST'])


def setup_auth(app):
    """Setup basic auth for all requests."""
    @app.before_request
    def requires_auth():
        if request.endpoint != 'index':
            cred = request.authorization
            if not cred or not auth.check_auth(cred.username, cred.password):
                return auth.authenticate()


def setup_csrf(app):
    """Setup csrf protection."""
    csrf.init_app(app)
    csrf.exempt(view.index)


def setup_z3950_manager(app):
    """Setup Flask-Z3950."""
    z3950_manager.init_app(app)
    z3950_manager.register_blueprint(url_prefix='/z3950')
