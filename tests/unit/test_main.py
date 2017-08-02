"""
Contains unit tests for :mod:`topchef.__main__`
"""
import unittest
import unittest.mock as mock
from flask import Flask
from topchef.__main__ import TopchefManager


class TestMain(unittest.TestCase):
    def setUp(self):
        self.app_constructor = mock.MagicMock(spec=type)
        self.manager = TopchefManager(self.app_constructor)


class TestRun(TestMain):
    def setUp(self):
        TestMain.setUp(self)
        self.app = mock.MagicMock(spec=Flask)
        self.command = TopchefManager.Run(self.app)

    def test_run(self):
        self.command.run()
        self.assertTrue(self.app.run.called)
