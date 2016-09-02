"""
Contains a client to access the TopChef API.

	* Don't use classes or methods beginning with an underscore ``_``. By
	  convention, these are "private" attributes. This means that their APIs
	  and methods may be subject to change, or are too granular to be 
	  effectively used outside this module. Python assumes that code is used 
	  by consenting adults, and makes no effort to hide these methods from you.
"""
import sys

LIBRARY_PATH = '/opt/topspin/exp/stan/nmr/py/user'

sys.path.append(LIBRARY_PATH)

import java.net
import java.io
import java.lang.Boolean.TRUE as JAVA_TRUE
import java.lang.Boolean.FALSE as JAVA_FALSE

import time

dict = {}.__class__ # Horrible hack to get the class from which dictionaries
										# derive
True = "1"
False = "0"


class NetworkError(IOError, RuntimeError):
	"""
	Exception thrown when a resource is unable to connect to the TopChef API
	"""
	pass

class ValidationError(ValueError):
	"""
	Exception thrown when a JSON object fails to validate against a JSON Schema
	"""
	def __init__(self, message, context, *args, **kwargs):
		ValueError.__init__(self, *args, **kwargs)
		self.message = message
		self.context = context
	
	def __str__(self):
		return 'message=%s. context=%s' % (self.message, self.context)

class JobNotReady(Exception):
	"""
	Thrown if the job results are not yet ready
	"""
	pass
	
class TimeoutError(NetworkError):
	"""
	Thrown if the request to get job results times out
	"""
	pass
	
class NetworkManager:
	"""
	Utility responsible for parsing JSON, as well as communicating with the
	API using the java.net API
	"""
	def __init__(self, api_host, net_client=java.net, io_manipulator=java.io):
		"""
		Initialize a network manager for the given hostname, using a
		networking library and I/O reader
		"""
		self.api_host = api_host
		self.net = net_client
		self.io = io_manipulator
		
	def _parse_json(self, json_string):
		"""
		Parse a string into a JSON dictionary
		"""
		true = True
		false = False
		null = None
		
		sanitized_string = json_string.replace('lambda', '" + "lambda" + "')
		
		try:
			parsed_json = eval(sanitized_string)
		except SyntaxError, NameError:
			raise ValueError('The string %s is not valid JSON')
		
		if not isinstance(parsed_json, dict):
			raise ValueError('The string %s is not valid JSON')
		
		return parsed_json

	def _write_json(self, json_dict):
		"""
		Write the dictionary to JSON.
		"""
		json_string = str(
			json_dict
		).replace(
			"'", '"'
		).replace(
			'"1"', 'true'
		).replace(
			'"0"', 'false'
		).replace(
			'None', 'null'
		)
		
		return json_string
		
	def is_server_alive(self):
		"""
		Pings the server over HTTP to check if the server is alive
		"""
		url = self.net.URL('%s/' % self.api_host)
		connection = url.openConnection()
		connection.setRequestMethod("GET")
		
		connection.connect()
		status_code = connection.getResponseCode()
		
		if (status_code == 200):
			return True
		else:
			return False
			
	def _read_json_error_stream(self, connection):
		connection_stream = connection.getErrorStream()
		stream_reader = self.io.InputStreamReader(connection_stream)
		stream_buffer = self.io.BufferedReader(stream_reader)
		
		input_line = stream_buffer.readLine()
		data = []
	
		while input_line is not None:
			data.append(str(input_line))
			input_line = stream_buffer.readLine()
			
		connection_stream.close()
		
		return self._parse_json(''.join(data))
			
	def _read_response_from_connection(self, connection):
		"""
		Using the provided connection, pull the connection's input
		stream into a buffer and concatentate the connection's input
		stream into a large string for processing. For the HTTP library,
		the input stream consists of the characters in the body of the HTTP
		request
		
		:param connection: An object of type java.net.URLConnection on which
			processing needs to be done
		:return: A string representing the body of the HTTP request
		:rtype: str
		"""
		connection_stream = connection.getInputStream()
		stream_reader = self.io.InputStreamReader(connection_stream)
		stream_buffer = self.io.BufferedReader(stream_reader)
		
		input_line = stream_buffer.readLine()
		data = []
		
		while input_line is not None:
			data.append(str(input_line))
			input_line = stream_buffer.readLine()
			
		connection_stream.close()
		
		return ''.join(data)

	def _read_json_from_connection(self, connection):
		"""
		Read the input stream from a connection
		
		:param connection: The connection to the required web resource
		"""
		return self._parse_json(
			self._read_response_from_connection(connection)
		)

	def _write_json_to_connection(self, json_to_write, connection, method="POST"):
		"""
		Take in an input dictionary, and an HTTP connection, and write
		the required JSON to the request.
		
		:param json_to_write: A dictionary representing the JSON that must
			be written to the API
		:param connection: An object of type java.net.URLConnection that is
			used to carry out the writing procedure
		:param method: A string representing the method to use when writing.
			by default, this is "POST"
		"""		
		connection.setRequestProperty("Content-Type", "application/json")
		connection.setRequestProperty("Charset", "utf-8")
		
		connection.setRequestMethod(method)
		
		connection.setDoOutput(JAVA_TRUE)
		
		json_string = self._write_json(json_to_write).encode('utf-8')
		
		stream = connection.getOutputStream()
		stream.write(json_string)
		
		stream.close()
		
	def loopback(self, test_json):
		"""
		Fire a request to the /echo endpoint with some JSON. Returns the
		response from the server
		"""
		url = self.net.URL('%s/echo' % (self.api_host))
		connection = url.openConnection()
		
		self._write_json_to_connection(test_json, connection)
		status_code = connection.getResponseCode()
		
		assert status_code == 200
		    
		response = self._read_json_from_connection(connection)
		return response
	
	def _open_connection(self, endpoint):
		url = self.net.URL('%s%s' % (self.api_host, endpoint))
		connection = url.openConnection()
		return connection
	
	def _open_getter_connection(self, endpoint):
		"""
		Safely open an HTTP connection to an API endpoint. The endpoint is
		prepended to the hostname that this API is tasked to manage
		
		:param str url_string: The URL to which this connection must connect
		"""
		url = self.net.URL('%s%s' % (self.api_host, endpoint))
		
		connection = url.openConnection()
		connection.setRequestMethod("GET")
		
		status_code = connection.getResponseCode()
		
		if (status_code != 200):
			raise NetworkError("Unable to get 200 OK response from %s" % url)
		else:
			return connection

