import sys

LIBRARY_PATH = '/opt/topspin/exp/stan/nmr/py/user'

sys.path.append(LIBRARY_PATH)

import unittest
from topchef_client import TopChefClient, TopChefJob, NetworkError
from topchef_client import _TopChefResource
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
			},
			'close': {
				'number_of_calls': 0
			}
		}
		self.mock_response_code = 200
		self.mock_method = "GET"
				
	def _increment(self, method):
		self.mock_details[method]['number_of_calls'] = self.mock_details[method]['number_of_calls'] + 1
		
	def URL(self, address):
		self._increment('URL')
		self.mock_details['URL']['address'].append(address)
		return self
	
	def openConnection(self):
		self._increment('openConnection')
		return self
		
	def getInputStream(self):
		self._increment('getInputStream')
		return self
		
	def getResponseCode(self):
		self._increment('getResponseCode')
		return self.mock_response_code
		
	def setRequestMethod(self, new_method):
		self._increment('setRequestMethod')
		self.mock_method = new_method
		
	def connect(self):
		self._increment('connect')
		
	def close(self):
		self._increment('close')
		
	
class MockIOLibrary:
	"""
	Contains methods for stubbing out the java.io library for unit
	testing the client
	"""
	def __init__(self):
		self.mock_details = {
			'InputStreamReader': {
				'number_of_calls' : 0,
				'last_called_with': None
			},
			'BufferedReader': {
				'number_of_calls': 0,
				'last_called_with': None
			}
		}
		
		self.readlist = [None]
		self.read_index = -1
	
	def _reset_read_index(self):
		self.read_index = -1
		
	def _set_read_list(self, new_readlist, newline_character='\n'):
		"""
		Pass in a new list of strings to read by readLine
		
		:param new_readlist: The new list of strings or single string
			to be read sequentially by this reader. If the new_readlist
			is a string, the string will be split by ``newline_character``.
			If ``new_readlist`` or the string resulting from splitting
			``new_readlist`` does not end with ``None``, then ``None``will be
			appended to ``new_readlist``.
		:param newline_character: If ``new_readlist`` is a string, then this
			is the character that will be used to split each line. By default, this
			is the line feed character ``\n``, due to the obvious superiority of
			UNIX line endings to any other OS :).
		"""
		self._reset_read_index()
		
		if isinstance(new_readlist, ''.__class__):
			new_readlist = new_readlist.split(newline_character)
		
		if new_readlist[len(new_readlist) - 1] is not None:
			new_readlist.append(None)
		
		assert new_readlist[len(new_readlist) - 1] is None
		
		self.readlist = new_readlist
			
	def _increment(self, method):
		self.mock_details[method]['number_of_calls'] = \
			self.mock_details[method]['number_of_calls'] + 1
		
	def InputStreamReader(self, stream):
		self._increment('InputStreamReader')
		self.mock_details['InputStreamReader']['last_called_with'] = stream
		
		return self
		
	def BufferedReader(self, stream):
		self._increment('BufferedReader')
		self.mock_details['BufferedReader']['last_called_with'] = stream
		
		return self
	
	def readLine(self):
		self.read_index = self.read_index + 1
		return self.readlist[self.read_index]

class TestModule(unittest.TestCase):
	"""
	Base class for all tests of :mod:`topchef_client`. Responsible
	for loading in all the required mock libraries, and providing values
	to be used across all test cases.
	
	It also implements an assertTrue and assertFalse method to use my
	pseudo-booleans throughout the test module. Jython 2.2 does not implement
	Booleans because reasons.
	"""
	def setUp(self):
		self.address = 'http://127.0.0.1'
		self.net = MockNetClient()
		self.io = MockIOLibrary()
		
	def assertTrue(self, value):
		self.assertEqual(value, True)
	
	def assertFalse(self, value):
		self.assertEqual(value, False)
		
class TestTopChefResourceConstructor(TestModule):
	"""
	Contains unit tests for :meth:`_TopChefResource.__init__`
	"""
	def test_constructor_default_args(self):
		fixture = _TopChefResource(self.address)
		
		self.assertEqual(fixture.api_host, self.address)
	
	def test_constructor_optional_args(self):
		fixture = _TopChefResource(self.address, net_client=self.net,
			io_manipulator=self.io
		)
		
		self.assertEqual(fixture.net, self.net)
		self.assertEqual(fixture.io, self.io)

