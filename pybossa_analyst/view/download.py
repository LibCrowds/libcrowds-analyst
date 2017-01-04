# -*- coding: utf8 -*-
"""Download view module for pybossa-analyst."""

import pbclient
from flask import Blueprint
from flask import render_template, request, abort, flash
from flask import current_app, Response, session
from werkzeug.utils import secure_filename
from pybossa_analyst import forms, zip_builder, client
from pybossa_analyst.login import login_required


blueprint = Blueprint('download', __name__)


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


@blueprint.route('/<short_name>', methods=['GET', 'POST'])
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