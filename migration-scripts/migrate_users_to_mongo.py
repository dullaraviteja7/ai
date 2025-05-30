import jaydebeapi
import json
from pymongo import MongoClient
import os

# --- Configuration ---
HSQLDB_DRIVER_PATH = os.path.abspath("../backend/lib/hsqldb.jar")
# For file-based HSQLDB, the path should be to the DB files, not the .script file directly in URL
# HSQLDB automatically appends .script, .properties, .log to this base name.
# The database name itself is usually what comes before .db (if that was the original full name)
# or just the prefix if you only have .script, .properties, .log files.
# Based on `database.py` using `data/study_planner_db.script`, the DB name for connection is `study_planner_db`
HSQLDB_DB_FILE_PATH_BASE = os.path.abspath("../backend/data/study_planner_db")
HSQLDB_URL = f"jdbc:hsqldb:file:{HSQLDB_DB_FILE_PATH_BASE};shutdown=true"
HSQLDB_USER = "sa"
HSQLDB_PASSWORD = ""

MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "user_service_db"
MONGO_COLLECTION_NAME = "users"

# --- Helper Functions ---

def json_string_to_list(json_string):
    """Converts a JSON string representation of a list to a Python list."""
    if json_string:
        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON string: {json_string}")
            return [] # Return empty list on error, or handle as appropriate
    return []

def transform_data(hsql_record):
    """Transforms a single record from HSQLDB to MongoDB user schema."""
    return {
        "id": str(hsql_record[0]), # Ensure ID is string
        "name": hsql_record[1],
        "age": hsql_record[2],
        "grade": hsql_record[3],
        "subjects": json_string_to_list(hsql_record[4]),
        "schoolName": hsql_record[5],
        "schoolTimings": hsql_record[6],
        "preferredStudyHours": hsql_record[7],
        "improvementAreas": json_string_to_list(hsql_record[8]),
        "preferredSubjects": json_string_to_list(hsql_record[9])
    }

# --- Main Migration Logic ---

def migrate_data():
    hsql_conn = None
    mongo_client = None
    migrated_count = 0
    skipped_count = 0
    cursor = None # Initialize cursor to None

    print("Starting data migration...")

    # 1. Connect to HSQLDB
    try:
        print(f"Connecting to HSQLDB: {HSQLDB_URL}")
        print(f"Using HSQLDB driver: {HSQLDB_DRIVER_PATH}")
        if not os.path.exists(HSQLDB_DRIVER_PATH):
            print(f"ERROR: HSQLDB_DRIVER_PATH does not exist: {HSQLDB_DRIVER_PATH}")
            return
        
        # Check if the database files exist to avoid HSQLDB creating a new empty one silently
        db_script_file = HSQLDB_DB_FILE_PATH_BASE + ".script"
        if not os.path.exists(db_script_file):
            print(f"ERROR: HSQLDB script file does not exist: {db_script_file}")
            print("Ensure the Python backend has been run at least once to create the database.")
            return

        hsql_conn = jaydebeapi.connect(
            "org.hsqldb.jdbcDriver",
            HSQLDB_URL,
            [HSQLDB_USER, HSQLDB_PASSWORD],
            HSQLDB_DRIVER_PATH
        )
        print("Successfully connected to HSQLDB.")
        cursor = hsql_conn.cursor()

        # 2. Fetch Data from HSQLDB
        cursor.execute("SELECT id, name, age, grade, subjects, school_name, school_timings, preferred_study_hours, improvement_areas, preferred_subjects FROM kids")
        hsql_records = cursor.fetchall()
        print(f"Fetched {len(hsql_records)} records from HSQLDB.")

        if not hsql_records:
            print("No records found in HSQLDB `kids` table. Nothing to migrate.")
            return

        # 3. Connect to MongoDB
        print(f"Connecting to MongoDB: {MONGO_URI}")
        mongo_client = MongoClient(MONGO_URI)
        db = mongo_client[MONGO_DB_NAME]
        collection = db[MONGO_COLLECTION_NAME]
        print(f"Successfully connected to MongoDB, database '{MONGO_DB_NAME}', collection '{MONGO_COLLECTION_NAME}'.")

        # 4. Transform and Insert Data
        for record in hsql_records:
            transformed_record = transform_data(record)
            
            # Idempotency check: Skip if user with this ID already exists
            if collection.count_documents({"_id": transformed_record["id"]}) > 0:
                print(f"User with ID {transformed_record['id']} already exists in MongoDB. Skipping.")
                skipped_count += 1
                continue

            # MongoDB uses _id for the primary key. We map our 'id' to MongoDB's '_id'.
            mongo_doc = {"_id": transformed_record.pop("id")} 
            mongo_doc.update(transformed_record) # Add other fields

            collection.insert_one(mongo_doc)
            migrated_count += 1
            print(f"Migrated user: {transformed_record.get('name')} (ID: {mongo_doc['_id']})")

        print(f"\nMigration summary:")
        print(f"Successfully migrated {migrated_count} records.")
        print(f"Skipped {skipped_count} records (already existed).")

    except jaydebeapi.DatabaseError as je:
        print(f"HSQLDB Database Error: {je}")
        if "database alias does not exist" in str(je) or "database doesn't exist" in str(je) :
             print(f"Potential issue: HSQLDB file not found at path base '{HSQLDB_DB_FILE_PATH_BASE}'. Searched for files like '{HSQLDB_DB_FILE_PATH_BASE}.script'.")
        elif "java.net.SocketException" in str(je) or "connection refused" in str(je):
            print("HSQLDB server not running or not accessible.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if hsql_conn:
            hsql_conn.close()
            print("HSQLDB connection closed.")
        if mongo_client:
            mongo_client.close()
            print("MongoDB connection closed.")

if __name__ == "__main__":
    migrate_data()
