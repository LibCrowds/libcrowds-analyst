# -*- coding: utf8 -*-

from rq import Queue
from redis import Redis
from flask import Blueprint
from flask import render_template, request, session, flash, redirect, url_for
from flask import current_app, send_file, Response
from pybossa_analyst import forms


blueprint = Blueprint('home', __name__)
queue = Queue('pybossa_analyst', connection=Redis())
MINUTE = 60


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    """Index view for receiving webhooks."""
    payload = request.json or {}
    if request.method == 'POST' and payload['event'] == 'task_completed':
        payload['api_key'] = current_app.config['API_KEY']
        payload['endpoint'] = current_app.config['ENDPOINT']
        payload['match_percentage'] = current_app.config['MATCH_PERCENTAGE']
        payload['excluded_keys'] = current_app.config['EXCLUDED_KEYS']
        queue.enqueue_call(func=analysis.analyse,
                           kwargs=payload,
                           timeout=10*MINUTE)
        return "OK"
    return redirect(url_for('analysis.index'))


@blueprint.route('login', methods=['GET', 'POST'])
def login():
    """Login view."""
    form = forms.LoginForm(request.form)
    if request.method == "POST" and form.validate():
        session['api_key'] = form.api_key.data
        return redirect(url_for('analysis.index'))
    elif request.method == "POST":
        flash('Please correct the errors.', 'danger')
    return render_template('login.html', title="Sign in", form=form,
                           next=request.args.get('next'))


@blueprint.route('logout')
def logout():
    """Logout view."""
    session.pop('api_key', None)
    flash('You are now logged out.', 'success')
    return redirect(url_for('.login'))
