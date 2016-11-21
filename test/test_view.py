# -*- coding: utf8 -*-

import json
from pytest_mock import mocker
from libcrowds_analyst import analysis
from libcrowds_analyst.core import zip_builder


class TestView(object):
    """Test view module."""

    def test_result_analysis_queued(self, test_client, payload, mocker):
        """Test result analysis is queued when a payload is recieved."""
        mock_queue = mocker.patch('libcrowds_analyst.view.queue')
        res = test_client.post('/', data=payload, follow_redirects=True,
                               headers={'Content-type': 'application/json'})
        payload_dict = json.loads(payload)
        mock_queue.enqueue_call.assert_called_with(func=analysis.analyse,
                                                   kwargs=payload_dict,
                                                   timeout=600)

    def test_next_unanalysed_result_returned(self, test_client, auth_headers,
                                             mocker, project, result):
        """Test redirect to display next unanalysed result."""
        mock_client = mocker.patch('libcrowds_analyst.view.pybossa_client')
        mock_client.get_results.return_value = [result]
        mock_redirect = mocker.patch('libcrowds_analyst.view.redirect')
        mock_redirect.return_value = "OK"
        url = '/{0}/'.format(project.short_name)
        redirect_url = '/{0}/{1}/'.format(project.short_name, result.id)
        test_client.get(url, headers=auth_headers)
        mock_redirect.assert_called_once_with(redirect_url)

    def test_reanalysis_of_all_tasks_triggered(self, test_client, mocker, task,
                                               project, auth_headers, app):
        """Test that reanalysis of all tasks is triggered correctly."""
        mock_queue = mocker.patch('libcrowds_analyst.view.queue')
        mock_client = mocker.patch('libcrowds_analyst.view.pybossa_client')
        mock_client.get_tasks.return_value = [task]
        mock_client.get_projects.return_value = [project]
        url = '/{0}/reanalyse/'.format(project.short_name)
        test_client.post(url, headers=auth_headers)
        kwargs = {'project_id': project.id,
                  'task_id': task.id,
                  'match_percentage': app.config['MATCH_PERCENTAGE'],
                  'exclude': app.config['EXCLUDED_KEYS']}
        mock_queue.enqueue_call.assert_called_with(func=analysis.analyse,
                                                   kwargs=kwargs,
                                                   timeout=600)

    def test_result_updated_after_analysis(self, test_client, mocker, result,
                                           project, auth_headers):
        """Test that the result is updated correctly following analysis."""
        mock_client = mocker.patch('libcrowds_analyst.view.pybossa_client')
        mock_client.get_projects.return_value = [project]
        mock_client.get_results.return_value = [result]
        url = '/{0}/{1}/'.format(project.short_name, result.id)
        info = {'n': '42'}
        test_client.post(url, headers=auth_headers, data=info)
        mock_client.update_result.assert_called_with(result)
        assert result.info == info

    def test_csrf_token_removed_after_analysis(self, test_client, mocker,
                                               result, project, auth_headers):
        """Test that the CSRF token is not saved to the final result info."""
        mock_client = mocker.patch('libcrowds_analyst.view.pybossa_client')
        mock_client.get_projects.return_value = [project]
        mock_client.get_results.return_value = [result]
        url = '/{0}/{1}/'.format(project.short_name, result.id)
        info = {'csrf_token': 'fake_token'}
        test_client.post(url, headers=auth_headers, data=info)
        mock_client.update_result.assert_called_with(result)
        assert result.info == {}

    def test_correct_data_returned_for_analysis(self, test_client, mocker,
                                                result, project, task,
                                                create_task_run, auth_headers):
        """Test that the correct data is returned for analysis."""
        info = {'n': 42}
        task_run = create_task_run(1, info)
        mock_render = mocker.patch('libcrowds_analyst.view.render_template')
        mock_render.return_value = "OK"
        mock_client = mocker.patch('libcrowds_analyst.view.pybossa_client')
        mock_client.get_projects.return_value = [project]
        mock_client.get_results.return_value = [result]
        mock_client.get_tasks.return_value = [task]
        mock_client.get_task_runs.return_value = [task_run]
        url = '/{0}/{1}/'.format(project.short_name, result.id)
        test_client.get(url, headers=auth_headers)
        short_name = project.short_name
        mock_client.get_projects.assert_called_with(short_name=short_name)
        mock_client.get_results.assert_called_with(project.id, id=result.id)
        mock_client.get_tasks.assert_called_with(project.id, id=result.task_id)
        mock_client.get_task_runs.assert_called_with(project.id,
                                                     task_id=result.task_id)
        mock_render.assert_called_with('analyse.html',
                                       project=project,
                                       result=result,
                                       task=task,
                                       task_runs=[task_run],
                                       title=project.name,
                                       keys=set('n'))

    def test_correct_project_returned_for_zip_preperation(self, test_client,
                                                          mocker, project,
                                                          auth_headers):
        """Test that the correct project is returned for zip preperation."""
        mock_render = mocker.patch('libcrowds_analyst.view.render_template')
        mock_render.return_value = "OK"
        mock_client = mocker.patch('libcrowds_analyst.view.pybossa_client')
        mock_client.get_projects.return_value = [project]
        url = '/{0}/download/'.format(project.short_name)
        test_client.get(url, headers=auth_headers)
        short_name = project.short_name
        mock_client.get_projects.assert_called_with(short_name=short_name)
        assert mock_render.call_args_list[0][1]['project'] == project

    def test_zip_preperation_is_queued(self, test_client, mocker, project,
                                       task, auth_headers):
        """Test that zip preperation is queued using the correct data."""
        mock_queue = mocker.patch('libcrowds_analyst.view.queue')
        mock_render = mocker.patch('libcrowds_analyst.view.render_template')
        mock_render.return_value = "OK"
        mock_client = mocker.patch('libcrowds_analyst.view.pybossa_client')
        mock_client.get_tasks.return_value = [task]
        mock_fn = mocker.patch('libcrowds_analyst.view.secure_filename')
        mock_fn.return_value = "fn.zip"
        url = '/{0}/download/'.format(project.short_name)
        data = {'task_ids': task.id, 'importer': 'flickr'}
        test_client.post(url, headers=auth_headers, data=data)
        fn = '{0}_task_input_1.zip'.format(project.short_name)
        args = ([task], 'fn.zip', data['importer'])
        mock_queue.enqueue_call.assert_called_with(func=zip_builder.build,
                                                   args=args,
                                                   timeout=3600)

    def test_invalid_task_ids_identified(self, test_client, mocker, project,
                                         auth_headers):
        """Test invalid task IDs are identified when preparing a zip file."""
        mock_queue = mocker.patch('libcrowds_analyst.view.queue')
        mock_render = mocker.patch('libcrowds_analyst.view.render_template')
        mock_render.return_value = "OK"
        mock_flash = mocker.patch('libcrowds_analyst.view.flash')
        mock_client = mocker.patch('libcrowds_analyst.view.pybossa_client')
        mock_client.get_tasks.return_value = []
        url = '/{0}/download/'.format(project.short_name)
        data = {'task_ids': '1 2 3', 'importer': 'flickr'}
        test_client.post(url, headers=auth_headers, data=data)
        msg = 'The following task IDs are invalid: 1, 2, 3'
        mock_flash.assert_called_with(msg, 'danger')
        assert not mock_queue.enqueue_call.called

    def test_zip_identified_as_ready(self, test_client, project, mocker,
                                     auth_headers):
        """Test zip identified as ready."""
        mock_zip_builder = mocker.patch('libcrowds_analyst.view.zip_builder')
        mock_zip_builder.check_zip.return_value = True
        url = '/{0}/download/some_filename/check/'.format(project.short_name)
        resp = test_client.get(url, headers=auth_headers)
        resp_json = json.loads(resp.data)
        assert resp_json['download_ready']

    def test_zip_identified_as_not_ready(self, test_client, project, mocker,
                                         auth_headers):
        """Test zip identified as not ready."""
        mock_zip_builder = mocker.patch('libcrowds_analyst.view.zip_builder')
        mock_zip_builder.check_zip.return_value = False
        url = '/{0}/download/some_filename/check/'.format(project.short_name)
        resp = test_client.get(url, headers=auth_headers)
        resp_json = json.loads(resp.data)
        assert not resp_json['download_ready']

    def test_correct_data_returned_for_zip_file_download(self, test_client,
                                                         project, mocker,
                                                         auth_headers):
        """Test that the correct data is returned when downloading zip."""
        mock_render = mocker.patch('libcrowds_analyst.view.render_template')
        mock_render.return_value = "OK"
        mock_client = mocker.patch('libcrowds_analyst.view.pybossa_client')
        mock_client.get_projects.return_value = [project]
        fn = 'some_filename.zip'
        url = '/{0}/download/{1}/'.format(project.short_name, fn)
        test_client.get(url, headers=auth_headers)
        short_name = project.short_name
        mock_client.get_projects.assert_called_with(short_name=short_name)
        assert mock_render.call_args_list[0][1]['project'] == project
        assert mock_render.call_args_list[0][1]['filename'] == fn

    def test_zip_file_response(self, test_client, project, mocker,
                               auth_headers):
        """Test that a zip file response is returned when ready."""
        mock_zip_builder = mocker.patch('libcrowds_analyst.view.zip_builder')
        mock_zip_builder.check_zip.return_value = True
        mock_zip_builder.response_zip.return_value = "OK"
        mock_client = mocker.patch('libcrowds_analyst.view.pybossa_client')
        mock_client.get_projects.return_value = [project]
        fn = 'some_filename.zip'
        url = '/{0}/download/{1}/'.format(project.short_name, fn)
        test_client.post(url, headers=auth_headers)
        mock_zip_builder.response_zip.assert_called_with(fn)
