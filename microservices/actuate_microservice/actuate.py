from kafka import KafkaConsumer
import random
import logging
import json
import Config

import logging
import time
import json
import random
from datetime import datetime
import pytz
import os
import requests

kafka_broker = os.environ.get('KAFKA_BROKER', 'kafka:9092') # Coloca la dirección de tus brokers Kafka
kafka_topic_receive = Config.KAFKA_TOPIC_RECEIVE
CLIENT_ID_KAFKA = Config.CLIENT_ID_KAFKA
kafka_group = Config.KAFKA_GROUP_ID

def connect_kafka_consumer():
    return KafkaConsumer(
        kafka_topic_receive,
        bootstrap_servers=kafka_broker,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id=kafka_group,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

def neededAction(msg):
    value = None
    device = None
    
    if msg["device"] == "presence_sensor":
        device = "light_bulb"
        if msg["value"] >= 50:
            value = 1
        else:
            value = 0
    elif msg["device"] == "temperature_sensor":
        device = "heat_pump"
        if msg["value"] <= 20:
            value = 20
        if msg["value"] >= 24:
            value = 24

    return value, device

def actuate(msg, client, mqtt_topic="actuators/heat_pump/action"):
    msg = json.dumps(msg)
    result = client.publish(mqtt_topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        logging.info(f"Send `{msg}` to topic `{mqtt_topic}`")
    else:
        logging.error(f"Failed to send message to topic {mqtt_topic}")

def run():
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)

    consumer_kafka = connect_kafka_consumer()
    for message in consumer_kafka:
        message = message.value
        logging.info(f"{message} is being processed")
        value, device = neededAction(message)
        if value is not None:
            response = requests.post(f'{Config.USER_API_URL[message["user"]]}:80/actuate/{device}/{value}', {})
if __name__ == '__main__':
    run()