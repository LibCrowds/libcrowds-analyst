# -*- coding: utf8 -*-
"""Forms module for libcrowds-analyst."""

import json
from flask.ext.wtf import Form
from wtforms import TextAreaField
from wtforms.validators import ValidationError


class JSONValidator(object):
    """Validator that checks for valid JSON."""

    def __init__(self):
        self.message = 'Invalid JSON.'

    def __call__(self, _form, field):
        try:
            json.loads(field.data)
        except (ValueError, TypeError):
            raise ValidationError(self.message)


class EditResultForm(Form):
    """Form for directly editing the info field of a result."""
    info = TextAreaField('Result Info:', validators=[JSONValidator()])
