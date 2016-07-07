"""
Contains user-serviceable configuration parameters
"""
import os
import logging
from collections import namedtuple, Iterable

LOG = logging.getLogger(__name__)


class Config(Iterable):

    # METADATA
    SOURCE_REPOSITORY = 'https://www.github.com/MichalKononenko/TopChef'
    VERSION = '0.1dev'
    AUTHOR = 'Michal Kononenko'
    AUTHOR_EMAIL = 'michalkononenko@gmail.com'

    # HOSTING PARAMETERS
    PORT = 5000
    HOSTNAME = 'localhost'
    THREADS = 3
    DEBUG = True

    #DIRECTORY
    BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    SCHEMA_DIRECTORY = os.path.join(BASE_DIRECTORY, 'schemas')

    # DATABASE
    DATABASE_URI = 'sqlite:////var/tmp/db.sqlite3'


    # ROOT USER
    ROOT_USERNAME = 'root'
    ROOT_EMAIL = 'mkononen@uwaterloo.ca'

    def __init__(self):

        Parameter = namedtuple('Parameter', ['key', 'from_env', 'from_file'])

        config_parameters = {
            Parameter(
                key=attribute,
                from_file=self.__class__.__dict__[attribute],
                from_env=self._safe_get_from_environment(attribute)
            )
            for attribute in self
        }

        ResolvedParameter = namedtuple('ResolvedParameter', ['key', 'value'])

        new_parameters = {
            ResolvedParameter(
                parameter.key,
                parameter.from_env if parameter.from_env != parameter.from_file
                                        and parameter.from_env is not None
                                   else parameter.from_file
            )

            for parameter in config_parameters
        }

        for parameter in new_parameters:
            self.__dict__[parameter.key] = parameter.value

    def _safe_get_from_environment(self, parameter):
        try:
            value_from_environment = os.environ[parameter]
        except KeyError:
            value_from_config = self.__class__.__dict__[parameter]
            LOG.info(
                'parameter %s not defined in os.environ, using value of '
                '%s', parameter, value_from_config
            )
            value_from_environment = None

    def __iter__(self):
        for attribute in self.__class__.__dict__:
            if attribute == attribute.upper():
                yield attribute

config = Config()
