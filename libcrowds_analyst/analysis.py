# -*- coding: utf8 -*-
"""Analysis module for libcrowds-analyst."""

import sys
import time
import enki
import pbclient
import numpy as np


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


def _get_task_run_dataframe(short_name, task_id):
    """Return a dataframe containing all task run info for a task."""
    p = pbclient.get_project(project_id)
    e = enki.Enki(pbclient.api_key, pbclient.endpoint, p.short_name, all=1)
    e.get_tasks(task_id=task_id)
    e.get_task_runs()
    t = e.tasks[0]
    return e.task_runs_df[t.id]


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


def analyse(project_id, task_id, match_percentage=60):
    """Analyser for all LibCrowds projects.

    Check that the info fields of each task run match n percent of the time or
    above, disregarding task runs where all of the info fields are blank. For
    tasks where we have a sufficent number of matches the result will be set to
    a dictionary containing the task run info keys and the matched values. For
    tasks where all info fields of all task runs are empty the result will be
    set to a dictionary containing the task run info keys and empty values. For
    all other tasks the result will be set to the string 'Unanalysed' so that
    the different answers can be checked manually later.
    """
    time.sleep(2)  # To handle API rate limit when analysing many results
    r = pbclient.find_results(project_id, task_id=task_id, limit=1, all=1)[0]
    df = _get_task_run_dataframe(project_id, task_id)
    keys = _extract_keys(df)
    df = df[keys]
    df = _drop_empty_rows(df)

    if df.empty:
        r.info = {k: "" for k in keys}
        pbclient.update_result(r)
        return

    # Check for n percent of matches
    df = df[df.duplicated(keys, keep=False)]
    if not df.dropna(how='all').empty:
        r.info = dict(oclc=df.iloc[0]['oclc'],
                      shelfmark=df.iloc[0]['shelfmark'], comments=comments)
        pbclient.update_result(r)
        return

    # Unanalysed result
    r.info = 'Unanalysed'
    pbclient.update_result(r)
