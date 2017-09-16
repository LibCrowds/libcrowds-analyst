# -*- coding: utf8 -*-
"""Analysis helpers module."""

import math
import numpy
from flask.ext.mail import Message
from libcrowds_analyst.core import mail


def init_result_info(doi, path, defaults=None):
    """Initialise result info."""
    info = defaults or {}
    info['analysis_complete'] = True
    info['analysis_doi'] = doi
    info['analysis_path'] = path
    return info


def drop_keys(task_run_df, keys):
    """Drop keys from the info fields of a task run dataframe."""
    keyset = set()
    for i in range(len(task_run_df)):
        for k in task_run_df.iloc[i]['info'].keys():
            keyset.add(k)
    keys = [k for k in keyset if k not in keys]
    return task_run_df[keys]


def drop_empty_rows(task_run_df):
    """Drop rows that contain no data."""
    task_run_df = task_run_df.replace('', numpy.nan)
    task_run_df = task_run_df.dropna(how='all')
    return task_run_df


def has_n_matches(task_run_df, n_task_runs, match_percentage):
    """Check if n percent of answers match for each key."""
    required_matches = int(math.ceil(n_task_runs * (match_percentage / 100.0)))

    # Replace NaN with the empty string
    task_run_df = task_run_df.replace(numpy.nan, '')

    for k in task_run_df.keys():
        if task_run_df[k].value_counts().max() < required_matches:
            return False
    return True


def get_task_run_df(enki, task_id):
    """Return a dataframe containing all task run info for a task."""
    enki.get_tasks(task_id=task_id)
    enki.get_task_runs()
    task = enki.tasks[0]
    return enki.task_runs_df[task.id]


def send_mail(message_dict):
    """Send email."""
    message = Message(**message_dict)
    mail.send(message)
