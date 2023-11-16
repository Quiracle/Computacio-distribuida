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
mqtt_topic = 'actuators/heat_pump'
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

routes=[[1,3,7],[1,3,1],[1,3,5]]

{
    "v0":[{"street":1,"duration":5},{"street":3,"duration":10},{"street":7,"duration":10}]
}
def publish(client):
    msg_count = 1
    while not FLAG_EXIT:
        t = time.localtime()
        #Define message to publish
        current_time = str(datetime.now(pytz.timezone("Europe/Gibraltar")).strftime("%Y-%m-%d %H:%M:%S"))

        msg_dict = {
            "timestamp": current_time,
            "value": random.randint(15,30),
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

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        logging.info(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        msg = json.loads(str(msg.payload.decode("utf-8")))
    client.subscribe(mqtt_topic)
    client.on_message = on_message


def run():
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                        level=logging.DEBUG)
    client = connect_mqtt()
    subscribe(client)
    client.loop_start() 
    time.sleep(1)
    if client.is_connected():
        publish(client)
    else:
        client.loop_stop()


if __name__ == '__main__':
    run()