# -*- coding: utf8 -*-

from rq import Queue
from redis import Redis
from flask import Blueprint
from flask import request
from flask import current_app
from pybossa_analyst import analysis


BP = Blueprint('api', __name__)
QUEUE = Queue('libcrowds_analyst', connection=Redis())
MINUTE = 60


def analyse(func):
    """Analyse a webhook."""
    payload = request.json or {}
    if payload['event'] == 'task_completed':
        payload['api_key'] = current_app.config['API_KEY']
        payload['endpoint'] = current_app.config['ENDPOINT']
        QUEUE.enqueue_call(func=func, kwargs=payload, timeout=10*MINUTE)
        return "OK"


@BP.route('/convert-a-card', methods=['POST'])
def convert_a_card():
    """Endpoint for Convert-a-Card webhooks."""
    return analyse(analysis.analyse)
