# -*- coding: utf8 -*-

from pytest_mock import mocker
from pybossa_analyst import analysis


class TestAnalysis(object):
    """Test analysis module."""

    def setup(self):
        super(TestAnalysis, self)

    def test_get_task_run_keys(self, create_task_run_df):
        """Test all task run keys are returned."""
        tr_info = [{'n': 42}, {'comment': 'hello'}]
        df = create_task_run_df(tr_info)
        keys = analysis._extract_keys(df)
        assert sorted(keys) == sorted(['n', 'comment'])

    def test_empty_rows_dropped(self, create_task_run_df):
        """Test empty rows are dropped."""
        tr_info = [{'n': 42, 'comment': ''}, {'n': '', 'comment': ''}]
        df = create_task_run_df(tr_info)[['n', 'comment']]
        df = analysis._drop_empty_rows(df)
        assert len(df) == 1
        assert df['n'][0] == 42

    def test_result_when_no_answers(self, create_task_run_df, mocker, project,
                                    task, result):
        """Test result info correct when no answers."""
        tr_info = [{'n': '', 'comment': ''}]
        df = create_task_run_df(tr_info)
        mock_client = mocker.patch('pybossa_analyst.analysis.pybossa_client')
        mock_client.get_task_run_dataframe.return_value = df
        mock_client.get_results.return_value = [result]
        analysis.analyse(project.id, task.id, 60, sleep=0)
        mock_client.update_result.assert_called_with(result)
        assert result.info == {'n': '', 'comment': ''}

    def test_result_when_matching_answers(self, create_task_run_df, mocker,
                                          project, task, result):
        """Test result info correct when match percentage met."""
        tr_info = [{'n': 42, 'comment': 'ok'}, {'n': 42, 'comment': ''},
                   {'n': 2, 'comment': 'ok'}, {'n': 1, 'comment': 'ok'},
                   {'n': 42, 'comment': ''}]
        df = create_task_run_df(tr_info)
        mock_client = mocker.patch('pybossa_analyst.analysis.pybossa_client')
        mock_client.get_task_run_dataframe.return_value = df
        mock_client.get_results.return_value = [result]
        analysis.analyse(project.id, task.id, 60, sleep=0)
        mock_client.update_result.assert_called_with(result)
        assert result.info == {'n': 42, 'comment': 'ok'}

    def test_result_when_non_matching_answers(self, create_task_run_df, mocker,
                                              project, task, result):
        """Test result info correct when match percentage not met."""
        tr_info = [{'n': 42, 'comment': 'ok'}, {'n': 42, 'comment': 'ok'},
                   {'n': 1, 'comment': '1'}, {'n': 2, 'comment': '2'},
                   {'n': 3, 'comment': '3'}]
        df = create_task_run_df(tr_info)
        mock_client = mocker.patch('pybossa_analyst.analysis.pybossa_client')
        mock_client.get_task_run_dataframe.return_value = df
        mock_client.get_results.return_value = [result]
        analysis.analyse(project.id, task.id, 60, sleep=0)
        mock_client.update_result.assert_called_with(result)
        assert result.info == 'Unanalysed'

    def test_result_when_some_matching_answers(self, create_task_run_df,
                                               mocker, project, task, result):
        """Test result info correct when match percentage partially met."""
        tr_info = [{'n': 1, 'comment': 'ok'}, {'n': 2, 'comment': 'ok'},
                   {'n': 3, 'comment': 'ok'}, {'n': 4, 'comment': 'ok'},
                   {'n': 5, 'comment': ''}]
        df = create_task_run_df(tr_info)
        mock_client = mocker.patch('pybossa_analyst.analysis.pybossa_client')
        mock_client.get_task_run_dataframe.return_value = df
        mock_client.get_results.return_value = [result]
        analysis.analyse(project.id, task.id, 60, sleep=0)
        mock_client.update_result.assert_called_with(result)
        assert result.info == 'Unanalysed'

    def test_keys_excluded(self, create_task_run_df, mocker, project, task,
                           result):
        """Test that the specified keys are excluded from analysis."""
        tr_info = [{'n': 42, 'comment': 'ok'}, {'n': 42, 'comment': 'ok'}]
        df = create_task_run_df(tr_info)
        mock_client = mocker.patch('pybossa_analyst.analysis.pybossa_client')
        mock_client.get_task_run_dataframe.return_value = df
        mock_client.get_results.return_value = [result]
        analysis.analyse(project.id, task.id, 60, exclude=['comment'], sleep=0)
        mock_client.update_result.assert_called_with(result)
        assert result.info == {'n': 42}
