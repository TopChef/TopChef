"""
Contains user-serviceable configuration parameters
"""
import os
import logging
from collections import namedtuple, Iterable
from sqlalchemy import create_engine

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

    LOGFILE = '/var/tmp/topchef.log'

    # DATABASE
    DATABASE_URI = 'sqlite:///%s/db.sqlite3' % BASE_DIRECTORY

    def __init__(self, environment=os.environ):

        Parameter = namedtuple('Parameter', ['key', 'from_env', 'from_file'])

        config_parameters = {
            Parameter(
                key=attribute,
                from_file=self.__class__.__dict__[attribute],
                from_env=self._safe_get_from_environment(
                    attribute, environment=environment)
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

        self._engine = create_engine(self.DATABASE_URI)

        if self.LOGFILE:
            hdlr = logging.FileHandler(self.LOGFILE)
            formatter = logging.Formatter(
                '%(asctime)s %(levelname)s %(message)s')
            hdlr.setFormatter(formatter)
            LOG.addHandler(hdlr)
            LOG.setLevel(logging.DEBUG)


    def _safe_get_from_environment(self, parameter, environment=os.environ):
        try:
            value_from_environment = environment[parameter]
        except KeyError:
            value_from_config = self.__class__.__dict__[parameter]
            LOG.info(
                'parameter %s not defined in environment, using value of '
                '%s', parameter, value_from_config
            )
            value_from_environment = value_from_config

        if parameter.upper() == 'DEBUG' \
            and isinstance(value_from_environment, str):
            if value_from_environment.upper() == "TRUE":
                return True
            elif value_from_environment.upper() == "FALSE":
                return False

        if parameter.upper() == "PORT":
            return int(value_from_environment)

        return value_from_environment

    def __iter__(self):
        for attribute in self.__class__.__dict__:
            if attribute == attribute.upper():
                yield attribute

    @property
    def parameter_dict(self):
        return {attribute: self.__dict__[attribute] for attribute in self}

    @property
    def database_engine(self):
        return self._engine

config = Config()
