# -*- coding: utf8 -*-
"""Test Convert-a-Card analysis."""

import json
from libcrowds_analyst.analysis import playbills


class TestPlaybillsMarkAnalysis(object):

    def test_correct_result_analysed(self, mocker, project, result, payload):
        """Test that the correct result is analysed."""
        mock_enki = mocker.patch(
            'libcrowds_analyst.analysis.playbills.enki'
        )

        kwargs = json.loads(payload)
        kwargs['api_key'] = 'token'
        kwargs['endpoint'] = 'example.com'
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
        playbills.analyse_selections(**kwargs)

        mock_enki.pbclient.update_result.assert_called_with(result)
        assert result.info == {
            'annotations': [],
            'analysis_complete': True
        }

    def test_similar_regions_combined(self, create_task_run_df, mocker,
                                      result, payload):
        """Test that regions with an intersection of >= 80% are combined."""
        mock_enki = mocker.patch(
            'libcrowds_analyst.analysis.convert_a_card.enki'
        )

        tr_info = [
            [
                {
                    "@context": "http://www.w3.org/ns/anno.jsonld",
                    "id": "d008efa2-42e5-494e-b463-c7b9b6744b67",
                    "type": "Annotation",
                    "motivation": "tagging",
                    "created": "2017-07-16T00:44:28.454Z",
                    "generated": "2017-07-16T00:44:28.454Z",
                    "target": {
                        "source": "http://example.org/iiif/book1/canvas/p1",
                        "selector": {
                            "conformsTo": "http://www.w3.org/TR/media-frags/",
                            "type": "FragmentSelector",
                            "value": "?xywh=100,100,100,100"
                        }
                    },
                    "body": [
                        {
                            "type": "TextualBody",
                            "purpose": "tagging",
                            "value": "title"
                        },
                        {
                            "type": "SpecificResource",
                            "purpose": "classifying",
                            "source": "http://purl.org/dc/terms/title"
                        }
                    ],
                    "modified": "2017-07-16T13:53:18.795Z"
                }
            ],
            [
                {
                    "@context": "http://www.w3.org/ns/anno.jsonld",
                    "id": "d008efa2-42e5-494e-b463-c7b9b6744b67",
                    "type": "Annotation",
                    "motivation": "tagging",
                    "created": "2017-07-16T00:44:28.454Z",
                    "generated": "2017-07-16T00:44:28.454Z",
                    "target": {
                        "source": "http://example.org/iiif/book1/canvas/p1",
                        "selector": {
                            "conformsTo": "http://www.w3.org/TR/media-frags/",
                            "type": "FragmentSelector",
                            "value": "?xywh=150,100,100,100"
                        }
                    },
                    "body": [
                        {
                            "type": "TextualBody",
                            "purpose": "tagging",
                            "value": "title"
                        },
                        {
                            "type": "SpecificResource",
                            "purpose": "classifying",
                            "source": "http://purl.org/dc/terms/title"
                        }
                    ],
                    "modified": "2017-07-16T13:53:18.795Z"
                }
            ]
        ]
        df = create_task_run_df(tr_info)
        mock_enki.pbclient.find_results.return_value = [result]
        mock_enki.Enki().task_runs_df.__getitem__.return_value = df

        kwargs = json.loads(payload)
        kwargs['api_key'] = 'token'
        kwargs['endpoint'] = 'example.com'
        playbills.analyse_selections(**kwargs)

        mock_enki.pbclient.update_result.assert_called_with(result)
        assert result.info == {
            'annotations': [],
            'shelfmark': '',
            'analysis_complete': False
        }

    # def test_dissimilar_regions_not_combined(self, create_task_run_df, mocker,
    #                                          result, payload):
    #     """Test that regions with an intersection of < 80% are not combined."""
    #     mock_enki = mocker.patch(
    #         'libcrowds_analyst.analysis.convert_a_card.enki'
    #     )
    #     tr_info = [
    #         [
    #             {
    #                 "@context": "http://www.w3.org/ns/anno.jsonld",
    #                 "id": "d008efa2-42e5-494e-b463-c7b9b6744b67",
    #                 "type": "Annotation",
    #                 "motivation": "tagging",
    #                 "created": "2017-07-16T00:44:28.454Z",
    #                 "generated": "2017-07-16T00:44:28.454Z",
    #                 "target": {
    #                     "source": "http://example.org/iiif/book1/canvas/p1",
    #                     "selector": {
    #                         "conformsTo": "http://www.w3.org/TR/media-frags/",
    #                         "type": "FragmentSelector",
    #                         "value": "?xywh=1000,400,100,100"
    #                     }
    #                 },
    #                 "body": [
    #                     {
    #                     "type": "TextualBody",
    #                     "purpose": "tagging",
    #                     "value": "title"
    #                     },
    #                     {
    #                     "type": "SpecificResource",
    #                     "purpose": "classifying",
    #                     "source": "http://purl.org/dc/terms/title"
    #                     }
    #                 ],
    #                 "modified": "2017-07-16T13:53:18.795Z"
    #             }
    #         ],
    #         [
    #             {
    #                 "@context": "http://www.w3.org/ns/anno.jsonld",
    #                 "id": "d008efa2-42e5-494e-b463-c7b9b6744b67",
    #                 "type": "Annotation",
    #                 "motivation": "tagging",
    #                 "created": "2017-07-16T00:44:28.454Z",
    #                 "generated": "2017-07-16T00:44:28.454Z",
    #                 "target": {
    #                     "source": "http://example.org/iiif/book1/canvas/p1",
    #                     "selector": {
    #                     "conformsTo": "http://www.w3.org/TR/media-frags/",
    #                     "type": "FragmentSelector",
    #                     "value": "?xywh=150,100,100,100"
    #                     }
    #                 },
    #                 "body": [
    #                     {
    #                     "type": "TextualBody",
    #                     "purpose": "tagging",
    #                     "value": "title"
    #                     },
    #                     {
    #                     "type": "SpecificResource",
    #                     "purpose": "classifying",
    #                     "source": "http://purl.org/dc/terms/title"
    #                     }
    #                 ],
    #                 "modified": "2017-07-16T13:53:18.795Z"
    #             }
    #         ]
    #     ]
    #     df = create_task_run_df(tr_info)
    #     mock_enki.pbclient.find_results.return_value = [result]
    #     mock_enki.Enki().task_runs_df.__getitem__.return_value = df

    #     kwargs = json.loads(payload)
    #     kwargs['api_key'] = 'token'
    #     kwargs['endpoint'] = 'example.com'
    #     playbills.analyse_selections(**kwargs)

    #     mock_enki.pbclient.update_result.assert_called_with(result)
    #     assert result.info == {
    #         'oclc': '',
    #         'shelfmark': '',
    #         'analysis_complete': False
    #     }


    # def test_matched_result_updated(self, create_task_run_df, mocker,
    #                                 project, result, task):
    #     """Test that a matched result is updated correctly."""
    #     mock_enki = mocker.patch(
    #         'libcrowds_analyst.analysis.convert_a_card.enki'
    #     )
    #     tr_info = [
    #         {'oclc': '123', 'shelfmark': '456'},
    #         {'oclc': '123', 'shelfmark': '456'}
    #     ]
    #     df = create_task_run_df(tr_info)
    #     mock_enki.pbclient.find_results.return_value = [result]
    #     mock_enki.Enki().task_runs_df.__getitem__.return_value = df
    #     kwargs = {
    #         'api_key': 'api_key',
    #         'endpoint': 'endpoint',
    #         'project_short_name': project.short_name,
    #         'project_id': project.id,
    #         'result_id': result.id,
    #         'match_percentage': 100,
    #         'excluded_keys': []
    #     }
    #     convert_a_card.analyse(**kwargs)
    #     mock_enki.pbclient.update_result.assert_called_with(result)
    #     assert result.info == {
    #         'oclc': '123',
    #         'shelfmark': '456',
    #         'analysis_complete': True
    #     }
