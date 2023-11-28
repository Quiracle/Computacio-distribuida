from kafka import KafkaConsumer
import random
import logging
import json
import os
import Config
import time
from influxdb import InfluxDBClient

DB_HOST = os.environ.get('DB_HOST', 'influxdb')
DB_PORT = os.environ.get('DB_PORT', 8086)
DB_USER = os.environ.get('DB_USER', 'admin')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Password1')
DB_NAME = os.environ.get('DB_NAME', 'mydb')

broker_kafka = os.environ.get('KAFKA_BROKER', 'kafka:9092')  # Coloca la dirección de tus brokers Kafka
kafka_topic = Config.KAFKA_TOPIC_RECEIVE
kafka_group = Config.KAFKA_GROUP_ID

def connect_kafka_consumer():
    return KafkaConsumer(
        bootstrap_servers=broker_kafka,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id=kafka_group,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        security_protocol='SASL_PLAINTEXT',
        sasl_mechanism='PLAIN',
        sasl_plain_username='admin',
        sasl_plain_password='admin-secret',
    )

def connect_db():
    client = InfluxDBClient(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)
    client.create_database(DB_NAME)
    client.get_list_database()
    client.switch_database(DB_NAME)
    return client

def save(client, message):
    json_payload = []
    data = {
    "measurement": "iotdata",
    "time": message.pop('timestamp'),
    "fields": message
    }
    json_payload.append(data)

    #Send our payload
    client.write_points(json_payload)

def run():
    time.sleep(20)
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)

    consumer_kafka = connect_kafka_consumer()
    consumer_kafka.subscribe(kafka_topic)
    logging.info(f'Subscribed to topic: {kafka_topic}')

    influx_client = connect_db()
    for message in consumer_kafka:
        status = message.topic.split('-')[1]
        message = message.value
        message['status'] = status
        logging.info(f"{message} is being saved")
        save(influx_client, message)
if __name__ == '__main__':
    run()