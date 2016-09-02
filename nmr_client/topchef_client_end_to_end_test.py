import sys
import time

LIBRARY_PATH = '/opt/topspin/exp/stan/nmr/py/user'

sys.path.append(LIBRARY_PATH)

from topchef_client import NetworkManager
from topchef_client import TopChefService

True = "1"
False = "0"

server_address = 'http://192.168.1.216/dev'
adder_service_id = '1cb40868-101f-11d9-9a55-000cf18a2ce6'

network = NetworkManager(server_address)

service = TopChefService(adder_service_id, network)

assert (service.has_timed_out() == False)

parameters = {'value': 10}

job = service.request_job(parameters)

result = service.get_result_for_job(job, polling_interval=5, timeout=30)

MSG(str(result))
