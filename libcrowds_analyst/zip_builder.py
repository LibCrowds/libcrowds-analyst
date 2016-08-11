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
from flask import send_file


scheduler = Scheduler('libcrowds_analyst_scheduled', connection=Redis())


class ZipBuilder(object):
    """A class for building and exporting zip files of task input."""

    def __init__(self, app=None):
        """Init method."""
        self.app = app
        if app is not None:  # pragma: no cover
            self.init_app(app)

    def init_app(self, app):
        self.zip_folder = app.config['ZIP_FOLDER']
        self.api_key = app.config['API_KEY']
        self.endpoint = app.config['ENDPOINT']
        self._create_zip_folders()

    def _create_zip_folders(self):
        """Ensure that the necessary internal folders exist."""
        def mkdir_if_not_exists(path):
            try:
                os.makedirs(path)
            except OSError:
                if not os.path.isdir(path):
                    raise
        self.build_folder = os.path.join(self.zip_folder, 'Building')
        self.completed_folder = os.path.join(self.zip_folder, 'Complete')
        mkdir_if_not_exists(self.build_folder)
        mkdir_if_not_exists(self.completed_folder)

    def _build_empty_zip(self, filename):
        """Build an empty zip file."""
        zip_path = os.path.join(self.build_folder, filename)
        zip_dir = os.path.splitext(os.path.basename(zip_path))[0]
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
            empty_file = os.path.join(zip_dir, 'no_data')
            archive.writestr(empty_file, '')

    def _build_flickr_zip(self, filename, tasks):
        """Build an image set containing images downloaded from Flickr."""
        zip_path = os.path.join(self.build_folder, filename)
        zip_dir = os.path.splitext(os.path.basename(zip_path))[0]
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
            for t in tasks:
                url = t.info['url']
                img_path = os.path.join(zip_dir, t.info['title'])
                img = requests.get(url).content
                archive.writestr(img_path, img)

    def _get_valid_tasks(self, short_name, task_ids):
        """Return tasks in the list of task IDs that belong to a project."""
        e = enki.Enki(self.api_key, self.endpoint, short_name)
        e.get_tasks()
        tasks = [t for t in e.tasks if str(t.id) in task_ids]
        return tasks

    def _move_to_completed_folder(self, filename):
        """Move a zip file to the completed folder."""
        build_path = os.path.join(self.build_folder, filename)
        completed_path = os.path.join(self.completed_folder, filename)
        os.rename(build_path, completed_path)

    def build(self, short_name, task_ids, filename, importer):
        """Build a zip file containing original task input."""
        tasks = self._get_valid_tasks(short_name, task_ids)
        if not tasks:
            self._build_empty_zip(filename)
        elif importer == 'flickr':
            self._build_flickr_zip(filename, tasks)
        else:
            raise ValueError("Unknown importer type")

        self._move_to_completed_folder(filename)

    def response_zip(self, filename):
        """Return a response to download the zip file."""
        completed_path = os.path.join(self.completed_folder, filename)
        if not os.path.isfile(completed_path):
            return None
        return send_file(filename_or_fp=completed_path,
                         mimetype='application/zip',
                         as_attachment=True,
                         attachment_filename=filename)
