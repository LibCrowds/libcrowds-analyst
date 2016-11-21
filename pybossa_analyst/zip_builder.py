# -*- coding: utf8 -*-
"""Zip builder module for pybossa-analyst."""

import os
import requests
import zipfile
from redis import Redis
from rq_scheduler import Scheduler
from flask import send_file


scheduler = Scheduler('pybossa_analyst', connection=Redis())


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
            except OSError:  # pragma: no cover
                if not os.path.isdir(path):
                    raise
        mkdir_if_not_exists(self.build_folder)
        mkdir_if_not_exists(self.completed_folder)

    def _build_flickr_zip(self, tasks, zip_path):
        """Build an image set containing images downloaded from Flickr."""
        zip_dir = os.path.splitext(os.path.basename(zip_path))[0]
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
            for t in tasks:
                if not t.info.get('url') or not t.info.get('title'):
                    raise ValueError('Invalid Flickr task')
                url = t.info['url']
                img_path = os.path.join(zip_dir, t.info['title'] + ".jpg")
                img = requests.get(url).content
                archive.writestr(img_path, img)

    def build(self, tasks, filename, importer):
        """Build a zip file containing original task input."""
        zip_path = os.path.join(self.build_folder, filename)
        if importer == 'flickr':
            self._build_flickr_zip(tasks, zip_path)
        else:
            raise ValueError("Unknown importer type")

        # Move to completed folder and schedule removal
        build_path = os.path.join(self.build_folder, filename)
        completed_path = os.path.join(self.completed_folder, filename)
        os.rename(build_path, completed_path)

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
