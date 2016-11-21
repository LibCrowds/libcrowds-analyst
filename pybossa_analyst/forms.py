# -*- coding: utf8 -*-
"""Forms module for pybossa-analyst."""

from flask.ext.wtf import Form
from wtforms import TextAreaField
from wtforms.fields import IntegerField, SelectField
from wtforms.validators import required


class ReanalysisForm(Form):
    """Form for triggering result reanalysis."""
    sleep = IntegerField('Sleep:', default=2)


class DownloadForm(Form):
    """Form for downloading original task input."""
    task_ids = TextAreaField('Task IDs:', validators=[required()])
    importer = SelectField('Importer Type:', choices=[('flickr', 'Flickr')])
