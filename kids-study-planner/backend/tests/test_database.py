import os
import pytest
import jaydebeapi
import shutil

# Adjust the import path to access the database module from the parent directory
# This assumes tests are run from the 'backend' directory or PYTHONPATH is set appropriately.
# For pytest, it often handles this if 'backend' is the root for discovery.
from .. import database 

# Store original DB path and JAR path for restoration if needed, though monkeypatch is preferred
ORIGINAL_DB_FILE_PATH = database.DB_FILE_PATH
ORIGINAL_HSQLDB_JAR_PATH = database.HSQLDB_JAR_PATH

TEST_DB_DIR = os.path.join(os.path.dirname(__file__), 'test_db_data')
TEST_DB_FILENAME = 'test_study_planner.db'
TEST_DB_FILE_PATH = os.path.join(TEST_DB_DIR, TEST_DB_FILENAME)

@pytest.fixture(scope="function") # Use "function" scope for a fresh DB per test
def test_db(monkeypatch):
    """
    Fixture to set up a temporary database for testing.
    It patches the DB_FILE_PATH in the database module and ensures
    the test database directory is clean before and after tests.
    """
    # Ensure the test_db_data directory exists
    os.makedirs(TEST_DB_DIR, exist_ok=True)
    
    # Clean up any old test database files before the test
    db_files_to_remove = [
        TEST_DB_FILE_PATH + ".script",
        TEST_DB_FILE_PATH + ".properties",
        TEST_DB_FILE_PATH + ".log",
        TEST_DB_FILE_PATH + ".lck",
        TEST_DB_FILE_PATH + ".data",
        TEST_DB_FILE_PATH + ".backup"
    ]
    for f_path in db_files_to_remove:
        if os.path.exists(f_path):
            os.remove(f_path)

    # Monkeypatch the database module's constants
    monkeypatch.setattr(database, 'DB_FILE_PATH', TEST_DB_FILE_PATH)
    
    # Ensure the HSQLDB JAR path is valid. 
    # It's relative to database.py, so construct the absolute path for the test environment.
    # database.py is in backend/, HSQLDB_JAR_PATH = ./lib/hsqldb.jar
    # tests/test_database.py is in backend/tests/
    # So, the path from backend/tests/ to backend/lib/hsqldb.jar is ../lib/hsqldb.jar
    
    # Path to database.py: os.path.dirname(database.__file__)
    # Path to hsqldb.jar from database.py: os.path.join(os.path.dirname(database.__file__), 'lib', 'hsqldb.jar')
    # This is already what database.HSQLDB_JAR_PATH should resolve to.
    # We need to ensure this path is valid from where pytest is run.
    # If pytest is run from 'backend' directory, this path should be fine.
    jar_path_in_module = database.HSQLDB_JAR_PATH 
    if not os.path.isabs(jar_path_in_module):
        # database.py is in 'backend/', its __file__ is 'backend/database.py'
        # HSQLDB_JAR_PATH is 'backend/lib/hsqldb.jar'
        # tests are in 'backend/tests'
        # If running pytest from 'backend', the path 'lib/hsqldb.jar' is correct relative to 'backend'
        # The original HSQLDB_JAR_PATH is os.path.join(os.path.dirname(__file__), 'lib', 'hsqldb.jar')
        # where __file__ is database.py. So it's already an absolute-like path from within database.py
        # No need to change it unless the JAR is moved for tests.
        pass


    yield TEST_DB_FILE_PATH # The value yielded by the fixture

    # Teardown: Clean up the test database files after the test
    for f_path in db_files_to_remove:
        if os.path.exists(f_path):
            os.remove(f_path)
    
    # Optionally remove the directory if it's empty and created by this fixture
    if os.path.exists(TEST_DB_DIR) and not os.listdir(TEST_DB_DIR):
        try:
            os.rmdir(TEST_DB_DIR)
        except OSError: # Might fail if .pytest_cache or other hidden files are there
            pass


