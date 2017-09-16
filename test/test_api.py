# -*- coding: utf8 -*-
"""Test the api module for libcrowds-analyst."""

from libcrowds_analyst import api, analysis


class TestApi(object):

    def test_ok_reponse_is_correct(self, app):
        """Test the standard API 200 reponse is correct."""
        with app.test_request_context():
            res = api.ok_response()
        assert res.status_code == 200

    def test_convert_a_card_calls_correct_function(self, test_client, mocker):
        """Test that the correct function is used for analysis."""
        mock_analyse = mocker.patch('libcrowds_analyst.api.analyse')
        mock_analyse.return_value = 'OK'
        test_client.post('/convert-a-card')
        mock_analyse.assert_called_with(analysis.convert_a_card.analyse)

    def test_get_convert_a_card_returns_ok(self, test_client):
        """Test that a 200 response is returned."""
        res = test_client.get('/convert-a-card')
        assert res.status_code == 200

    def test_convert_a_card_analyse_all(self, mocker, test_client, project):
        """Test that analyse all calls the right function."""
        mock_analyse = mocker.patch('libcrowds_analyst.api.analyse_all')
        mock_analyse.return_value = 'OK'
        params = 'project_short_name={}'.format(project.short_name)
        test_client.post('/convert-a-card?{}'.format(params))
        mock_analyse.assert_called_with(analysis.convert_a_card.analyse_all)

    def test_playbills_select_calls_correct_function(self, test_client,
                                                     mocker):
        """Test that the correct function is used for analysis."""
        mock_analyse = mocker.patch('libcrowds_analyst.api.analyse')
        mock_analyse.return_value = 'OK'
        test_client.post('/playbills/select')
        mock_analyse.assert_called_with(analysis.playbills.analyse_selections)

    def test_get_playbills_select_returns_ok(self, test_client):
        """Test that a 200 response is returned."""
        res = test_client.get('/playbills/select')
        assert res.status_code == 200

    def test_playbills_select_analyse_all(self, mocker, test_client, project):
        """Test that analyse all calls the right function."""
        mock_analyse = mocker.patch('libcrowds_analyst.api.analyse_all')
        mock_analyse.return_value = 'OK'
        params = 'project_short_name={}'.format(project.short_name)
        test_client.post('/playbills/select?{}'.format(params))
        func = analysis.playbills.analyse_all_selections
        mock_analyse.assert_called_with(func)

    def test_invalid_webook_request_aborted(self, test_client, mocker):
        """Test that an invalid webhook analyse request returns 400."""
        mock_abort = mocker.patch('libcrowds_analyst.api.abort')
        mocker.patch('libcrowds_analyst.api.Queue.enqueue')
        test_client.post('/convert-a-card', data=dict())
        assert mock_abort.called
        assert mock_abort.call_args[0][0] == 400

    def test_doi_added_to_payload(self, mocker, app):
        """Test that the DOI is added to the payload."""
        mock_request = mocker.patch('libcrowds_analyst.api.request')
        mock_request.args = {'api_key': 'token'}
        mock_request.json = {}
        pl = api.process_payload()
        assert pl['doi'] == app.config['DOI']

    def test_endpoint_added_to_payload(self, mocker, app):
        """Test that the endpoint is added to the payload."""
        mock_request = mocker.patch('libcrowds_analyst.api.request')
        mock_request.args = {'api_key': 'token'}
        mock_request.json = {}
        pl = api.process_payload()
        assert pl['endpoint'] == app.config['ENDPOINT']

    def test_api_key_added_to_payload(self, mocker, app):
        """Test that the API key is added to the payload."""
        mock_request = mocker.patch('libcrowds_analyst.api.request')
        key = 'token'
        mock_request.args = {'api_key': key}
        mock_request.json = {}
        pl = api.process_payload()
        assert pl['api_key'] == key

    def test_path_added_to_payload(self, mocker, app):
        """Test that the analysis path is added to the payload."""
        mock_request = mocker.patch('libcrowds_analyst.api.request')
        mock_request.args = {'api_key': 'token'}
        path = '/example'
        mock_request.path = path
        mock_request.json = {}
        pl = api.process_payload()
        assert pl['path'] == path

    def test_throttle_added_to_payload(self, mocker, app):
        """Test that the number of seconds to throttle is added."""
        mock_request = mocker.patch('libcrowds_analyst.api.request')
        mock_request.args = {'api_key': 'token'}
        throttle = app.config['THROTTLE']
        mock_request.json = {}
        pl = api.process_payload()
        assert pl['throttle'] == throttle

    def test_analyse_all_function_queued(self, mocker, app):
        """Test that the correct function is added to the queue."""
        mock_enqueue = mocker.patch('libcrowds_analyst.api.Queue.enqueue')
        mocker.patch('libcrowds_analyst.api.request')

        def mock_func():
            return True
        api.analyse_all(mock_func)
        assert mock_enqueue.call_args[1]['func'] == mock_func
