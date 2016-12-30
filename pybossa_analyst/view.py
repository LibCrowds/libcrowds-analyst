# -*- coding: utf8 -*-
"""View module for pybossa-analyst."""

import os
import time
from redis import Redis
from rq import Queue
from flask import Blueprint
from flask import render_template, request, abort, flash, redirect, url_for
from flask import current_app, send_file, Response
from werkzeug.utils import secure_filename
from pybossa_analyst import analysis, forms, zip_builder, client


blueprint = Blueprint('analyse', __name__)

queue = Queue('pybossa_analyst', connection=Redis())
MINUTE = 60


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    """Index view."""
    api_key = current_app.config['API_KEY']
    endpoint = current_app.config['ENDPOINT']
    if request.method == 'POST':
        queue.enqueue_call(func=analysis.analyse,
                           kwargs=request.json,
                           timeout=10*MINUTE)
        return "OK"
    return render_template('index.html', title="PyBossa Analyst")


@blueprint.route('/<short_name>/')
def analyse_next_empty_result(short_name):
    """View for analysing the next empty result."""
    api_key = current_app.config['API_KEY']
    endpoint = current_app.config['ENDPOINT']
    try:
        p = client.get_projects(api_key, endpoint,
                                        short_name=short_name, limit=1)[0]
    except IndexError:  # pragma: no cover
        abort(404)

    results = client.get_results(api_key, endpoint, p.id, limit=1,
                                         info='Unanalysed')
    if not results:  # pragma: no cover
        flash('There are no unanlysed results to process!', 'success')
        return redirect(url_for('.index'))
    result = results[0]
    return redirect(url_for('.analyse_result', short_name=short_name,
                            result_id=result.id))


@blueprint.route('/<short_name>/<result_id>/', methods=['GET', 'POST'])
def analyse_result(short_name, result_id):
    """View for analysing a result."""
    api_key = current_app.config['API_KEY']
    endpoint = current_app.config['ENDPOINT']
    try:
        project = client.get_projects(api_key, endpoint, short_name=short_name)[0]
    except IndexError:  # pragma: no cover
        abort(404)

    try:
        result = client.get_results(api_key, endpoint, project.id, id=int(result_id))[0]
    except (IndexError, ValueError):  # pragma: no cover
        abort(404)

    if request.method == 'POST':
        data = request.form.to_dict()
        data.pop('csrf_token', None)
        result.info = data
        client.update_result(api_key, endpoint, result)
        url = url_for('.analyse_next_empty_result', short_name=short_name)
        return redirect(url)

    task = client.get_tasks(api_key, endpoint, project.id, id=result.task_id)[0]
    taskruns = client.get_task_runs(api_key, endpoint, project.id, task_id=result.task_id)
    exclude = current_app.config['EXCLUDED_KEYS']
    keys = set(k for tr in taskruns for k in tr.info.keys()
               if k not in exclude)
    return render_template('analyse.html', project=project, result=result,
                           task=task, task_runs=taskruns,
                           title=project.name, keys=keys)


@blueprint.route('/<short_name>/reanalyse/', methods=['GET', 'POST'])
def reanalyse(short_name):
    """View for triggering reanalysis of all results."""
    api_key = current_app.config['API_KEY']
    endpoint = current_app.config['ENDPOINT']
    try:
        project = client.get_projects(api_key, endpoint, short_name=short_name)[0]
    except IndexError:  # pragma: no cover
        abort(404)

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
def prepare_zip(short_name):
    """View to prepare a zip file for download."""
    api_key = current_app.config['API_KEY']
    endpoint = current_app.config['ENDPOINT']
    try:
        project = client.get_projects(api_key, endpoint, short_name=short_name)[0]
    except IndexError:  # pragma: no cover
        abort(404)

    form = forms.DownloadForm(request.form)
    if request.method == 'POST' and form.validate():
        importer = form.importer.data
        task_ids = form.task_ids.data.split()
        tasks = client.get_tasks(api_key, endpoint, project_id=project.id)
        valid_task_ids = [str(t.id) for t in tasks]
        tasks_to_export = [t for t in tasks if str(t.id) in task_ids and
                           str(t.id) in valid_task_ids]
        invalid_ids = ", ".join([t_id for t_id in task_ids
                                 if t_id not in valid_task_ids])
        if invalid_ids:
            msg = 'The following task IDs are invalid: {0}'.format(invalid_ids)
            flash(msg, 'danger')
            return render_template('prepare_zip.html', project=project,
                                   title="Download task input", form=form)

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

    return render_template('prepare_zip.html', title="Download task input",
                           project=project, form=form)
