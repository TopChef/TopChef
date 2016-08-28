"""
Contains a base class for a client capable of working with the TopChef
client
"""
import threading
import requests
import abc
import six


@six.add_metaclass(abc.ABCMeta)
class Client(object):

    def __init__(self, address, service_id):
        """
        Initialize a client to listen on a server
        and look for jobs for the next service id
        
        :param str address: The hostname of the topchef API on which
            the client is to listen
        :param str service_id: The ID of the service that this client
            represents
        """
        self.address = address
        self.id = service_id

    @abc.abstractmethod
    def run(self, parameters):
        raise NotImplementedError

