# -*- coding: utf8 -*-
"""API module for libcrowds-analyst."""

import json
from rq import Queue
from redis import Redis
from flask import Blueprint, request, current_app, abort, make_response
from libcrowds_analyst import analysis


BP = Blueprint('api', __name__)
QUEUE = Queue('libcrowds_analyst', connection=Redis())
MINUTE = 60


def analyse(func):
    """Analyse a webhook."""
    payload = request.json or {}
    if request.method != 'POST' or payload.get('event') != 'task_completed':
        abort(400)
    if not request.args.get('api_key'):
        abort(400)

    payload['api_key'] = request.args.get('api_key')
    payload['endpoint'] = current_app.config['ENDPOINT']
    payload['doi'] = current_app.config['DOI']
    payload['path'] = request.path
    QUEUE.enqueue_call(func=func, kwargs=payload, timeout=10*MINUTE)
    return ok_response()


def ok_response():
    """Return a basic HTTP 200 response."""
    response = make_response(
        json.dumps({
            "message": "OK",
            "status": 200,
        })
    )
    response.mimetype = 'application/json'
    response.status_code = 200
    return response


@BP.route('convert-a-card', methods=['GET', 'POST'])
def convert_a_card():
    """Endpoint for Convert-a-Card webhooks."""
    if request.method == 'GET':
        return ok_response()
    return analyse(analysis.convert_a_card.analyse)


@BP.route('playbills/select', methods=['GET', 'POST'])
def playbills_mark():
    """Endpoint for In the Spotlight select task webhooks."""
    if request.method == 'GET':
        return ok_response()
    return analyse(analysis.playbills.analyse_selections)