class _TopChefResource:
	"""
	Abstract (as far as Jython 2.2 will let me *grumble grumble*) class that
	provides methods for manipulating network resources using the Java HTTP API. 
	This class contains methods for reading from resources and parsing JSON.
	
	Don't use this class directly in production. TopChefClient and related
	resources will provide a much friendlier user experience.
	"""	
	VALIDATION_ENDPOINT = '/validator'
	SERVICES_ENDPOINT = '/services'
	JOBS_ENDPOINT = '/jobs'

	def __init__(self, network_manager):
		"""
		Initialize a resource, passing in the required libraries.
		
		:param str api_host: The hostname to which the client should attempt a 
			connection
		:param net_client: The library that will be used in this client to create
			and manage HTTP connections. Defaults to ``java.net``
		:param io_manipulator: The I/O client that will be used to read and process
			character streams resulting from HTTP connections
		"""
		self.net = network_manager
		
	def validate_json_schema(self, object, schema):
		"""
		Use the API's JSON Schema validator to validate the dictionary ```object```
		against the dictionary ```schema```.
		"""
		data_to_send = {'object': object, 'schema': schema}
		
		connection = self.net._open_connection(self.VALIDATION_ENDPOINT)
		
		self.net._write_json_to_connection(data_to_send, connection, method="POST")
		
		status_code = connection.getResponseCode()
		
		if (status_code == 400):
			response = self.net._read_json_error_stream(connection)
			self._handle_validation_error(response)
		elif (status_code != 200):
			raise NetworkError(
				'Unable to connect to validator. Request returned status %d' % (
				status_code)
			)
			
	def _handle_validation_error(self, response):
		message = response['errors']['message']
		context = response['errors']['context']
		
		raise ValidationError(message, context)
		
	
class TopChefClient(_TopChefResource):
	"""
	Contains methods concerning the operation of the entire TopChef service
	as a whole.
	"""
	def loopback(self, json_to_loop):
		return self.net.loopback(json_to_loop)
		
	def is_server_alive(self):
		return self.net.is_server_alive()
			
	def get_service_ids(self):
		"""
		Returns the ID of all services registered with the API at the client's host
		"""
		connection = self.net._open_getter_connection(self.SERVICES_ENDPOINT)
		response = self.net._read_json_from_connection(connection)
		service_ids = [service['id'] for service in response['data']]
		
		return service_ids

	def get_service_by_id(self, service_id):
		url = '%s/%s' % (self.SERVICES_ENDPOINT, service_id)
		connection = self.net._open_getter_connection(url)
				
		status_code = connection.getResponseCode()
		
		if (status_code == 404):
			raise NetworkError(
				'404 response. The service with id %s does not exist' % 
				service_id
			)
		elif (status_code == 200):
			return TopChefService(service_id, self.net)
		else:
			raise NetworkError(
				'Unable to get service with id %s. Status code %d' % (
					service_id, status_code
				)
			)

	def get_job_ids(self):
		connection = self.net._open_getter_connection(self.SERVICES_ENDPOINT)
		job_list = self.net._read_json_from_connection(connection)['data']		
		job_ids = [job['id'] for job in job_list]
		
		return job_ids

	def get_job_by_id(self, job_id):
		api_endpoint = '%s/%s' % (self.JOBS_ENDPOINT, job_id)
		
		connection = self.net._open_connection(self.JOBS_ENDPOINT)
		connection.setRequestMethod("GET")
		
		status_code = connection.getResponseCode()
		
		if (status_code == 404):
			raise NetworkError(
				'404 response. The job with id %s does not exist' % (
				job_id
			))
		elif (status_code == 200):
			return TopChefJob(job_id, self.net)
		else:
			raise NetworkError(
				'Unable to get job with id %s. Status code %d' % (
				job_id, status_code
			))

