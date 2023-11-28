import random

KAFKA_TOPIC_RECEIVE = "sensors-raw"
KAFKA_TOPIC_SEND = "sensors-clean"
KAFKA_GROUP_ID = "my-group-1"
CLIENT_ID_KAFKA = f'python-kafka-{random.randint(0, 1000)}'