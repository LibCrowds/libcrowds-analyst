# -*- coding: utf8 -*-

import pytest
from pytest_mock import mocker
from werkzeug.exceptions import Unauthorized
from libcrowds_analyst import auth


class TestAuth(object):

    def test_unauthorized_to_update(self, mocker, project):
        """Test unauthorized error raised when error response returned."""
        mock_pbclient = mocker.patch('libcrowds_analyst.auth.pbclient')
        mock_pbclient.update_result.return_value = {'status_code': 401}
        with pytest.raises(Unauthorized) as excinfo:
            auth.ensure_authorized_to_update(project.short_name)
        err_msg = ("You are not authorised to update results for this project",
                   "using the API key provided.")
        assert excinfo.value.description == err_msg
