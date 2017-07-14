"""
Contains API models
"""
from topchef.wsgi_app import APP_FACTORY
from passlib.apps import custom_app_context as passlib_context

db = APP_FACTORY.db


class User(db.Model):
    """
    Model class for an authenticated user
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password_hash = db.Column(db.String)
    email = db.Column(db.String)

    def set_password(self, password):
        self.password_hash = passlib_context.encrypt(password)

    def verify_password(self, password):
        return passlib_context.verify(password, self.password_hash)


class Service(db.Model):
    """
    The database model for a compute service. This service has one job
    parameters schema, and one job result schema. These must be satisfied in
    order to allow jobs to be submitted
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    maintainer_id = db.Column(db.ForeignKey())

    maintainer = db.relationship('User', backref=db.backref(
        'managed_services'))