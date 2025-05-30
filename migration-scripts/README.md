# User Data Migration Script (HSQLDB to MongoDB)

This script migrates user data from the HSQLDB database used by the Python backend to the MongoDB database used by the User Service.

## Prerequisites

1.  **Python 3**: Ensure Python 3 is installed.
2.  **HSQLDB JDBC Driver**: The `hsqldb.jar` file must be accessible. This script assumes it's located in `../backend/lib/hsqldb.jar` relative to the script's location.
3.  **Running Databases**:
    *   HSQLDB: The database file (`study_planner.db.script`) is expected at `../backend/data/`. The script will access this directly.
    *   MongoDB: A MongoDB instance must be running and accessible at `mongodb://localhost:27017/`.
4.  **Python Dependencies**: Install the required Python libraries:
    ```bash
    pip install jaydebeapi pymongo
    ```

## Configuration

The script uses the following hardcoded paths and connection details:

*   **HSQLDB JDBC Driver Path**: `../backend/lib/hsqldb.jar`
*   **HSQLDB Database URL**: `jdbc:hsqldb:file:../backend/data/study_planner_db;shutdown=true` (Note: the db file is `study_planner_db` not `study_planner.db.script` for connection purposes, HSQLDB handles the `.script` part)
*   **MongoDB Connection URI**: `mongodb://localhost:27017/`
*   **MongoDB Database Name**: `user_service_db`
*   **MongoDB Collection Name**: `users`

If your setup differs, you may need to modify these directly in the `migrate_users_to_mongo.py` script.

## Running the Script

1.  Navigate to the `migration-scripts` directory:
    ```bash
    cd migration-scripts
    ```
2.  Run the script:
    ```bash
    python migrate_users_to_mongo.py
    ```

The script will:
1.  Connect to the HSQLDB.
2.  Fetch all records from the `kids` table.
3.  Transform the data (including converting JSON strings to lists and mapping field names).
4.  Connect to MongoDB.
5.  Insert the transformed records into the `users` collection in the `user_service_db` database.
    *   It will skip inserting a user if a document with the same `id` already exists in MongoDB to ensure idempotency.

## Important Notes
* This script assumes the HSQLDB database is not running as a server but is being accessed directly via its file. Ensure the Python backend is not running and locking the HSQLDB files when you run this script.
* Ensure the `user-service` (Java/Spring Boot) is running if you want to immediately verify data via its API, but it's not required for the migration script itself to run.
* The script expects the HSQLDB database file to be named `study_planner_db.script` (and corresponding `.properties`, `.log` files) in the `../backend/data/` directory. The connection string uses `study_planner_db` as the database name.
* This script is designed for a one-time migration but includes a basic check for existing IDs to allow for safe re-runs (idempotency).
```
