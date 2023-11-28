import random

POSSIBLE_STATES = range(15, 30)
MQTT_TOPIC_SEND = 'sensors/temperature_sensor/state'
CLIENT_ID = f'python-mqtt-{random.randint(0, 1000)}'
DEVICE_NAME = 'temperature_sensor'