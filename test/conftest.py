# -*- coding: utf8 -*-

import os
import pytest
import base64
from libcrowds_analyst.app import create_app

os.environ['LIBCROWDS_ANALYST_SETTINGS'] = '../settings_test.py'
flask_app = create_app()


@pytest.fixture(scope='session')
def app(request):
    print flask_app
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
def analysis_kwargs():
    return {'api_key': 'k', 'endpoint': 'e', 'project_short_name':
            'sn', 'task_id': 123, 'sleep': 0}


@pytest.fixture(scope='session')
def payload():
    return dict(fired_at=u'2014-11-17 09:49:27',
                project_short_name=u'project',
                project_id=1,
                task_id=1,
                result_id=1,
                event=u'task_completed')
