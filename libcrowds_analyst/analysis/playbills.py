# -*- coding: utf8 -*-
"""In the Spotlight analysis module."""

import itertools
import enki
from libcrowds_analyst.analysis import helpers


MERGE_PERCENTAGE = 90


def analyse_selections(api_key, endpoint, project_id, result_id,
                       project_short_name, **kwargs):
    """Analyse In the Spotlight results."""
    e = enki.Enki(api_key, endpoint, project_short_name, all=1)
    result = enki.pbclient.find_results(project_id, id=result_id, limit=1,
                                        all=1)[0]
    df = helpers.get_task_run_df(e, result.task_id)

    # Flatten annotations into a single list
    anno_list = df['info'].tolist()
    anno_list = list(itertools.chain.from_iterable(anno_list))

    n_annotations = len(anno_list)
    result.info = {
        'annotations': anno_list,
        'analysis_complete': True
    }

    # Merge similar regions
    if n_annotations > 0:
        print True

    enki.pbclient.update_result(result)
