import random

POSSIBLE_STATES = [0, 1]
MQTT_TOPIC_SEND = 'actuators/light_bulb/state'
MQTT_TOPIC_RECEIVE = 'actuators/light_bulb/action'
CLIENT_ID = f'python-mqtt-{random.randint(0, 1000)}'
DEVICE_NAME = 'light_bulb'