# -*- coding: utf8 -*-

import pytest
from pytest_mock import mocker
from pybossa_analyst import zip_builder


class TestZipBuilder(object):

    def test_invalid_importer_identified(self):
        """Test error raised when attempting to build with invalid importer."""
        with pytest.raises(ValueError) as excinfo:
            zip_builder.generate([], 'unknown_importer')
        assert excinfo.value.message == 'Unknown importer type'

    def test_flickr_importer_identified(self, mocker, task):
        """Test Flickr importer identified."""
        mock_gen = mocker.patch('pybossa_analyst.zip_builder._generate_zip')
        zip_builder.generate([task], 'flickr')
        mock_gen.assert_called_with([task], "title", "url")

    def test_dropbox_importer_identified(self, mocker, task):
        """Test Dropbox importer identified."""
        mock_gen = mocker.patch('pybossa_analyst.zip_builder._generate_zip')
        zip_builder.generate([task], 'dropbox')
        mock_gen.assert_called_with([task], "filename", "link_raw")

    def test_correct_file_downloaded(self, mocker, task):
        """Test zip file is built with the correct task input."""
        mock_download = mocker.patch('pybossa_analyst.zip_builder._download')
        gen = zip_builder._generate_zip([task], 'title', 'url')
        [x for x in gen]
        url = task.info['url']
        mock_download.assert_called_once_with(url)
