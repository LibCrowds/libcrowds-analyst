# -*- coding: utf8 -*-

import json
from rq import Queue
from redis import Redis
from flask import Blueprint, request, current_app, jsonify
from libcrowds_analyst import analysis


BP = Blueprint('api', __name__)
QUEUE = Queue('libcrowds_analyst', connection=Redis())
MINUTE = 60


def analyse(func):
    """Analyse a webhook."""
    payload = json.loads(request.json) or {}
    if payload['event'] == 'task_completed':
        payload['api_key'] = current_app.config['API_KEY']
        payload['endpoint'] = current_app.config['ENDPOINT']
        payload['doi'] = current_app.config['DOI']
        QUEUE.enqueue_call(func=func, kwargs=payload, timeout=10*MINUTE)
        return jsonify({
            "message": "Accepted",
            "status": 202
        })
    return jsonify({
        "message": "Bad Request",
        "status": 400
    })


@BP.route('/convert-a-card', methods=['POST'])
def convert_a_card():
    """Endpoint for Convert-a-Card webhooks."""
    return analyse(analysis.convert_a_card.analyse)

@BP.route('/playbills/select', methods=['POST'])
def playbills_mark():
    """Endpoint for In the Spotlight select task webhooks."""
    return analyse(analysis.playbills.analyse_selections)
