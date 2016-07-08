#!/usr/bin/env python
"""
Very very very basic application
"""
from .config import config
from flask import Flask, jsonify, request
from datetime import datetime
from .models import Service
from .decorators import check_json
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
app.config.update(config.parameter_dict)

SESSION_FACTORY = sessionmaker(bind=config.database_engine)


@app.route('/')
def hello_world():
    """
    Confirms that the API is working, and returns some metadata for the API

    **Example Response**

    .. sourcecode:: http

        HTTP/1.1 / GET
        Content-Type: application/json

        {
            "meta": {
                "author": "Michal Kononenko",
                "email": "michalkononenko@gmail.com",
                "source_repository":
                    "https://www.github.com/MichalKononenko/TopChef",
                "version": "0.1dev"
            }
        }

    :statuscode 200: The request was successful
    """
    return jsonify({
        'meta': {
            'source_repository': config.SOURCE_REPOSITORY,
            'version': config.VERSION,
            'author': config.AUTHOR,
            'email': config.AUTHOR_EMAIL
        }
    })


@app.route('/services', methods=["GET"])
def get_services():
    session = SESSION_FACTORY()
    service_list = session.query(Service).all()

    response = jsonify({
        'data': Service.ServiceSchema(many=True).dump(service_list).data
    })

    response.status_code = 200

    return response


@app.route('/services', methods=["POST"])
@check_json
def register_service():
    return jsonify({'data': 'good post'})


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