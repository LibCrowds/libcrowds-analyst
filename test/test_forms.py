# -*- coding: utf8 -*-

import pytest
from wtforms.validators import ValidationError
from libcrowds_analyst.forms import JSONValidator, EditResultForm

class TestForms(object):

    def test_json_validator(self, app):
        v = JSONValidator()
        with app.test_request_context('/'):
            form = EditResultForm()
            with pytest.raises(ValidationError) as exc_info:
                v.__call__(form, form.info)
            assert exc_info.value.message == 'Invalid JSON.'
