"""
Contains a client to access the TopChef API. This is a trial implementation
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

class TopChefClient:
	def __init__(self, api_host, net_client=java.net, io_manipulator=java.io):
		"""
		Start up a client
		
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
