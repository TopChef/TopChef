#!/usr/bin/env python
"""
Very very very basic application
"""
from .config import config
from flask import Flask, jsonify, request, url_for
from datetime import datetime
from .models import Service, UnableToFindItemError
from .decorators import check_json
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

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
    session = SESSION_FACTORY()

    new_service, errors = Service.DetailedServiceSchema().load(request.json)

    if errors:
        response = jsonify({
            'errors': {
                'message':'Invalid request, serializer produced errors.',
                'serializer_errors': errors
            }
        })
        response.status_code = 400
        return response

    session.add(new_service)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        response = jsonify({'errors': 'A job with that ID already exists'})
        response.status_code = 400
        return response

    response = jsonify(
        {'data': 'Service %s successfully registered' % new_service}
    )
    response.headers['Location'] = url_for(
        'get_service_data', service_id=new_service.id, _external=True
    )
    return response


@app.route('/services/<service_id>', methods=["GET"])
def get_service_data(service_id):
    session = SESSION_FACTORY()

    service = session.query(Service).filter_by(id=service_id).first()

    if service is None:
        response = jsonify({
            'errors': 'service with id=%s does not exist' % service_id
        })
        response.status_code = 404
        return response

    data, _ = service.DetailedServiceSchema().dump(service)

    return jsonify({'data': data})


@app.route('/services/<service_id>', methods=["PATCH"])
def heartbeat(service_id):
    session = SESSION_FACTORY()

    try:
        service = Service.from_session(session, service_id)
    except UnableToFindItemError:
        response = jsonify({
            'errors': 'The job with id %s does not exist'
        })
        response.status_code = 404
        return response

    service.heartbeat()

    if not request.json:
        response = jsonify({
            'data': 'service %s checked in at %s' % (
                service.id, datetime.utcnow().isoformat()
            )
        })
        response.status_code = 200
        return response

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