from confluent_kafka import Producer
import random
import logging

broker_kafka = 'localhost:9092'  # Coloca la dirección de tus brokers Kafka
topic_kafka = "python/kafka/corners"
CLIENT_ID_KAFKA = f'python-kafka-{random.randint(0, 1000)}-1'

def connect_kafka_producer():
    config = {
        'bootstrap.servers': broker_kafka,
        'client.id': CLIENT_ID_KAFKA
    }
    return Producer(config)

def subscribe(producer_kafka):
    subscribe()

def run():
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)

    producer_kafka = connect_kafka_producer()

    subscribe(producer_kafka)
if __name__ == '__main__':
    run()