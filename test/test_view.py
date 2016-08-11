# -*- coding: utf8 -*-

import enki
import json
from mock import MagicMock
from pytest_mock import mocker
from libcrowds_analyst import view


class TestView(object):

    def test_basic_auth_not_required_for_index(self, test_client, payload):
        get_res = test_client.get('/')
        assert get_res.status_code == 200

    def test_basic_auth_required(self, test_client):
        res = test_client.get('/short_name')
        assert res.status_code == 401

    def test_auth_credentials_accepted(self, test_client, auth_headers):
        res = test_client.get("/", headers=auth_headers)
        assert res.status_code == 200

    def test_webhook_triggers_analysis(self, test_client, payload, mocker):
        mock_enki = mocker.patch('libcrowds_analyst.view.enki')
        mock_queue = mocker.patch('libcrowds_analyst.view.queue')
        analysis = mocker.patch('libcrowds_analyst.view.analysis')
        analyser_func = (lambda x: x + 1)
        analysis.get_analyst_func.return_value = analyser_func
        test_client.post('/', data=payload, follow_redirects=True,
                         headers={'Content-type': 'application/json'})
        mock_queue.enqueue.assert_called_once_with(analyser_func, 'yourkey',
                                                   'http://localhost:5001',
                                                   'short_name', 100,
                                                   timeout=600)

    def test_webhook_404_when_no_analyser(self, test_client, payload, mocker):
        mock_enki = mocker.patch('libcrowds_analyst.view.enki')
        res = test_client.post('/', data=payload, follow_redirects=True,
                               headers={'Content-type': 'application/json'})
        assert res.status_code == 404

    def test_unanalysed_result_get(self, test_client, auth_headers, mocker,
                                   result):
        mock_enki = mocker.patch('libcrowds_analyst.view.enki')
        mock_pbclient = mocker.patch('libcrowds_analyst.view.enki.pbclient')
        mock_pbclient.find_results.return_value = [result]
        mock_render = mocker.patch('libcrowds_analyst.view.render_template')
        mock_render.return_value = "OK"
        test_client.get('/short_name/1/', headers=auth_headers)
        assert mock_render.call_args_list[0][1]['result'] == result

    def test_unanalysed_result_post(self, test_client, auth_headers, mocker,
                                    result):
        mock_enki = mocker.patch('libcrowds_analyst.view.enki')
        mock_pbclient = mocker.patch('libcrowds_analyst.view.enki.pbclient')
        mock_pbclient.find_results.return_value = [result]
        mock_pbclient.update_result.return_value = True
        mock_render = mocker.patch('libcrowds_analyst.view.render_template')
        mock_render.return_value = "OK"
        res = test_client.post('/short_name/1/', headers=auth_headers)
        mock_pbclient.update_result.assert_called_once_with(result)

    def test_next_unanalysed_result(self, test_client, auth_headers, mocker,
                                    result):
        mock_enki = mocker.patch('libcrowds_analyst.view.enki')
        mock_pbclient = mocker.patch('libcrowds_analyst.view.enki.pbclient')
        mock_pbclient.find_results.return_value = [result]
        mock_pbclient.update_result.return_value = True
        mock_redirect = mocker.patch('libcrowds_analyst.view.redirect')
        mock_redirect.return_value = "OK"
        res = test_client.post('/short_name/', headers=auth_headers)
        mock_redirect.assert_called_once_with('/short_name/1/')

    def test_edit_result_get(self, test_client, auth_headers, mocker, result):
        mock_enki = mocker.patch('libcrowds_analyst.view.enki')
        mock_pbclient = mocker.patch('libcrowds_analyst.view.enki.pbclient')
        mock_pbclient.find_results.return_value = [result]
        mock_render = mocker.patch('libcrowds_analyst.view.render_template')
        mock_render.return_value = "OK"
        test_client.get('/short_name/1/edit/', headers=auth_headers)
        form = mock_render.call_args_list[0][1]['form']
        assert form.info.data == json.dumps({"n": 1})

    def test_edit_result_post(self, test_client, auth_headers, mocker, result):
        mock_enki = mocker.patch('libcrowds_analyst.view.enki')
        mock_pbclient = mocker.patch('libcrowds_analyst.view.enki.pbclient')
        mock_pbclient.find_results.return_value = [result]
        mock_pbclient.update_result.return_value = True
        mock_render = mocker.patch('libcrowds_analyst.view.render_template')
        mock_render.return_value = "OK"
        form_data = {"info": json.dumps(result.info)}
        test_client.post('/short_name/1/edit/', data=form_data,
                         headers=auth_headers)
        mock_pbclient.update_result.assert_called_once_with(result)

    def test_reanalyse_get(self, test_client, auth_headers, mocker, result):
        mock_enki = mocker.patch('libcrowds_analyst.view.enki')
        mock_project = MagicMock()
        mock_enki.Enki.return_value.project = mock_project
        mock_render = mocker.patch('libcrowds_analyst.view.render_template')
        mock_render.return_value = "OK"
        test_client.get('/short_name/reanalyse/', headers=auth_headers)
        project = mock_render.call_args_list[0][1]['project']
        assert project == mock_project

    def test_reanalyse_post(self, test_client, auth_headers, mocker, task):
        mock_queue = mocker.patch('libcrowds_analyst.view.queue')
        mock_enki = mocker.patch('libcrowds_analyst.view.enki')
        mock_enki.Enki().tasks = [task]
        analysis = mocker.patch('libcrowds_analyst.view.analysis')
        analyser_func = (lambda x: x + 1)
        analysis.get_analyst_func.return_value = analyser_func
        test_client.post('/short_name/reanalyse/', headers=auth_headers,
                         data={'sleep': 1})
        mock_queue.enqueue.assert_called_once_with(analyser_func, 'yourkey',
                                                   'http://localhost:5001',
                                                   'short_name', 100, sleep=1,
                                                   timeout=3600)
