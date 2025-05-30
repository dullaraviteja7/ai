from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
# This ensures that when this module is imported, MONGO_URI is available if set in .env
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME_AI_INSIGHTS", "ai_insights_db")

client = None
db = None

def connect_to_mongo():
    """Establishes a connection to MongoDB and initializes the database object."""
    global client, db
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        # You can verify the connection by trying to list collections or ping the server
        # For example, client.admin.command('ping') 
        print(f"Successfully connected to MongoDB database: {MONGO_DB_NAME} at {MONGO_URI.split('@')[-1].split('/')[0]}")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        # Handle connection errors appropriately, e.g., raise an exception or exit
        # For now, just printing the error

def get_db():
    """Returns the database object. Connects if not already connected."""
    if db is None:
        connect_to_mongo()
    return db

def close_mongo_connection():
    """Closes the MongoDB connection."""
    global client
    if client:
        client.close()
        print("MongoDB connection closed.")

# Example of how to get a specific collection
# def get_insights_collection():
#     database = get_db()
#     if database:
#         return database.insights # "insights" would be the collection name
#     return None

if __name__ == '__main__':
    # This is for testing the connection directly if you run this file
    connect_to_mongo()
    if db:
        print(f"Collections in '{MONGO_DB_NAME}': {db.list_collection_names()}")
    close_mongo_connection()
```
