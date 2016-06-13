# -*- coding: utf8 -*-
"""View module for libcrowds-analyst."""

import json
import enki
from redis import Redis
from rq import Queue
from flask import Blueprint
from flask import render_template, request, abort, flash, current_app
from libcrowds_analyst import analysis, auth, forms


queue = Queue('libcrowds_analyst', connection=Redis())


def _get_first_result(project_id, **kwargs):
    """Return a result or abort an exception is thrown."""
    res = enki.pbclient.find_results(project_id, limit=1, all=1, **kwargs)
    if isinstance(res, dict) and 'status_code' in res:
        abort(res['status_code'])
    elif not res:
        abort(404)
    return res[0]


def _update_result(result):
    """Update a result or abort if exception thrown."""
    res = enki.pbclient._update_result(result)
    if isinstance(res, dict) and 'status_code' in res:
        abort(res.status_code)


def index():
    """Index view."""
    if request.method == 'GET':
        return render_template('index.html', title="LibCrowds Analyst")
    else:
        try:
            e = enki.Enki(current_app.config['API_KEY'],
                          current_app.config['ENDPOINT'],
                          request.json.project_short_name)
        except enki.ProjectNotFound:
            abort(404)
        analyst_func = analysis.get_analyst_func(e.project.category_id)
        queue.enqueue(func, current_app.config['API_KEY'],
                      current_app.config['ENDPOINT'],
                      request.json.project_short_name, request.json.task_id)


def analyse_empty_result(short_name):
    """View for analysing empty results."""
    try:
        print short_name
        e = enki.Enki(current_app.config['API_KEY'],
                      current_app.config['ENDPOINT'], short_name)
    except enki.ProjectNotFound:
        abort(404)

    if request.method == 'POST':
        data = dict((k, request.form.getlist(k)) for k in request.form.keys())
        data.pop('csrf_token')
        result = _get_first_result(e.project.id, id=data.pop('result_id'))
        result.info = json.dumps(data)
        _update_result(result)

    result = _get_first_result(e.project.id, info='Unanalysed')
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
    except enki.ProjectNotFound:
        abort(404)
    result = _get_first_result(e.project.id, id=result_id)
    title = "Editing result {0}".format(result.id)
    form = forms.EditResultForm(request.form)
    if request.method == 'POST' and form.validate():
        result.info = json.loads(form.info.data)
        _update_result(result)
        flash('Result updated.', 'success')
    elif request.method == 'POST' and not form.validate():
        flash('Please correct the errors.', 'danger')
    form.info.data = json.dumps(result.info)
    return render_template('edit_result.html', form=form, title=title)


def reanalyse(short_name):
    """View for triggering reanalysis of all results."""
    try:
        e = enki.Enki(current_app.config['API_KEY'],
                      current_app.config['ENDPOINT'], short_name)
    except enki.ProjectNotFound:
        abort(404)
    analyst_func = analysis.get_analyst_func(e.project.category_id)
    if not analyst_func:
        flash('No analyst configured for this category of project.', 'danger')
    elif request.method == 'POST':
        e.get_tasks()
        for t in e.tasks:
            queue.enqueue(analyst_func, current_app.config['API_KEY'],
                          current_app.config['ENDPOINT'], short_name, t.id,
                          sleep=2)
        flash('''Results for {0} completed tasks will be reanalysed.
              '''.format(len(e.tasks)), 'success')
    return render_template('reanalyse.html', title="Reanalyse results",
                           project=e.project)
