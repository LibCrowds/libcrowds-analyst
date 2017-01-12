# -*- coding: utf8 -*-
"""Forms module for pybossa-analyst."""

from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.fields import SelectField, TextField
from wtforms.validators import required


class SetupForm(FlaskForm):
    """Form for triggering result reanalysis."""
    info_filter = SelectField('Filter:',
                              choices=[('All', 'All'), ('New', 'New'),
                                       ('Unverified', 'Unverified')])


class DownloadForm(FlaskForm):
    """Form for downloading original task input."""
    task_ids = TextAreaField('Task IDs:', validators=[required()])
    importer = SelectField('Importer Type:',
                           choices=[('flickr', 'Flickr'),
                                    ('dropbox', 'Dropbox')])


class LoginForm(FlaskForm):
    """Form for logging in user's using their PyBossa API key."""
    err_msg = "The API key is required"
    api_key = TextField('API Key:', validators=[required(err_msg)])
