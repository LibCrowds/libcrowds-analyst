# -*- coding: utf8 -*-
"""Test analysis helpers."""

import numpy
from libcrowds_analyst.analysis import helpers


class TestAnalysisHelpers(object):

    def test_all_keys_returned(self, create_task_run_df):
        """Test all task run keys are returned when none are dropped."""
        tr_info = [
            {'n': '42'},
            {'comment': 'hello'}
        ]
        excluded = []
        df = create_task_run_df(tr_info)
        df = helpers.drop_keys(df, excluded)
        assert sorted(df.keys()) == ['comment', 'n']

    def test_keys_excluded(self, create_task_run_df):
        """Test excluded keys are not returned."""
        tr_info = [
            {'n': '42'},
            {'comment': 'hello'}
        ]
        excluded = ['comment']
        df = create_task_run_df(tr_info)
        df = helpers.drop_keys(df, excluded)
        assert df.keys() == ['n']

    def test_empty_rows_dropped(self, create_task_run_df):
        """Test empty rows are dropped."""
        tr_info = [
            {'n': '42'},
            {'n': ''}
        ]
        df = create_task_run_df(tr_info)[['n']]
        df = helpers.drop_empty_rows(df)
        assert len(df) == 1 and df['n'][0] == '42'

    def test_partial_rows_not_dropped(self, create_task_run_df):
        """Test partial rows are not dropped."""
        tr_info = [
            {'n': '42', 'comment': ''}
        ]
        df = create_task_run_df(tr_info)
        df = helpers.drop_empty_rows(df)
        assert tr_info == df['info'].tolist()

    def test_match_fails_when_percentage_not_met(self, create_task_run_df):
        """Test False is returned when match percentage not met."""
        tr_info = [
            {'n': '42'},
            {'n': ''}
        ]
        df = create_task_run_df(tr_info)[['n']]
        has_matches = helpers.has_n_matches(df, 2, 100)
        assert not has_matches

    def test_match_fails_when_nan_cols(self, create_task_run_df):
        """Test False is returned when NaN columns."""
        tr_info = [
            {'n': '', 'comment': ''}
        ]
        df = create_task_run_df(tr_info)[['n', 'comment']]
        df = df.replace('', numpy.nan)
        has_matches = helpers.has_n_matches(df, 2, 100)
        assert not has_matches

    def test_match_succeeds_when_percentage_met(self, create_task_run_df):
        """Test True returned when match percentage met."""
        tr_info = [
            {'n': '42'},
            {'n': '42'}
        ]
        df = create_task_run_df(tr_info)[['n']]
        has_matches = helpers.has_n_matches(df, 2, 100)
        assert has_matches

    def test_doi_added_to_result_info(self):
        doi = '10.5281/zenodo.888152'
        info = helpers.init_result_info(doi)
        assert info['doi'] == doi

    def test_analysis_complete_true_added_to_result_info(self):
        info = helpers.init_result_info(None)
        assert info['analysis_complete']

    def test_defaults_added_to_result_info(self):
        defaults = {'some_key': 'some_value'}
        info = helpers.init_result_info(None, defaults)
        assert info['some_key'] == 'some_value'
