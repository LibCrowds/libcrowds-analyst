# -*- coding: utf8 -*-
"""Extensions module for libcrowds-analyst."""

from flask_wtf.csrf import CsrfProtect
from flask.ext.z3950 import Z3950Manager
from libcrowds_analyst.client import PyBossaClient
from libcrowds_analyst.zip_builder import ZipBuilder


__all__ = ['zip_builder', 'csrf', 'pybossa_client', 'z3950_manager']


zip_builder = ZipBuilder()
csrf = CsrfProtect()
pybossa_client = PyBossaClient()
z3950_manager = Z3950Manager()
