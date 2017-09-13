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

    def test_playbills_select_calls_correct_function(self, test_client, mocker):
        """Test that the correct function is used for analysis."""
        mock_analyse = mocker.patch('libcrowds_analyst.api.analyse')
        mock_analyse.return_value = 'OK'
        test_client.post('/playbills/select')
        mock_analyse.assert_called_with(analysis.playbills.analyse_selections)

    def test_get_playbills_select_returns_ok(self, test_client):
        """Test that a 200 response is returned."""
        res = test_client.get('/playbills/select')
        assert res.status_code == 200

    def test_invalid_webook_request_aborted(self, test_client, mocker):
        """Test that an invalid webhook analyse request returns 400."""
        mock_abort = mocker.patch('libcrowds_analyst.api.abort')
        mocker.patch('libcrowds_analyst.api.Queue.enqueue_call')
        test_client.post('/convert-a-card', data=dict())
        mock_abort.assert_called_with(400)

    def test_doi_added_to_payload(self, app, test_client, payload, mocker):
        """Test that the DOI is added to the payload."""
        mock_enqueue = mocker.patch('libcrowds_analyst.api.Queue.enqueue_call')
        test_client.post('/convert-a-card', data=payload,
                         content_type='application/json')
        kwargs = mock_enqueue.call_args[1]['kwargs']
        assert kwargs['doi'] == app.config['DOI']

    def test_endpoint_added_to_payload(self, app, test_client, payload, mocker):
        """Test that the endpoint is added to the payload."""
        mock_enqueue = mocker.patch('libcrowds_analyst.api.Queue.enqueue_call')
        test_client.post('/convert-a-card', data=payload,
                         content_type='application/json')
        kwargs = mock_enqueue.call_args[1]['kwargs']
        assert kwargs['endpoint'] == app.config['ENDPOINT']

    def test_url_rule_added_to_payload(self, app, test_client, payload, mocker):
        """Test that the analysis path is added to the payload."""
        mock_enqueue = mocker.patch('libcrowds_analyst.api.Queue.enqueue_call')
        path = '/convert-a-card'
        test_client.post(path, data=payload, content_type='application/json')
        kwargs = mock_enqueue.call_args[1]['kwargs']
        assert kwargs['path'] == path
