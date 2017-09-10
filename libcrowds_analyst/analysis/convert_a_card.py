# -*- coding: utf8 -*-
"""Convert-a-Card analysis module."""

import enki
from libcrowds_analyst.analysis import helpers


MATCH_PERCENTAGE = 60
VALID_KEYS = ['oclc', 'shelfmark', 'comments']


def analyse(api_key, endpoint, project_id, result_id, project_short_name,
            **kwargs):
    """Analyse Convert-a-Card results."""
    e = enki.Enki(api_key, endpoint, project_short_name, all=1)
    result = enki.pbclient.find_results(project_id, id=result_id, limit=1,
                                        all=1)[0]
    df = helpers.get_task_run_df(e, result.task_id)
    df = df[VALID_KEYS]
    df = helpers.drop_empty_rows(df)
    n_task_runs = len(df.index)
    result.info = {k: "" for k in df.keys()}
    result.info['']

    # No answers
    if df.empty:
        result.info['analysis_complete'] = True

    # Matching answers
    elif helpers.has_n_matches(df, n_task_runs, MATCH_PERCENTAGE):
        result.info['analysis_complete'] = True
        for k in df.keys():
            result.info[k] = df[k].value_counts().idxmax()

    # Varied answers
    else:
        result.info['analysis_complete'] = False
    enki.pbclient.update_result(result)
