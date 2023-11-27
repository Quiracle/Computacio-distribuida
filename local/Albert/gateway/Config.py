import random

MQTT_TOPIC_RECEIVE = ['actuators/light_bulb/state', 
                      'actuators/heat_pump/state',
                      'sensors/presence_sensor/state',
                      'sensors/temperature_sensor/state',]
MQTT_CLIENT_ID = f'python-mqtt-{random.randint(0, 1000)}'
USER_NAME = "Albert"

KAFKA_TOPIC = 'sensor-raw'
KAFKA_CLIENT_ID = f'python-kafka-{random.randint(0, 1000)}'