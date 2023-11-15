from paho.mqtt import client as mqtt_client
import logging
from datetime import datetime, timedelta
import time
import json
import random
import pytz

VEHICLE_TYPES = ['car', 'truck']

#Broker connection parameters
broker = 'localhost'
port = 1883
topic = "python/mqtt/corners"
CLIENT_ID = f'python-mqtt-{random.randint(0, 1000)}-1'
USERNAME = 'subscriber'
PASSWORD = 'public'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(CLIENT_ID)
    client.username_pw_set(USERNAME, PASSWORD)

    # Security settings, not working
    # client.tls_set(certfile=None,
    #            keyfile=None,
    #            cert_reqs=ssl.CERT_REQUIRED)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(broker, port)
    return client

# Connection settings
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

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        msg = json.loads(str(msg.payload.decode("utf-8")))
        #Save to db every recieved message
        save(msg)
    client.subscribe(topic)
    client.on_message = on_message


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
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                        level=logging.DEBUG)
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

if __name__ == '__main__':
    run()