# -*- coding: utf8 -*-

import json
from flask import session
from pytest_mock import mocker
from pybossa_analyst import analysis


class TestView(object):
    """Test view module."""

    def test_webhook_processed(self, test_client, payload, mocker, app):
        """Test result analysis is queued when a webhook is recieved."""
        mock_queue = mocker.patch('pybossa_analyst.view.home.queue')
        res = test_client.post('/', data=payload,
                               headers={'Content-type': 'application/json'})
        payload_dict = json.loads(payload)
        payload_dict['api_key'] = app.config['API_KEY']
        payload_dict['endpoint'] = app.config['ENDPOINT']
        payload_dict['match_percentage'] = app.config['MATCH_PERCENTAGE']
        payload_dict['excluded_keys'] = app.config['EXCLUDED_KEYS']
        mock_queue.enqueue_call.assert_called_with(func=analysis.analyse,
                                                   kwargs=payload_dict,
                                                   timeout=600)

    def test_login(self, test_client):
        """Test login successful."""
        fake_key = '123'
        data = {'api_key': fake_key}
        with test_client as c:
            c.post('/login', data=data)
            assert session['api_key'] == fake_key

    def test_logout(self, test_client, login):
        """Test logout successful."""
        test_client.get('/logout')
        assert not session.get('api_key')

    def test_next_unanalysed_result_returned(self, test_client,
                                             mocker, project, result):
        """Test redirect to display next unanalysed result."""
        pass

    def test_reanalysis_of_all_tasks(self, test_client, mocker, result,
                                     project, app):
        """Test that reanalysis of all tasks is triggered correctly."""
        pass

    def test_reanalysis_of_new_tasks(self, test_client, mocker, result,
                                     project, app):
        """Test that reanalysis of new tasks is triggered correctly."""
        pass

    def test_reanalysis_of_unanalysed_tasks(self, test_client, mocker, result,
                                            project, app):
        """Test that reanalysis of Unanalysed tasks is triggered correctly."""
        pass

    def test_reanalysis_of_no_tasks(self, test_client, mocker, task, result,
                                    project, app):
        """Test reanalysis of tasks filter works when no tasks selected."""
        pass

    def test_result_updated_after_analysis(self, test_client, mocker, result,
                                           project):
        """Test that the result is updated correctly following analysis."""
        pass

    def test_csrf_token_removed_after_analysis(self, test_client, mocker,
                                               result, project):
        """Test that the CSRF token is not saved to the final result info."""
        pass

    def test_correct_data_returned_for_analysis(self, test_client, mocker,
                                                result, project, task,
                                                create_task_run):
        """Test that the correct data is returned for analysis."""
        pass

    def test_invalid_task_ids_identified(self, test_client, login, mocker,
                                         project, task):
        """Test invalid task IDs are identified when preparing a zip file."""
        mock_flash = mocker.patch('pybossa_analyst.view.download.flash')
        mock_flash.return_value = True
        mock_pbclient = mocker.patch('pybossa_analyst.view.download.pbclient')
        mock_pbclient.find_tasks.return_value = [task]
        url = '/download/{0}'.format(project.short_name)
        bad_task_id = "some_bad_id"
        data = {'importer': 'flickr', 'task_ids': bad_task_id}
        resp = test_client.post(url, data=data)
        err_msg = 'Invalid task IDs: {0}'.format(bad_task_id)
        mock_flash.assert_called_with(err_msg, 'danger')

    def test_zip_file_response_headers(self, test_client, login, mocker, task,
                                       project):
        """Test the correct headers are returned with a zip file response."""
        mock_pbclient = mocker.patch('pybossa_analyst.view.download.pbclient')
        mock_pbclient.find_tasks.return_value = [task]
        mock_fn = mocker.patch('pybossa_analyst.view.download.secure_filename')
        fake_fn = "fake_filename"
        mock_fn.return_value = fake_fn
        url = '/download/{0}'.format(project.short_name)
        data = {'importer': 'flickr', 'task_ids': task.id}
        resp = test_client.post(url, data=data)
        content_disposition = "attachment; filename={}".format(fake_fn)
        assert resp.headers['Content-Type'] == "application/zip"
        assert resp.headers['Content-Disposition'] == content_disposition

    def test_zip_file_generated(self, test_client, login, project, mocker, task):
        """Test that a zip file is generated on download."""
        mock_pbclient = mocker.patch('pybossa_analyst.view.download.pbclient')
        mock_pbclient.find_tasks.return_value = [task]
        mock_zb = mocker.patch('pybossa_analyst.view.download.zip_builder')
        url = '/download/{0}'.format(project.short_name)
        importer = 'flickr'
        data = {'importer': importer, 'task_ids': task.id}
        resp = test_client.post(url, data=data)
        mock_zb.generate.assert_called_with([task], importer)
