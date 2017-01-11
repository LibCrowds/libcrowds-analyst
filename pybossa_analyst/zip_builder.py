# -*- coding: utf8 -*-
"""Zip builder module for pybossa-analyst."""

import requests
import zipstream


def _stream_content(url):
    """Stream response data."""
    r = requests.get(url, stream=True)
    for chunk in r.iter_content():
        yield chunk


def _generate_zip(tasks, fn_key, url_key):
    """Generate a zip containing downloaded task data."""
    z = zipstream.ZipFile(compression=zipstream.ZIP_DEFLATED)
    for t in tasks:
        fn = t.info[fn_key]
        url = t.info[url_key]
        z.write_iter(fn, _stream_content(url))
    for chunk in z:
        yield chunk


def generate(tasks, importer):
    """Generate a zip file containing original task input."""
    z = zipstream.ZipFile(compression=zipstream.ZIP_DEFLATED)
    if importer == 'flickr':
        return _generate_zip("title", "url")
    else:
        raise ValueError("Unknown importer type")
