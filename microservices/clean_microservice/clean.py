from kafka import KafkaConsumer
from kafka import KafkaProducer
import random
import logging
import json

broker_kafka = 'kafka:9092'  # Coloca la dirección de tus brokers Kafka
topic_kafka = "sensors-raw"
topic_kafka_clean = "sensors-clean"
CLIENT_ID_KAFKA = f'python-kafka-{random.randint(0, 1000)}-1'

def connect_kafka_consumer():
    return KafkaConsumer(
        topic_kafka,
        bootstrap_servers='kafka:9092',
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='my-group1',
        api_version=(0, 11, 5),
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def publish_message(producer, topic, key, message):
    producer.produce(topic, key=key, value=json.dumps(message))
    producer.flush()


def isAccepted(msg):
    if msg["dispositive"] == "presence_sensor":
        return msg["value"] == 1
    if msg["dispositive"] == "temperature_sensor":
        return msg["value"] > 20 and msg["value"] < 30
    if msg["dispositive"] == "heat_pump":
        return msg["value"] > 20 and msg["value"] < 30
    if msg["dispositive"] == "light_bulb":
        return msg["value"] == 1

def subscribe(consumer_producer_kafka):
    consumer_producer_kafka.subscribe([topic_kafka])
    logging.info("Subscribed to topic")

    while True:
        msg = consumer_producer_kafka.poll(1.0)

        if msg is None:
            logging.info("No message received by consumer")
        elif msg.error() is not None:
            logging.error(f"Received error from consumer {msg.error()}")
        else:
            logging.info(f"Received message from consumer {msg.value().decode('utf-8')}")
            if isAccepted(msg):
                publish_message(consumer_producer_kafka, topic_kafka_clean, 'llave', msg.value().decode('utf-8'))  # Publica en Kafka

def run():
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)

    consumer_producer_kafka = connect_kafka_consumer()
    my_producer = KafkaProducer(
        bootstrap_servers='kafka:9092',
        api_version=(0,11,5),
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    for message in consumer_producer_kafka:
        message = message.value
        logging.info(f"{message} is being processed")
        if isAccepted(message):
            logging.info(f"{message} is being published")
            my_producer.send(topic_kafka_clean, value=message)
        
if __name__ == '__main__':
    run()