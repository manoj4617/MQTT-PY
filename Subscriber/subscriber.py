import paho.mqtt.client as mqtt
import pymongo as MongoClient
import random
import time
import json


broker_addr         = "mqtt://mosquitto"
port                = 1883

temperature_topic   = "sensor/tempperature"
humidity_topic      = "sensor/humidity"

mongo_uri           = "mongodb://mqttmongodb:27017/"
mongo_client        = MongoClient(mongo_uri)
db                  = mongo_client["sensor_data"]


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT broker with code {rc}")
        client.subscribe([(temperature_topic, 1), (humidity_topic, 1)])
    else:
        print(f"could not connect, return code: {rc}")

def on_message(client, userdata, message):
    try:
        payload         = json.loads(message.payload)
        collection_name = "temperature" if message.topic == temperature_topic else "humidity"
        collection      = db[collection_name]
        collection.insert_one(payload)
        print(f"Saved {collection_name} data to Database {payload}")
    except Exception as exp:
        print(f"Error saving data to Database: {exp}")
    

client = mqtt.Client("Subscriber")

client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_addr, port)

client.loop_forever()





