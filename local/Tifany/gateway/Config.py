import random

MQTT_TOPIC_RECEIVE = ['actuators/light_bulb/state', 
                      'actuators/heat_pump/state',
                      'sensors/presence_sensor/state',
                      'sensors/temperature_sensor/state',]
MQTT_CLIENT_ID = f'python-mqtt-{random.randint(0, 1000)}'
USER_NAME = "Tifany"

KAFKA_TOPIC = 'sensors-raw'
KAFKA_CLIENT_ID = f'python-kafka-{random.randint(0, 1000)}'

MQTT_TOPICS = {"heat_pump": "actuators/heat_pump/action",
               "light_bulb": "actuators/light_bulb/action",}
