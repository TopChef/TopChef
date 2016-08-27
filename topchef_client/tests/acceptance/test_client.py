from topchef-client import Client
import pytest
import fixtures

class TestClientConstructor(object):

    def test_constructor(self):
        client = Client(self.id)

        assert client.id == self.id

