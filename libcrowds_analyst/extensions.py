# -*- coding: utf8 -*-
"""Extensions module for libcrowds-analyst."""

from flask.ext.z3950 import Z3950Manager

__all__ = ['z3950_manager']

z3950_manager = Z3950Manager()
