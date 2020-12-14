import os
import sys
import time
import json
from typing import Dict
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT

# Obtain the location of the rti.routing module so can configure the
# path for Python to find it. This is useful if rti.routing is not
# installed as Python package
PROC_MODULE_PATH = os.getenv("RTI_PROC_MODULE_PATH")
if PROC_MODULE_PATH:
    sys.path.append(os.path.abspath(PROC_MODULE_PATH))
else:
    # consider default location wthin the install dir <root_dir>/dist
    sys.path.append(os.path.abspath("../../../dist/modules"))

from rti.routing import proc
from rti.routing import service


ENDPOINT = "a28hekebdxkvd3-ats.iot.us-west-2.amazonaws.com"
CLIENT_ID = "rti_connext_gw"
PATH_TO_CERT = "rti_connext_gw.cert.pem"
PATH_TO_KEY = "rti_connext_gw.private.key"
PATH_TO_ROOT = "root-CA.crt"

class AwsIotConnector(proc.Processor):
    def __init__(self, route: proc.Route, properties : Dict):
        # # Spin up resources
        self.mqtt_connection = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
        self.mqtt_connection.configureEndpoint(ENDPOINT, 8883)
        self.mqtt_connection.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)
        self.mqtt_connection.connect()

    def on_data_available(self, route) -> None:
        for input in route.inputs:
            topic_name = input.info["stream_info"]["stream_name"]
            with input.take() as samples:
                for sample in samples:
                    sample_out = {"data" : sample.data, "info:" : sample.info}
                    self.mqtt_connection.publish(topic_name, json.dumps(sample_out), 0)


def create_processor(route: proc.Route, properties: Dict) -> proc.Processor:
    return AwsIotConnector(route, properties)