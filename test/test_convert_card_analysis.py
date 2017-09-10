# -*- coding: utf8 -*-
"""Test Convert-a-Card analysis."""

from libcrowds_analyst.analysis import convert_a_card


class TestConvertACardAnalysis(object):

    def test_correct_result_analysed(self, mocker, project, result):
        """Test that the correct result is analysed."""
        mock_enki = mocker.patch(
            'libcrowds_analyst.analysis.convert_a_card.enki'
        )
        kwargs = {
            'api_key': 'api_key',
            'endpoint': 'endpoint',
            'project_short_name': project.short_name,
            'project_id': project.id,
            'result_id': result.id,
            'match_percentage': 100,
            'excluded_keys': []
        }
        convert_a_card.analyse(**kwargs)
        mock_enki.pbclient.find_results.assert_called_with(project.id, limit=1,
                                                           id=result.id, all=1)

    def test_empty_result_updated(self, create_task_run_df, mocker, project,
                                  result):
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
        kwargs = {
            'api_key': 'api_key',
            'endpoint': 'endpoint',
            'project_short_name': project.short_name,
            'project_id': project.id,
            'result_id': result.id,
            'match_percentage': 100,
            'excluded_keys': []
        }
        convert_a_card.analyse(**kwargs)
        mock_enki.pbclient.update_result.assert_called_with(result)
        assert result.info == {
            'oclc': '',
            'shelfmark': '',
            'analysis_complete': True
        }

    def test_varied_answers_identified(self, create_task_run_df, mocker,
                                       project, result, task):
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
        kwargs = {
            'api_key': 'api_key',
            'endpoint': 'endpoint',
            'project_short_name': project.short_name,
            'project_id': project.id,
            'result_id': result.id,
            'match_percentage': 100,
            'excluded_keys': []
        }
        convert_a_card.analyse(**kwargs)
        mock_enki.pbclient.update_result.assert_called_with(result)
        assert result.info == {
            'oclc': '',
            'shelfmark': '',
            'analysis_complete': False
        }


    def test_matched_result_updated(self, create_task_run_df, mocker,
                                    project, result, task):
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
        kwargs = {
            'api_key': 'api_key',
            'endpoint': 'endpoint',
            'project_short_name': project.short_name,
            'project_id': project.id,
            'result_id': result.id,
            'match_percentage': 100,
            'excluded_keys': []
        }
        convert_a_card.analyse(**kwargs)
        mock_enki.pbclient.update_result.assert_called_with(result)
        assert result.info == {
            'oclc': '123',
            'shelfmark': '456',
            'analysis_complete': True
        }
