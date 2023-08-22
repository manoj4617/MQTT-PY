# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /mqtt_publisher

# Copy the current directory contents into the container at /app
COPY . /mqtt_publisher

# Install any needed packages specified in requirements.txt
RUN pip install paho-mqtt 

# Run mqtt_publisher.py when the container launches
CMD ["python", "publisher.py"]
