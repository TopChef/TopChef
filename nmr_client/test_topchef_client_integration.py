"""
Contains integration tests for :mod:`topchef_client`
"""
import sys

LIBRARY_PATH = '/opt/topspin/exp/stan/nmr/py/user'

sys.path.append(LIBRARY_PATH)

import unittest
from topchef_client import TopChefClient
from unit_test_runner import UnitTestRunner

True = "1"					# Horrible hack to bring Booleans back into this Jython
False = "0"					#

class TestClient(unittest.TestCase):
	def setUp(self):
		self.host = 'http://192.168.1.39'
		self.client = TopChefClient(self.host)
		
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

running_man = UnitTestRunner([
	TestIsServerAlive('test_is_server_alive'),
	TestGetJobIDs('test_get_job_ids')
])
running_man.run_with_callback(MSG)