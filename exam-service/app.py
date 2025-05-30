# app.py
from flask import Flask, jsonify
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

# Import blueprints
from routes.exam_routes import exam_bp

from kafka import KafkaProducer # Add Kafka import
import json # For Kafka message serialization

# Load environment variables from .env file
load_dotenv()

# Global Kafka Producer instance
kafka_producer = None

def create_app():
    global kafka_producer
    app = Flask(__name__)

    # Configure MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/exam_service_db")
    app.config["MONGO_URI"] = mongo_uri
    
    try:
        PyMongo(app)
        # Avoid logging credentials if MONGO_URI contains them
        safe_mongo_uri_display = mongo_uri.split('@')[-1].split('/')[0] if '@' in mongo_uri else mongo_uri.split('//')[-1].split('/')[0]
        print(f"Successfully connected to MongoDB at {safe_mongo_uri_display}")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")


    # Configure Kafka Producer
    kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    app.config["KAFKA_EXAM_TOPIC"] = os.getenv("KAFKA_EXAM_TOPIC", "exam_events") # Store topic in app.config for routes

    try:
        print(f"Attempting to connect to Kafka brokers at {kafka_bootstrap_servers}...")
        kafka_producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers.split(','), # Support comma-separated list
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=3, # Retry sending a message up to 3 times
            request_timeout_ms=3000 # Timeout for producer requests
        )
        # To check connectivity, you could try sending a test message or use kafka_producer.bootstrap_connected()
        # However, bootstrap_connected() might not be a foolproof way to check full connectivity for sending.
        # For now, we assume initialization without error means it's likely okay, or will fail on first send.
        app.extensions['kafka_producer'] = kafka_producer # Make producer available to routes
        print("KafkaProducer initialized. Connection will be attempted on first message send.")
    except Exception as e:
        print(f"Could not initialize KafkaProducer: {e}. Kafka messaging will be unavailable.")
        app.extensions['kafka_producer'] = None # Ensure it's None if initialization fails


    # Register Blueprints
    app.register_blueprint(exam_bp, url_prefix='/api/exams') # All routes in exam_bp will be prefixed with /api/exams

    return app

if __name__ == '__main__':
    app = create_app()
    # Flask's built-in server is not suitable for production.
    # Use a WSGI server like Gunicorn or uWSGI in production.
    # Debug mode should be enabled via FLASK_ENV=development or FLASK_DEBUG=1
    
    # Ensure FLASK_RUN_PORT is used if set, otherwise default to 5001 for this service
    port = int(os.getenv("FLASK_RUN_PORT", 5001)) 
    debug_mode = (os.getenv("FLASK_ENV") == "development" or os.getenv("FLASK_DEBUG") == "1")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
