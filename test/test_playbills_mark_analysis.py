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

    def test_correct_result_analysed(self, mocker, project, result, payload):
        """Test that the correct result is analysed."""
        mock_enki = mocker.patch(
            'libcrowds_analyst.analysis.playbills.enki'
        )

        kwargs = json.loads(payload)
        kwargs['api_key'] = 'token'
        kwargs['endpoint'] = 'example.com'
        kwargs['doi'] = '123/456'
        kwargs['url_rule'] = '/example'
        playbills.analyse_selections(**kwargs)

        mock_enki.pbclient.find_results.assert_called_with(project.id, limit=1,
                                                           id=result.id, all=1)

    def test_empty_result_updated(self, create_task_run_df, mocker, result,
                                  payload):
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

        kwargs = json.loads(payload)
        kwargs['api_key'] = 'token'
        kwargs['endpoint'] = 'example.com'
        kwargs['doi'] = '123/456'
        kwargs['url_rule'] = '/example'
        playbills.analyse_selections(**kwargs)

        mock_enki.pbclient.update_result.assert_called_with(result)
        assert result.info == {
            'annotations': [],
            'analysis_complete': True
        }

    def test_equal_regions_combined(self, create_task_run_df, mocker,
                                    result, payload, select_annotation):
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

        kwargs = json.loads(payload)
        kwargs['api_key'] = 'token'
        kwargs['endpoint'] = 'example.com'
        kwargs['doi'] = '123/456'
        kwargs['url_rule'] = '/example'
        playbills.analyse_selections(**kwargs)

        mock_enki.pbclient.update_result.assert_called_with(result)
        expected = '?xywh=400,200,100,100'
        annotations = result.info['annotations']
        assert len(annotations) == 1
        assert annotations[0]['target']['selector']['value'] == expected

    def test_similar_regions_combined(self, create_task_run_df, mocker,
                                      result, payload, select_annotation):
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

        kwargs = json.loads(payload)
        kwargs['api_key'] = 'token'
        kwargs['endpoint'] = 'example.com'
        kwargs['doi'] = '123/456'
        kwargs['url_rule'] = '/example'
        playbills.analyse_selections(**kwargs)

        mock_enki.pbclient.update_result.assert_called_with(result)
        expected = '?xywh=100,100,100,100'
        annotations = result.info['annotations']
        assert len(annotations) == 1
        assert annotations[0]['target']['selector']['value'] == expected
