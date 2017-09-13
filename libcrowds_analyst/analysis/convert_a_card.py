# -*- coding: utf8 -*-
"""Convert-a-Card analysis module."""

import enki
from libcrowds_analyst.analysis import helpers
from libcrowds_analyst import object_loader


MATCH_PERCENTAGE = 60
VALID_KEYS = ['oclc', 'shelfmark', 'comments']


def analyse(api_key, endpoint, doi, project_id, result_id, project_short_name,
            path, **kwargs):
    """Analyse Convert-a-Card results."""
    e = enki.Enki(api_key, endpoint, project_short_name, all=1)
    result = enki.pbclient.find_results(project_id, id=result_id, limit=1,
                                        all=1)[0]
    df = helpers.get_task_run_df(e, result.task_id)
    df = df.loc[:, df.columns.isin(VALID_KEYS)]
    df = helpers.drop_empty_rows(df)
    n_task_runs = len(df.index)

    # Initialise the result
    defaults = {k: "" for k in df.keys()}
    result.info = helpers.init_result_info(doi, path, defaults)

    has_answers = not df.empty
    has_matches = helpers.has_n_matches(df, n_task_runs, MATCH_PERCENTAGE)

    # Matching answers
    if has_answers and has_matches:
        for k in df.keys():
            result.info[k] = df[k].value_counts().idxmax()

    # Varied answers
    elif has_answers:
        result.info['analysis_complete'] = False
    enki.pbclient.update_result(result)


def analyse_all(project_short_name, **kwargs):
    """Analyse all Convert-a-Card results."""
    e = enki.Enki(kwargs['api_key'], kwargs['endpoint'], project_short_name,
                  all=1)
    results = object_loader.load(enki.pbclient.find_results,
                                 project_id=e.project.id, all=1)
    for result in results:
        kwargs['project_id'] = e.project.id
        kwargs['result_id'] = result.id
        analyse(**kwargs.copy())
