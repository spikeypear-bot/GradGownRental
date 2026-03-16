import json
import logging
import threading
import os


from flask import Flask
from kafka import KafkaConsumer, KafkaProducer

class KafkaService:
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KafkaService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

kafka_client = KafkaService()

def init_kafka(app):
    global kafka_client
    if not kafka_client.producer or not kafka_client.producer:
        kafka_client.connect()
