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
from .method_override_middleware import HTTPMethodOverrideMiddleware
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc

app = Flask(__name__)
app.config.update(config.parameter_dict)
app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)

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
            "data": {},
            "meta":
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
    response = jsonify({'data': request.get_json()})
    response.status_code = 200
    return response


@app.route('/validator', methods=["GET"])
def get_validator_data():
    """
    Returns information for API consumers describing how to use the JSON
    schema validator

    **Example Response**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            'data': {},
            'meta': {
                'validation_schema': {
                    '$schema': 'http://json-schema.org/draft-04/schema#',
                    'type': 'object',
                    'properties': {
                        'object': {
                            'type': 'object'
                        },
                        'schema': {
                            'type': 'object'
                        }
                    },
                    'required': ['object', 'schema']
                }
            }
        }

    :statuscode 200: The request completed successfully

    :return: A Flask response containing the required data
    :rtype: Flask.Response

    """
    response = jsonify({
        'data': {},
        'meta': {
            'validation_schema': {
                '$schema': 'http://json-schema.org/draft-04/schema#',
                'type': 'object',
                'properties': {
                    'object': {
                        'type': 'object'
                    },
                    'schema': {
                        'type': 'object'
                    }
                },
                'required': ['object', 'schema']
            }
        }
    })
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
    schema = request.get_json()['schema']
    _ , errors = JSONSchema().load(request.get_json()['schema'])
    
    if errors:
        response = jsonify({'errors': errors})
        response.status_code = 400
        return response

    object_to_validate = request.get_json()['object']
   
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

        GET /services HTTP/1.1
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

        POST /services HTTP/1.1
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

    new_service, errors = Service.DetailedServiceSchema().load(request.get_json())

    if errors:
        response = jsonify({
            'errors': {
                'message': 'Invalid request, serializer produced errors.',
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
    """
    Retrieve data for a particular service

    **Example Response**

    .. sourcecode:: http

        HTTP/1.1 200 OK
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

    :statuscode 200: The request completed successfully
    :statuscode 404: A service with that UUID was not found

    :param str service_id: The UUID representing the service for which data
    is to be retrieved
    :return: A response containing the service data
    :rtype: Flask.Response
    """
    try:
        service_id = UUID(service_id)
    except ValueError:
        response = jsonify({'errors': "The service id %s is not a UUID. "
        "No service with this id exists" % service_id})
        response.status_code = 404
        return response
    
    session = SESSION_FACTORY()

    service = session.query(Service).filter_by(id=service_id).first()

    if service is None:
        response = jsonify({
            'errors': 'service with id=%s does not exist' % service_id
        })
        response.status_code = 404
        return response
    service.file_manager = FILE_MANAGER

    data, _ = service.DetailedServiceSchema().dump(service)

    return jsonify({'data': data})


@app.route('/services/<service_id>', methods=["PATCH"])
def heartbeat(service_id):
    """
    If JSON is sent to this endpoint, update the service data with the new
    schema. If no JSON is sent, the polling interval is reset. If the time
    runs out before one of these requests is sent, then it will be assumed
    that the service is not accessible. The schema for editing a service is
    the same as the one for creating a service.

    **Example Response With No JSON sent**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "data": "service 4487a994-415d-11e7-a880-843a4b768af4 checked in
                at 2017-05-25T15:30:07.729941"
        }

    ** Example Response With JSON**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "meta":
                "service 4487a994-415d-11e7-a880-843a4b768af4 has
                heartbeated at 2017-05-25T11:34:29.302623"
        }

    :statuscode 200: The request completed successfully
    :statuscode 400: The request JSON was formatted incorrectly
    :statuscode 404: A service with that UUID could not be found.

    :param str service_id: The service ID
    :return: The appropriate response
    :rtype: Flask.Response
    """
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

    if not request.get_json():
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
    """
    Returns a list of all the jobs that have been registered with a
    particular service

    **Example Response**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
          "data": [
            {
              "date_submitted": "2017-06-09T17:23:32.656168+00:00",
              "id": "5caedeca-4d38-11e7-a611-3c970e7271f5",
              "status": "REGISTERED"
            }
          ]
        }

    :statuscode 200: The request completed successfully
    :statuscode 404: A service with the desired id could not be found


    :param str service_id: The ID of the service for which Jjobs are to be
        retrieved
    :return: The appropriate flask response
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

    **Example Request**

    Let's say that we are working with a service that takes in an integer
    from 1 to 10, and does something to it. In that case, we must adhere to
    the schema that we have defined for this service, placing all the
    parameters into a "parameters" field.

    .. sourcecode:: http

        POST /services/514d373a-e9af-41cf-a7d0-efe6a675f820/jobs HTTP/1.1
        Content-Type: application/json

        {
            "parameters": {
                "value": 1
            }
        }

    **Example Response**
    
    .. sourcecode:: http

        HTTP/1.1 201 CREATED
        Content-Type: application/json
        Location: http://localhost:5000/jobs/d222b8fc-4162-11e7-a880-843a4b768af4
      
       {
          "data": {
            "job_details": {
              "date_submitted": "2017-05-25T15:57:14.618164+00:00",
              "id": "d222b8fc-4162-11e7-a880-843a4b768af4",
              "parameters": {
                "value": 1
              },
              "status": "REGISTERED"
            },
            "message": "Job Job(parent_service=Service(id=91091903262496590623915637806013516532, name=TestService, description=Some test data, schema={'type': 'object', 'properties': {'value': {'type': 'integer', 'minimum': 1, 'maximum': 10}}}), job_parameters={'value': 1}, attached_session=<sqlalchemy.orm.session.Session object at 0x7f65b13ccb00>, file_manager=SchemaDirectoryOrganizer(schema_directory_path=/home/mkononen/.virtualenvs/TopChef/lib/python3.5/site-packages/topchef/schemas)) successfully created"
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

    job_data, errors = Job.JobSchema().load(request.get_json())

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


@app.route('/services/<service_id>/jobs/next', methods=["GET"])
def get_next_job_for_service(service_id):
    """
    If the service has a next job, returns this job with a 200 response. If
    not, returns a 204 response.

    **Example Response - Job Found**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "date_submitted": "2017-05-25T15:57:14.618164+00:00",
            "id": "d222b8fc-4162-11e7-a880-843a4b768af4",
            "parameters": {
            "value": 1
            },
            "status": "REGISTERED"
        }

    :statuscode 200: The next job exists
    :statuscode 204: The next job does not exist

    :param str service_id: The ID of the service for which the next job is
        to be obtained
    :return: The appropriate Flask response
    :rtype: Flask.Response
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
    next_job = session.query(Job).filter(
        Job.parent_service == service
    ).filter(
        Job.status == "REGISTERED"
    ).order_by(
        desc(Job.date_submitted)
    ).first()

    if next_job is None:
        return ('', 204)
    else:
        next_job.file_manager = FILE_MANAGER
        job_data = Job.JobSchema().dump(next_job).data
        response = jsonify({'data': job_data})
        response.status_code = 200
        return response


@app.route('/services/<service_id>/queue', methods=["GET"])
def get_service_queue(service_id):
    """
    Returns the list of jobs that are queued for this service to process.
    The job list is in the order that the jobs will be processed.

    **Example Response**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
          "data": [
            {
              "date_submitted": "2017-05-25T15:57:14.618164+00:00",
              "id": "d222b8fc-4162-11e7-a880-843a4b768af4",
              "status": "REGISTERED"
            }
          ]
        }

    :statuscode 200: The request completed successfully
    :statuscode 404: A service with that particular service ID was not found

    :param service_id: The UUID of the service for which this job is to be
        created
    :return: The appropriate Flask response
    """
    session = SESSION_FACTORY()

    try:
        service_id = UUID(service_id)
    except ValueError:
        response = jsonify({
            'errors': 'Could not parse job_id=%s as a UUID' % service_id
        })
        response.status_code = 404
        return response

    service = session.query(Service).filter_by(id=service_id).first()

    if not service:
        response = jsonify({
            'errors': 'Could not find service with id %s' % str(service_id)
        })
        response.status_code = 404
        return response

    job_list = [job for job in service.jobs if job.status == "REGISTERED"]

    job_data = Job.JobSchema(many=True).dump(job_list).data

    response = jsonify({'data': job_data})

    if len(job_list) == 0:
        response.status_code = 204
    else:
        response.status_code = 200

    return response
    

@app.route('/jobs', methods=["GET"])
def get_jobs():
    """
    Responds with a list of all jobs that are queued with this server

    **Example Response**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
          "data": [
            {
              "date_submitted": "2017-05-25T15:57:14.618164+00:00",
              "id": "d222b8fc-4162-11e7-a880-843a4b768af4",
              "status": "REGISTERED"
            }
          ]
        }

    :statuscode 200: The request was completed successfully

    :return: A flask response with the jobs listed
    :rtype: Flask.Response
    """
    session = SESSION_FACTORY()
    job_list = session.query(Job).all()

    for job in job_list:
        job.file_manager = FILE_MANAGER

    response = jsonify({'data': Job.JobSchema(many=True).dump(job_list).data})
    response.status_code = 200

    return response


@app.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """
    Returns data for a particular job.

    **Example Response**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "data": {
                "date_submitted": "2017-05-25T15:57:14.618164+00:00",
                "id": "d222b8fc-4162-11e7-a880-843a4b768af4",
                "parameters": {
                "value": 1
            },
            "result": {},
            "status": "REGISTERED"
            }
        }

    :statuscode 200: The request successfully completed
    :statuscode 404: A job with that ID could not be found

    :param str job_id: The ID of a particular job to use
    :return: A flask response showing the details for a particular job
    :rtype: Flask.Response
    """
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


@app.route('/jobs/<job_id>', methods=["PUT"])
@check_json
def put_job_details(job_id):
    """
    Update the job with new data

   **Example Request**

    .. sourcecode:: http

        PUT /jobs/514d373a-e9af-41cf-a7d0-efe6a675f820 HTTP/1.1
        Content-Type: application/json

        {
            "date_submitted": "2017-05-25T17:04:37.212708+00:00",
            "id": "3bb5b090-416c-11e7-a880-843a4b768af4",
            "parameters": {
              "value": 1
            },
            "result": {},
            "status": "WORKING"
        }

    **Example Response**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json
        Location: http://localhost:5000/jobs/3bb5b090-416c-11e7-a880-843a4b768af4

        {
          "data": {
            "job_schema": {
              "date_submitted": "2017-05-25T17:04:37.212708+00:00",
              "id": "3bb5b090-416c-11e7-a880-843a4b768af4",
              "parameters": {
                "value": 1
              },
              "result": {},
              "status": "WORKING"
            },
            "message": "Job Job(parent_service=Service(id=262472146097748129118538192143273855732, name=TestService, description=Some test data, schema={'properties': {'value': {'minimum': 1, 'maximum': 10, 'type': 'integer'}}, 'type': 'object'}), job_parameters={'value': 1}, attached_session=<sqlalchemy.orm.session.Session object at 0x7ffaa689bf28>, file_manager=SchemaDirectoryOrganizer(schema_directory_path=/home/mkononen/git/TopChef/TopChef/topchef/schemas)) updated successfully"
          }
        }

    :statuscode 200: The request completed succesfully
    :statuscode 400: The JSON was not correctly formatted
    :statuscode 404: A service or job with that particular ID could not be
        found

    :param job_id: The ID of the job to update
    :return: The appropriate Flask Response
    """
    try:
        job_id = UUID(job_id)
    except ValueError:
        response = jsonify({
            'errors': 'Unable to cast job id %s to a UUID' % str(job_id)
        })
        response.status_code = 404
        return response

    session = SESSION_FACTORY()

    job = session.query(Job).filter_by(id=job_id).first()

    if not job:
        response = jsonify({
            'errors': 'Unable to find job with id %s' % str(job_id)
        })
        response.status_code = 404
        return response

    job.file_manager = FILE_MANAGER
    job.session = session
    job.parent_service.file_manager = FILE_MANAGER
    
    new_job_data, errors = Job.DetailedJobSchema().load(request.get_json())
    
    if errors:
        response = jsonify({'errors': errors})
        response.status_code = 400
        return response

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
            'message': 'Job %s updated successfully' % str(job_id),
            'job_schema': job.DetailedJobSchema().dump(job).data
            }
        }
    )
    response.status_code = 200
    response.headers['Location'] = url_for(
        '.get_job', job_id=job.id, _external=True
    )
    return response


