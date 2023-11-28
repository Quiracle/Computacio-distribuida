from kafka import KafkaConsumer
from kafka import KafkaProducer
import random
import logging
import json
import os
import Config
import time

kafka_broker = os.environ.get('KAFKA_BROKER', 'kafka:9092') # Coloca la dirección de tus brokers Kafka
topic_kafka_receive = Config.KAFKA_TOPIC_RECEIVE
topic_kafka_send = Config.KAFKA_TOPIC_SEND
CLIENT_ID_KAFKA = Config.CLIENT_ID_KAFKA
kafka_group = Config.KAFKA_GROUP_ID


def connect_kafka_consumer():
    return KafkaConsumer(
        topic_kafka_receive,
        bootstrap_servers=kafka_broker,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id=kafka_group,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        security_protocol='SASL_PLAINTEXT',
        sasl_mechanism='PLAIN',
        sasl_plain_username='admin',
        sasl_plain_password='admin-secret',
        )

def isAccepted(msg):
    logging.info(f"{msg} is being validated")
    if msg["device"] == "presence_sensor":
        return msg["value"] >= 0 and msg["value"] <= 100
    if msg["device"] == "temperature_sensor":
        return msg["value"] >= 18 and msg["value"] <= 28
    return False

def run():
    time.sleep(20)
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)

    consumer_producer_kafka = connect_kafka_consumer()
    my_producer = KafkaProducer(
        bootstrap_servers='kafka:9092',
        api_version=(0,11,5),
        value_serializer=lambda x: json.dumps(x).encode('utf-8'),
        security_protocol='SASL_PLAINTEXT',
        sasl_mechanism='PLAIN',
        sasl_plain_username='admin',
        sasl_plain_password='admin-secret',
    )
    for message in consumer_producer_kafka:
        message = message.value
        if isAccepted(message):
            logging.info(f"{message} is being published")
            my_producer.send(topic_kafka_send, value=message)
        
if __name__ == '__main__':
    run()