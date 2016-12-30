# -*- coding: utf8 -*-
"""Analysis module for pybossa-analyst."""

import time
import numpy as np
from pybossa_analyst import client


def _extract_keys(df):
    """Return all keys from all task run info fields."""
    keyset = set()
    for i in range(len(df)):
        for k in df.iloc[i]['info'].keys():
            keyset.add(k)
    return list(keyset)


def _drop_empty_rows(df):
    """Drop rows that contain no data."""
    df = df.replace('', np.nan)
    df = df.dropna(how='all')
    return df


def analyse(api_key, endpoint, project_id, result_id, match_percentage,
            exclude=[], sleep=2, **kwargs):
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
    time.sleep(sleep)  # To handle API rate limit when analysing many results
    r = client.get_results(api_key, endpoint, project_id, id=result_id, limit=1)[0]
    df = client.get_task_run_dataframe(api_key, endpoint, project_id, r.task_id)
    keys = [k for k in _extract_keys(df) if k not in exclude]
    df = df[keys]
    df = _drop_empty_rows(df)

    if df.empty:
        r.info = {k: "" for k in keys}
        client.update_result(r)
        return

    # Check for n percent of matches
    required_matches = int(round(len(df.index)*(match_percentage / 100.0)))
    info = {}
    for k in keys:
        if df[k].value_counts().max() < required_matches:
            info = 'Unanalysed'
            continue
        info[k] = df[k].value_counts().idxmax()
    r.info = info
    client.update_result(api_key, endpoint, r)
