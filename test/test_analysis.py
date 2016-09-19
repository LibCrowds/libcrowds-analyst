# -*- coding: utf8 -*-

import enki
from mock import MagicMock, PropertyMock
from pytest_mock import mocker
from libcrowds_analyst import analysis


class TestAnalysis(object):

    def create_tr_dataframe(self, data, task_id):
        task_runs = []
        for i in range(len(data)):
            tr = {'id': i, 'info': data[i]}
            task_runs.append(enki.pbclient.DomainObject(tr))
        return {task_id: enki.dataframer.create_data_frame(task_runs)}

    def test_get_valid_analyst_func(self):
        valid_func = analysis.get_analyst_func(1)
        assert valid_func == analysis.category_1

    def test_get_invalid_analyst_func(self):
        invalid_func = analysis.get_analyst_func(0)
        assert invalid_func is None


class TestCategoryOneAnalysis(TestAnalysis):

    def setup(self):
        super(TestCategoryOneAnalysis, self)
        self.tr_data = {'oclc': '123', 'shelfmark': '456', 'comments': 'hello'}
        self.empty_tr_data = {'oclc': '', 'shelfmark': '', 'comments': 'hello'}

    def analyse(self, data, mock_enki, analysis_kwargs, task):
        mock_info = PropertyMock()
        mock_result = MagicMock()
        type(mock_result).info = mock_info
        mock_enki.pbclient.find_results.return_value = [mock_result]
        mock_enki.Enki().tasks = [task]
        mock_enki.Enki().task_runs_df = self.create_tr_dataframe(data, task.id)
        analysis.category_1(**analysis_kwargs)
        return mock_result, mock_info

    def test_cat_1_analysis_no_answers(self, mocker, analysis_kwargs, task):
        mock_enki = mocker.patch('libcrowds_analyst.analysis.enki')
        mock_client = mocker.patch('libcrowds_analyst.analysis.api_client')
        data = [self.empty_tr_data for i in range(3)]
        (mock_result, mock_info) = self.analyse(data, mock_enki,
                                                analysis_kwargs, task)
        mock_client.update_result.assert_called_once_with(mock_result)
        mock_info.assert_called_once_with(self.empty_tr_data)

    def test_cat_1_analysis_two_matches(self, mocker, analysis_kwargs, task):
        mock_enki = mocker.patch('libcrowds_analyst.analysis.enki')
        mock_client = mocker.patch('libcrowds_analyst.analysis.api_client')
        data = [self.empty_tr_data] + [self.tr_data for i in range(2)]
        (mock_result, mock_info) = self.analyse(data, mock_enki,
                                                analysis_kwargs, task)
        mock_client.update_result.assert_called_once_with(mock_result)
        mock_info.assert_called_once_with(self.tr_data)

    def test_cat_1_no_matches(self, mocker, analysis_kwargs, task):
        mock_enki = mocker.patch('libcrowds_analyst.analysis.enki')
        mock_client = mocker.patch('libcrowds_analyst.analysis.api_client')
        data = [self.tr_data] + [self.empty_tr_data for i in range(2)]
        (mock_result, mock_info) = self.analyse(data, mock_enki,
                                                analysis_kwargs, task)
        mock_client.update_result.assert_called_once_with(mock_result)
        mock_info.assert_called_once_with('Unanalysed')


class TestCategorySevenAnalysis(TestAnalysis):

    def setup(self):
        super(TestCategorySevenAnalysis, self)
        self.tr_data = {'title': '123', 'author': '456', 'date': 'hello',
                        'reference': 'xx', 'former_reference': 'yy',
                        'other_information': 'zz'}
        self.empty_tr_data = {'title': '', 'author': '', 'date': '',
                              'reference': '', 'former_reference': '',
                              'other_information': ''}

    def analyse(self, data, mock_enki, analysis_kwargs, task):
        mock_info = PropertyMock()
        mock_result = MagicMock()
        type(mock_result).info = mock_info
        mock_enki.pbclient.find_results.return_value = [mock_result]
        mock_enki.Enki().tasks = [task]
        mock_enki.Enki().task_runs_df = self.create_tr_dataframe(data, task.id)
        analysis.category_7(**analysis_kwargs)
        return mock_result, mock_info

    def test_cat_7_analysis_no_answers(self, mocker, analysis_kwargs, task):
        mock_enki = mocker.patch('libcrowds_analyst.analysis.enki')
        mock_client = mocker.patch('libcrowds_analyst.analysis.api_client')
        data = [self.empty_tr_data for i in range(2)]
        (mock_result, mock_info) = self.analyse(data, mock_enki,
                                                analysis_kwargs, task)
        mock_client.update_result.assert_called_once_with(mock_result)
        mock_info.assert_called_once_with(self.empty_tr_data)

    def test_cat_7_analysis_two_matches(self, mocker, analysis_kwargs, task):
        mock_enki = mocker.patch('libcrowds_analyst.analysis.enki')
        mock_client = mocker.patch('libcrowds_analyst.analysis.api_client')
        data = [self.tr_data for i in range(2)]
        (mock_result, mock_info) = self.analyse(data, mock_enki,
                                                analysis_kwargs, task)
        mock_client.update_result.assert_called_once_with(mock_result)
        mock_info.assert_called_once_with(self.tr_data)

    def test_cat_7_no_matches(self, mocker, analysis_kwargs, task):
        mock_enki = mocker.patch('libcrowds_analyst.analysis.enki')
        mock_client = mocker.patch('libcrowds_analyst.analysis.api_client')
        data = [self.tr_data] + [self.empty_tr_data]
        (mock_result, mock_info) = self.analyse(data, mock_enki,
                                                analysis_kwargs, task)
        mock_client.update_result.assert_called_once_with(mock_result)
        mock_info.assert_called_once_with('Unanalysed')
