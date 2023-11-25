from kafka import KafkaConsumer
import random
import logging
import json

broker_kafka = 'kafka:9092'  # Coloca la dirección de tus brokers Kafka
topic_kafka = ["sensors-raw", "sensors-clean"]
CLIENT_ID_KAFKA = f'python-kafka-{random.randint(0, 1000)}-1'

def connect_kafka_consumer():
    return KafkaConsumer(
        bootstrap_servers=['kafka:9092'],
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='my-group2',
        api_version=(0,11,5),
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )


# this function subscrives to the defined argument topics ans defines on message function
def subscribe(consumer_kafka):
    consumer_kafka.subscribe(topic_kafka)
    logging.info("Subscribed to topic")

    while True:
        msg = consumer_kafka.poll(1.0)

        if msg is None:
            logging.info("No message received by consumer")
        elif msg.error() is not None:
            logging.error(f"Received error from consumer {msg.error()}")
        else:
            logging.info(f"Received message from consumer {msg.value().decode('utf-8')}")

def run():
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)

    consumer_kafka = connect_kafka_consumer()
    consumer_kafka.subscribe(topic_kafka)
    for message in consumer_kafka:
        message = message.value
        logging.info(f"{message} is being processed")
if __name__ == '__main__':
    run()