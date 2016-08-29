"""
Contains integration tests for :mod:`topchef_client`
"""
import sys


LIBRARY_PATH = '/opt/topspin/exp/stan/nmr/py/user'

sys.path.append(LIBRARY_PATH)

import unittest
from topchef_client import TopChefClient, NetworkManager
from topchef_client import ValidationError
from unit_test_runner import UnitTestRunner

True = "1"
False = "0"

class TestClient(unittest.TestCase):
	def setUp(self):
		self.host = 'http://192.168.1.39'
		self.manager = NetworkManager(self.host)
		self.client = TopChefClient(self.manager)
		
	def assertTrue(self, value):
		self.assertEqual(True, value)
		
	def assertFalse(self, value):
		self.assertEqual(False, value)
		
		
class TestIsServerAlive(TestClient):
	def test_is_server_alive(self):
		self.assertTrue(self.client.is_server_alive())

class TestGetJobIDs(TestClient):
	def test_get_job_ids(self):
		ids = self.client.get_job_ids()
		
		self.assertEqual(ids.__class__, [].__class__)
		
class TestLoopback(TestClient):
	def setUp(self):
		TestClient.setUp(self)
		self.json_to_loop = {'number': 1, 'boolean': True, 'string': 'string'}
		
	def test_loopback(self):
		response = self.client.loopback(self.json_to_loop)
		
		self.assertEqual(response['data'], self.json_to_loop)

class TestJSONSchemaValidation(TestClient):
	def setUp(self):
		TestClient.setUp(self)
		self.schema = {
			'type':'object',
			'properties': {
				'value': {
					'type': 'integer',
					'minimum': 0,
					'maximum': 2
				}
			}
		}
		self.valid_object = {'value': 1}
		self.invalid_object = {'value': 3}
		
	def test_validate_schema(self):
		self.client.validate_json_schema(self.valid_object, self.schema)
		
	def test_invalid_schema(self):
		def _thunk(client, object, schema):
			client.validate_json_schema(object, schema)
		
		self.assertRaises(
			ValidationError, _thunk, self.client, self.invalid_object, self.schema
		)

running_man = UnitTestRunner([
	TestIsServerAlive('test_is_server_alive'),

	TestGetJobIDs('test_get_job_ids'),
	
	TestLoopback('test_loopback'),
	
	TestJSONSchemaValidation('test_validate_schema'),
	TestJSONSchemaValidation('test_invalid_schema')
])
running_man.run_with_callback(MSG)