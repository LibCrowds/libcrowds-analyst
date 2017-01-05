# -*- coding: utf8 -*-
"""Analysis module for pybossa-analyst."""

import time
import enki
import numpy
from pybossa_analyst import object_loader


def _drop_excluded_keys(df, excluded_keys):
    """Drop excluded keys from task run info fields."""
    keyset = set()
    for i in range(len(df)):
        for k in df.iloc[i]['info'].keys():
            keyset.add(k)
    keys = [k for k in keyset if k not in excluded_keys]
    return df[keys]


def _drop_empty_rows(df):
    """Drop rows that contain no data."""
    df = df.replace('', numpy.nan)
    df = df.dropna(how='all')
    return df


def _check_for_n_percent_of_matches(df, n_task_runs, match_percentage):
    """Check if n percent of answers match for each key."""
    required_matches = int(round(n_task_runs*(match_percentage / 100.0)))
    info = {}
    for k in df.keys():
        if df[k].value_counts().max() < required_matches:
            info = 'Unanalysed'
            continue
        info[k] = df[k].value_counts().idxmax()
    return info


def _get_task_run_df(api_key, endpoint, project_short_name, task_id):
    """Return a dataframe containing all task run info for a task."""
    e = enki.Enki(api_key, endpoint, project_short_name)
    e.get_tasks(task_id=task_id)
    e.get_task_runs()
    t = e.tasks[0]
    return e.task_runs_df[t.id]


def analyse(api_key, endpoint, project_id, result_id, project_short_name,
            match_percentage, excluded_keys=[], **kwargs):
    """Analyser for all projects.

    Check that the info fields of each task run match n percent of the time
    or above, disregarding task runs where all of the info fields are blank.
    For tasks where we have a sufficent number of matches the result will be
    set to a dictionary containing the task run info keys and the matched
    values. For tasks where all info fields of all task runs are empty the
    result will be set to a dictionary containing the task run info keys and
    empty values. For all other tasks the result will be set to the string
    'Unanalysed' so that the different answers can be checked manually later.
    """
    enki.pbclient.set('api_key', api_key)
    enki.pbclient.set('endpoint', endpoint)
    r = enki.pbclient.find_results(project_id, id=result_id, limit=1, all=1)[0]
    df = _get_task_run_df(api_key, endpoint, project_short_name, r.task_id)
    n_task_runs = len(df.index)

    df = _drop_excluded_keys(df, excluded_keys)
    df = _drop_empty_rows(df)

    if df.empty:
        r.info = {k: "" for k in df.keys()}
        enki.pbclient.update_result(r)
        return

    r.info = _check_for_n_percent_of_matches(df, n_task_runs, match_percentage)
    enki.pbclient.update_result(r)


def analyse_multiple(api_key, endpoint, project_id, project_short_name,
                     info_filter, match_percentage, excluded_keys=[]):
    """Analyse multiple results."""
    enki.pbclient.set('api_key', api_key)
    enki.pbclient.set('endpoint', endpoint)
    time.sleep(2)  # To handle API rate limit when analysing many results
    results = object_loader.load(enki.pbclient.find_results,
                                 project_id=project.id)
    results = filter(lambda x: str(x.info) == info_filter
                     if info_filter != 'all' else True, results)
    for result in results:
        kwargs = {
            'api_key': api_key,
            'endpoint': endpoint,
            'project_id': project_id,
            'result_id': result.id,
            'project_short_name': project_short_name,
            'match_percentage': match_percentage,
            'excluded_keys': excluded_keys
        }
        analyse(**kwargs)
