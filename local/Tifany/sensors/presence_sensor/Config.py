import random

POSSIBLE_STATES = range(-10, 110)
MQTT_TOPIC_SEND = 'sensors/presence_sensor/state'
CLIENT_ID = f'python-mqtt-{random.randint(0, 1000)}'
DEVICE_NAME = 'presence_sensor'