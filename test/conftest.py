# -*- coding: utf8 -*-

import os
import json
import enki
import copy
import pytest
import base64
from libcrowds_analyst.core import create_app

os.environ['LIBCROWDS_ANALYST_SETTINGS'] = '../settings_test.py'
flask_app = create_app()


@pytest.fixture(scope='session')
def app(request):
    ctx = flask_app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()
    request.addfinalizer(teardown)
    return flask_app


@pytest.fixture(scope='session')
def test_client(app):
    return app.test_client()


@pytest.fixture
def auth_headers():
    user = base64.b64encode(b"admin:secret")
    return {"Authorization": "Basic {user}".format(user=user)}


@pytest.fixture
def project():
    return enki.pbclient.DomainObject({'short_name': 'short_name', 'id': 1})


@pytest.fixture
def task(project):
    return enki.pbclient.DomainObject({
        "id": 1,
        "project_id": project.id,
        "info": {"key": "value"},
        "n_answers": 10,
        "quorum": 0,
        "calibration": 0,
        "state": "completed",
        "priority_0": 0.0
    })


@pytest.fixture
def result(task):
    return enki.pbclient.DomainObject({
        "id": 1,
        "task_id": task.id,
        "info": {"n": 42}
    })


@pytest.fixture
def create_task_run(task, project):
    def create(id, info):
        return enki.pbclient.DomainObject({
            "id": id,
            "project_id": project.id,
            "info": info,
            "task_id": task.id,
        })
    return create


@pytest.fixture
def create_task_run_df(task, create_task_run):
    def create(task_run_info):
        tasks = [task]
        task_runs = []
        tr_data = {task.id: task_runs}

        # Create task runs using task run fixture as template
        for i in range(len(task_run_info)):
            tr = create_task_run(i, task_run_info[i])
            task_runs.append(tr)
        df = enki.dataframer.create_task_run_data_frames(tasks, tr_data)
        return df[task.id]
    return create


@pytest.fixture
def payload(project, task, result):
    load = dict(fired_at=u'2014-11-17 09:49:27',
                project_short_name=project.short_name,
                project_id=project.id,
                task_id=task.id,
                result_id=result.id,
                event=u'task_completed')
    return json.dumps(load)