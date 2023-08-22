# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /mqtt_subscriber

# Copy the current directory contents into the container at /app
COPY . /mqtt_subscriber

# Install any needed packages specified in requirements.txt
RUN pip install paho-mqtt redis[hiredis] pymongo

# Run mqtt_subscriber.py when the container launches
CMD ["python", "subscriber.py"]
