# -*- coding: utf8 -*-
"""Zip builder module for pybossa-analyst."""

import os
import time
import requests
import zipfile
import zipstream
from flask import send_file


ONE_HOUR = 60*60


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

    def _generate_flickr_zip(self, tasks):
        """Build an image set containing images downloaded from Flickr."""
        z = zipstream.ZipFile()
        for t in tasks:
            if not t.info.get('url') or not t.info.get('title'):
                raise ValueError('Invalid Flickr task')
            url = t.info['url']
            title = t.info['title']
            z.write_iter(title, requests.get(url).content)
        for chunk in z:
            yield chunk

    def generate(self, tasks, importer):
        """Generate a zip file containing original task input."""
        if importer == 'flickr':
            return self._generate_flickr_zip(tasks)
        else:
            raise ValueError("Unknown importer type")



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

    def remove_old_zips(self):
        """Remove zip files created over an hour ago."""
        now = time.time()
        for f in os.listdir(self.completed_folder):
            path = os.path.join(self.completed_folder, f)
            f_created = os.path.getmtime(path)
            if (now - f_created) // ONE_HOUR >= 1:
                os.remove(path)
