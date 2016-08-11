# -*- coding: utf8 -*-
"""View module for libcrowds-analyst."""

import os
import json
import enki
import time
import pbclient
from redis import Redis
from rq import Queue
from flask import render_template, request, abort, flash, redirect, url_for
from flask import current_app, Response, send_file
from werkzeug.utils import secure_filename
from libcrowds_analyst import analysis, auth, forms
from libcrowds_analyst.core import zip_builder


queue = Queue('libcrowds_analyst', connection=Redis())


def _get_first_result(project_id, **kwargs):
    """Return a result or abort an exception is thrown."""
    resp = pbclient.find_results(project_id, limit=1, all=1, **kwargs)
    if isinstance(resp, dict) and 'status_code' in resp:  # pragma: no cover
        abort(resp['status_code'])
    return resp[0] if resp else None


def _update_result(result):
    """Update a result or abort if an exception is thrown."""
    resp = pbclient._update_result(result)
    if isinstance(resp, dict) and 'status_code' in resp:  # pragma: no cover
        abort(resp.status_code)


def index():
    """Index view."""
    if request.method == 'GET':
        return render_template('index.html', title="LibCrowds Analyst")
    else:
        try:
            e = enki.Enki(current_app.config['API_KEY'],
                          current_app.config['ENDPOINT'],
                          request.json['project_short_name'])
        except enki.ProjectNotFound:  # pragma: no cover
            abort(404)

        analyst_func = analysis.get_analyst_func(e.project.category_id)
        if analyst_func:
            queue.enqueue(analyst_func, current_app.config['API_KEY'],
                          current_app.config['ENDPOINT'],
                          request.json['project_short_name'],
                          request.json['task_id'], timeout=600)
            return "OK"
        else:
            abort(404)


def analyse_next_empty_result(short_name):
    """View for analysing the next empty result."""
    try:
        e = enki.Enki(current_app.config['API_KEY'],
                      current_app.config['ENDPOINT'], short_name)
    except enki.ProjectNotFound:  # pragma: no cover
        abort(404)

    result = _get_first_result(e.project.id, info='Unanalysed')
    if not result:  # pragma: no cover
        flash('There are no unanlysed results to process!', 'success')
        return redirect(url_for('.index'))
    return redirect(url_for('.analyse_result', short_name=short_name,
                            result_id=result.id))


def analyse_result(short_name, result_id):
    """View for analysing a result."""
    try:
        e = enki.Enki(current_app.config['API_KEY'],
                      current_app.config['ENDPOINT'], short_name)
    except enki.ProjectNotFound:  # pragma: no cover
        abort(404)

    result = _get_first_result(e.project.id, id=result_id)
    if not result:  # pragma: no cover
        flash('Result {0} not found for {1}!'.format(result_id, short_name),
              'warning')
        return redirect(url_for('.index'))

    if request.method == 'POST':
        data = request.form.to_dict()
        data.pop('csrf_token', None)
        result.info = data
        _update_result(result)
        return redirect(url_for('.analyse_next_empty_result',
                                short_name=short_name))

    e.get_tasks(task_id=result.task_id)
    e.get_task_runs()
    task = e.tasks[0]
    task_runs = e.task_runs[task.id]
    url = 'category_{0}.html'.format(e.project.category_id)
    return render_template(url, project=e.project, result=result, task=task,
                           task_runs=task_runs, title=e.project.name)


def edit_result(short_name, result_id):
    """View for directly editing a result."""
    try:
        e = enki.Enki(current_app.config['API_KEY'],
                      current_app.config['ENDPOINT'], short_name)
    except enki.ProjectNotFound:  # pragma: no cover
        abort(404)

    result = _get_first_result(e.project.id, id=result_id)
    if not result:  # pragma: no cover
        abort(404)

    form = forms.EditResultForm(request.form)
    if request.method == 'POST' and form.validate():
        result.info = json.loads(form.info.data)
        _update_result(result)
        flash('Result updated.', 'success')
    elif request.method == 'POST' and not form.validate():  # pragma: no cover
        flash('Please correct the errors.', 'danger')
    form.info.data = json.dumps(result.info)
    title = "Editing result {0}".format(result.id)
    return render_template('edit_result.html', form=form, title=title)


def reanalyse(short_name):
    """View for triggering reanalysis of all results."""
    try:
        e = enki.Enki(current_app.config['API_KEY'],
                      current_app.config['ENDPOINT'], short_name)
    except enki.ProjectNotFound:  # pragma: no cover
        abort(404)
    form = forms.ReanalysisForm(request.form)
    analyst_func = analysis.get_analyst_func(e.project.category_id)
    if not analyst_func:
        flash('No analyst configured for this category of project.', 'danger')
    elif request.method == 'POST' and form.validate():
        e.get_tasks()
        sleep = int(request.form.get('sleep', 2))  # To handle API rate limit
        for t in e.tasks:
            queue.enqueue(analyst_func, current_app.config['API_KEY'],
                          current_app.config['ENDPOINT'], short_name, t.id,
                          sleep=sleep, timeout=3600)
        flash('''Results for {0} completed tasks will be reanalysed.
              '''.format(len(e.tasks)), 'success')
    elif request.method == 'POST' and not form.validate():  # pragma: no cover
        flash('Please correct the errors.', 'danger')
    return render_template('reanalyse.html', title="Reanalyse results",
                           project=e.project, form=form)


def prepare_zip(short_name):
    """View to prepare a zip file for download."""
    try:
        e = enki.Enki(current_app.config['API_KEY'],
                      current_app.config['ENDPOINT'], short_name)
    except enki.ProjectNotFound:  # pragma: no cover
        abort(404)

    form = forms.DownloadForm(request.form)
    if request.method == 'POST' and form.validate():
        importer = form.importer.data
        task_ids = form.task_ids.data.split()
        filename = '{0}_input_{1}.zip'.format(short_name, int(time.time()))
        filename = secure_filename(filename)
        queue.enqueue(zip_builder.build, short_name, task_ids, filename,
                      importer, timeout=3600)
        return redirect(url_for('.download_zip', filename=filename,
                                short_name=e.project.short_name))
    elif request.method == 'POST' and not form.validate():  # pragma: no cover
        flash('Please correct the errors.', 'danger')

    return render_template('prepare_zip.html', title="Download task input",
                           project=e.project, form=form)


def download_zip(short_name, filename):
    """View to download a zip file."""
    resp = zip_builder.response_zip(filename)
    if resp is not None:
        return resp
    return render_template('download_zip.html', title="Download task input",
                           short_name=short_name, filename=filename)
