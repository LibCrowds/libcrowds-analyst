# -*- coding: utf8 -*-
"""Download view module for pybossa-analyst."""

import time
import pbclient
from flask import Blueprint
from flask import render_template, request, abort, flash
from flask import current_app, Response, session
from werkzeug.utils import secure_filename
from pybossa_analyst import zip_builder, object_loader
from pybossa_analyst.forms import DownloadForm
from pybossa_analyst.login import login_required


blueprint = Blueprint('download', __name__)


@blueprint.route('/<short_name>', methods=['GET', 'POST'])
@login_required
def download_input(short_name):
    """View to prepare a zip file for download."""
    pbclient.set('api_key', session['api_key'])
    pbclient.set('endpoint', current_app.config['ENDPOINT'])
    projects = pbclient.find_project(short_name=short_name, limit=1, all=1)
    if not projects:  # pragma: no cover
        abort(404)

    project = projects[0]
    form = DownloadForm(request.form)
    if request.method == 'POST' and form.validate():
        importer = form.importer.data
        task_ids = form.task_ids.data.split()
        tasks = object_loader.load(pbclient.find_tasks, project_id=project.id)
        valid_ids = [str(t.id) for t in tasks]
        tasks_to_export = [t for t in tasks if str(t.id) in task_ids and
                           str(t.id) in valid_ids]
        invalid_ids = [t_id for t_id in task_ids if t_id not in valid_ids]
        if invalid_ids:
            err_msg = 'Invalid task IDs: {0}'.format(', '.join(invalid_ids))
            flash(err_msg, 'danger')
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