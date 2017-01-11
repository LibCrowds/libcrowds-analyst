# -*- coding: utf8 -*-

from functools import wraps
from flask import session, request, redirect, url_for


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.args.get('api_key')
        if api_key:
            session["api_key"] = api_key
        if session.get('api_key') is None:
            return redirect(url_for('home.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
