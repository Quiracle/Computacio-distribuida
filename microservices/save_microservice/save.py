from confluent_kafka import Consumer
import random
import logging

broker_kafka = 'kafka:9092'  # Coloca la dirección de tus brokers Kafka
topic_kafka = "sensors"
CLIENT_ID_KAFKA = f'python-kafka-{random.randint(0, 1000)}-1'

def connect_kafka_consumer():
    conf = {
        'bootstrap.servers': broker_kafka,
        'auto.offset.reset': 'smallest'}

    return Consumer(conf)


# this function subscrives to the defined argument topics ans defines on message function
def subscribe(consumer_kafka):
    consumer_kafka.subscribe([topic_kafka])
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
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)

    consumer_kafka = connect_kafka_consumer()

    subscribe(consumer_kafka)
if __name__ == '__main__':
    run()