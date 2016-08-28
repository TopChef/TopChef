"""
Contains the routing map for the API, along with function definitions for the
endpoints
"""
import logging
import jsonschema
from uuid import uuid1, UUID
from marshmallow_jsonschema import JSONSchema
from .config import config
from flask import Flask, jsonify, request, url_for, redirect
from datetime import datetime
from .models import Service, Job, UnableToFindItemError, FILE_MANAGER
from .decorators import check_json
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config.update(config.parameter_dict)

SESSION_FACTORY = sessionmaker(bind=config.database_engine)
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


@app.route('/')
def hello_world():
    """
    Returns metadata relating to the API, the maintainer, and the version
    
    **Example Response**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            'meta':
            {
                "author": "Michal Kononenko"
            }
        }

    :statuscode 200: The request completed successfully

    :return: A Flask response with required metadata
    :rtype: Flask.Response
    """
    return jsonify({
        'meta': {
           'source_repository': config.SOURCE_REPOSITORY,
            'version': config.VERSION,
            'author': config.AUTHOR,
            'email': config.AUTHOR_EMAIL
        },
        'data': {}
    })

@app.route('/echo', methods=["POST"])
@check_json
def repeat_json():
    response = jsonify({'data': request.json})
    response.status_code = 200
    return response

@app.route('/validator', methods=["POST"])
@check_json
def validate_json():
    """
    With a provided JSON object and JSON Schema, use the validator
    in this API to check whether the JSON object matches the JSON
    schema

    **Example Request**

    .. sourcecode:: http
        
        POST /validator HTTP/1.1
        Host: example.com
        Accept: application/json, text/javascript
        
        {
            'object':
            {
                'value': 1
            },
            'schema':
            {
                "type": "object",
                "properties": 
                {
                    "value": 
                    {
                        "type": "integer"
                    }
                }
            }
        }

    **Example Response**

    .. sourcecode:: http
        
        HTTP/1.1 200 OK

    :statuscode 200: The object matched the given JSON schema
    :statuscode 400: The object did not match the JSON schema. Errors are
        returned in the ``errors`` key in the data

    """
    schema = request.json['schema']
    _ , errors = JSONSchema().load(request.json['schema'])
    
    if errors:
        response = jsonify({'errors': errors})
        response.status_code = 400
        return response

    object_to_validate = request.json['object']
   
    try:
        jsonschema.validate(object_to_validate, schema)
    except jsonschema.ValidationError as error:
        error_message = {
            'message': error.message,
            'context': error.context
        }
        response = jsonify({'errors': error_message})
        response.status_code = 400
        return response
    else: 
        response = jsonify({'data': {}})
        response.status_code = 200
        return response


@app.route('/services', methods=["GET"])
def get_services():
    """
    Returns a list of services that have been registered with this API

    **Example Response**

    .. sourcecode:: http

        HTTP/1.1 /services GET
        Content-Type: application/json

        {
            "data": [{
                "has_timed_out": true,
                "id": "d1b691f6-68c9-11e6-93a9-3c970e7271f5",
                "name": "TestService",
                "url": "http://localhost:5000/services/d1b691f6-68c9-11e6-93a9-3c970e7271f5"
            }],
            "meta": {
                "POST_schema": {
                    "$ref": "http://localhost:5000/services#/meta/POST_schema"
                }
            }
        }

    The value POST_schema describes the JSON Schema that must be satisfied
    in order to allow registration of a service.

    :statuscode 200: Services were returned succesfully
    """
    session = SESSION_FACTORY()
    service_list = session.query(Service).all()

    response = jsonify({
        'data': Service.ServiceSchema(many=True).dump(service_list).data,
        'meta': {
            "POST_schema":
                JSONSchema().dump(Service.DetailedServiceSchema()).data
        }
    })

    response.status_code = 200

    return response


