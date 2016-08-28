from topchef_client import Client
import pytest

ADDRESS = 'localhost'
SERVICE_ID = 'a5b00b5a-6c8b-11e6-b090-843a4b768af4'

class ClientForTesting(Client):
    """
    A simple test client that implements the abstract
    client for contacting the topchef server
    """
    def run(self, parameters):
        return parameters

class TestClientConstructor(object):
    
    def test_is_client_abstract(self):
        with pytest.raises(TypeError):
            Client(ADDRESS, SERVICE_ID)


    def test_constructor(self):
        client = ClientForTesting(ADDRESS, SERVICE_ID)

        assert client.id == SERVICE_ID
        assert client.address == ADDRESS
