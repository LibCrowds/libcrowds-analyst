# -*- coding: utf8 -*-
"""Extensions module for libcrowds-analyst."""

from flask_wtf.csrf import CsrfProtect
from libcrowds_analyst.client import PyBossaClient
from libcrowds_analyst.zip_builder import ZipBuilder


__all__ = ['zip_builder', 'csrf', 'pybossa_client']


zip_builder = ZipBuilder()
csrf = CsrfProtect()
pybossa_client = PyBossaClient()