@app.route('/services', methods=["POST"])
@check_json
def register_service():
    """
    Register a new service with the API

    **Example Request**

    .. sourcecode:: http

        HTTP/1.1 /services POST
        Content-Type: application/json

        {
            "name": "TestService",
            "description": "Some test data",
            "job_registration_schema": {
            "type": "object",
            "properties": {
                "value": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10
                    }
                }
            }
        }

    **Example Response**

    .. sourcecode:: http

        HTTP/1.1 201 CREATED
        Content-Type:application/json
        Location: http://localhost:5000/services/8643f414-6959-11e6-b090-843a\
                4b768af4 

        {
          "data": "Service Service(id=178469385849810706677982978614863760116\
                  , name=TestService, description=Some test data, \
                  schema={'type': 'object', 'properties': {'value': \
                  {'type': 'integer', 'minimum': 1, 'maximum': 10}}}) \
                  successfully registered"
        }

    :statuscode 201: The service was created successfully
    :statuscode 400: The service could not be registered due to a bad request
    """
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
    except IntegrityError as error:
        case_number = uuid1()
        LOG.error('case_number: %s; message: %s', case_number, error)
        session.rollback()
        response = jsonify({
            'errors': {
                'message': 'Integrity error thrown when trying to commit',
                'case_number': case_number
            }
        })
        response.status_code = 400
        return response

    response = jsonify(
        {
            'data': {
                'message': 'Service %s successfully registered' % new_service,
                'service_details': 
                    new_service.DetailedServiceSchema().dump(new_service).data
            }
        }
    )
    response.headers['Location'] = url_for(
        'get_service_data', service_id=new_service.id, _external=True
    )
    response.status_code = 201
    return response


@app.route('/services/<service_id>', methods=["GET"])
def get_service_data(service_id):
    try:
        service_id = UUID(service_id)
    except ValueError:
        response = jsonify({'errors': "The service id %s is not a UUID. "
        "No service with this id exists" % service_id})
        response.status_code = 404
        return response
    
    session = SESSION_FACTORY()

    service = session.query(Service).filter_by(id=service_id).first()
    service.file_manager = FILE_MANAGER

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
        service_id = UUID(service_id)
    except ValueError:
        response = jsonify({
            'errors': 'Unable to parse id %s as a UUID' % (service_id)
        })
        response.status_code = 404
        return response

    try:
        service = Service.from_session(session, service_id)
    except UnableToFindItemError:
        response = jsonify({
            'errors': 'The job with id %s does not exist'
        })
        response.status_code = 404
        return response

    service.heartbeat()

    session.add(service)
    session.commit()

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
    session = SESSION_FACTORY()
    service = session.query(Service).filter_by(id=service_id).first()

    if not service:
        response = jsonify({
            'errors': 'A service with id %s was not found' % service_id
        })
        response.status_code = 404
        return response

    service.file_manager = FILE_MANAGER

    response = jsonify({
        'data': Job.JobSchema(many=True).dump(service.jobs).data
    })

    response.status_code = 200
    return response


@app.route('/services/<service_id>/jobs', methods=["POST"])
@check_json
def request_job(service_id):
    """
    Request a job from a particular service to run on the system

    **Example Response**
    
    .. sourcecode:: http
      
        {
          "data": {
            "message": "Service Service(id=312789728539838762115097976762654683637, name=TestService, description=Some test data, schema={'type': 'object', 'properties': {u'value': {u'minimum': 1, u'type': u'integer', u'maximum': 10}}}) successfully registered",
            "service_details": [
              {
                "description": "Some test data",
                "has_timed_out": false,
                "id": "eb511c46-6577-11e6-a72a-3c970e7271f5",
                "job_registration_schema": {
                  "properties": {
                    "value": {
                      "maximum": 10,
                      "minimum": 1,
                      "type": "integer"
                    }
                  },
                  "type": "object"
                },
                "name": "TestService",
                "url": "http://localhost:5000/services/eb511c46-6577-11e6-a72a-3c970e7271f5"
              },
            ]
          }
        }

    :statuscode 201: The job was created successfully
    :statuscode 400: An error occurred with the job created
    :statuscode 404: The service for which the job is to be requested 
        was not found
    """
    
    session = SESSION_FACTORY()
    service = session.query(Service).filter_by(id=service_id).first()

    if not service:
        response = jsonify({
            'errors': 'A service with id %s was not found' % service_id
        })
        response.status_code = 404
        return response

    service.file_manager = FILE_MANAGER

    job_data, errors = Job.JobSchema().load(request.json)

    if errors:
        response = jsonify({
            'errors': 'Schema loading produced errors %s' % errors
        })
        response.status_code = 400
        return response

    job = Job(service, job_data['parameters'])

    session.add(job)

    try:
        session.commit()
    except IntegrityError as error:
        case_number = uuid1()
        LOG.error('case_number: %s, message: %s' % case_number, error)
        session.rollback()

        response = jsonify({
            'errors': {
                'case_number': case_number,
                'message': 'Integrity error thrown when attempting commit'
            }
        })
        response.status_code = 400
        return response

    response = jsonify({
        'data': {
            'message': 'Job %s successfully created' % job.__repr__(),
            'job_details': job.JobSchema().dump(job).data
        }
    })

    response.headers['Location'] = url_for(
        'get_job', job_id=job.id, _external=True
    )
    response.status_code = 201
    return response