class TopChefService(_TopChefResource):
	"""
	Class representing a TopChef Service
	"""			
	def __init__(self, service_id, network_manager):
		_TopChefResource.__init__(
			self, network_manager
		)
		self.id = service_id
		
	def _get_service_dictionary(self):
		endpoint = '%s/%s' % (self.SERVICES_ENDPOINT, self.id)
		
		connection = self.net._open_getter_connection(endpoint)
		response = self.net._read_json_from_connection(connection)['data']
		
		return response
		
	def has_timed_out(self):
		dict = self._get_service_dictionary()
		return dict['has_timed_out']
			
		
	def request_job(self, job_parameters):
		"""
		Check with the server to see if the provided dictionary satisfies the
		job schema, and then send it to the server.
		"""
		endpoint = '%s/%s/jobs' % (self.SERVICES_ENDPOINT, self.id)
		
		job_details = self._get_service_dictionary()
		
		schema_to_validate = job_details['job_registration_schema']
		
		self.validate_json_schema(job_parameters, schema_to_validate)
		
		data_to_write = {'parameters': job_parameters}
		
		connection = self.net._open_connection(endpoint)
		self.net._write_json_to_connection(
			data_to_write, connection, method="POST"
		)
		
		status_code = connection.getResponseCode()
		
		if (status_code != 201):
			raise NetworkError(
				'Status code %s. Unable to request job with parameters %s' % (
				status_code, job_parameters
				))
		else:
			response = self.net._read_json_from_connection(connection)
			job_id = response['data']['job_details']['id']
			
			return TopChefJob(job_id, self.net)
			
	def get_job_result_schema(self):
		job_details = self._get_service_dictionary()
		return job_details['job_result_schema']
			
	def get_result_for_job(self, job, polling_interval=10, timeout=30):
		"""
		Return the result for a particular job, waiting until the job is
		complete. Prior to returning the result, validate the result against the
		job result schema for the service. If it does not match, throw a
		ValidationError.
		
		:param TopChefJob job: The job for which the result is to be obtained
		:param int polling interval: The amount of time in seconds 
			that the client should wait before trying to ask for the job results
		:param int timeout: The amount of time in seconds that the client should
			wait for the job results. It is best to give more time for the client to
			get the results than is necessary. If the timeout has expired, a TimeoutError
			will be thrown.
			
		"""
		job.wait_until_result(polling_interval=polling_interval, timeout=timeout)
		result = job.get_result()
		self.validate_json_schema(result, self.get_job_result_schema())
		return result
					
			
class TopChefJob(_TopChefResource):
	"""
	Class Representing a TopChef Job
	"""
	def __init__(self, job_id, network_manager):
		_TopChefResource.__init__(
			self, network_manager
		)
		self.id = job_id
	
	def _get_job_dict(self):
		endpoint = '%s/%s' % (self.JOBS_ENDPOINT, self.id)
		
		connection = self.net._open_getter_connection(endpoint)
		
		response = self.net._read_json_from_connection(connection)
		
		return response['data']

	def is_result_available(self):
		details = self._get_job_dict()
		
		if details['status'] == 'COMPLETED':
			return True
		else:
			return False
		
	def get_result(self):
		details = self._get_job_dict()
		
		if details['status'] != 'COMPLETED':
			raise JobNotReady('The job %s was not yet completed' % self.id)
		
		return details['result']
		
	def wait_until_result(self, polling_interval=10, timeout=30):
		"""
		Wait until a job result is available.
		"""
		starting_time = time.time()
		
		has_timed_out = (time.time() - starting_time) > timeout
	
		while not has_timed_out and (self.is_result_available() == False):
			has_timed_out = (time.time() - starting_time) > timeout
			time.sleep(polling_interval)
			continue
			
		if (self.is_result_available() == True):
			return self.get_result()
		else:
			raise TimeoutError('The request for job %s has timed out' % self.id)
		
