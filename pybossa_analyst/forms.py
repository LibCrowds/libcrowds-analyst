# -*- coding: utf8 -*-
"""Forms module for pybossa-analyst."""

from flask.ext.wtf import Form
from wtforms import TextAreaField
from wtforms.fields import SelectField
from wtforms.validators import required


class ReanalysisForm(Form):
    """Form for triggering result reanalysis."""
    result_filter = SelectField('Filter:',
                                choices=[('all', 'All'), ('None', 'New'),
                                         ('Unanalysed', 'Unanalysed')])


class DownloadForm(Form):
    """Form for downloading original task input."""
    task_ids = TextAreaField('Task IDs:', validators=[required()])
    importer = SelectField('Importer Type:', choices=[('flickr', 'Flickr')])