@app.route('/jobs', methods=["GET"])
def get_jobs():
    session = SESSION_FACTORY()
    job_list = session.query(Job).all()

    for job in job_list:
        job.file_manager = FILE_MANAGER

    response = jsonify({'data': Job.JobSchema(many=True).dump(job_list).data})
    response.status_code = 200

    return response


@app.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    try:
        job_id = UUID(job_id)
    except ValueError:
        response = jsonify({
            'errors': 'Could not parse job_id=%s as a UUID' % job_id
        })
        response.status_code = 404
        return response

    session = SESSION_FACTORY()
    job = session.query(Job).filter_by(id=job_id).first()

    if not job:
        response = jsonify({
            'errors': 'A job with id %s was not found' % job_id
        })
        response.status_code = 404
        return response

    job.file_manager = FILE_MANAGER

    response = jsonify({'data': job.DetailedJobSchema().dump(job).data})
    response.status_code = 200
    return response

@app.route('/jobs/<job_id>/next', methods=['GET'])
def get_next_job(job_id):
    """
    If a job has a next job, return a redirect to that job.
    Otherwise, return a 204 response
    """
    session = SESSION_FACTORY()
    try:
        job_id = UUID(job_id)
    except ValueError:
        response = jsonify({
            'errors': 'id %s could not be coerced to a UUID' % job_id
        })
        response.status_code = 404
        return response

    current_job = session.query(Job).filter_by(id=job_id).first()

    next_job = current_job.next(session)
    
    if next_job is None:
        return ('', 204)

    redirection_url = url_for('get_job', job_id=next_job.id, _external=True)

    response = jsonify(
        {
            'data': 
            {
                'message': 'Redirecting to URL %s' % redirection_url,
                'target': redirection_url
            }
        }
    )
    response.status_code = 302
    response.headers['Location'] = redirection_url

    redirect(redirection_url, code=302)

    return response
       

@app.route('/services/<service_id>/jobs/<job_id>', methods=["PUT"])
@check_json
def update_job_results(service_id, job_id):
    session = SESSION_FACTORY()

    service=session.query(Service).filter_by(id=service_id).first()
    if not service:
        response = jsonify({
            'errors': 'A service with id %s was not found' % service_id
        })
        response.status_code = 404
        return response

    job = session.query(Job).filter_by(id=job_id).first()
    if not job:
        response = jsonify({
            'errors': 'A job with id %s was not found' % job_id
        })
        response.status_code = 404
        return response

    new_job_data, errors = Job.DetailedJobSchema().load(request.json)

    job.update(new_job_data)

    session.add(job)

    try:
        session.commit()
    except IntegrityError as error:
        case_number = uuid1()
        LOG.error('case_number: %s, message: %s' % case_number, error)
        session.rollback()

        response = jsonify({
            'errors': {
                'case_number': case_number,
                'message': 'Integrity error thrown when attempting commit'
            }
        })
        response.status_code = 400
        return response

    response = jsonify({
        'data': {
            'message': 'Job %s updated successfully' % job,
            'job_schema': job.DetailedJobSchema().dump(job).data()
            }
        }
    )
    response.status_code = 200
    response.headers['Location'] = url_for(
        '.get_job', job_id=job.id, _external=True
    )
    return response

