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

dict = {}.__class__ # Horrible hack to get the class from which dictionaries
										# derive
True = "1"					# Horrible hack to bring Booleans back into this Jython
False = "0"					#


class NetworkError(IOError, RuntimeError):
	"""
	Exception thrown when a resource is unable to connect to the TopChef API
	"""
	pass
	
class _TopChefResource:
	"""
	Abstract (as far as Jython 2.2 will let me *grumble grumble*) class that
	provides methods for manipulating network resources using the Java HTTP API. 
	This class contains methods for reading from resources and parsing JSON.
	
	Don't use this class directly in production. TopChefClient and related
	resources will provide a much friendlier user experience.
	"""
	def __init__(self, api_host, net_client=java.net, io_manipulator=java.io):
		"""
		Initialize a resource, passing in the required libraries.
		
		:param str api_host: The hostname to which the client should attempt a 
			connection
		:param net_client: The library that will be used in this client to create
			and manage HTTP connections. Defaults to ``java.net``
		:param io_manipulator: The I/O client that will be used to read and process
			character streams resulting from HTTP connections
		"""
		self.api_host = api_host
		self.net = net_client
		self.io = io_manipulator

	def parse_json(self, json_string):
		"""
		Parse a string into a JSON dictionary
		"""
		true = "1"
		false = "0"
		
		sanitized_string = json_string.replace('lambda', '" + "lambda" + "')
		
		try:
			parsed_json = eval(sanitized_string)
		except SyntaxError, NameError:
			raise ValueError('The string %s is not valid JSON')
		
		if not isinstance(parsed_json, dict):
			raise ValueError('The string %s is not valid JSON')
		
		return parsed_json


class TopChefClient(_TopChefResource):
	"""
	Contains methods concerning the operation of the entire TopChef service
	as a whole.
	"""
	JOBS_ENDPOINT = '/jobs'
			

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
			
	def get_job_ids(self):
		url = self.net.URL('%s%s' % (self.api_host, self.JOBS_ENDPOINT))
		
		connection = url.openConnection()
		connection.setRequestMethod("GET")
		
		status_code = connection.getResponseCode()
		
		if (status_code != 200):
			raise NetworkError('Unable to get a 200 OK response from %s' % url)
		
		
		
	def get_job_by_id(self, job_id):
		pass

class TopChefJob:
	pass