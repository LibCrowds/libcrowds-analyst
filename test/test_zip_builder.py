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

    def test_flickr_importer_identified(self, app):
        """Test Flickr importer identified."""
        gen = zip_builder.generate([], 'flickr')
        assert gen.__name__ == '_generate_flickr_zip'

    def test_correct_image_downloaded_from_flickr(self, app, task, mocker):
        """Test filckr zip file is built with the correct tasks."""
        mock_requests = mocker.patch('pybossa_analyst.zip_builder.requests')
        gen = zip_builder._generate_flickr_zip([task])
        gen.next()
        mock_requests.get.assert_called_once_with(task.info['url'])

    def test_error_when_flickr_url_not_in_task_info(self, app, task):
        """Test error raised when url not in task info."""
        task.info.pop("url")
        gen = zip_builder._generate_flickr_zip([task])
        with pytest.raises(ValueError) as excinfo:
            gen.next()
        assert excinfo.value.message == 'Invalid Flickr task'

    def test_error_when_title_not_in_task_info(self, app, task):
        """Test error raised when title not in task info."""
        task.info.pop("title")
        gen = zip_builder._generate_flickr_zip([task])
        with pytest.raises(ValueError) as excinfo:
            gen.next()
        assert excinfo.value.message == 'Invalid Flickr task'
