import paho.mqtt.client as mqtt
from pymongo import MongoClient
import json
import redis

broker_addr         = "mosquitto"
port                = 1883

temperature_topic   = "sensor/tempperature"
humidity_topic      = "sensor/humidity"

mongo_uri           = "mongodb://mqtt-mongodb:27017"
mongo_client        = MongoClient(mongo_uri)
db                  = mongo_client["sensor_data"]

redis_host          = "redis"
redis_port          = 6379
redis_client        = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

def save_latest_ten_messages(payload):
    # inserts message to the front of the list
    redis_client.lpush("latest_sensor_readings", payload)

    # when a new message is inserted using the above lpush method
    # it is inserted at the begining and it is trimmed using
    # the below function call, only the first 10 messages
    # are saved 10th message is discarded
    redis_client.ltrim("latest_sensor_readings", 0, 9)


def get_latest_messages():
    latest_messages = redis_client.lrange("latest_messages", 0, 9)
    return latest_messages


def save_to_db(message):

    payload         = json.loads(message.payload)
    collection_name = "temperature" if message.topic == temperature_topic else "humidity"
    collection      = db[collection_name]

    # save to database
    collection.insert_one(payload)
    print(f"Saved {collection_name} data to Database. Payload: {payload}")

    # save into in-memory-database
    save_latest_ten_messages(payload)
    print(f"Saved Payload: {payload} to redis")

    
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT broker with code {rc}")
        client.subscribe([(temperature_topic, 1), (humidity_topic, 1)])
    else:
        print(f"could not connect, return code: {rc}")

def on_message(client, userdata, message):
    try:
        save_to_db(message)
    except Exception as exp:
        print(f"Error saving data to Database: {exp}")
    

client = mqtt.Client("Subscriber")

client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_addr, port)

client.loop_forever()