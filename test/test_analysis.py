# -*- coding: utf8 -*-

import numpy
from pytest_mock import mocker
from pybossa_analyst import analysis


class TestAnalysis(object):
    """Test analysis module."""

    def test_all_keys_returned(self, create_task_run_df):
        """Test all task run keys are returned when none are excluded."""
        tr_info = [{'n': '42'}, {'comment': 'hello'}]
        excluded = []
        df = create_task_run_df(tr_info)
        df = analysis._drop_excluded_keys(df, excluded)
        assert sorted(df.keys()) == sorted(['n', 'comment'])

    def test_keys_excluded(self, create_task_run_df):
        """Test excluded keys are not returned."""
        tr_info = [{'n': '42'}, {'comment': 'hello'}]
        excluded = ['comment']
        df = create_task_run_df(tr_info)
        df = analysis._drop_excluded_keys(df, excluded)
        assert df.keys() == ['n']

    def test_empty_rows_dropped(self, create_task_run_df):
        """Test empty rows are dropped."""
        tr_info = [{'n': '42'}, {'n': ''}]
        df = create_task_run_df(tr_info)[['n']]
        df = analysis._drop_empty_rows(df)
        assert len(df) == 1 and df['n'][0] == '42'

    def test_partial_rows_are_not_dropped(self, create_task_run_df):
        """Test partial rows are not dropped."""
        tr_info = [{'n': '42', 'comment': ''}]
        df = create_task_run_df(tr_info)
        df = analysis._drop_empty_rows(df)
        assert len(df) == 1 and df['n'][0] == '42'

    def test_match_percent_not_met(self, create_task_run_df):
        """Test that 'Unanalysed' is returned when match percentage not met."""
        tr_info = [{'n': '42'}, {'n': ''}]
        df = create_task_run_df(tr_info)[['n']]
        info = analysis._check_for_n_percent_of_matches(df, 2, 100)
        assert info == "Unanalysed"

    def test_match_percent_not_met_with_nan_cols(self, create_task_run_df):
        """Test that 'Unanalysed' is still returned with NaN columns."""
        tr_info = [{'n': '', 'comment': ''}]
        df = create_task_run_df(tr_info)[['n', 'comment']]
        df = df.replace('', numpy.nan)
        info = analysis._check_for_n_percent_of_matches(df, 2, 100)
        assert info == "Unanalysed"

    def test_match_percent_not_met_with_empty_rows(self, create_task_run_df):
        """Test that 'Unanalysed' is still returned when empty rows dropped."""
        tr_info = [{'n': '42'}]
        df = create_task_run_df(tr_info)[['n']]
        info = analysis._check_for_n_percent_of_matches(df, 2, 100)
        assert info == "Unanalysed"

    def test_answer_set_when_match_percent_met(self, create_task_run_df):
        """Test that answer is set correctly when match percentage not met."""
        tr_info = [{'n': '42'}, {'n': '42'}]
        df = create_task_run_df(tr_info)[['n']]
        info = analysis._check_for_n_percent_of_matches(df, 2, 100)
        assert info == {'n': '42'}

    def test_correct_result_analysed(self, create_task_run_df, mocker,
                                       project, result, task):
        """Test that the correct result is analysed."""
        mock_enki = mocker.patch('pybossa_analyst.analysis.enki')
        kwargs = {
            'api_key': 'api_key',
            'endpoint': 'endpoint',
            'project_short_name': project.short_name,
            'project_id': project.id,
            'result_id': result.id,
            'match_percentage': 100,
            'excluded_keys': []
        }
        analysis.analyse(**kwargs)
        mock_enki.pbclient.find_results.assert_called_with(project.id, limit=1,
                                                           id=result.id, all=1)

    def test_empty_result_updated(self, create_task_run_df, mocker, project,
                                  result, task):
        """Test that an empty result is updated correctly."""
        mock_enki = mocker.patch('pybossa_analyst.analysis.enki')
        tr_info = [{'n': ''}]
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
        analysis.analyse(**kwargs)
        mock_enki.pbclient.update_result.assert_called_with(result)
        assert result.info == {'n': ''}

    def test_unanalysed_result_updated(self, create_task_run_df, mocker,
                                       project, result, task):
        """Test that an 'Unanalysed' result is updated correctly."""
        mock_enki = mocker.patch('pybossa_analyst.analysis.enki')
        tr_info = [{'n': '42'}, {'n': ''}]
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
        analysis.analyse(**kwargs)
        mock_enki.pbclient.update_result.assert_called_with(result)
        assert result.info == 'Unanalysed'

    def test_matched_result_updated(self, create_task_run_df, mocker,
                                    project, result, task):
        """Test that a matched result is updated correctly."""
        mock_enki = mocker.patch('pybossa_analyst.analysis.enki')
        tr_info = [{'n': '42'}, {'n': '42'}]
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
        analysis.analyse(**kwargs)
        mock_enki.pbclient.update_result.assert_called_with(result)
        assert result.info == {'n': '42'}

    def test_new_results_filtered(self, result):
        """Test new results filtered correctly."""
        result.info = None
        filtered = analysis._filter_results([result], "New")
        assert filtered == [result]
