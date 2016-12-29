# -*- coding: utf8 -*-

import json
from pytest_mock import mocker
from pybossa_analyst import analysis


class TestView(object):
    """Test view module."""

    def test_result_analysis_queued(self, test_client, payload, mocker):
        """Test result analysis is queued when a payload is recieved."""
        mock_queue = mocker.patch('pybossa_analyst.view.queue')
        res = test_client.post('/', data=payload, follow_redirects=True,
                               headers={'Content-type': 'application/json'})
        payload_dict = json.loads(payload)
        mock_queue.enqueue_call.assert_called_with(func=analysis.analyse,
                                                   kwargs=payload_dict,
                                                   timeout=600)

    def test_next_unanalysed_result_returned(self, test_client, auth_headers,
                                             mocker, project, result):
        """Test redirect to display next unanalysed result."""
        mock_client = mocker.patch('pybossa_analyst.view.pybossa_client')
        mock_client.get_results.return_value = [result]
        mock_redirect = mocker.patch('pybossa_analyst.view.redirect')
        mock_redirect.return_value = "OK"
        url = '/{0}/'.format(project.short_name)
        redirect_url = '/{0}/{1}/'.format(project.short_name, result.id)
        test_client.get(url, headers=auth_headers)
        mock_redirect.assert_called_once_with(redirect_url)

    def test_reanalysis_of_all_tasks(self, test_client, mocker, task, project,
                                     auth_headers, app):
        """Test that reanalysis of all tasks is triggered correctly."""
        mock_queue = mocker.patch('pybossa_analyst.view.queue')
        mock_client = mocker.patch('pybossa_analyst.view.pybossa_client')
        mock_client.get_tasks.return_value = [task]
        mock_client.get_projects.return_value = [project]
        url = '/{0}/reanalyse/'.format(project.short_name)
        data = {'result_filter': 'all'}
        test_client.post(url, headers=auth_headers, data=data)
        kwargs = {'project_id': project.id,
                  'task_id': task.id,
                  'match_percentage': app.config['MATCH_PERCENTAGE'],
                  'exclude': app.config['EXCLUDED_KEYS']}
        mock_queue.enqueue_call.assert_called_with(func=analysis.analyse,
                                                   kwargs=kwargs,
                                                   timeout=600)

    def test_reanalysis_of_new_tasks(self, test_client, mocker, task,
                                     project, auth_headers, app):
        """Test that reanalysis of new tasks is triggered correctly."""
        mock_queue = mocker.patch('pybossa_analyst.view.queue')
        mock_client = mocker.patch('pybossa_analyst.view.pybossa_client')
        task.info = None
        mock_client.get_tasks.return_value = [task]
        mock_client.get_projects.return_value = [project]
        url = '/{0}/reanalyse/'.format(project.short_name)
        data = {'result_filter': 'None'}
        test_client.post(url, headers=auth_headers, data=data)
        kwargs = {'project_id': project.id,
                  'task_id': task.id,
                  'match_percentage': app.config['MATCH_PERCENTAGE'],
                  'exclude': app.config['EXCLUDED_KEYS']}
        mock_queue.enqueue_call.assert_called_with(func=analysis.analyse,
                                                   kwargs=kwargs,
                                                   timeout=600)

    def test_reanalysis_of_unanalysed_tasks(self, test_client, mocker, task,
                                            project, auth_headers, app):
        """Test that reanalysis of Unanalysed tasks is triggered correctly."""
        mock_queue = mocker.patch('pybossa_analyst.view.queue')
        mock_client = mocker.patch('pybossa_analyst.view.pybossa_client')
        task.info = 'Unanalysed'
        mock_client.get_tasks.return_value = [task]
        mock_client.get_projects.return_value = [project]
        url = '/{0}/reanalyse/'.format(project.short_name)
        data = {'result_filter': 'Unanalysed'}
        test_client.post(url, headers=auth_headers, data=data)
        kwargs = {'project_id': project.id,
                  'task_id': task.id,
                  'match_percentage': app.config['MATCH_PERCENTAGE'],
                  'exclude': app.config['EXCLUDED_KEYS']}
        mock_queue.enqueue_call.assert_called_with(func=analysis.analyse,
                                                   kwargs=kwargs,
                                                   timeout=600)

    def test_reanalysis_of_no_tasks(self, test_client, mocker, task,
                                    project, auth_headers, app):
        """Test reanalysis of tasks filter works when no tasks selected."""
        mock_queue = mocker.patch('pybossa_analyst.view.queue')
        mock_client = mocker.patch('pybossa_analyst.view.pybossa_client')
        mock_client.get_tasks.return_value = [task]
        mock_client.get_projects.return_value = [project]
        url = '/{0}/reanalyse/'.format(project.short_name)
        data = {'result_filter': None}
        test_client.post(url, headers=auth_headers, data=data)
        mock_queue.enqueue_call.assert_not_called()

    def test_result_updated_after_analysis(self, test_client, mocker, result,
                                           project, auth_headers):
        """Test that the result is updated correctly following analysis."""
        mock_client = mocker.patch('pybossa_analyst.view.pybossa_client')
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
        mock_client = mocker.patch('pybossa_analyst.view.pybossa_client')
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
        mock_render = mocker.patch('pybossa_analyst.view.render_template')
        mock_render.return_value = "OK"
        mock_client = mocker.patch('pybossa_analyst.view.pybossa_client')
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
        mock_render = mocker.patch('pybossa_analyst.view.render_template')
        mock_render.return_value = "OK"
        mock_client = mocker.patch('pybossa_analyst.view.pybossa_client')
        mock_client.get_projects.return_value = [project]
        url = '/{0}/download/'.format(project.short_name)
        test_client.get(url, headers=auth_headers)
        short_name = project.short_name
        mock_client.get_projects.assert_called_with(short_name=short_name)
        assert mock_render.call_args_list[0][1]['project'] == project

    def test_invalid_task_ids_identified(self, test_client, mocker, project,
                                         auth_headers):
        """Test invalid task IDs are identified when preparing a zip file."""
        mock_queue = mocker.patch('pybossa_analyst.view.queue')
        mock_render = mocker.patch('pybossa_analyst.view.render_template')
        mock_render.return_value = "OK"
        mock_flash = mocker.patch('pybossa_analyst.view.flash')
        mock_client = mocker.patch('pybossa_analyst.view.pybossa_client')
        mock_client.get_tasks.return_value = []
        url = '/{0}/download/'.format(project.short_name)
        data = {'task_ids': '1 2 3', 'importer': 'flickr'}
        test_client.post(url, headers=auth_headers, data=data)
        msg = 'The following task IDs are invalid: 1, 2, 3'
        mock_flash.assert_called_with(msg, 'danger')
        assert not mock_queue.enqueue_call.called

    def test_zip_file_response(self, test_client, project, mocker, task,
                               auth_headers):
        """Test that a zip file generator is returned."""
        mock_client = mocker.patch('pybossa_analyst.view.pybossa_client')
        mock_client.get_projects.return_value = [project]
        mock_client.get_tasks.return_value = [task]
        url = '/{0}/download/'.format(project.short_name)
        data = {'task_ids': '1', 'importer': 'flickr'}
        resp = test_client.post(url, headers=auth_headers, data=data)
        assert resp.headers['Content-Type'] == 'application/zip'
