import random

KAFKA_GROUP_ID = "my-group-2"
CLIENT_ID_KAFKA = f'python-kafka-{random.randint(0, 1000)}'

KAFKA_TOPIC_RECEIVE = "sensors-clean"

USER_API_URL = {"Albert": "http://albert-api:80",
                "Tommy": "http://tommy-api:83",
                "Dakota": "http://dakota-api:82",
                "Tifany": "http://tifany-api:81",}