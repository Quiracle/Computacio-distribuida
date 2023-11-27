from kafka import KafkaConsumer
import random
import logging
import json
import os
import Config

broker_kafka = os.environ.get('KAFKA_BROKER', 'kafka:9092')  # Coloca la dirección de tus brokers Kafka
kafka_topic = Config.KAFKA_TOPIC_RECEIVE
kafka_group = Config.KAFKA_GROUP_ID

def connect_kafka_consumer():
    return KafkaConsumer(
        bootstrap_servers=broker_kafka,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id=kafka_group,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

def run():
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)

    consumer_kafka = connect_kafka_consumer()
    consumer_kafka.subscribe(kafka_topic)
    logging.info(f'Subscribed to topic: {kafka_topic}')
    for message in consumer_kafka:
        message = message.value
        logging.info(f"{message} is being saved")
if __name__ == '__main__':
    run()