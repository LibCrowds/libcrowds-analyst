# -*- coding: utf8 -*-
"""Convert-a-Card analysis module."""

import enki
from libcrowds_analyst.analysis import helpers


MATCH_PERCENTAGE = 60
EXCLUDED_KEYS = []


def analyse(api_key, endpoint, project_id, result_id, short_name, **kwargs):
    """Analyse Convert-a-Card results."""
    enki.pbclient.set('api_key', api_key)
    enki.pbclient.set('endpoint', endpoint)
    result = enki.pbclient.find_results(project_id, id=result_id, limit=1,
                                        all=1)[0]
    df = helpers.get_task_run_df(api_key, endpoint, short_name, result.task_id)
    n_task_runs = len(df.index)

    df = helpers.drop_keys(df, EXCLUDED_KEYS)
    df = helpers.drop_empty_rows(df)

    # No answers
    if df.empty:
        result.info = {k: "" for k in df.keys()}
        result.info['analysis_complete'] = True
        result.info['check_required'] = False

    # Matching answers
    elif helpers.has_n_matches(df, n_task_runs, MATCH_PERCENTAGE):
        result.info['analysis_complete'] = True
        result.info['check_required'] = False
        for k in df.keys():
            result.info[k] = df[k].value_counts().idxmax()

    # Varied answers
    else:
        result.info = {k: "" for k in df.keys()}
        result.info['analysis_complete'] = False
        result.info['check_required'] = False
    enki.pbclient.update_result(result)
