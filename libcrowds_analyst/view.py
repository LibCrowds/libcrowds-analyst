# -*- coding: utf8 -*-
"""View module for libcrowds-analyst."""

import os
import json
import time
from redis import Redis
from rq import Queue
from flask import Blueprint
from flask import render_template, request, abort, flash, redirect, url_for
from flask import current_app, Response, send_file, jsonify
from werkzeug.utils import secure_filename
from libcrowds_analyst import analysis, auth, forms
from libcrowds_analyst.core import zip_builder, pybossa_client


blueprint = Blueprint('analyse', __name__)

queue = Queue('libcrowds_analyst', connection=Redis())
MINUTE = 60


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    """Index view."""
    if request.method == 'POST':
        queue.enqueue_call(func=analysis.analyse,
                           kwargs=request.json,
                           timeout=10*MINUTE)
        return "OK"
    return render_template('index.html', title="LibCrowds Analyst")


@blueprint.route('/<short_name>/')
def analyse_next_empty_result(short_name):
    """View for analysing the next empty result."""
    try:
        project = pybossa_client.get_projects(short_name)[0]
    except IndexError: # pragma: no cover
        abort(404)

    try:
        results = pybossa_client.get_results(project.id, info='Unanalysed')
    except IndexError: # pragma: no cover
        abort(404)


    results = pybossa_client.get_results(project.id, info='Unanalysed')
    if not results:  # pragma: no cover
        flash('There are no unanlysed results to process!', 'success')
        return redirect(url_for('.index'))
    result = results[0]
    return redirect(url_for('.analyse_result', short_name=short_name,
                            result_id=result.id))


@blueprint.route('/<short_name>/<result_id>/', methods=['GET', 'POST'])
def analyse_result(short_name, result_id):
    """View for analysing a result."""
    try:
        project = pybossa_client.get_projects(short_name)[0]
    except IndexError: # pragma: no cover
        abort(404)

    try:
        results = pybossa_client.get_results(project.id, id=result_id)
    except IndexError: # pragma: no cover
        abort(404)

    if request.method == 'POST':
        data = request.form.to_dict()
        data.pop('csrf_token', None)
        result.info = data
        pybossa_client.update_result(result)
        return redirect(url_for('.analyse_next_empty_result',
                                short_name=short_name))

    task = pybossa_client.get_tasks(e.project.id, result.task_id)[0]
    task_runs = pybossa_client.get_task_runs(e.project.id, result.task_id)
    return render_template('analyse.html', project=e.project, result=result,
                           task=task, task_runs=task_runs, title=project.name)


@blueprint.route('/<short_name>/<result_id>/edit/', methods=['GET', 'POST'])
def edit_result(short_name, result_id):
    """View for directly editing a result."""
    try:
        project = pybossa_client.get_projects(short_name)[0]
    except IndexError: # pragma: no cover
        abort(404)

    try:
        result = pybossa_client.get_results(project.id, id=result_id)[0]
    except IndexError: # pragma: no cover
        abort(404)

    form = forms.EditResultForm(request.form)
    if request.method == 'POST' and form.validate():
        result.info = json.loads(form.info.data)
        pybossa_client.update_result(result)
        flash('Result updated.', 'success')
    elif request.method == 'POST' and not form.validate():  # pragma: no cover
        flash('Please correct the errors.', 'danger')
    form.info.data = json.dumps(result.info)
    title = "Editing result {0}".format(result.id)
    return render_template('edit_result.html', form=form, title=title)


@blueprint.route('/<short_name>/reanalyse/', methods=['GET', 'POST'])
def reanalyse(short_name):
    """View for triggering reanalysis of all results."""
    try:
        project = pybossa_client.get_projects(short_name)[0]
    except IndexError: # pragma: no cover
        abort(404)

    form = forms.ReanalysisForm(request.form)
    if request.method == 'POST' and form.validate():
        tasks = pybossa_client.get_tasks(project.id)
        for task in tasks:
            queue.enqueue_call(func=analysis.analyse,
                               args=(project.id, task.id),
                               timeout=10*MINUTE)
        flash('{0} tasks will be reanalysed.'.format(len(tasks)), 'success')
    elif request.method == 'POST':  # pragma: no cover
        flash('Please correct the errors.', 'danger')
    return render_template('reanalyse.html', title="Reanalyse results",
                           project=project, form=form)


@blueprint.route('/<short_name>/download/', methods=['GET', 'POST'])
def prepare_zip(short_name):
    """View to prepare a zip file for download."""
    try:
        project = pybossa_client.get_projects(short_name)[0]
    except IndexError: # pragma: no cover
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
                                short_name=project.short_name))
    elif request.method == 'POST' and not form.validate():  # pragma: no cover
        flash('Please correct the errors.', 'danger')

    return render_template('prepare_zip.html', title="Download task input",
                           project=project, form=form)


@blueprint.route('/<short_name>/download/<path:filename>/check/')
def check_zip(short_name, filename):
    """Check if a zip file is ready for download."""
    download_ready = zip_builder.check_zip(filename)
    return jsonify(download_ready=download_ready)


@blueprint.route('/<short_name>/download/<path:filename>/',
                 methods=['GET', 'POST'])
def download_zip(short_name, filename):
    """View to download a zip file."""
    try:
        project = pybossa_client.get_projects(short_name)[0]
    except IndexError: # pragma: no cover
        abort(404)

    if request.method == 'POST':
        try:
            file_ready = check_zip(filename)
        except ValueError: # pragma: no cover
            abort(404)

        if file_ready:
            return zip_builder.response_zip(filename)
    return render_template('download_zip.html', title="Download task input",
                           short_name=short_name, filename=filename)
