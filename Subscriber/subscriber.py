import paho.mqtt.client as mqtt
from pymongo import MongoClient
import json
import redis
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SensorSubscriber:
    def __init__(self, mongo_uri, redis_host, redis_port):
        self.mongo_uri                  = mongo_uri
        self.redis_host                 = redis_host
        self.redis_port                 = redis_port
        
        self.broker_addr                = "mosquitto"
        self.port                       = 1883
        self.temperature_topic          = "sensor/temperature"
        self.humidity_topic             = "sensor/humidity"

        self.mqtt_client                = mqtt.Client("Subscriber")
        self.mqtt_client.on_connect     = self.on_connect
        self.mqtt_client.on_message     = self.on_message

        self.mongo_client               = MongoClient(self.mongo_uri)
        self.db                         = self.mongo_client["sensor_data"]

        self.redis_client               = redis.StrictRedis(host=self.redis_host, port=self.redis_port, decode_responses=True)
    
    def connect(self):
        self.mqtt_client.connect(self.broker_addr, self.port)
        self.mqtt_client.loop_forever()

    def save_latest_ten_messages(self, sensor_id, value, timestamp, topic_name):
        reading = {
            "sensor_id": sensor_id,
            "value": value,
            "timestamp": timestamp,
        }
        
        # convert the dict to json string
        json_reading = json.dumps(reading)

        # inserts message to the front of the list for a topic
        redis_list_key = f"{topic_name}_sensor_readings"
        self.redis_client.lpush(redis_list_key, json_reading)

        # when a new message is inserted using the above lpush method
        # it is inserted at the begining and it is trimmed using
        # the below function call, only the first 10 messages
        # are saved 10th message is discarded
        self.redis_client.ltrim(redis_list_key, 0, 9)

    def save_to_db(self, message):
        payload = json.loads(message.payload)

        if message.topic.startswith(self.temperature_topic):
            collection_name = "temperature"
        elif message.topic.startswith(self.humidity_topic):
            collection_name = "humidity"
        else:
            return

        collection = self.db[collection_name]
        collection.insert_one(payload)

        logger.info(f"Saved {collection_name} to database payload: {payload}")
        try:
            self.save_latest_ten_messages(
                payload["sensor_id"], payload["value"], payload["timestamp"], collection_name
            )
            logger.info(f"Saved payload to redis")
        except Exception as exp:
            logger.error(f"Error saving data to redis: {exp}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"Connected to MQTT broker with code {rc}")
            client.subscribe([(self.temperature_topic, 1), (self.humidity_topic, 1)])
        else:
            logger.error(f"Could not connect, return code: {rc}")

    def on_message(self, client, userdata, message):
        try:
            self.save_to_db(message)
        except Exception as exp:
            logger.error(f"Error saving data to Database: {exp}")


if __name__ == "__main__":
    subscriber = SensorSubscriber(
        mongo_uri   = "mongodb://mqtt-mongodb:27017",
        redis_host  = "redis-mqtt",
        redis_port  = 6379,
    )
    subscriber.connect()
