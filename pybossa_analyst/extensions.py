# -*- coding: utf8 -*-
"""Extensions module for pybossa-analyst."""

from flask_wtf.csrf import CsrfProtect
from flask.ext.z3950 import Z3950Manager
from pybossa_analyst.client import PyBossaClient


__all__ = ['csrf', 'pybossa_client', 'z3950_manager']


csrf = CsrfProtect()
pybossa_client = PyBossaClient()
z3950_manager = Z3950Manager()
