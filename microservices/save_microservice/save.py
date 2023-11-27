from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, WritePrecision, Point  # Cambio en la importación
from influxdb_client.client.write_api import SYNCHRONOUS
import random
import logging
import json

# Variables de la base de datos (ajusta según tu configuración)
db_hostname = 'influxdb'
db_port = 8086
db_token = 's2d3rf67ren42i0gg666er9'
db_org = 'computacio'
db_bucket = 'dades'

broker_kafka = 'kafka:9092'
topic_kafka = ["sensors-raw", "sensors-clean"]
CLIENT_ID_KAFKA = f'python-kafka-{random.randint(0, 1000)}-1'

def connect_kafka_consumer():
    return KafkaConsumer(
        bootstrap_servers=[broker_kafka],
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='my-group2',
        api_version=(0, 11, 5),
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

def prepareDbClient():
    client = InfluxDBClient(
        url=f"http://{db_hostname}:{db_port}",
        token=db_token,
        org=db_org,
    )
    twrite_api = client.write_api(write_options=SYNCHRONOUS)
    return client, twrite_api



def save_to_influxdb(influx_client, twrite_api, data):
    logging.info(f"Writing to InfluxDB: {data}")

    try:
        # p = Point("temperatura") \
        #     .time(data['timestamp']) \
        #     .field("value", data['value']) \
        #     .tag("dispositive", data['dispositive']) \
        #     .tag("user", data['user']) 
        p = Point('temperatura').tag("User", data['user']).tag("dispositive", data['dispositive']).field("value", int(data['value'])).time(data['timestamp'], WritePrecision.MS)
    
        twrite_api.write(bucket=db_bucket, record=p)
    except Exception as e:
        logging.error(f"Error writing to InfluxDB: {e}")



def subscribe(consumer_kafka, influx_client, twrite_api):
    consumer_kafka.subscribe(topic_kafka)
    logging.info("Subscribed to topic")

    for message in consumer_kafka:
        data = message.value
        logging.info(f"Consumed from topic: {data}")

        save_to_influxdb(influx_client, twrite_api, data)

def run():
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)

    consumer_kafka = connect_kafka_consumer()
    influx_client, twrite_api = prepareDbClient()
    subscribe(consumer_kafka, influx_client, twrite_api)

if __name__ == '__main__':
    run()
