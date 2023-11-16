from paho.mqtt import client as mqtt_client
import logging
from datetime import datetime, timedelta
import time
import json
import random
import pytz
from confluent_kafka import Producer

# Connection settings
FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60
FLAG_EXIT = False

# Configuración de MQTT
broker_mqtt = 'localhost'
port_mqtt = 1883
topic_mqtt = "python/mqtt/corners"
CLIENT_ID_MQTT = f'python-mqtt-{random.randint(0, 1000)}-1'
USERNAME_MQTT = 'subscriber'
PASSWORD_MQTT = 'public'

# Configuración de Kafka
broker_kafka = 'localhost:9092'  # Coloca la dirección de tus brokers Kafka
topic_kafka = "python/kafka/corners"
CLIENT_ID_KAFKA = f'python-kafka-{random.randint(0, 1000)}-1'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(CLIENT_ID_MQTT)
    client.username_pw_set(USERNAME_MQTT, PASSWORD_MQTT)

    # Security settings, not working
    # client.tls_set(certfile=None,
    #            keyfile=None,
    #            cert_reqs=ssl.CERT_REQUIRED)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(broker_mqtt, port_mqtt)
    return client

def connect_kafka_producer():
    config = {
        'bootstrap.servers': broker_kafka,
        'client.id': CLIENT_ID_KAFKA
    }
    return Producer(config)

def publish_message(producer, topic, key, message):
    producer.produce(topic, key=key, value=json.dumps(message))
    producer.flush()
    

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

def subscribe_and_publish(client_mqtt, producer_kafka):
    def on_message(client, userdata, msg):
        print(f"Recibido `{msg.payload.decode()}` del tópico `{msg.topic}` en MQTT")
        msg = json.loads(str(msg.payload.decode("utf-8")))
        publish_message(producer_kafka, topic_kafka, 'llave', msg)  # Publica en Kafka

    client_mqtt.subscribe(topic_mqtt)
    client_mqtt.on_message = on_message



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
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)
    
    client_mqtt = connect_mqtt()
    producer_kafka = connect_kafka_producer()
    
    subscribe_and_publish(client_mqtt, producer_kafka)
    
    client_mqtt.loop_forever()
    

if __name__ == '__main__':
    run()