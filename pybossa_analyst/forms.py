# -*- coding: utf8 -*-
"""Forms module for pybossa-analyst."""

from flask.ext.wtf import Form
from wtforms import TextAreaField
from wtforms.fields import SelectField, TextField
from wtforms.validators import required


class SetupForm(Form):
    """Form for triggering result reanalysis."""
    result_filter = SelectField('Filter:',
                                choices=[('all', 'All'), ('None', 'New'),
                                         ('Unanalysed', 'Unanalysed')])


class DownloadForm(Form):
    """Form for downloading original task input."""
    task_ids = TextAreaField('Task IDs:', validators=[required()])
    importer = SelectField('Importer Type:', choices=[('flickr', 'Flickr')])



class LoginForm(Form):
    """Form for logging in user's using their PyBossa API key."""
    err_msg = "The API key is required"
    api_key = TextField('API Key:', validators=[required(err_msg)])
