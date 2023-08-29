from typing import Union
from fastapi import FastAPI, Query
from pymongo import MongoClient

app = FastAPI()

mongo_uri               = "mongodb://mqtt-mongodb:27017"
mongo_client            = MongoClient(mongo_uri)
db                      = mongo_client["sensor_data"]

temperature_collection  = "temperature"
humidity_collection     = "hummidity"

@app.get("/get_readings")
def get_readings_for_range():
    return

@app.get("/get_readings/{sensor_id}")
def get_reading_for_sensor():
    return
