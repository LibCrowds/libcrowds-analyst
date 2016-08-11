# -*- coding: utf8 -*-
"""Zip builder module for libcrowds-analyst."""

import os
import enki
import time
import requests
import zipfile
from redis import Redis
from rq_scheduler import Scheduler
from datetime import timedelta


scheduler = Scheduler('libcrowds_analyst_scheduled', connection=Redis())


def _build_empty_zip(zip_path):
    """Build an image set containing images downloaded from Flickr."""
    filename = os.path.splitext(os.path.basename(zip_path))[0]
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        empty_path = os.path.join(filename, 'no_data')
        archive.writestr(empty_path, '')


def _build_flickr_zip(zip_path, tasks):
    """Build an image set containing images downloaded from Flickr."""
    filename = os.path.splitext(os.path.basename(zip_path))[0]
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for t in tasks:
            url = t.info['url']
            img_path = os.path.join(filename, t.info['title'])
            img = requests.get(url).content
            archive.writestr(img_path, img)


def build(api_key, endpoint, zip_path, short_name, importer, task_ids):
    """Build a zip file containing original task input."""
    e = enki.Enki(api_key, endpoint, short_name)
    e.get_tasks()
    tasks = [t for t in e.tasks if str(t.id) in task_ids]
    if not tasks:
        _build_empty_zip(zip_path)
    elif importer == 'flickr':
        _build_flickr_zip(zip_path, tasks)
    else:
        raise ValueError("Unknown importer type")

    # Schedule removal of the file after 10 minutes
    scheduler.enqueue_in(timedelta(minutes=10), os.remove, zip_path)


def get_zip(path):
    """Return the zip file if it is ready for download."""
    print zipfile.is_zipfile(path)
    try:
        return open(path)
    except IOError as e:
        return None
