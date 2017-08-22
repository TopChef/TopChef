Consuming the API
=================

In order to design implementations of services, we must poll the API
regularly in order to let TopChef know that the server is still up. This
will be done by sending PATCH requests without the ``Content-Type`` header
and without a request body. The ``service_timeout`` parameter describes how
much time will pass before TopChef considers a service dead. The best way to
do this is by thread-based programming. For Python, the
:mod:`topchef_client` will take care of polling the service.

An example of Python 2-compliant code that implements a service is given below.
Python 3 programmers should avoid using this code, instead creating tasks
for :mod:`concurrent.futures`. This will do a much better job of separating
concerns of functionality (what the thing does) versus execution policy (how
 the task is run).

.. sourcecode:: python

    import requests
    from time import sleep
    from threading import Thread

    class Service(object):
        """
        Defines a service
        """
        def __init__(self, topchef_service_url):
            """
            Create two threads. One will be checking for new jobs, and one
            will be polling the service to make sure that it is not dead.
            Both threads are daemon (read "demon") threads. This means that
            these threads will not prevent the program from terminating, and
            will be terminated by the Python interpreter after all other
            non-daemon threads have been terminated.

            :param topchef_service_url: The URL to the
                ``/services/<service_id>`` endpoint of the TopChef API.
            """
            self._url = topchef_service_url
            self._polling_thread = Thread(
                target=self._checkin_loop
            )
            self._new_job_thread = Thread(
                target=self._new_job_loop
            )

            self._polling_thread.daemon = True
            self._new_job_thread.daemon = True

        def start(self):
            """
            Start all the background threads
            """
            self._polling_thread.start()
            self._new_job_thread.start()

        def stop(self):
            """
            Stop all the background threads
            """
            self._polling_thread.stop()
            self._new_job_thread.stop()

        def poll_service(self):
            """
            Poll the service
            """
            response = requests.patch(
                self._url
            )
            assert response.status_code == 200

        def check_for_new_jobs(self):
            """
            Check if there are new jobs. If there are, run the job callback
            with the new data
            """
            url_to_check = '%s/next' % self._url

            response = requests.get(
                url_to_check, headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                self.handle_new_job(response.get_json())

        def handle_new_job(self, job_data):
            """
            Handler that does something with the new job

            :param job_data: The new job data
            """

        def _new_job_loop(self, polling_interval=3):
            """
            Run a loop to check for new jobs, polling every certain amount
            of seconds

            :param polling_interval: The time to elapse before checking for
                new jobs
            """
            while True:
                self.check_for_new_jobs()
                sleep(polling_interval)

        def _checkin_loop(self, polling_interval=30):
            """
            Check in with the service to let it know that it's not dead
            """
            while True:
                self.poll_service()
                sleep(polling_interval)
