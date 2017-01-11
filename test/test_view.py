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

    def test_list_of_projects_returned(self, test_client, login, mocker,
                                       project, result):
        """Test the main projects page is rendered with a list of projects."""
        mock_rd = mocker.patch('pybossa_analyst.view.projects.render_template')
        mock_rd.return_value = "OK"
        mock_ld = mocker.patch('pybossa_analyst.view.projects.object_loader')
        mock_ld.load.return_value = [project]
        resp = test_client.get('/projects/')
        mock_rd.assert_called_with('index.html', projects=[project])

    def test_next_unverified_result_returned(self, test_client, login,
                                             mocker, project, result):
        """Test redirect to display next unanalysed result."""
        mock_redirect = mocker.patch('pybossa_analyst.view.projects.redirect')
        mock_redirect.return_value = "OK"
        mock_pbclient = mocker.patch('pybossa_analyst.view.projects.pbclient')
        mock_pbclient.find_results.return_value = [result]
        url = "/projects/{}".format(project.short_name)
        test_client.get(url)
        expected = '/projects/{0}/{1}'.format(project.short_name, result.id)
        mock_redirect.assert_called_with(expected)

    def test_excluded_keys_not_returned(self, test_client, login, mocker,
                                        project, result, create_task_run, app):
        """Test excluded keys are not returned for analysis."""
        mock_auth = mocker.patch('pybossa_analyst.view.projects.auth')
        mock_rd = mocker.patch('pybossa_analyst.view.projects.render_template')
        mock_rd.return_value = "OK"
        mock_pbclient = mocker.patch('pybossa_analyst.view.projects.pbclient')
        tr_info = {"foo": "bar", "n": "42"}
        task_run = create_task_run(1, tr_info)
        app.config['EXCLUDED_KEYS'] = ["foo"]
        mock_pbclient.find_taskruns.return_value = [task_run]
        url = '/projects/{0}/{1}'.format(project.short_name, result.id)
        test_client.get(url)
        assert mock_rd.call_args[1]['keys'] == {'n'}

    def test_reanalysis(self, test_client, login, mocker, result, project,
                        app):
        """Test that result reanalysis is triggered correctly."""
        mock_auth = mocker.patch('pybossa_analyst.view.projects.auth')
        mock_pbclient = mocker.patch('pybossa_analyst.view.projects.pbclient')
        mock_pbclient.find_project.return_value = [project]
        mock_queue = mocker.patch('pybossa_analyst.view.projects.queue')
        url = "/projects/{}/setup".format(project.short_name)
        info_filter = "All"
        data = {"info_filter": info_filter}
        test_client.post(url, data=data)
        func = analysis.analyse_multiple
        kwargs = {
            'api_key': app.config['API_KEY'],
            'endpoint': app.config['ENDPOINT'],
            'project_id': project.id,
            'project_short_name': project.short_name,
            'info_filter': info_filter,
            'match_percentage': app.config['MATCH_PERCENTAGE'],
            'excluded_keys': app.config['EXCLUDED_KEYS']
        }
        mock_queue.enqueue_call.assert_called_with(func=func,
                                                   kwargs=kwargs,
                                                   timeout=600)

    def test_verified_result_updated(self, test_client, login, mocker, result,
                                     project):
        """Test that the result is updated correctly following verification."""
        mock_auth = mocker.patch('pybossa_analyst.view.projects.auth')
        mock_pbclient = mocker.patch('pybossa_analyst.view.projects.pbclient')
        mock_pbclient.find_results.return_value = [result]
        url = "/projects/{0}/{1}".format(project.short_name, result.id)
        data = {"foo": "bar"}
        test_client.post(url, data=data)
        assert result.info == data
        mock_pbclient.update_result.assert_called_with(result)

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

    def test_zip_headers(self, test_client, login, mocker, task, project):
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

    def test_zip_generated(self, test_client, login, project, mocker, task):
        """Test that a zip file is generated on download."""
        mock_pbclient = mocker.patch('pybossa_analyst.view.download.pbclient')
        mock_pbclient.find_tasks.return_value = [task]
        mock_zb = mocker.patch('pybossa_analyst.view.download.zip_builder')
        url = '/download/{0}'.format(project.short_name)
        importer = 'flickr'
        data = {'importer': importer, 'task_ids': task.id}
        resp = test_client.post(url, data=data)
        mock_zb.generate.assert_called_with([task], importer)
