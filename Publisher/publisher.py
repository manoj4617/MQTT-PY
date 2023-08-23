import paho.mqtt.client as mqtt
import random
import time
import json
import uuid


broker_addr         = "tcp://mqtt-broker"
port                = 1883

temperature_topic   = "sensor/temperature"
humidity_topic      = "sensor/humidity"

client = mqtt.Client("Publisher")

def on_publish(client, userdata, mid):
    print(f"Message published with MID {mid}")


def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("Connected")
    else:
        print(f"Coulld not connect, return code: {return_code}")

# Set the callbacks, this function will be called when the message is published
client.on_publish = on_publish
client.on_connect = on_connect

def publish_message(topic_name, message):
    (result,mid) = client.publish(topic_name, json.dumps(message), qos=1)
    return (result, mid)

client.connect(broker_addr, port)
client.loop_start()

try:
    while True:
        sensor_data = {
            "sensor_id" : str(uuid.uuid4().hex),
            "value" :  round(random.uniform(20,30),4),
            "timestamp" :time.strftime("%Y-%m-%dT%H:%M:%S")
        }

        #publish temperature data
        (result,mid) = publish_message(temperature_topic, sensor_data)
        if result != mqtt.MQTT_ERR_SUCCESS:
            print(f"Failed to publish temperature data with MID: {mid}")

        # modify message for humidity sensors
        sensor_data["sensor_id"] = str(uuid.uuid4().hex)
        sensor_data["value"] = round(random.uniform(40, 60), 4)

        (result,mid) = publish_message(humidity_topic, sensor_data)
        if result != mqtt.MQTT_ERR_SUCCESS:
            print(f"Failed to publish humidity data with MID: {mid}")

        time.sleep(5)
finally:
    client.loop_stop()

