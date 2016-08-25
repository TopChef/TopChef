import sys


LIBRARY_PATH = '/opt/topspin/exp/stan/nmr/py/user'

sys.path.append(LIBRARY_PATH)

import unittest
from topchef_client import TopChefClient, TopChefJob, NetworkError
from topchef_client import _TopChefResource
from topchef_client import NetworkManager
from unit_test_runner import UnitTestRunner

import java.lang.Boolean.TRUE as JAVA_TRUE
import java.lang.Boolean.FALSE as JAVA_FALSE

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
			},
			'setRequestProperty': {
				'number_of_calls': 0,
				'request_props': {}
			},
			'getOutputStream': {
				'number_of_calls': 0
			},
			'write': {
				'number_of_calls': 0,
				'written_text': ''
			},
			'setDoOutput': {
				'number_of_calls': 0,
				'value': ''
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
	
	def getOutputStream(self):
		self._increment('getOutputStream')
		return self
	
	def getResponseCode(self):
		self._increment('getResponseCode')
		return self.mock_response_code
		
	def setRequestMethod(self, new_method):
		self._increment('setRequestMethod')
		self.mock_method = new_method
	
	def setRequestProperty(self, key, value):
		self._increment('setRequestProperty')
		self.mock_details['setRequestProperty']['request_props'][key] = value
	
	def connect(self):
		self._increment('connect')
		
	def close(self):
		self._increment('close')
		
	def write(self, text_to_write):
		self._increment('write')
		self.mock_details['write']['written_text'] = text_to_write
		
	def setDoOutput(self, value):
		self._increment('setDoOutput')
		self.mock_details['setDoOutput']['value'] = value
	
	
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
		
class TestNetworkManagerConstructor(TestModule):
	"""
	Contains unit tests for :class:`_NetworkManager
	"""
	def test_constructor_min_args(self):
		"""
		Tests that a :class:`_NetworkManager` can be created using just an 
		address. It should load the ``java.net`` and ``java.io`` libraries 
		by default.
		"""
		manager = NetworkManager(self.address)
		
		self.assertEqual(manager.api_host, self.address)
		
	def test_constructor_optional_args(self):
		"""
		Tests that a :class:`_NetworkManager` can be created with optional
		arguments for the networking and IO library.
		"""
		manager = NetworkManager(self.address, net_client=self.net,
			io_manipulator=self.io)
		
		self.assertEqual(manager.net, self.net)
		self.assertEqual(manager.io, self.io)
		
class TestNetworkManager(TestModule):
	def setUp(self):
		TestModule.setUp(self)
		self.manager = NetworkManager(
			self.address, net_client=self.net, io_manipulator=self.io
		)
		
class TestParseJson(TestNetworkManager):
	"""
	Contains tests for :meth:`_TopChefResource.parse_json`. Tests that the JSON
	parser works according to specifications
	"""
	def setUp(self):
		TestNetworkManager.setUp(self)
		
		self.json_string = '{"this": "is", "valid": "json", "number": 1, "boolean": true}'
		self.expected_dict = {"this": "is", "valid": "json", "number": 1, "boolean": True}
		
		self.bad_syntax_json = '{"this": "is", "bad", "json", "notice": "the", "comma"}'
		
		self.bad_json = 'Not a valid JSON'
		
	def test_parse_json(self):
		"""
		Tests that the parser is able to parse JSON correctly
		"""
		parsed_dict = self.manager._parse_json(self.json_string)
		
		self.assertEqual(self.expected_dict, parsed_dict)
		
	def test_parse_bad_syntax_json(self):
		"""
		Tests that the parser throws an appropriate exception if badly-formatted
		JSON is passed into it, but the JSON string still begins and ends with {}.
		This string resembles JSON, but it isn't quite right.
		"""		
		def _parsing_thunk(client, json):
			client._parse_json(json)
	
		self.assertRaises(
			ValueError, _parsing_thunk, self.manager, self.bad_syntax_json
		)
		
	def test_parse_bad_json(self):
		"""
		Tests that the client throws an exception if a string is passed
		that is a valid Python string, but does not evaluate to a dictionary.
		It is assumed that all JSON contains a key-value mapping as part of its
		top structure.
		"""
		def _parsing_thunk(client, json):
			client._parse_json(json)
	
		self.assertRaises(
			ValueError, _parsing_thunk, self.manager, self.bad_json
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
			client._parse_json(json)
			
		self.assertRaises(
			ValueError, _parsing_thunk, self.manager, json_to_parse
		)
		
	def test_parse_string_lambda(self):
		"""
		Tests that the word "lambda" is allowed if it's in a string. This tests
		that the lambda was escaped correctly.
		"""
		json_to_parse = '{"string": "lambda is a nice word"}'
		expected_dict = {'string': 'lambda is a nice word'}
		
		self.assertEqual(expected_dict, self.manager._parse_json(json_to_parse))

class TestWriteJson(TestNetworkManager):
	"""
	Contains unit tests for :meth:`_TopChefResource.write_json`
	"""
	def setUp(self):
		TestNetworkManager.setUp(self)
		self.expected_result = '{"boolean": true, "number": 1, "data": "string"}'
		self.dict_to_parse = {"data": "string", "number": 1, "boolean": True}
		
	def test_write_json(self):
		self.assertEqual(
			self.expected_result, self.manager._write_json(self.dict_to_parse)
		)		

class TestIsServerAlive(TestNetworkManager):
	"""
	Contains unit tests for :meth:`_TopChefResource.is_server_alive`
	"""	
	def test_is_alive_true(self):
		"""
		Tests that a response code of 200 will ensure that the
		method returns a True value
		"""
		self.net.mock_response_code = 200
		self.assertTrue(self.manager.is_server_alive())
		self._make_connection_assertions()
		
	def test_is_alive_false(self):
		"""
		Tests that a non-200 response code will make the method
		return False
		"""
		self.net.mock_response_code = 404
		self.assertFalse(self.manager.is_server_alive())
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

class TestReadResponseFromConnection(TestNetworkManager):
	def setUp(self):
		TestNetworkManager.setUp(self)
		
		self.connection = MockNetClient()
		self.expected_output = '{"data": "hello"}'
		self.input_stream = ['{', '"data": "hello"', '}', None]
		
		self.io._set_read_list(self.input_stream)
	
	def test_read_response_from_connection(self):
		response = self.manager._read_response_from_connection(self.connection)
		
		self.assertEqual(self.expected_output, response)
		
		self.assertEqual(
			self.connection.mock_details['getInputStream']['number_of_calls'], 1
		)
		self.assertEqual(
			self.io.mock_details['InputStreamReader']['number_of_calls'], 1
		)
		self.assertEqual(
			self.io.mock_details['InputStreamReader']['last_called_with'],
			self.connection
		)
	
		self.assertEqual(
			self.io.mock_details['BufferedReader']['number_of_calls'], 1
		)
		self.assertEqual(
			self.io.mock_details['BufferedReader']['last_called_with'],
			self.io
		)
		
		self.assertEqual(self.connection.mock_details['close']['number_of_calls'], 1)

class TestReadJsonFromConnection(TestNetworkManager):
	def mock_reader(self, connection):
		self.mock_reader_number_of_calls = self.mock_reader_number_of_calls + 1
		self.mock_reader_last_called_with = connection
		
		return self.mock_reader_output
		
	def setUp(self):
		TestNetworkManager.setUp(self)
		
		self.connection = MockNetClient()
		self.mock_reader_number_of_calls = 0
		self.mock_reader_last_called_with = None
		self.mock_reader_output = '{"data":"string"}'
		
		self.expected_output = {'data': 'string'}
		
		self.manager._read_response_from_connection = self.mock_reader
		
	def test_read_json_from_connection(self):
		self.assertEqual(
			self.expected_output,	
			self.manager._read_json_from_connection(self.connection)
		)

class TestWriteJsonToConnection(TestNetworkManager):
	
	def setUp(self):
		TestNetworkManager.setUp(self)

		self.json_to_write = {'data': 'hello'}
		
		self.mock_server_response = '{"data": "hello"}'
		self.mock_connection_list = []
		self.mock_number_of_calls = 0
		
		self.manager._read_response_from_connection = \
			self._mock_response_reader
	
	def _mock_response_reader(self, connection):
		self.mock_connection_list.append(connection)
		self.mock_number_of_calls = self.mock_number_of_calls + 1
		
		return self.mock_server_response	
	
	def test_write_json(self):
		self.manager._write_json_to_connection(
			self.json_to_write, self.net
		)
		
		self.assertEqual(
			2, self.net.mock_details['setRequestProperty']['number_of_calls']
		)
		self.assertEqual(
			{'Content-Type': 'application/json', 'Charset': 'utf-8'},
			self.net.mock_details['setRequestProperty']['request_props']
		)
		
		self.assertEqual(
			self.net.mock_details['getOutputStream']['number_of_calls'], 1
		),
		
		self.assertEqual(
			self.net.mock_details['close']['number_of_calls'], 1
		)
		self.assertEqual(
			self.net.mock_details['setRequestMethod']['number_of_calls'], 1
		)
		
		self.assertEqual(
			self.net.mock_details['setDoOutput']['number_of_calls'], 1
		)
		self.assertEqual(
			self.net.mock_details['setDoOutput']['value'], JAVA_TRUE
		)
		
	def test_write_json_custom_method(self):
		request_method = "PUT"
		
		self.manager._write_json_to_connection(
			self.json_to_write, self.net, method=request_method
		)
		
		self.assertEqual(
			self.net.mock_method, request_method
		)
		
class TestLoopback(TestNetworkManager):
	def mock_read(self, connection):
		return self.test_json

	def mock_write(self, text, connection):
		self.mock_write_number_of_calls = self.mock_write_number_of_calls + 1
	
	def setUp(self):
		TestNetworkManager.setUp(self)
		self.mock_write_number_of_calls = 0
		self.test_json = {'data': 'string'}
		
		self.manager._write_json_to_connection = self.mock_write
		self.manager._read_json_from_connection = self.mock_read

	def test_loopback(self):
		response = self.manager.loopback(self.test_json)
	
		self.assertEqual(response, self.test_json)
	
class TestOpenGetterConnection(TestNetworkManager):
	def setUp(self):
		TestNetworkManager.setUp(self)
		self.endpoint = '/some_place'
	
	def test_open_getter_connection(self):
		self.net.mock_response_code = 200
		
		connection = self.manager._open_getter_connection(self.endpoint)
		self.assertEqual(self.net, connection)
		
		self.assertEqual(
			self.net.mock_details['URL']['number_of_calls'], 1
		)
		self.assertEqual(
			self.net.mock_details['openConnection']['number_of_calls'], 1
		)
		
		self.assertEqual(
			self.net.mock_details['setRequestMethod']['number_of_calls'], 1
		)
		self.assertEqual(
			"GET", self.net.mock_method
		)
		
		self.assertEqual(
			self.net.mock_details['getResponseCode']['number_of_calls'], 1
		)
	
	def test_open_getter_connection_network_error(self):
		self.net.mock_response_code = 500
		
		def _testing_thunk(manager, url):
			manager._open_getter_connection(url)
			
		self.assertRaises(NetworkError, _testing_thunk, self.manager, self.endpoint)
		
		self.assertEqual(
			self.net.mock_details['getResponseCode']['number_of_calls'], 1
		)

class MockNetworkManager:
	def __init__(self):
		self.mock_details = {
			'_open_getter_connection': {
				'number_of_calls': 0,
				'url': None
			},
			'_read_json_from_connection': {
				'number_of_calls': 0,
				'data_to_read': {},
				'last_called_with': None
			},
			'_open_connection': {
				'number_of_calls': 0,
				'last_called_with': None
			},
			'setRequestMethod': {
				'number_of_calls': 0,
				'method': "GET"
			},
			'getResponseCode': {
				'number_of_calls': 0,
				'code': 200
			}
		}
		
	def set_data_to_read(self, new_json):
		self.mock_details['_read_json_from_connection']['data_to_read'] = new_json
		
	def _increment(self, attribute):
		self.mock_details[attribute]['number_of_calls'] = \
			self.mock_details[attribute]['number_of_calls'] + 1
		
	def _open_getter_connection(self, url):
		self._increment('_open_getter_connection')
		self.mock_details['_open_getter_connection']['url'] = url
		return self
		
	def _read_json_from_connection(self, connection):
		self._increment('_read_json_from_connection')
		self.mock_details['_read_json_from_connection']['last_called_with'] = \
			connection
		return self.mock_details['_read_json_from_connection']['data_to_read']
		
	def _open_connection(self, endpoint):
		self._increment('_open_connection')
		self.mock_details['_open_connection']['last_called_with'] = endpoint
		return self
		
	def setRequestMethod(self, new_method):
		self._increment('setRequestMethod')
		self.mock_details['setRequestMethod']['method'] = new_method

	def getResponseCode(self):
		self._increment('getResponseCode')
		return self.mock_details['getResponseCode']['code']

	def set_response_code(self, new_code):
		self.mock_details['getResponseCode']['code'] = new_code

class TestTopChefResourceConstructor(TestModule):
	"""
	Contains unit tests for :meth:`_TopChefResource.__init__`
	"""
	def setUp(self):
		TestModule.setUp(self)
		self.network_manager = NetworkManager(
			self.address, net_client=self.net, io_manipulator=self.io
		)
		
	def test_constructor_default_args(self):
		fixture = _TopChefResource(self.network_manager)
		
		self.assertEqual(fixture.net, self.network_manager)

class TestTopChefResource(TestModule):
	"""
	Base class for all tests on :class:`_TopChefResource`. This test sets
	up a _Resource with some basic parameters
	"""
	def setUp(self):
		TestModule.setUp(self)
		self.network_manager = _NetworkManager(
			self.address, net_client=self.net, io_manipulator=self.io
		)
		self.resource = _TopChefResource(self.address, self.network_manager)
		
class TestTopChefClient(TestModule):
	def setUp(self):
		TestModule.setUp(self)
		
		self.network_manager = MockNetworkManager()
		
		self.client = TopChefClient(self.network_manager)

class TestGetServiceIds(TestTopChefClient):
	def setUp(self):
		TestTopChefClient.setUp(self)
		self.service_ids = [
			'1d305560-6960-11e6-8591-001018737a6d', 
			'37bdb0be-6963-11e6-9860-001018737a6d'
		]
		self.json_from_api = {'data': [{'id': id} for id in self.service_ids]}
		self.network_manager.set_data_to_read(self.json_from_api)
		
	def test_get_service_ids(self):
		service_ids = self.client.get_service_ids()
		self.assertEqual(self.service_ids, service_ids)
		
		self.assertEqual(
			self.network_manager.mock_details\
				['_open_getter_connection']['number_of_calls'],
			1
		)
		self.assertEqual(
			self.network_manager.mock_details\
				['_read_json_from_connection']['number_of_calls'],
			1
		)
		
class TestGetJobIDs(TestTopChefClient):
	def setUp(self):
		TestTopChefClient.setUp(self)
		self.job_ids = [
			'1d305560-6960-11e6-8591-001018737a6d', 
			'37bdb0be-6963-11e6-9860-001018737a6d'
		]
		self.json_from_api = {'data': [{'id': job_id} for job_id in self.job_ids]}
		
		self.network_manager.set_data_to_read(self.json_from_api)
	
	def test_get_job_ids(self):
		job_ids = self.client.get_job_ids()
		
		self.assertEqual(self.job_ids, job_ids)
		self.assertEqual(
			self.network_manager.mock_details\
				['_open_getter_connection']['number_of_calls'],
			1
		)
		self.assertEqual(
			self.network_manager.mock_details\
				['_read_json_from_connection']['number_of_calls'],
			1
		)

class TestGetJobByID(TestTopChefClient):
	def setUp(self):
		TestTopChefClient.setUp(self)
		self.job_id = '1d305560-6960-11e6-8591-001018737a6d'
	
	def test_get_job_by_id(self):
		self.network_manager.set_response_code(200)
		
		job = self.client.get_job_by_id(self.job_id)
		
		self.assertEqual(job.id, self.job_id)
		self.assertEqual(job.__class__, TopChefJob)

	def test_get_job_by_id_404(self):
		self.network_manager.set_response_code(404)
		
		def _response_thunk(client, job_id):
			client.get_job_by_id(job_id)
		
		self.assertRaises(
			NetworkError, _response_thunk, self.client, self.job_id
		)
		
	def test_get_job_by_id_generic_error(self):
		self.network_manager.set_response_code(500)
		
		def _response_thunk(client, job_id):
			client.get_job_by_id(job_id)
		
		self.assertRaises(
			NetworkError, _response_thunk, self.client, self.job_id	
		)
		

blade_runner = UnitTestRunner([
	TestNetworkManagerConstructor('test_constructor_min_args'),
	TestNetworkManagerConstructor('test_constructor_optional_args'),
	
	TestParseJson('test_parse_json'),
	TestParseJson('test_parse_bad_syntax_json'),
	TestParseJson('test_parse_bad_json'),
	TestParseJson('test_parse_code_injection'),
	TestParseJson('test_parse_string_lambda'),
	
	TestWriteJson('test_write_json'),
	
	TestIsServerAlive('test_is_alive_true'),
	TestIsServerAlive('test_is_alive_false'),
	
	TestReadResponseFromConnection('test_read_response_from_connection'),
	
	TestReadJsonFromConnection('test_read_json_from_connection'),
	
	TestWriteJsonToConnection('test_write_json'),
	TestWriteJsonToConnection('test_write_json_custom_method'),
	
	TestLoopback('test_loopback'),
	
	TestOpenGetterConnection('test_open_getter_connection'),
	TestOpenGetterConnection('test_open_getter_connection_network_error'),
	
	TestTopChefResourceConstructor('test_constructor_default_args'),
	
	TestGetServiceIds('test_get_service_ids'),
	
	TestGetJobIDs('test_get_job_ids'),
	
	TestGetJobByID('test_get_job_by_id'),
	TestGetJobByID('test_get_job_by_id_404'),
	TestGetJobByID('test_get_job_by_id_generic_error')
])

blade_runner.run_with_callback(MSG)
