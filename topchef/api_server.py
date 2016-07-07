#!/usr/bin/env python
"""
Very very very basic application
"""
from .config import SOURCE_REPOSITORY, VERSION, AUTHOR, AUTHOR_EMAIL
from .database import SESSION_FACTORY
from flask import Flask, jsonify
from datetime import datetime
from .models import Service

app = Flask(__name__)


@app.route('/')
def hel1lo_world():
    return jsonify({
        'meta': {
            'source_repository': SOURCE_REPOSITORY,
            'version': VERSION,
            'author': AUTHOR,
            'email': AUTHOR_EMAIL
        }
    })


@app.route('/services', methods=["GET"])
def get_services():
    session = SESSION_FACTORY()
    service_list = session.query(Service).all()

    response = jsonify({
        'data': Service.ServiceSchema(many=True).dump(service_list)
    })

    response.status_code = 200

    return response


@app.route('/services', methods=["POST"])
def register_service():
    return jsonify({'meta': 'here is where services get registered'})


@app.route('/services/<service_id>', methods=["GET"])
def get_service_data(service_id):
    return jsonify({'data': {'service_id': service_id}})


@app.route('/services/<service_id>', methods=["PATCH"])
def heartbeat(service_id):
    return jsonify({'meta': 'service %s has heartbeated at %s' % (
        service_id, datetime.now().isoformat()
    )})


@app.route('/services/<service_id>/jobs', methods=["GET"])
def get_jobs_for_service(service_id):
    pass


@app.route('/services/<service_id>/jobs', methods=["POST"])
def request_job():
    pass


@app.route('/services/<service_id>/jobs', methods=["PATCH"])
def post_job_results():
    pass