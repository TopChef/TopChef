import sys

LIBRARY_PATH = '/opt/topspin/exp/stan/nmr/py/user'

sys.path.append(LIBRARY_PATH)

import unittest
from topchef_client import TopChefClient
from unit_test_runner import UnitTestRunner

True = "1"
False = "0"

class MockNetClient:
	"""
	Contains methods for stubbing out the java.net library in order
	to enable unit testing of the TopChef client
	"""
	def __init__(self):
		self.mock_details = {
			'URL': {
				'address': [],
				'number_of_calls': 0
			},
			'openConnection': {
				'number_of_calls': 0
			},
			'getInputStream': {
				'number_of_calls': 0
			},
			'getResponseCode': {
				'number_of_calls': 0
			},
			'setRequestMethod': {
				'number_of_calls': 0,
			},
			'connect': {
				'number_of_calls': 0
			}
		}
		self.mock_response_code = 200
		self.mock_method = "GET"
		
	def _increment(self, attribute):
		attribute = attribute + 1
		
	def URL(self, address):
		self._increment(self.mock_details['URL']['number_of_calls'])
		self.mock_details['URL']['address'].append(address)
		return self
	
	def openConnection(self):
		self._increment(self.mock_details['openConnection']['number_of_calls'])
		return self
		
	def getInputStream(self):
		self._increment(self.mock_details['getInputStream']['number_of_calls'])
		return self
		
	def getResponseCode(self):
		self._increment(self.mock_details['getResponseCode']['number_of_calls'])
		return self.mock_response_code
		
	def setRequestMethod(self, new_method):
		self._increment(self.mock_details['setRequestMethod']['number_of_calls'])
		self.mock_method = new_method
		
	def connect(self):
		self._increment(self.mock_details['connect']['number_of_calls'])
		
	
class MockIOLibrary:
	"""
	Contains methods for stubbing out the java.io library for unit
	testing the client
	"""
	

class TestTopChefClient(unittest.TestCase):
	def setUp(self):
		self.address = 'http://127.0.0.1'
		self.net = MockNetClient()
		self.io = MockIOLibrary()
		
	def assertTrue(self, value):
		self.assertEqual(value, True)
	
	def assertFalse(self, value):
		self.assertEqual(value, False)
	
class TestTopChefClientConstructor(TestTopChefClient):
	def test_constructor_default_args(self):
		client = TopChefClient(self.address)
		
		self.assertEqual(client.api_host, self.address)
		
	def test_constructor_optional_args(self):
		client = TopChefClient(self.address, net_client=self.net,
			io_manipulator=self.io
		)
		
		self.assertEqual(client.net, self.net)
		self.assertEqual(client.io, self.io)

class TestTopChefClientWithFixture(TestTopChefClient):
	def setUp(self):
		TestTopChefClient.setUp(self)
		
		self.client = TopChefClient(
			self.address, net_client=self.net, io_manipulator=self.io
		)
		
class TestTopChefParseJson(TestTopChefClientWithFixture):
	def setUp(self):
		TestTopChefClientWithFixture.setUp(self)
		
		self.json_string = '{"this": "is", "valid": "json", "number": 1, "boolean": true}'
		self.expected_dict = {"this": "is", "valid": "json", "number": 1, "boolean": True}
		
		self.bad_syntax_json = '{"this": "is", "bad", "json", "notice": "the", "comma"}'
		
		self.bad_json = 'Not a valid JSON'
		
	def test_parse_json(self):
		"""
		Tests that the parser is able to parse JSON correctly
		"""
		parsed_dict = self.client.parse_json(self.json_string)
		
		self.assertEqual(self.expected_dict, parsed_dict)
		
	def test_parse_bad_syntax_json(self):
		"""
		Tests that the parser throws an appropriate exception if badly-formatted
		JSON is passed into it
		"""		
		def _parsing_thunk(client, json):
			client.parse_json(json)
	
		self.assertRaises(
			ValueError, _parsing_thunk, self.client, self.bad_syntax_json
		)
		
	def test_parse_bad_json(self):
		"""
		Tests that the client throws an exception if bad JSON is passed into it
		"""
		def _parsing_thunk(client, json):
			client.parse_json(json)
	
		self.assertRaises(
			ValueError, _parsing_thunk, self.client, self.bad_json
		)
		
	def test_parse_code_injection(self):
		"""
		Tests that the JSON parser mitigates a basic lambda-based code injection
		attack, where malicious code is placed in a thunk and then executed
		"""
		json_to_parse = '(lambda: {"Malicious": "code"})()'
		
		def _parsing_thunk(client, json):
			client.parse_json(json)
			
		self.assertRaises(
			ValueError, _parsing_thunk, self.client, json_to_parse
		)
		
	def test_parse_string_lambda(self):
		"""
		Tests that the word "lambda" is allowed if it's in a string
		"""
		json_to_parse = '{"string": "lambda is a nice word"}'
		expected_dict = {'string': 'lambda is a nice word'}
		
		self.assertEqual(expected_dict, self.client.parse_json(json_to_parse))
		
class TestIsServerAlive(TestTopChefClientWithFixture):
	
	def test_is_alive_true(self):
		self.net.mock_response_code = 200
		self.assertTrue(self.client.is_server_alive())
	
	def test_is_alive_false(self):
		self.net.mock_response_code = 404
		self.assertFalse(self.client.is_server_alive())

blade_runner = UnitTestRunner([
	TestTopChefClientConstructor('test_constructor_default_args'),
	TestTopChefClientConstructor('test_constructor_optional_args'),
	TestTopChefParseJson('test_parse_json'),
	TestTopChefParseJson('test_parse_bad_syntax_json'),
	TestTopChefParseJson('test_parse_bad_json'),
	TestTopChefParseJson('test_parse_code_injection'),
	TestTopChefParseJson('test_parse_string_lambda'),
	TestIsServerAlive('test_is_alive_true'),
	TestIsServerAlive('test_is_alive_false')
])

blade_runner.run_with_callback(MSG)
