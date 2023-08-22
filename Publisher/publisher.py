import paho.mqtt.client as mqtt
import pymongo as MongoClient
import random
import time
import json
import uuid


broker_addr         = "localhost"
port                = 1883

temperature_topic   = "sensor/tempperature"
humidity_topic      = "sensor/humidity"

mongo_uri           = "mongodb://mqttmongodb:27017/"
mongo_client        = MongoClient(mongo_uri)
db                  = mongo_client["sensor_data"]

client = mqtt.Client()

client.connect(broker_addr, port)


# save message to database
def save_to_database(data, sensor_type):
    sensor = sensor_type + "_collection"
    
    sensor = db[sensor_type]
    sensor.insert_one(data)
    
    return

def on_publish(mid):
    print(f"Message published with MID {mid}")

# Set the on_publish callback
client.on_publish = on_publish

def publish_message(topic_name, message):
    (result,mid) = client.publish(topic_name, json.dumps(message))
    return (result, mid)


while True:
    sensor_data = {
        "sensor_id" : str(uuid.uuid4()),
        "value" :  round(random(20,30),4),
        "timestamp" :time.strftime("%Y-%m-%dT%H:%M:%S")
    }

    #publish temperature data
    (result,mid) = publish_message(temperature_topic, sensor_data)
    if result != mqtt.MQTT_ERR_SUCCESS:
        print(f"Failed to publish temperature data with MID: {mid}")

    # save to database
    save_to_database(sensor_data, "temperature")

    # modify message for humidity sensors
    sensor_data["sensor_id"] = str(uuid.uuid4())
    sensor_data["value"] = round(random(40, 60), 4)

    (result,mid) = publish_message(humidity_topic, sensor_data)
    if result != mqtt.MQTT_ERR_SUCCESS:
        print(f"Failed to publish humidity data with MID: {mid}")
    
    # save to database
    save_to_database(sensor_data, "humidity")

    time.sleep(5)

