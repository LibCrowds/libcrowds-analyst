# -*- coding: utf8 -*-
"""Zip builder module for pybossa-analyst."""

import requests
import zipstream


def _generate_flickr_zip(tasks):
    """Generate an image set containing images downloaded from Flickr."""
    z = zipstream.ZipFile(compression=zipstream.ZIP_DEFLATED)
    for t in tasks:
        if not t.info.get('url') or not t.info.get('title'):
            raise ValueError('Invalid Flickr task')
        url = t.info['url']
        title = t.info['title']
        img = requests.get(url).content
        z.write_iter(title, img)
        for chunk in z:
            yield chunk


def generate(tasks, importer):
    """Generate a zip file containing original task input."""
    if importer == 'flickr':
        return _generate_flickr_zip(tasks)
    else:
        raise ValueError("Unknown importer type")
