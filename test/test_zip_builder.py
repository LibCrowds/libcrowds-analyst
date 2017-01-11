# -*- coding: utf8 -*-

import pytest
from pytest_mock import mocker
from pybossa_analyst import zip_builder


class TestZipBuilder(object):

    def test_invalid_importer_identified(self, app):
        """Test error raised when attempting to build with invalid importer."""
        with pytest.raises(ValueError) as excinfo:
            zip_builder.generate([], 'unknown_importer')
        assert excinfo.value.message == 'Unknown importer type'

    def test_correct_file_downloaded(self, app, task, mocker):
        """Test zip file is built with the correct task input."""
        mock_requests = mocker.patch('pybossa_analyst.zip_builder.requests')
        gen = zip_builder._generate_zip([task], 'title', 'url')
        [x for x in gen]
        url = task.info['url']
        mock_requests.get.assert_called_once_with(url, stream=True)
