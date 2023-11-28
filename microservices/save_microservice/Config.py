import random

KAFKA_TOPIC_RECEIVE = ["sensors-raw", "sensors-clean"]
KAFKA_GROUP_ID = "my-group-0"
CLIENT_ID_KAFKA = f'python-kafka-{random.randint(0, 1000)}'