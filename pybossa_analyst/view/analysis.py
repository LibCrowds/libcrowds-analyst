# -*- coding: utf8 -*-
"""View module for pybossa-analyst."""

import os
import pbclient
from redis import Redis
from rq import Queue
from flask import Blueprint
from flask import render_template, request, abort, flash, redirect, url_for
from flask import current_app, send_file, Response, session
from werkzeug.utils import secure_filename
from pybossa_analyst import analysis, forms, zip_builder, client
from pybossa_analyst.login import login_required


blueprint = Blueprint('analysis', __name__)

queue = Queue('pybossa_analyst', connection=Redis())
MINUTE = 60


def _get_projects(**kwargs):
    """Configure PyBossa client and retrieve projects"""
    pbclient.set('api_key', session['api_key'])
    pbclient.set('endpoint', current_app.config['ENDPOINT'])
    projects = pbclient.find_project(**kwargs)
    if not projects:
        if pbclient.find_project(short_name=short_name, limit=1, all=1):
            abort(403)
        else:
            abort(404)
    return projects


@blueprint.route('/')
@login_required
def index():
    """Projects view."""
    projects = _get_projects()
    api_key = session['api_key']
    return render_template('index.html', projects=projects, api_key=api_key)


@blueprint.route('/<short_name>/')
@login_required
def analyse(short_name):
    """View for analysing the next empty result."""
    project = _get_projects(short_name=short_name, limit=1)[0]
    results = pbclient.find_results(project.id, limit=1, info='Unanalysed')
    if not results:  # pragma: no cover
        flash('There are no unanlysed results to process!', 'success')
        return redirect(url_for('.index'))

    result = results[0]
    return redirect(url_for('.analyse_result', short_name=short_name,
                            result_id=result.id))


@blueprint.route('/<short_name>/<result_id>/', methods=['GET', 'POST'])
@login_required
def analyse_result(short_name, result_id):
    """View for analysing a result."""
    project = _get_projects(short_name=short_name, limit=1)[0]
    results = pbclient.find_results(project.id, limit=1)
    if not results:  # pragma: no cover
        abort(404)

    result = results[0]
    if request.method == 'POST':
        data = request.form.to_dict()
        data.pop('csrf_token', None)
        result.info = data
        pbclient.update_result(result)
        url = url_for('.analyse', short_name=short_name)
        return redirect(url)

    task = pbclient.find_tasks(project.id, id=result.task_id)[0]
    taskruns = pbclient.find_taskruns(project.id, task_id=task.id)
    excluded_keys = current_app.config['EXCLUDED_KEYS']
    keys = set(k for tr in taskruns for k in tr.info.keys()
               if k not in excluded_keys)
    return render_template('analyse.html', project=project, result=result,
                           task=task, task_runs=taskruns,
                           title=project.name, keys=keys)


@blueprint.route('/<short_name>/reanalyse/', methods=['GET', 'POST'])
@login_required
def reanalyse(short_name):
    """View for triggering reanalysis of all results."""
    project = _get_projects(short_name=short_name, limit=1)[0]
    form = forms.ReanalysisForm(request.form)
    if request.method == 'POST' and form.validate():
        _filter = form.result_filter.data
        results = client.get_all_results(api_key, endpoint, project.id)
        results = filter(lambda x: str(x.info) == _filter if _filter != 'all'
                         else True, results)
        for r in results:
            match_percentage = current_app.config['MATCH_PERCENTAGE']
            exclude = current_app.config['EXCLUDED_KEYS']
            kwargs = {'project_id': project.id,
                      'result_id': r.id,
                      'match_percentage': match_percentage,
                      'exclude': exclude}
            queue.enqueue_call(func=analysis.analyse,
                               kwargs=kwargs,
                               timeout=10*MINUTE)
        flash('''{0} results will be reanalysed.
              '''.format(len(results)), 'success')
    elif request.method == 'POST':  # pragma: no cover
        flash('Please correct the errors.', 'danger')
    return render_template('reanalyse.html', title="Reanalyse results",
                           project=project, form=form)


@blueprint.route('/<short_name>/download/', methods=['GET', 'POST'])
@login_required
def download_input(short_name):
    """View to prepare a zip file for download."""
    project = _get_projects(short_name=short_name, limit=1)[0]
    form = forms.DownloadForm(request.form)
    if request.method == 'POST' and form.validate():
        importer = form.importer.data
        task_ids = form.task_ids.data.split()
        tasks = pbclient.find_tasks(project_id=project.id)
        valid_task_ids = [str(t.id) for t in tasks]
        tasks_to_export = [t for t in tasks if str(t.id) in task_ids and
                           str(t.id) in valid_task_ids]
        invalid_ids = ", ".join([t_id for t_id in task_ids
                                 if t_id not in valid_task_ids])
        if invalid_ids:
            msg = 'The following task IDs are invalid: {0}'.format(invalid_ids)
            flash(msg, 'danger')
            return render_template('download_input.html', project=project,
                                   title="Download Input", form=form)

        ts = int(time.time())
        fn = '{0}_task_input_{1}.zip'.format(short_name, ts)
        fn = secure_filename(fn)
        content_disposition = 'attachment; filename={}'.format(fn)
        response = Response(zip_builder.generate(tasks_to_export, importer),
                            mimetype='application/zip')
        response.headers['Content-Disposition'] = content_disposition
        return response

    elif request.method == 'POST':  # pragma: no cover
        flash('Please correct the errors.', 'danger')

    return render_template('download_input.html', title="Download Input",
                           project=project, form=form)
