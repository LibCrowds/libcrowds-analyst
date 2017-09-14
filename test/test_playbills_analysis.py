# -*- coding: utf8 -*-
"""Test Convert-a-Card analysis."""

import json
from libcrowds_analyst.analysis import playbills


class TestPlaybillsMarkAnalysis(object):

    def test_overlap_ratio_100_with_equal_rects(self):
        """Test for an overlap ratio of 1."""
        rect = {'x': 100, 'y': 100, 'w': 100, 'h': 100}
        overlap = playbills.get_overlap_ratio(rect, rect)
        assert overlap == 1

    def test_overlap_ratio_0_with_adjacent_rects(self):
        """Test for an overlap ratio of 0."""
        r1 = {'x': 100, 'y': 100, 'w': 100, 'h': 100}
        r2 = {'x': 100, 'y': 201, 'w': 100, 'h': 100}
        overlap = playbills.get_overlap_ratio(r1, r2)
        assert overlap == 0

    def test_overlap_ratio_with_overlapping_rects(self):
        """Test form an overlap ratio of 0.5."""
        r1 = {'x': 100, 'y': 100, 'w': 100, 'h': 100}
        r2 = {'x': 150, 'y': 100, 'w': 100, 'h': 100}
        overlap = playbills.get_overlap_ratio(r1, r2)
        assert '{:.2f}'.format(overlap) == '0.33'

    def test_correct_result_analysed(self, mocker, project, result,
                                     processed_payload):
        """Test that the correct result is analysed."""
        mock_enki = mocker.patch(
            'libcrowds_analyst.analysis.playbills.enki'
        )
        playbills.analyse_selections(**processed_payload)
        mock_enki.pbclient.find_results.assert_called_with(project.id, limit=1,
                                                           id=result.id, all=1)

    def test_empty_result_updated(self, create_task_run_df, mocker, result,
                                  processed_payload):
        """Test that an empty result is updated correctly."""
        mock_enki = mocker.patch(
            'libcrowds_analyst.analysis.playbills.enki'
        )
        tr_info = [
            [],
            [],
        ]
        df = create_task_run_df(tr_info)
        mock_enki.pbclient.find_results.return_value = [result]
        mock_enki.Enki().task_runs_df.__getitem__.return_value = df
        playbills.analyse_selections(**processed_payload)
        mock_enki.pbclient.update_result.assert_called_with(result)
        assert result.info == {
            'annotations': [],
            'analysis_complete': True,
            'analysis_doi': '123/456',
            'analysis_path': '/example'
        }

    def test_equal_regions_combined(self, create_task_run_df, mocker,
                                    result, processed_payload,
                                    select_annotation):
        """Test that equal regions are combined."""
        mock_enki = mocker.patch(
            'libcrowds_analyst.analysis.playbills.enki'
        )
        selection = {'x': 400, 'y': 200, 'w': 100, 'h': 100}
        tr_info = [
            [
                select_annotation(**selection),
                select_annotation(**selection)
            ]
        ]
        df = create_task_run_df(tr_info)
        mock_enki.pbclient.find_results.return_value = [result]
        mock_enki.Enki().task_runs_df.__getitem__.return_value = df
        playbills.analyse_selections(**processed_payload)
        mock_enki.pbclient.update_result.assert_called_with(result)
        expected = '?xywh=400,200,100,100'
        annotations = result.info['annotations']
        assert len(annotations) == 1
        assert annotations[0]['target']['selector']['value'] == expected

    def test_similar_regions_combined(self, create_task_run_df, mocker,
                                      result, processed_payload,
                                      select_annotation):
        """Test that regions with an intersection of >= 80% are combined."""
        mock_enki = mocker.patch(
            'libcrowds_analyst.analysis.playbills.enki'
        )
        selection1 = {'x': 100, 'y': 100, 'w': 100, 'h': 100}
        selection2 = {'x': 110, 'y': 110, 'w': 90, 'h': 90}
        tr_info = [
            [
                select_annotation(**selection1),
                select_annotation(**selection2)
            ]
        ]
        df = create_task_run_df(tr_info)
        mock_enki.pbclient.find_results.return_value = [result]
        mock_enki.Enki().task_runs_df.__getitem__.return_value = df
        playbills.analyse_selections(**processed_payload)
        mock_enki.pbclient.update_result.assert_called_with(result)
        expected = '?xywh=100,100,100,100'
        annotations = result.info['annotations']
        assert len(annotations) == 1
        assert annotations[0]['target']['selector']['value'] == expected

    def test_rect_from_selection(self, select_annotation):
        """Test that we get the correct rect."""
        selection = {'x': 400, 'y': 200, 'w': 100, 'h': 100}
        anno = select_annotation(**selection)
        rect = playbills.get_rect_from_selection(anno)
        assert rect == selection

    def test_rect_from_selection_works_with_floats(self, select_annotation):
        """Test that we can use floats when converting rects."""
        selection = {'x': 400.123, 'y': 200.456, 'w': 100.789, 'h': 100.511}
        anno = select_annotation(**selection)
        rect = playbills.get_rect_from_selection(anno)
        assert rect == {'x': 400, 'y': 200, 'w': 101, 'h': 101}

    def test_all_selection_results_analysed(self, mocker, result, project):
        """Test that analysis of all selection results triggered correctly."""
        mock_enki = mocker.patch(
            'libcrowds_analyst.analysis.playbills.enki'
        )
        mock_enki.Enki().project = project
        mock_analyse = mocker.patch(
            'libcrowds_analyst.analysis.playbills.analyse_selections'
        )
        mock_object_loader = mocker.patch(
            'libcrowds_analyst.analysis.playbills.object_loader'
        )
        kwargs = {
          'api_key': 'token',
          'endpoint': 'example.com',
          'doi': '123/456',
          'path': '/example',
          'project_short_name': 'some_project'
        }
        mock_object_loader.load.return_value = [result]
        playbills.analyse_all_selections(**kwargs)
        expected = kwargs.copy()
        expected['result_id'] = result.id
        expected['project_id'] = result.project_id
        mock_analyse.assert_called_with(**expected)

    def test_select_result_initialised_properly(self, mocker,
                                                processed_payload):
        """Test that the result is initialised using the helper function."""
        mocker.patch('libcrowds_analyst.analysis.playbills.enki')
        mock_init_info = mocker.patch('libcrowds_analyst.analysis.playbills.'
                                      'helpers.init_result_info')
        playbills.analyse_selections(**processed_payload)
        assert mock_init_info.call_args[0][0] == processed_payload['doi']
        assert mock_init_info.call_args[0][1] == processed_payload['path']

    def test_select_analysis_throttled(self, mocker, processed_payload):
        """Test that the result is initialised using the helper function."""
        mocker.patch('libcrowds_analyst.analysis.playbills.enki')
        mock_sleep = mocker.patch(
          'libcrowds_analyst.analysis.playbills.time.sleep'
        )
        playbills.analyse_selections(**processed_payload)
        mock_sleep.assert_called_with(processed_payload['throttle'])
