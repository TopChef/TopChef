#!/usr/bin/env python
"""
Very very very basic application
"""
from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/users', methods=["GET"])
def get_users():
    return '/users endpoint'


@app.route('/users', methods=["POST"])
def make_user():
    return 'POST /users, no user made'


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

if __name__ == '__main__':
    app.run()
