from kafka import KafkaConsumer
import random
import logging
import json

broker_kafka = 'kafka:9092'  # Coloca la dirección de tus brokers Kafka
topic_kafka = "sensors-clean"
CLIENT_ID_KAFKA = f'python-kafka-{random.randint(0, 1000)}-1'

from paho.mqtt import client as mqtt_client
import logging
import time
import json
import random
from datetime import datetime
import pytz
import os

broker = os.environ.get('MQTT_BROKER', 'localhost')
port = int(os.environ.get('MQTT_PORT', 1883))
mqtt_topic = 'actuators/light_bulb'
CLIENT_ID = f'python-mqtt-{random.randint(0, 1000)}'

USERNAME = os.environ.get('MQTT_USERNAME', 'public')
PASSWORD = os.environ.get('MQTT_PASSWORD', 'public')

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT Broker!")
        else:
            logging.error("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(CLIENT_ID)    
    client.username_pw_set(USERNAME, PASSWORD)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(broker, port)
    return client

#Connection behaviour settings
FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60
FLAG_EXIT = False

def on_disconnect(client, userdata, rc):
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)
    global FLAG_EXIT
    FLAG_EXIT = True

def publish(client):
    msg_count = 1
    while not FLAG_EXIT:
        t = time.localtime()
        #Define message to publish
        current_time = str(datetime.now(pytz.timezone("Europe/Gibraltar")).strftime("%Y-%m-%d %H:%M:%S"))

        msg_dict = {
            "timestamp": current_time,
            "value": random.randint(0,1),
        }
        
        if not client.is_connected():
            logging.error("publish: MQTT client is not connected!")
            time.sleep(1)
            continue
        time.sleep(1)
        msg = json.dumps(msg_dict)
        result = client.publish(mqtt_topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            logging.info(f"Send `{msg}` to topic `{mqtt_topic}`")
        else:
            logging.error(f"Failed to send message to topic {mqtt_topic}")
        msg_count += 1

def connect_kafka_consumer():
    return KafkaConsumer(
        topic_kafka,
        bootstrap_servers=['kafka:9092'],
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='my-group2',
        api_version=(0,11,5),
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )


# this function subscrives to the defined argument topics ans defines on message function
def subscribe(consumer_kafka):
    logging.info("Subscribed to topic")

    while True:
        msg = consumer_kafka.poll(1.0)

        if msg is None:
            logging.info("No message received by consumer")
        elif msg.error() is not None:
            logging.error(f"Received error from consumer {msg.error()}")
        else:
            logging.info(f"Received message from consumer {msg.value().decode('utf-8')}")

def needsAction(msg):
    if msg["dispositive"] == "presence_sensor":
        return msg["value"] == 1
    if msg["dispositive"] == "temperature_sensor":
        return msg["value"] > 20 and msg["value"] < 30
    if msg["dispositive"] == "heat_pump":
        return msg["value"] > 20 and msg["value"] < 30
    if msg["dispositive"] == "light_bulb":
        return msg["value"] == 1

def actuate(msg, client):
    logging.info(f"ACTUATIIING")
    msg = json.dumps(msg)
    result = client.publish(mqtt_topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        logging.info(f"Send `{msg}` to topic `{mqtt_topic}`")
    else:
        logging.error(f"Failed to send message to topic {mqtt_topic}")
    msg_count += 1

def run():
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)
    client = connect_mqtt()
    client.loop_start() 
    time.sleep(1)
    consumer_kafka = connect_kafka_consumer()
    for message in consumer_kafka:
        message = message.value
        logging.info(f"{message} is being processed")
        if needsAction(message):
            actuate(message, client)
if __name__ == '__main__':
    run()