def test_get_db_connection(test_db):
    """Test that a database connection can be established."""
    # test_db fixture has already patched DB_FILE_PATH
    # The .script file for an HSQLDB file DB is typically created on first shutdown,
    # or when data is actually written and committed, not just on connection.
    # So, we'll just check if the connection can be made.
    
    conn = None
    try:
        conn = database.get_db_connection()
        assert conn is not None, "Connection object should not be None"
        # A more robust check would be to execute a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM (VALUES(0))") # HSQLDB specific dummy query
        assert cursor.fetchone() is not None
        cursor.close()
    except jaydebeapi.DatabaseError as e:
        pytest.fail(f"Database connection or simple query failed: {e}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred during get_db_connection test: {e}")
    finally:
        if conn:
            conn.close()

def test_init_db_creates_file_and_tables(test_db):
    """Test that init_db creates the DB file and all necessary tables, and is idempotent."""
    assert not os.path.exists(TEST_DB_FILE_PATH + ".script"), "Test DB .script file should not exist before init_db"

    # Call init_db for the first time
    database.init_db()
    assert os.path.exists(TEST_DB_FILE_PATH + ".script"), "HSQLDB .script file was not created after first init_db call"

    conn = None
    try:
        conn = database.get_db_connection() # Uses the patched path
        cursor = conn.cursor()

        # Verify tables are created
        tables_to_check = ['kids', 'exams', 'ai_insights']
        for table_name in tables_to_check:
            try:
                # HSQLDB stores table names in uppercase by default unless quoted during creation
                cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name.upper()}'")
                table_exists = cursor.fetchone()[0]
                assert table_exists == 1, f"Table '{table_name.upper()}' was not found in schema."
                
                # Check if table is empty
                cursor.execute(f"SELECT COUNT(*) FROM {table_name.upper()}")
                count = cursor.fetchone()[0]
                assert count == 0, f"Table '{table_name}' should be empty after initialization."
            except jaydebeapi.DatabaseError as e:
                pytest.fail(f"Table '{table_name}' check failed. Error: {e}")
        
        # Call init_db again to test idempotency
        database.init_db()
        
        # Re-verify tables still exist and are empty
        for table_name in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name.upper()}")
                count = cursor.fetchone()[0]
                assert count == 0, f"Table '{table_name}' should still be empty after second init_db call."
            except jaydebeapi.DatabaseError as e:
                pytest.fail(f"Table '{table_name}' check failed after second init_db. Error: {e}")

    except jaydebeapi.DatabaseError as e:
        pytest.fail(f"Database operation failed during test_init_db: {e}")
    finally:
        if conn:
            if cursor:
                cursor.close()
            conn.close()

def test_init_db_jar_not_found(test_db, monkeypatch, caplog):
    """Test init_db behavior when HSQLDB JAR is not found."""
    # Temporarily make HSQLDB_JAR_PATH invalid
    original_jar_path = database.HSQLDB_JAR_PATH
    non_existent_jar_path = os.path.join(os.path.dirname(__file__), 'non_existent_hsqldb.jar')
    monkeypatch.setattr(database, 'HSQLDB_JAR_PATH', non_existent_jar_path)
    
    # Clear previous logs if any, specific to this test
    caplog.clear()
    
    with pytest.raises(FileNotFoundError) as excinfo:
        # init_db calls get_db_connection, which will raise FileNotFoundError
        database.init_db() 
    
    assert "HSQLDB JAR file not found" in str(excinfo.value)
    # Check logger messages from database.py
    # Ensure logger in database.py is configured to a level that caplog can capture (e.g. INFO, ERROR)
    # The logger in database.py is already logging at ERROR for this.
    assert f"HSQLDB JAR file not found at {non_existent_jar_path}" in caplog.text
    assert "Error connecting to HSQLDB" in caplog.text # This is logged by get_db_connection
    assert "Error during database initialization" in caplog.text # This is logged by init_db

    # Restore for other tests if necessary, though test_db fixture should handle its scope
    monkeypatch.setattr(database, 'HSQLDB_JAR_PATH', original_jar_path)
