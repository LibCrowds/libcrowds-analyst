# -*- coding: utf8 -*-
"""View module for pybossa-analyst."""

import pbclient
from redis import Redis
from rq import Queue
from flask import Blueprint
from flask import render_template, request, abort, flash, redirect, url_for
from flask import current_app, session
from pybossa_analyst import analysis, forms, client, object_loader
from pybossa_analyst.login import login_required


blueprint = Blueprint('analysis', __name__)

queue = Queue('pybossa_analyst', connection=Redis())
MINUTE = 60


def _configure_pbclient():
    """Configure PyBossa client."""
    pbclient.set('api_key', session['api_key'])
    pbclient.set('endpoint', current_app.config['ENDPOINT'])


def _ensure_authorized_to_update(project):
    """Ensure that a project can be updated using the current API key."""
    resp = pbclient.update_project(project)
    if isinstance(resp, dict) and resp.get('status_code') == 401:
        abort(401)


@blueprint.route('/')
@login_required
def index():
    """Projects view."""
    _configure_pbclient()
    projects = object_loader.load(pbclient.find_project)
    if not projects:
        abort(404)

    return render_template('index.html', projects=projects)


@blueprint.route('/<short_name>')
@login_required
def analyse(short_name):
    """View for analysing the next empty result."""
    _configure_pbclient()
    projects = pbclient.find_project(short_name=short_name, limit=1)
    if not projects:
        abort(404)

    project = projects[0]
    results = pbclient.find_results(project.id, limit=1, info='Unanalysed')
    _ensure_authorized_to_update(project)
    if not results:  # pragma: no cover
        flash('There are no unanlysed results to process for this project!',
              'success')
        return redirect(url_for('.index'))

    result = results[0]
    return redirect(url_for('.analyse_result', short_name=short_name,
                            result_id=result.id))


@blueprint.route('/<short_name>/<result_id>', methods=['GET', 'POST'])
@login_required
def analyse_result(short_name, result_id):
    """View for analysing a result."""
    _configure_pbclient()
    projects = pbclient.find_project(short_name=short_name, limit=1)
    if not projects:
        abort(404)

    project = projects[0]
    results = pbclient.find_results(project.id, limit=1)
    if not results:  # pragma: no cover
        abort(404)

    result = results[0]
    task = pbclient.find_tasks(project.id, id=result.task_id)[0]
    taskruns = pbclient.find_taskruns(project.id, task_id=task.id)
    _ensure_authorized_to_update(project)

    if request.method == 'POST':
        data = request.form.to_dict()
        data.pop('csrf_token', None)
        result.info = data
        resp = pbclient.update_result(result)
        if isinstance(resp, dict) and resp.get('exception_msg'):
            err_msg = '{0}: {1}'.format(resp['exception_cls'],
                                        resp['exception_msg'])
            flash(err_msg, 'danger')
        url = url_for('.analyse', short_name=short_name)
        return redirect(url)

    excluded_keys = current_app.config['EXCLUDED_KEYS']
    keys = set(k for tr in taskruns for k in tr.info.keys()
               if k not in excluded_keys)
    return render_template('analyse.html', project=project, result=result,
                           task=task, task_runs=taskruns,
                           title=project.name, keys=keys)


@blueprint.route('/<short_name>/setup', methods=['GET', 'POST'])
@login_required
def setup(short_name):
    """View for setting up results analysis."""
    _configure_pbclient()
    projects = pbclient.find_project(short_name=short_name, limit=1)
    if not projects:
        abort(404)

    project = projects[0]
    _ensure_authorized_to_update(project)
    project = pbclient.find_project(short_name=short_name, limit=1)[0]

    form = forms.SetupForm(request.form)
    if request.method == 'POST' and form.validate():
        kwargs = {
            'api_key': session['api_key'],
            'endpoint': current_app.config['ENDPOINT'],
            'project_id': project.id,
            'project_short_name': project.short_name,
            'info_filter': form.info_filter.data,
            'match_percentage': current_app.config['MATCH_PERCENTAGE'],
            'excluded_keys': current_app.config['EXCLUDED_KEYS']
        }
        queue.enqueue_call(func=analysis.analyse_multiple,
                           kwargs=kwargs,
                           timeout=10*MINUTE)
        flash('"{0}" results will be reanalysed.'.format(_filter), 'success')
    elif request.method == 'POST':  # pragma: no cover
        flash('Please correct the errors.', 'danger')
    return render_template('setup.html', title="Setup", project=project,
                           form=form)
