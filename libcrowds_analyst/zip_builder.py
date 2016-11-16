# -*- coding: utf8 -*-
"""Zip builder module for libcrowds-analyst."""

import os
import enki
import requests
import zipfile
from redis import Redis
from rq_scheduler import Scheduler
from datetime import timedelta
from flask import send_file
from libcrowds_analyst.core import pybossa_client


scheduler = Scheduler('libcrowds_analyst_scheduled', connection=Redis())


class ZipBuilder(object):
    """A class for building and exporting zip files containing task input."""

    def __init__(self, app=None):
        """Init method."""
        self.app = app
        if app is not None:  # pragma: no cover
            self.init_app(app)

    def init_app(self, app):
        zip_folder = app.config['ZIP_FOLDER']
        self.build_folder = os.path.join(zip_folder, 'Building')
        self.completed_folder = os.path.join(zip_folder, 'Complete')
        self._create_zip_folders()

    def _create_zip_folders(self):
        """Ensure that the necessary internal folders exist."""
        def mkdir_if_not_exists(path):
            try:
                os.makedirs(path)
            except OSError:
                if not os.path.isdir(path):
                    raise
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
                img_path = os.path.join(zip_dir, t.info['title'] + ".jpg")
                img = requests.get(url).content
                archive.writestr(img_path, img)

    def _get_tasks_to_export(self, short_name, task_ids):
        """Return the tasks to be exported."""
        project = pybossa_client.get_projects(short_name=short_name)[0]
        tasks = pybossa_client.get_tasks(project_id=project.id)
        tasks_to_export = [t for t in e.tasks if str(t.id) in task_ids]
        return tasks_to_export

    def build(self, short_name, task_ids, filename, importer):
        """Build a zip file containing original task input."""
        tasks = self._get_tasks_to_export(short_name, task_ids)
        if not tasks:
            self._build_empty_zip(filename)
        elif importer == 'flickr':
            self._build_flickr_zip(filename, tasks)
        else:
            raise ValueError("Unknown importer type")

        # Move to completed folder and schedule removal
        build_path = os.path.join(self.build_folder, filename)
        completed_path = os.path.join(self.completed_folder, filename)
        os.rename(build_path, completed_path)
        scheduler.enqueue_in(timedelta(minutes=30), os.remove, completed_path)

    def check_zip(self, filename):
        """Check if a zip file is ready for download."""
        build_path = os.path.join(self.build_folder, filename)
        completed_path = os.path.join(self.completed_folder, filename)
        building = os.path.isfile(build_path)
        completed = os.path.isfile(completed_path)
        if not building and not completed:
            raise ValueError("Unknown filename")
        return os.path.isfile(completed_path)

    def response_zip(self, filename):
        """Return a response to download the zip file."""
        completed_path = os.path.join(self.completed_folder, filename)
        return send_file(filename_or_fp=completed_path,
                         mimetype='application/octet-stream',
                         as_attachment=True,
                         attachment_filename=filename)