class TestTopChefResource(TestModule):
	"""
	Base class for all tests on :class:`_TopChefResource`. This test sets
	up a _Resource with some basic parameters
	"""
	def setUp(self):
		TestModule.setUp(self)
		self.resource = _TopChefResource(self.address, net_client=self.net,
			io_manipulator=self.io
		)

class TestParseJson(TestTopChefResource):
	"""
	Contains tests for :meth:`_TopChefResource.parse_json`. Tests that the JSON
	parser works according to specifications
	"""
	def setUp(self):
		TestTopChefResource.setUp(self)
		
		self.json_string = '{"this": "is", "valid": "json", "number": 1, "boolean": true}'
		self.expected_dict = {"this": "is", "valid": "json", "number": 1, "boolean": True}
		
		self.bad_syntax_json = '{"this": "is", "bad", "json", "notice": "the", "comma"}'
		
		self.bad_json = 'Not a valid JSON'
		
	def test_parse_json(self):
		"""
		Tests that the parser is able to parse JSON correctly
		"""
		parsed_dict = self.resource.parse_json(self.json_string)
		
		self.assertEqual(self.expected_dict, parsed_dict)
		
	def test_parse_bad_syntax_json(self):
		"""
		Tests that the parser throws an appropriate exception if badly-formatted
		JSON is passed into it, but the JSON string still begins and ends with {}.
		This string resembles JSON, but it isn't quite right.
		"""		
		def _parsing_thunk(client, json):
			client.parse_json(json)
	
		self.assertRaises(
			ValueError, _parsing_thunk, self.resource, self.bad_syntax_json
		)
		
	def test_parse_bad_json(self):
		"""
		Tests that the client throws an exception if a string is passed
		that is a valid Python string, but does not evaluate to a dictionary.
		It is assumed that all JSON contains a key-value mapping as part of its
		top structure.
		"""
		def _parsing_thunk(client, json):
			client.parse_json(json)
	
		self.assertRaises(
			ValueError, _parsing_thunk, self.resource, self.bad_json
		)
		
	def test_parse_code_injection(self):
		"""
		Tests that the JSON parser mitigates a basic lambda-based code injection
		attack, where malicious code is placed in a thunk and then executed upon
		the eval. The method should treat this kind of code as any regular string.
		It should throw a ValueError.
		"""
		json_to_parse = '(lambda: {"Malicious": "code"})()'
		
		def _parsing_thunk(client, json):
			client.parse_json(json)
			
		self.assertRaises(
			ValueError, _parsing_thunk, self.resource, json_to_parse
		)
		
	def test_parse_string_lambda(self):
		"""
		Tests that the word "lambda" is allowed if it's in a string. This tests
		that the lambda was escaped correctly.
		"""
		json_to_parse = '{"string": "lambda is a nice word"}'
		expected_dict = {'string': 'lambda is a nice word'}
		
		self.assertEqual(expected_dict, self.resource.parse_json(json_to_parse))		


class TestIsServerAlive(TestTopChefResource):
	"""
	Contains unit tests for :meth:`_TopChefResource.is_server_alive`
	"""	
	def test_is_alive_true(self):
		"""
		Tests that a response code of 200 will ensure that the
		method returns a True value
		"""
		self.net.mock_response_code = 200
		self.assertTrue(self.resource.is_server_alive())
		self._make_connection_assertions()
		
	def test_is_alive_false(self):
		"""
		Tests that a non-200 response code will make the method
		return False
		"""
		self.net.mock_response_code = 404
		self.assertFalse(self.resource.is_server_alive())
		self._make_connection_assertions()
		
	def _make_connection_assertions(self):
		"""
		Performs a series of assertions to ensure that the library used the java.net
		API correctly
		"""
		self.assertEqual(self.net.mock_details['URL']['number_of_calls'], 1)
		self.assertEqual(self.net.mock_details['openConnection']['number_of_calls'], 1)
		
		self.assertEqual(self.net.mock_details['setRequestMethod']['number_of_calls'], 1)
		self.assertEqual(self.net.mock_method, "GET")
		
		self.assertEqual(self.net.mock_details['connect']['number_of_calls'], 1)
		self.assertEqual(self.net.mock_details['getResponseCode']['number_of_calls'], 1)
		
