from flask import Flask
from flask_script import Manager, Command
from topchef.wsgi_app import WSGIAppFactory, ProductionWSGIAppFactory
from typing import Type


class TopchefManager(Manager):
    def __init__(
            self,
            app_factory_constructor: Type[
                WSGIAppFactory
            ]=ProductionWSGIAppFactory
    ) -> None:
        super(TopchefManager, self).__init__()
        self.app = app_factory_constructor().app
        self.add_default_commands()
        self.add_command('run', self.Run(self.app))

    class Run(Command):
        def __init__(self, app: Flask) -> None:
            Command.__init__(self)
            self.app = app

        def run(self) -> None:
            self.app.run()

if __name__ == '__main__':
    manager = TopchefManager()
    manager.run()
