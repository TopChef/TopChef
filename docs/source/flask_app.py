"""
Contains a Flask app with all the endpoints registered
"""
from topchef.wsgi_app import APP_FACTORY

app = APP_FACTORY.app
