"""
The base module of entry for the application. This module contains the
command line argument parser, allowing for starting and maintaining the
server from the CLI. This is meant to be used when starting the app from the
Flask development server.

.. note::

    This module is intended for use only when running the application direct
    from the command line. If this application is going to be run through a
    web server like Apache, it is recommended to use the ``APP_FACTORY``
    variable in :mod:`topchef.wsgi_app`.
"""
from flask import Flask
from flask_script import Manager, Command
from topchef.wsgi_app import WSGIAppFactory
from topchef.wsgi_app import DatabaseEngineFactory
from topchef import APP_FACTORY
from topchef.database.schemas import DatabaseSchema, AbstractDatabaseSchema


class TopchefManager(Manager):
    """
    Responsible for starting and running the server
    """
    def __init__(
            self,
            app_factory_constructor: WSGIAppFactory=APP_FACTORY,
            db_engine_factory: DatabaseEngineFactory=APP_FACTORY
    ) -> None:
        """

        :param app_factory_constructor: The application factory to use for
            running this manager.
        """
        super(TopchefManager, self).__init__()
        self.app = app_factory_constructor.app
        self.add_default_commands()
        self.add_command('run', self.Run(self.app))
        self.add_command('create-db', self.CreateDB(db_engine_factory))

    class Run(Command):
        def __init__(self, app: Flask) -> None:
            Command.__init__(self)
            self.app = app

        def run(self) -> None:
            self.app.run()

    class CreateDB(Command):
        def __init__(
                self,
                app_factory: DatabaseEngineFactory,
                database_schema: AbstractDatabaseSchema=DatabaseSchema()
        ) -> None:
            super(self.__class__, self).__init__()
            self.app_factory = app_factory
            self.schema = database_schema

        def run(self):
            engine = self.app_factory.engine
            self.schema.metadata.create_all(bind=engine)


if __name__ == '__main__':
    manager = TopchefManager()
    manager.run()