@app.route('/jobs/<job_id>/next', methods=['GET'])
def get_next_job(job_id):
    """
    If a job has a next job, return a redirect to that job.
    Otherwise, return a 204 response

    **Example Response: No Content**

    ..sourcecode:: http

        HTTP/1.1 204 NO CONTENT

    **Example Response: Next Job**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
          "data": {
            "date_submitted": "2017-05-25T17:38:18.979594+00:00",
            "id": "f0c6d58c-4170-11e7-a880-843a4b768af4",
            "parameters": {
              "value": 2
            },
            "result": {},
            "status": "REGISTERED"
          }
        }

    :statuscode 200: This job has a next job. The job data is given in the
        body of the response
    :statuscode 204: This job has no next jobs.

    :param str job_id: The UUID of the job for which a next job is to be
        retrieved
    :return: The appropriate Flask response
    :rtype: Flask.Response

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
    """

    **Example Request**

    .. sourcecode:: http

        PUT /services/514d373a-e9af-41cf-a7d0-efe6a675f820/jobs
            /8e877afc-bd9e-4f26-86e0-a53b353c56b5 HTTP/1.1
        Content-Type: application/json

        {
            "date_submitted": "2017-05-25T17:04:37.212708+00:00",
            "id": "3bb5b090-416c-11e7-a880-843a4b768af4",
            "parameters": {
              "value": 1
            },
            "result": {},
            "status": "WORKING"
        }

    **Example Response**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json
        Location: http://localhost:5000/jobs/3bb5b090-416c-11e7-a880-843a4b768af4

        {
          "data": {
            "job_schema": {
              "date_submitted": "2017-05-25T17:04:37.212708+00:00",
              "id": "3bb5b090-416c-11e7-a880-843a4b768af4",
              "parameters": {
                "value": 1
              },
              "result": {},
              "status": "WORKING"
            },
            "message": "Job Job(parent_service=Service(id=262472146097748129118538192143273855732, name=TestService, description=Some test data, schema={'properties': {'value': {'minimum': 1, 'maximum': 10, 'type': 'integer'}}, 'type': 'object'}), job_parameters={'value': 1}, attached_session=<sqlalchemy.orm.session.Session object at 0x7ffaa689bf28>, file_manager=SchemaDirectoryOrganizer(schema_directory_path=/home/mkononen/git/TopChef/TopChef/topchef/schemas)) updated successfully"
          }
        }

    :statuscode 200: The request completed succesfully
    :statuscode 400: The JSON was not correctly formatted
    :statuscode 404: A service or job with that particular ID could not be
        found

    :param str service_id: The ID of the service for which this job is to be updated
    :param job_id: The ID of the job that is to be updated
    :return: The appropriate Flask response
    """
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

    job.file_manager = FILE_MANAGER
    job.session = session
    job.parent_service.file_manager = FILE_MANAGER
    new_job_data, errors = Job.DetailedJobSchema(strict=True).load(
        request.get_json())

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
            'job_schema': job.DetailedJobSchema().dump(job).data
            }
        }
    )
    response.status_code = 200
    response.headers['Location'] = url_for(
        '.get_job', job_id=job.id, _external=True
    )
    return response
