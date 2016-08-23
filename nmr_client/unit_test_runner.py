"""
Created by Michal Kononenko

This file implements a simple test runner for running unit tests on
Jython code on this machine, built with the `unittest`_ library for
Python. The runner uses TopSpin's MSG function to output a run report
for test cases, covering which cases failed or errored.

If a test case fails or errors out, then the MSG report will include a stack
trace of the failure
"""
import unittest
import traceback

class UnitTestRunner:
	"""
	Responsible for running unit tests. The library supports loading in test
	cases, and running these test cases. Output can be done to a string or to
	a TopSpin message
	"""
	def __init__(self, test_cases):
		"""
		Initialize the runner by registering a list of test cases
		"""
		self.test_cases = test_cases
		
	def register_case(self, test_case):
		"""
		Append a case
		"""
		self.test_cases.append(test_case)
	
	def _run_tests(self):
			result_feed = unittest.TestResult()
			
			for test in self.test_cases:
				test.run(result_feed)
			
			return result_feed
			
	def _process_results(self, result):
			if not (result.failures or result.errors):
				run_report = 'PASSED \n ran %s tests' % result.testsRun
				return run_report
			else:
				run_report = 'FAILED \n'
	
			if result.failures:
	 			run_report = run_report + 'failures %s \n' % len(result.failures)
	
			if result.errors:
				run_report = run_report + 'errors %s \n' % len(result.errors)
				
			run_report = run_report + 'DETAILS \n\n Failures: \n\n'
			
			for failure in result.failures:
				run_report = run_report + '    %s\n %s\n %s\n\n' % (
					failure[0].__repr__(), str(failure[1][0]), traceback.extract_tb(failure[1][2])
				)
			
			run_report = run_report + 'Errors: \n\n'
			
			for error in result.errors:
				run_report = run_report + '    \%s\n %s\n %s\n\n' % (
					error[0].__repr__(), str(error[1][0]), traceback.extract_tb(error[1][2])
				)
				
			run_report = run_report + 'Tests Ran: %s' % result.testsRun

			return run_report
		
	def run(self):
			return self._process_results(self._run_tests())
		
	def run_with_callback(self, callback):
			callback(self.run())