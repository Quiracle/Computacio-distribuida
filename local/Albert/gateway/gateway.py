from paho.mqtt import client as mqtt_client
import logging
import time
import json
import random
from kafka import KafkaProducer
import Config
import os

# Connection settings
FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60
FLAG_EXIT = False

# Configuración de MQTT
mqtt_broker = os.environ.get('MQTT_BROKER', 'mosquitto')
mqtt_port = int(os.environ.get('MQTT_PORT', 1883))
topic_mqtt = Config.MQTT_TOPIC_RECEIVE
MQTT_CLIENT_ID = Config.MQTT_CLIENT_ID
MQTT_USERNAME = os.environ.get('MQTT_USERNAME', 'public')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', 'public')

# Configuración de Kafka
kafka_broker = os.environ.get('KAFKA_BROKER','kafka:9092')  # Coloca la dirección de tus brokers Kafka
kafka_topic = Config.KAFKA_TOPIC
KAFKA_CLIENT_ID = Config.KAFKA_CLIENT_ID

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(MQTT_CLIENT_ID)
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    # Security settings, not working
    # client.tls_set(certfile=None,
    #            keyfile=None,
    #            cert_reqs=ssl.CERT_REQUIRED)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(mqtt_broker, mqtt_port)
    return client

def connect_kafka_producer():
    try:
        return KafkaProducer(
            bootstrap_servers=kafka_broker,
            # api_version=(0,11,5),
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
    except Exception as err:
        logging.error("Failed to connect to Kafka. %s", err)
    

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

def subscribe_and_publish(mqtt_client, producer_kafka):
    def on_message(client, userdata, msg):
        logging.info(f"Received `{msg.payload.decode()}` from topic `{msg.topic}` in MQTT")
        msg = json.loads(str(msg.payload.decode("utf-8")))
        msg["user"] = Config.USER_NAME
        producer_kafka.send(kafka_topic, value=msg)
        logging.info(f'Sent Kafka message: {msg}')

    for topic in topic_mqtt:
        mqtt_client.subscribe(topic)
        logging.info(f'Subscribed to topic {topic}')
    mqtt_client.on_message = on_message

def save(msg):
    logging.info("Saving sensor data...")
    # sql = """INSERT INTO traffic
    #          VALUES(%s, %s, %s, %s, %s, %s, %s);"""
    # conn = None
    # try:
    #     # connect to the PostgreSQL database
    #     conn = psycopg2.connect(dbname="postgres", user="postgres", password="postgres", host="db")
    #     # create a new cursor
    #     cur = conn.cursor()
    #     # execute the INSERT statement
    #     cur.execute(sql, (msg['vehicle_id'], msg['vehicle_type'], msg['street_event'], msg['street_id'], msg['camera_id'], 'pending', msg['time']))
    #     # commit the changes to the database
    #     conn.commit()
    #     print("Successfully saved sensor data") 
    #     # close communication with the database
    #     cur.close()
    # except (Exception, psycopg2.DatabaseError) as error:
    #     print(error)
    # finally:
    #     if conn is not None:
    #         conn.close()


def run():
    global mqtt_client
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)
    
    mqtt_client = connect_mqtt()
    kafka_produce = connect_kafka_producer()
    logging.info("Connected to Kafka!")
    subscribe_and_publish(mqtt_client, kafka_produce)

    mqtt_client.loop_forever()
    

if __name__ == '__main__':
    run()