class TestReadJsonFromConnection(TestTopChefResource):
	"""
	Contains unit tests for :meth:`_TopChefResource._read_json_from_connection`
	"""
	def setUp(self):
		TestTopChefResource.setUp(self)
		self.expected_output = {'data': 'hello'}
		self.input_stream = ['{', '"data": "hello"', '}', None]
		
		self.io._set_read_list(self.input_stream)
		
	def test_read_json(self):
		"""
		Tests that the method is able to successfully read the mock input stream
		"""
		self.assertEqual(
			self.expected_output, 
			self.resource._read_json_from_connection(self.net)
		)
				
		self.assertEqual(
			self.net.mock_details['getInputStream']['number_of_calls'], 1
		)
		
		self.assertEqual(
			self.io.mock_details['InputStreamReader']['number_of_calls'], 1
		)
		self.assertEqual(
			self.io.mock_details['InputStreamReader']['last_called_with'], 
			self.net
		)
		
		self.assertEqual(
			self.io.mock_details['BufferedReader']['number_of_calls'], 1
		)
		self.assertEqual(
			self.io.mock_details['BufferedReader']['last_called_with'],
			self.io
		)
		
		self.assertEqual(self.net.mock_details['close']['number_of_calls'], 1)
	
class TestTopChefClient(TestModule):
	def setUp(self):
		TestModule.setUp(self)
		
		self.client = TopChefClient(
			self.address, net_client=self.net, io_manipulator=self.io
		)
		
class TestGetJobIDs(TestTopChefClient):
	def setUp(self):
		TestTopChefClient.setUp(self)
		self.job_ids = [
			'1d305560-6960-11e6-8591-001018737a6d', 
			'37bdb0be-6963-11e6-9860-001018737a6d'
		]
		
		self.json_from_api = {'data': [{'id': job_id} for job_id in self.job_ids]}
		
		self.io._set_read_list(str(self.json_from_api))
	
	def test_get_job_ids(self):
		job_ids = self.client.get_job_ids()
		
		self.assertEqual(self.net.mock_details['URL']['number_of_calls'], 1)
		self.assertEqual(
			self.net.mock_details['URL']['address'][0],
			'%s/jobs' % (self.client.api_host)
		)
		self.assertEqual(
			self.net.mock_method, 
			"GET"
		)
		
	def test_get_job_ids_conn_error(self):
		self.net.mock_response_code = 500
			
		def _error_thunk(client):
			client.get_job_ids()
				
		self.assertRaises(NetworkError, _error_thunk, self.client)
			
class TestGetJobByID(TestTopChefClient):
	def setUp(self):
		TestTopChefClient.setUp(self)
		self.job_id = '1d305560-6960-11e6-8591-001018737a6d'
		self.job_class = TopChefJob
	
	def test_get_job_by_id(self):
		
		job = self.client.get_job_by_id(self.job_id)
		
		self.assertEqual(job.id, self.job_id)
		self.assertEqual(job.__class__, self.job_class)

blade_runner = UnitTestRunner([
	TestTopChefResourceConstructor('test_constructor_default_args'),
	TestTopChefResourceConstructor('test_constructor_optional_args'),
	
	TestParseJson('test_parse_json'),
	TestParseJson('test_parse_bad_syntax_json'),
	TestParseJson('test_parse_bad_json'),
	TestParseJson('test_parse_code_injection'),
	TestParseJson('test_parse_string_lambda'),
	
	TestIsServerAlive('test_is_alive_true'),
	TestIsServerAlive('test_is_alive_false'),
	
	TestReadJsonFromConnection('test_read_json'),
	
	TestGetJobIDs('test_get_job_ids'),
	TestGetJobIDs('test_get_job_ids_conn_error')
])

blade_runner.run_with_callback(MSG)
