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


def process_payload():
    """Check that a payload is valid and complete it."""
    payload = request.json or {}
    if not request.args.get('api_key'):
        err_msg = 'api_key is key missing'
        abort(400, err_msg)

    payload['api_key'] = request.args.get('api_key')
    payload['endpoint'] = current_app.config['ENDPOINT']
    payload['doi'] = current_app.config['DOI']
    payload['path'] = request.path
    payload['throttle'] = current_app.config['THROTTLE']
    return payload


def analyse(func):
    """Analyse a webhook."""
    payload = process_payload()
    if payload.get('event') != 'task_completed':
        err_msg = 'This is not a task_completed event'
        abort(400, err_msg)

    QUEUE.enqueue_call(func=func, kwargs=payload, timeout=10*MINUTE)
    return ok_response()


def analyse_all(func):
    """Analyse all results for a project."""
    payload = process_payload()
    payload['project_short_name'] = request.args.get('project_short_name')
    QUEUE.enqueue_call(func=func, kwargs=payload)
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

    if request.args.get('project_short_name'):
        return analyse_all(analysis.convert_a_card.analyse_all)

    return analyse(analysis.convert_a_card.analyse)


@BP.route('playbills/select', methods=['GET', 'POST'])
def playbills_mark():
    """Endpoint for In the Spotlight select task webhooks."""
    if request.method == 'GET':
        return ok_response()

    if request.args.get('project_short_name'):
        return analyse_all(analysis.playbills.analyse_all_selections)

    return analyse(analysis.playbills.analyse_selections)
