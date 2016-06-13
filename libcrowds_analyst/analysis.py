# -*- coding: utf8 -*-
"""Analyst module for libcrowds-analyst."""

import sys
import enki
import time
import numpy as np


def _normalise_shelfmarks(df):
    """Normalise all shelfmarks in a dataframe."""
    df['shelfmark'].replace(r',', '.', inplace=True)
    df['shelfmark'].replace(r'\s+', '.', inplace=True)
    df['shelfmark'].replace(r'\.+', '.', inplace=True)
    df['shelfmark'].replace(r'\.$', '', inplace=True)
    df['shelfmark'].replace(r'^\.', '.', inplace=True)
    df['shelfmark'].replace(r'(?i)^chi', 'CHI', inplace=True)


def get_analyst_func(category_id):
    """Return the analyst function for a category."""
    func = 'category_{0}'.format(category_id)
    this_module = sys.modules[__name__]
    if hasattr(this_module, func):
        return getattr(this_module, func)


def category_1(api_key, endpoint, project_short_name, task_id, sleep=0):
    """Analyser for Convert-a-Card projects."""
    time.sleep(sleep)  # To throttle when many API calls
    e = enki.Enki(api_key, endpoint, project_short_name)
    e.get_tasks(task_id=task_id)
    e.get_task_runs()
    for t in e.tasks:
        r = enki.pbclient.find_results(e.project.id, task_id=task_id, all=1)[0]
        df = e.task_runs_df[t.id][['oclc', 'shelfmark']]

        # Check for populated rows
        df = df.replace('', np.nan)
        if df.dropna(how='all').empty:
            r.info = dict(oclc="", shelfmark="")
            enki.pbclient.update_result(r)
            continue

        # Check for two or more matches
        _normalise_shelfmarks(df)
        df = df[df.duplicated(['oclc', 'shelfmark'], keep=False)]
        if not df.dropna(how='all').empty:
            r.info = dict(oclc=df.iloc[0]['oclc'],
                          shelfmark=df.iloc[0]['shelfmark'])
            enki.pbclient.update_result(r)
            continue

        # Unanalysed result
        r.info = 'Unanalysed'
        enki.pbclient.update_result(r)

    return "OK"
