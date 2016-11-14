# -*- coding: utf8 -*-
"""Analysis module for libcrowds-analyst."""

import sys
import time
import enki
import numpy as np
from libcrowds_analyst.core import pybossa_client


#def _concat(df, col):
#    """Return concatenated, non-duplicated column values.
#
#    :param df: The dataframe of task runs (i.e enki.task_runs_df[task_id]).
#    :param col: The name of the column.
#    """
#    deduped_df = df[col].drop_duplicates(keep='first')
#    return '; '.join([item for item in deduped_df if len(item) > 0])
#
#
#def _normalise_shelfmarks(df, col):
#    """Normalise all shelfmarks in a dataframe.
#
#    :param df: The dataframe.
#    :param col: The name of the column.
#    """
#    df[col].fillna("", inplace=True)
#    df[col].replace(r',', '.', inplace=True)
#    df[col].replace(r'\s+', '.', inplace=True)
#    df[col].replace(r'\.+', '.', inplace=True)
#    df[col].replace(r'\.$', '', inplace=True)
#    df[col].replace(r'^\.', '.', inplace=True)
#    df[col].replace(r'(?i)^chi', 'CHI', inplace=True)


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


def analyse(project_id, task_id, match_percentage):
    """Analyser for all LibCrowds projects.

    Check that the info fields of each task run match n percent of the time
    or above, disregarding task runs where all of the info fields are blank.
    For tasks where we have a sufficent number of matches the result will be
    set to a dictionary containing the task run info keys and the matched
    values. For tasks where all info fields of all task runs are empty the
    result will be set to a dictionary containing the task run info keys and
    empty values. For all other tasks the result will be set to the string
    'Unanalysed' so that the different answers can be checked manually later.
    """
    time.sleep(2)  # To handle API rate limit when analysing many results
    df = pybossa_client.get_task_run_dataframe(project_id, task_id)
    keys = _extract_keys(df)
    df = df[keys]
    df = _drop_empty_rows(df)
    r = pybossa_client.get_results(project_id, task_id=task_id, limit=1)[0]

    if df.empty:
        r.info = {k: "" for k in keys}
        pybossa_client.update_result(r)
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
    pybossa_client.update_result(r)
