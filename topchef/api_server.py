#!/usr/bin/env python
"""
Very very very basic application
"""
from flask import Flask, jsonify, request, url_for
from .database import SESSION_FACTORY, METADATA, ENGINE
from .models import User
from .config import ROOT_EMAIL, ROOT_USERNAME
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)


@app.route('/')
def hello_world():
    return jsonify({
        'meta': {
            'source_repository': 'https://www.github.com/whitewhim2718/TopChef',
            'version': '0.1dev',
            'author': 'Michal Kononenko',
            'email': "michalkononenko@gmail.com"
        }
    })


@app.route('/users', methods=["GET"])
def get_users():
    session = SESSION_FACTORY()

    user_list = session.query(User).all()

    return jsonify({
        'data': {
            'users': User.UserSchema(many=True).dump(user_list).data
        }
    })


@app.route('/users', methods=["POST"])
def make_user():
    session = SESSION_FACTORY()

    if not request.json:
        response = jsonify({'errors': 'The supplied data is not JSON'})
        response.status_code = 400
        return response

    user, errors = User.UserSchema().load(request.json)

    if errors:
        response = jsonify({'errors': errors})
        response.status_code = 400
        return response

    try:
        session.add(user)
        session.commit()
    except IntegrityError:
        session.rollback()
        response = jsonify({'errors': 'A user with username %s already exists' % user.username})
        response.status_code = 400
        return response

    response = jsonify({'data': 'user %s successfully created' % user.username})
    response.headers['Location'] = url_for('get_user_info', username=user.username, _external=True)
    response.status_code = 201
    return response


@app.route('/users/<username>', methods=["GET"])
def get_user_info(username):
    return '/users/<username> endpoint. Found user %s' % username


@app.route('/users/<username>/jobs', methods=["GET"])
def get_jobs_for_user(username):
    return 'There will be jobs for user %s here' % username


@app.route('/users/<username>/jobs', methods=["POST"])
def make_job_for_user(username):
    return 'The User %s makes jobs here' % username


@app.route('/users/<username>/jobs/<int:job_id>', methods=["GET"])
def get_job_details(username, job_id):
    return 'The user %s got data for job %d' % (username, job_id)


@app.route('/users/<username>/jobs/next', methods=["GET"])
def get_next_job(username):
    return "The Job user with username %s will be redirected to the next job" % username


@app.route('/users/<username>/jobs/<int:job_id>', methods=["PATCH"])
def do_stuff_to_job(username, job_id):
    return "Post results, change state, for user %s and job %d" % (username, job_id)


@app.route('/programs', methods=["GET"])
def get_programs():
    return 'Here is a list of NMR programs'


@app.route('/programs/<int:program_id>', methods=["GET"])
def get_program_by_id(program_id):
    return 'Here is business logic to retrieve a program file with id %d' % program_id


def create_root_user():
    session = SESSION_FACTORY()
    root_user = User(ROOT_USERNAME, ROOT_EMAIL)

    if session.query(User).filter_by(username=ROOT_USERNAME).first() is None:
        session.add(root_user)

    session.commit()


def create_metadata():
    METADATA.create_all(bind=ENGINE)
