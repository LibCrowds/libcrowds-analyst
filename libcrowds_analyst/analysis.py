# -*- coding: utf8 -*-
"""Analysis module for libcrowds-analyst."""

import sys
import enki
import time
import numpy as np
from libcrowds_analyst.core import api_client


def _concat(df, col):
    """Return concatenated, non-duplicated column values.

    :param df: The dataframe of task runs (i.e enki.task_runs_df[task_id]).
    :param col: The name of the column.
    """
    deduped_df = df[col].drop_duplicates(keep='first')
    return '; '.join([item for item in deduped_df if len(item) > 0])


def _normalise_shelfmarks(df, col):
    """Normalise all shelfmarks in a dataframe.

    :param df: The dataframe.
    :param col: The name of the column.
    """
    df[col].fillna("", inplace=True)
    df[col].replace(r',', '.', inplace=True)
    df[col].replace(r'\s+', '.', inplace=True)
    df[col].replace(r'\.+', '.', inplace=True)
    df[col].replace(r'\.$', '', inplace=True)
    df[col].replace(r'^\.', '.', inplace=True)
    df[col].replace(r'(?i)^chi', 'CHI', inplace=True)


def get_analyst_func(category_id):
    """Return the analyst function for a category."""
    func = 'category_{0}'.format(category_id)
    this_module = sys.modules[__name__]
    if hasattr(this_module, func):
        return getattr(this_module, func)


def category_1(api_key, endpoint, project_short_name, task_id, sleep=0):
    """Analyser for Convert-a-Card projects.

    The fields being compared are 'oclc' and 'shelfmark'. For all tasks where
    two or more contributors submitted the same answer the result will be set
    to that answer. For those tasks where no contributors were able to find a
    matching WorldCat record the result will be set to a blank value for both
    'oclc' and 'shelfmark'. All other tasks will remain unanalysed. The
    'comments' are added for all analysed results.
    """
    time.sleep(sleep)  # To throttle when many API calls
    e = enki.Enki(api_key, endpoint, project_short_name)
    e.get_tasks(task_id=task_id)
    e.get_task_runs()
    for t in e.tasks:
        r = enki.pbclient.find_results(e.project.id, task_id=task_id, all=1)[0]
        df = e.task_runs_df[t.id][['oclc', 'shelfmark']]
        comments = _concat(e.task_runs_df[t.id], 'comments')
        _normalise_shelfmarks(df, 'shelfmark')

        # Drop empty rows
        df = df.replace('', np.nan)
        df = df.dropna(subset=['oclc', 'shelfmark'])

        # Check for populated rows
        if df.empty:
            r.info = dict(oclc="", shelfmark="", comments=comments)
            api_client.update_result(r)
            continue

        # Check for two or more matches
        df = df[df.duplicated(['oclc', 'shelfmark'], keep=False)]
        if not df.dropna(how='all').empty:
            r.info = dict(oclc=df.iloc[0]['oclc'],
                          shelfmark=df.iloc[0]['shelfmark'], comments=comments)
            api_client.update_result(r)
            continue

        # Unanalysed result
        r.info = 'Unanalysed'
        api_client.update_result(r)


def category_7(api_key, endpoint, project_short_name, task_id, sleep=0):
    """Analyser for LCP projects.

    For all tasks where two or more contributors submitted the same answer the
    result will be set to that answer. All other tasks will remain unanalysed.
    """
    time.sleep(sleep)  # To throttle when many API calls
    e = enki.Enki(api_key, endpoint, project_short_name)
    e.get_tasks(task_id=task_id)
    e.get_task_runs()
    for t in e.tasks:
        r = enki.pbclient.find_results(e.project.id, task_id=task_id, all=1)[0]
        df = e.task_runs_df[t.id][['title', 'author', 'date', 'reference',
                                   'former-reference', 'other-information']]

        # Check for two or more matches
        df = df[df.duplicated(['title', 'author', 'date', 'reference',
                               'former-reference', 'other-information'
                               ], keep=False)]
        if not df.dropna(how='all').empty:
            r.info = dict(oclc=df.iloc[0]['title'],
                          author=df.iloc[0]['author'],
                          date=df.iloc[0]['date'],
                          reference=df.iloc[0]['reference'],
                          former_reference=df.iloc[0]['former-reference'],
                          other_information=df.iloc[0]['other-information'])
            api_client.update_result(r)
            continue

        # Unanalysed result
        r.info = 'Unanalysed'
        api_client.update_result(r)
