from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, WriteOptions  # Cambio en la importación
import random
import logging
import json

# Variables de la base de datos (ajusta según tu configuración)
db_hostname = 'influxdb'
db_port = 8086
db_token = 's2d3rf67ren42i0gg666er9'
db_org = 'computacio'

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
    write_options = WriteOptions()
    write_options.batch_size = 500
    write_options.flush_interval = 10_000
    write_options.flush_jitter = 1_000

    twrite_api = client.write_api(write_options=write_options)
    return client, twrite_api



def save_to_influxdb(influx_client, twrite_api, data):
    json_body = [
        {
            "measurement": "your_measurement_name",
            "fields": data,
        }
    ]

    # Utilizamos el método write del write_api
    twrite_api.write(bucket=db_org, record=json_body)

def subscribe(consumer_kafka, influx_client, twrite_api):
    consumer_kafka.subscribe(topic_kafka)
    logging.info("Subscribed to topic")

    while True:
        msg = consumer_kafka.poll(1.0)

        if msg is None:
            logging.info("No message received by consumer")
        elif 'error' in msg:
            logging.error(f"Received error from consumer {msg['error']}")
        else:
            data = msg.get('value', {})
            logging.info(f"Received message from consumer {data}")
            save_to_influxdb(influx_client, twrite_api, data)

def run():
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)

    consumer_kafka = connect_kafka_consumer()
    influx_client, twrite_api = prepareDbClient()
    subscribe(consumer_kafka, influx_client, twrite_api)

if __name__ == '__main__':
    run()
