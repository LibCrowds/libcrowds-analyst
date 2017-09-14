# -*- coding: utf8 -*-
"""Test Convert-a-Card analysis."""

import json
from libcrowds_analyst.analysis import convert_a_card


class TestConvertACardAnalysis(object):

    def test_correct_result_analysed(self, mocker, project, result,
                                     processed_payload):
        """Test that the correct result is analysed."""
        mock_enki = mocker.patch(
            'libcrowds_analyst.analysis.convert_a_card.enki'
        )
        convert_a_card.analyse(**processed_payload)
        mock_enki.pbclient.find_results.assert_called_with(project.id, limit=1,
                                                           id=result.id, all=1)

    def test_empty_result_updated(self, create_task_run_df, mocker, result,
                                  processed_payload):
        """Test that an empty result is updated correctly."""
        mock_enki = mocker.patch(
            'libcrowds_analyst.analysis.convert_a_card.enki'
        )
        tr_info = [
            {'oclc': '', 'shelfmark': ''},
            {'oclc': '', 'shelfmark': ''}
        ]
        df = create_task_run_df(tr_info)
        mock_enki.pbclient.find_results.return_value = [result]
        mock_enki.Enki().task_runs_df.__getitem__.return_value = df
        convert_a_card.analyse(**processed_payload)

        mock_enki.pbclient.update_result.assert_called_with(result)
        assert result.info == {
            'oclc': '',
            'shelfmark': '',
            'analysis_complete': True,
            'analysis_doi': processed_payload['doi'],
            'analysis_path': processed_payload['path']
        }

    def test_varied_answers_identified(self, create_task_run_df, mocker,
                                       result, processed_payload):
        """Test that a result with varied answers is updated correctly."""
        mock_enki = mocker.patch(
            'libcrowds_analyst.analysis.convert_a_card.enki'
        )
        tr_info = [
            {'oclc': '123', 'shelfmark': '456'},
            {'oclc': '789', 'shelfmark': '101'}
        ]
        df = create_task_run_df(tr_info)
        mock_enki.pbclient.find_results.return_value = [result]
        mock_enki.Enki().task_runs_df.__getitem__.return_value = df
        convert_a_card.analyse(**processed_payload)

        mock_enki.pbclient.update_result.assert_called_with(result)
        assert result.info == {
            'oclc': '',
            'shelfmark': '',
            'analysis_complete': False,
            'analysis_doi': processed_payload['doi'],
            'analysis_path': processed_payload['path']
        }

    def test_matched_result_updated(self, create_task_run_df, mocker, result,
                                    processed_payload):
        """Test that a matched result is updated correctly."""
        mock_enki = mocker.patch(
            'libcrowds_analyst.analysis.convert_a_card.enki'
        )
        tr_info = [
            {'oclc': '123', 'shelfmark': '456'},
            {'oclc': '123', 'shelfmark': '456'}
        ]
        df = create_task_run_df(tr_info)
        mock_enki.pbclient.find_results.return_value = [result]
        mock_enki.Enki().task_runs_df.__getitem__.return_value = df
        convert_a_card.analyse(**processed_payload)

        mock_enki.pbclient.update_result.assert_called_with(result)
        assert result.info == {
            'oclc': '123',
            'shelfmark': '456',
            'analysis_complete': True,
            'analysis_doi': processed_payload['doi'],
            'analysis_path': processed_payload['path']
        }

    def test_all_results_analysed(self, mocker, result, project):
        """Test that analysis of all results is triggered correctly."""
        mock_enki = mocker.patch(
            'libcrowds_analyst.analysis.convert_a_card.enki'
        )
        mock_enki.Enki().project = project
        mock_analyse = mocker.patch(
            'libcrowds_analyst.analysis.convert_a_card.analyse'
        )
        mock_object_loader = mocker.patch(
            'libcrowds_analyst.analysis.convert_a_card.object_loader'
        )
        kwargs = {
          'api_key': 'token',
          'endpoint': 'example.com',
          'doi': '123/456',
          'path': '/example',
          'project_short_name': 'some_project'
        }
        mock_object_loader.load.return_value = [result]
        convert_a_card.analyse_all(**kwargs)
        expected = kwargs.copy()
        expected['result_id'] = result.id
        expected['project_id'] = result.project_id
        mock_analyse.assert_called_with(**expected)

    def test_result_initialised_properly(self, mocker, processed_payload):
        """Test that the result is initialised using the helper function."""
        mocker.patch('libcrowds_analyst.analysis.convert_a_card.enki')
        mock_init_info = mocker.patch("libcrowds_analyst.analysis."
                                      "convert_a_card.helpers."
                                      "init_result_info")
        convert_a_card.analyse(**processed_payload)
        assert mock_init_info.call_args[0][0] == processed_payload['doi']
        assert mock_init_info.call_args[0][1] == processed_payload['path']

    def test_analysis_throttled(self, mocker, processed_payload):
        """Test that the result is initialised using the helper function."""
        mocker.patch('libcrowds_analyst.analysis.convert_a_card.enki')
        mock_sleep = mocker.patch(
            'libcrowds_analyst.analysis.convert_a_card.time.sleep'
        )
        convert_a_card.analyse(**processed_payload)
        mock_sleep.assert_called_with(processed_payload['throttle'])
