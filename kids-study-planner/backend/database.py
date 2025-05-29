import jaydebeapi
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HSQLDB connection parameters
# The database file will be stored in backend/data/study_planner.db
DB_FILE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'study_planner.db')
HSQLDB_JAR_PATH = os.path.join(os.path.dirname(__file__), 'lib', 'hsqldb.jar') # Assuming hsqldb.jar is in a 'lib' subdirectory

# JDBC connection URL
# 'shutdown=true' ensures data is saved to file upon last connection close
DB_URL = f'jdbc:hsqldb:file:{DB_FILE_PATH};shutdown=true'
DB_DRIVER = 'org.hsqldb.jdbcDriver'
DB_USER = 'SA'
DB_PASSWORD = '' # Default for HSQLDB

def get_db_connection():
    """Establishes and returns an HSQLDB connection using jaydebeapi."""
    try:
        # Ensure the directory for the database file exists
        os.makedirs(os.path.dirname(DB_FILE_PATH), exist_ok=True)
        
        if not os.path.exists(HSQLDB_JAR_PATH):
            logger.error(f"HSQLDB JAR file not found at {HSQLDB_JAR_PATH}")
            raise FileNotFoundError(f"HSQLDB JAR file not found at {HSQLDB_JAR_PATH}")

        conn = jaydebeapi.connect(
            DB_DRIVER,
            DB_URL,
            [DB_USER, DB_PASSWORD],
            HSQLDB_JAR_PATH
        )
        logger.info("Successfully connected to HSQLDB.")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to HSQLDB: {e}")
        raise

def init_db():
    """Initializes the database and creates tables if they don't already exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create kids table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS kids (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            age INTEGER,
            grade VARCHAR(255),
            subjects VARCHAR(1024), -- JSON string for list of subjects
            school_name VARCHAR(255),
            school_timings VARCHAR(255),
            preferred_study_hours VARCHAR(255),
            improvement_areas VARCHAR(1024), -- JSON string
            preferred_subjects VARCHAR(1024) -- JSON string
        )
        """)
        logger.info("Table 'kids' checked/created successfully.")

        # Create exams table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            exam_id VARCHAR(255) PRIMARY KEY,
            kid_id VARCHAR(255) NOT NULL,
            exam_name VARCHAR(255) NOT NULL,
            exam_date VARCHAR(255),
            subject VARCHAR(255) NOT NULL,
            marks_obtained_percentage REAL,
            class_top_percentage REAL,
            FOREIGN KEY (kid_id) REFERENCES kids(id) ON DELETE CASCADE
        )
        """)
        logger.info("Table 'exams' checked/created successfully.")

        # Create ai_insights table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_insights (
            insight_id VARCHAR(255) PRIMARY KEY,
            kid_id VARCHAR(255) NOT NULL UNIQUE,
            last_updated VARCHAR(255),
            progress_analysis VARCHAR(4096), -- Larger text field
            daily_schedule VARCHAR(4096),    -- JSON string
            weekly_schedule VARCHAR(4096),   -- JSON string
            monthly_schedule VARCHAR(4096),  -- JSON string
            suggestions VARCHAR(4096),       -- JSON string
            FOREIGN KEY (kid_id) REFERENCES kids(id) ON DELETE CASCADE
        )
        """)
        logger.info("Table 'ai_insights' checked/created successfully.")

        conn.commit()
        logger.info("Database initialization complete. Tables are ready.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            logger.info("Database connection closed.")

if __name__ == '__main__':
    # For testing purposes, you can run this script directly
    # to initialize the database and create the .db file and its directory.
    logger.info("Running database initialization directly...")
    init_db()
    # Verify file creation
    if os.path.exists(DB_FILE_PATH + ".script"): # HSQLDB creates a .script file
         logger.info(f"Database file created at {DB_FILE_PATH}.script")
    else:
         logger.error(f"Database file NOT created at {DB_FILE_PATH}.script")
