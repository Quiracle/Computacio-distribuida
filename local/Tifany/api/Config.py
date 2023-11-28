import random

MQTT_CLIENT_ID = f'python-mqtt-{random.randint(0, 1000)}'
MQTT_TOPICS = {"heat_pump": "actuators/heat_pump/action",
               "light_bulb": "actuators/light_bulb/action",}