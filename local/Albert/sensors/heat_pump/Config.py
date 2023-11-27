import random

POSSIBLE_STATES = [20, 24]
MQTT_TOPIC_SEND = 'actuators/heat_pump/state'
MQTT_TOPIC_RECEIVE = 'actuators/heat_pump/action'
CLIENT_ID = f'python-mqtt-{random.randint(0, 1000)}'
DEVICE_NAME = 'heat_pump'