# -*- coding: utf8 -*-

import json
from mock import MagicMock, patch
from pytest_mock import mocker
from libcrowds_analyst import view, analysis


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

    def test_result_updated_following_analysis(self):
        pass

    def test_correct_data_returned_for_analysis(self):
        pass

    def test_zip_preperation_is_queued(self):
        pass

    def test_zip_ready_check_is_correct(self):
        pass

    def test_zip_file_downloaded(self):
        pass
