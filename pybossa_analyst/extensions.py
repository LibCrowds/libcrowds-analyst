# -*- coding: utf8 -*-
"""Extensions module for libcrowds-analyst."""

from flask_wtf.csrf import CsrfProtect
from flask.ext.z3950 import Z3950Manager


__all__ = ['csrf', 'z3950_manager']


csrf = CsrfProtect()
z3950_manager = Z3950Manager()
