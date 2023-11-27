from paho.mqtt import client as mqtt_client
import logging
import json
import random
import Config
import os
from fastapi import FastAPI
import time

app = FastAPI()

@app.post("/actuate/{device}/{value}")
async def actuate(device: str, value):
    global client
    msg = {
        "device": device,
        "value": value
    }
    msg = json.dumps(msg)
    result = client.publish(Config.MQTT_TOPICS[device], msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        logging.info(f'Send `{msg}` to topic `{Config.MQTT_TOPICS["heat_pump"]}`')
    else:
        logging.error(f'Failed to send message to topic {Config.MQTT_TOPICS["heat_pump"]}')

# Connection settings
FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60
FLAG_EXIT = False

# Configuración de MQTT
mqtt_broker = os.environ.get('MQTT_BROKER', 'mosquitto')
mqtt_port = int(os.environ.get('MQTT_PORT', 1883))
MQTT_CLIENT_ID = Config.MQTT_CLIENT_ID
MQTT_USERNAME = os.environ.get('MQTT_USERNAME', 'public')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', 'public')

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(MQTT_CLIENT_ID)
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(mqtt_broker, mqtt_port)
    return client

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

client = connect_mqtt()
client.loop_start()

