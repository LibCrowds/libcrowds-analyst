# -*- coding: utf8 -*-

import os
import time
import pytest
import tempfile
from pytest_mock import mocker
from pybossa_analyst.zip_builder import ZipBuilder


class TestZipBuilder(object):

    def test_build_and_completed_folders_created(self, app):
        """Test that the build and completed subfolders are created."""
        zf = app.config['ZIP_FOLDER']
        build_folder = os.path.join(zf, 'Building')
        completed_folder = os.path.join(zf, 'Complete')
        zb = ZipBuilder(app)
        assert os.path.isdir(build_folder)
        assert os.path.isdir(completed_folder)

    def test_completed_zipfile_marked_as_ready(self, app):
        """Test a completed file is identified as ready for download."""
        zb = ZipBuilder(app)
        tmpzf = tempfile.NamedTemporaryFile(dir=zb.completed_folder)
        fn = os.path.basename(tmpzf.name)
        file_ready = zb.check_zip(fn)
        assert file_ready

    def test_incomplete_zipfile_not_marked_as_ready(self, app):
        """Test an incomplete file is identified as not ready for download."""
        zb = ZipBuilder(app)
        tmpzf = tempfile.NamedTemporaryFile(dir=zb.build_folder)
        fn = os.path.basename(tmpzf.name)
        file_ready = zb.check_zip(fn)
        assert not file_ready

    def test_unknown_filename_raises_error(self, app):
        """Test error raised when checking if an unknown filename is ready."""
        zb = ZipBuilder(app)
        with pytest.raises(ValueError) as excinfo:
            zb.check_zip('nothing.zip')
        assert excinfo.value.message == 'Unknown filename'

    def test_zipfile_download_response_valid(self, app, mocker):
        """Test that a valid response to download a zipfile is returned."""
        mock_send = mocker.patch('pybossa_analyst.zip_builder.send_file')
        zb = ZipBuilder(app)
        tmpzf = tempfile.NamedTemporaryFile(dir=zb.completed_folder)
        fn = os.path.basename(tmpzf.name)
        zb.response_zip(fn)
        mock_send.assert_called_with(filename_or_fp=tmpzf.name,
                                     mimetype='application/octet-stream',
                                     as_attachment=True,
                                     attachment_filename=fn)

    def test_invalid_importer_identified(self, app):
        """Test error raised when attempting to build with invalid importer."""
        zb = ZipBuilder(app)
        with pytest.raises(ValueError) as excinfo:
            zb.build([], 'test.zip', 'unknown_importer')
        assert excinfo.value.message == 'Unknown importer type'

    def test_correct_images_downloaded_from_flickr(self, app, task, mocker):
        """Test filckr zip file is build with the correct tasks."""
        mocker.patch('pybossa_analyst.zip_builder.zipfile.ZipFile')
        mock_requests = mocker.patch('pybossa_analyst.zip_builder.requests')
        zb = ZipBuilder(app)
        tmpzf = tempfile.NamedTemporaryFile(dir=zb.build_folder)
        zb._build_flickr_zip([task], tmpzf.name)
        mock_requests.get.assert_called_once_with(task.info['url'])

    def test_completed_zip_moved_to_completed_folder(self, app, task, mocker):
        """Test filckr zip file is build with the correct tasks."""
        mocker.patch('pybossa_analyst.zip_builder.zipfile.ZipFile')
        mock_requests = mocker.patch('pybossa_analyst.zip_builder.requests')
        zb = ZipBuilder(app)
        tmpzf = tempfile.NamedTemporaryFile(dir=zb.build_folder)
        fn = os.path.basename(tmpzf.name)
        zb.build([task], fn, 'flickr')
        completed_path = os.path.join(zb.completed_folder, fn)
        assert os.path.isfile(completed_path)

    def test_error_when_flickr_url_not_in_task_info(self, app, task, mocker):
        """Test error raised when url not in task info."""
        task.info.pop("url")
        mock_requests = mocker.patch('pybossa_analyst.zip_builder.requests')
        zb = ZipBuilder(app)
        tmpzf = tempfile.NamedTemporaryFile(dir=zb.build_folder)
        with pytest.raises(ValueError) as excinfo:
            zb._build_flickr_zip([task], tmpzf.name)
        assert excinfo.value.message == 'Invalid Flickr task'

    def test_error_when_title_not_in_task_info(self, app, task, mocker):
        """Test error raised when title not in task info."""
        task.info.pop("title")
        mock_requests = mocker.patch('pybossa_analyst.zip_builder.requests')
        zb = ZipBuilder(app)
        tmpzf = tempfile.NamedTemporaryFile(dir=zb.build_folder)
        with pytest.raises(ValueError) as excinfo:
            zb._build_flickr_zip([task], tmpzf.name)
        assert excinfo.value.message == 'Invalid Flickr task'

    def test_new_zip_file_not_removed(self, app, mocker):
        """Test new zip files are not removed."""
        zb = ZipBuilder(app)
        f = tempfile.NamedTemporaryFile(dir=zb.completed_folder)
        fn = os.path.basename(f.name)
        zb.remove_old_zips()
        assert fn in os.listdir(zb.completed_folder)

    def test_old_zip_file_removed(self, app, mocker):
        """Test old zip files are removed."""
        zb = ZipBuilder(app)
        mock_time = mocker.patch('pybossa_analyst.zip_builder.time')
        mock_time.time.return_value = time.time() + 3600
        f = tempfile.NamedTemporaryFile(dir=zb.completed_folder)
        fn = os.path.basename(f.name)
        zb.remove_old_zips()
        assert fn not in os.listdir(zb.completed_folder)
