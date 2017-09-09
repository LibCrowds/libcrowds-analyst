# -*- coding: utf8 -*-
"""Zip builder module for libcrowds-analyst."""

import requests
import zipstream


def _download(url):
    """Download data from a URL."""
    yield requests.get(url).content


def _generate_zip(tasks, fn_key, url_key):
    """Generate a zip containing downloaded task data."""
    z = zipstream.ZipFile(compression=zipstream.ZIP_DEFLATED)
    for t in tasks:
        fn = t.info[fn_key]
        url = t.info[url_key]
        z.write_iter(fn, _download(url))
    for chunk in z:
        yield chunk


def generate(tasks, importer):
    """Generate a zip file containing original task input."""
    if importer == 'flickr':
        for t in tasks:
            t.info["title"] = "{0}.{1}".format(t.info["title"], "jpg")
        return _generate_zip(tasks, "title", "url")
    else:
        raise ValueError("Unknown importer type")
