from datetime import datetime
import paho.mqtt.client as mqtt
import random
import time
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SensorPublisher:
    def __init__(self, broker_addr, port, topics) -> None:
        self.broker_addr        = broker_addr
        self.port               = port
        self.topics             = topics
        self.client             = mqtt.Client("Publisher")

        # Set the callbacks, this function will be called when the message is published
        self.client.on_publish  = self.on_publish
        self.client.on_connect  = self.on_connect

    def on_publish(self, client, userdata, mid):
        logger.info(f"Message published with MID {mid}")
    
    def on_connect(self, client, userdata, flags, return_code):
        if return_code == 0:
            logger.info("Connected")
        else:
            logger.error(f"Coulld not connect, return code: {return_code}")

    def publish_message(self,topic_name, message):
        try:
            (result,mid) = self.client.publish(topic_name, json.dumps(message), qos=1)
            if result != mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Failed to publish data to topic {topic_name}")
            return (result, mid)
        except Exception as e:
            logger.error(f"Error publish message: {str(e)}")

    def generate_sensor_data(self, sensor_type):
        if sensor_type == "temperature":
            return {
                "sensor_id" : "sensor_temperature_" + str(round(random.uniform(10,20))),
                "value" :  round(random.uniform(20,30),4),
                "timestamp" : datetime.now().isoformat()
            }
        elif sensor_type == "humidity":
            return {
                "sensor_id" : "sensor_humidity_" + str(round(random.uniform(10,20))),
                "value" :  round(random.uniform(40, 60), 4),
                "timestamp" : datetime.now().isoformat()
            }
        else:
            return None

    def run(self):
        self.client.connect(self.broker_addr, self.port)
        self.client.loop_start()

        try:
            while True:
                for topic in topics:
                    sensor_data  = self.generate_sensor_data(topic.split("/")[-1])
                    if sensor_data:
                        self.publish_message(topic, sensor_data)

                time.sleep(5)
        finally:
            self.client.loop_stop()

        


if __name__ == "__main__":
    broker_addr         = "mosquitto"
    port                = 1883

    topics   = ["sensor/temperature","sensor/humidity"]

    publisher           = SensorPublisher(broker_addr, port, topics)
    publisher.run()



