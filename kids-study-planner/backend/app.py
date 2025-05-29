from flask import Flask, request, jsonify
from flask_cors import CORS
import json # Keep for request.get_json() and potential future JSON string handling in DB
import os # Keep for os.path_join if needed, and for database.py
import uuid
from datetime import datetime, timezone

# Import database initialization and connection functions
from database import init_db, get_db_connection
import logging # For better logging
import requests # For making HTTP requests to the AI model
import pytesseract # For OCR
from PIL import Image # For opening images with Pytesseract
from dotenv import load_dotenv # To load environment variables from .env file

# Load environment variables from .env file at the very beginning
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
# Configure logging for app.py
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Define and create UPLOAD_FOLDER for exam result images
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
logger.info(f"Upload folder set to: {UPLOAD_FOLDER}")


# Initialize the database and create tables when the app starts
try:
    init_db()
except Exception as e:
    # Log this error appropriately in a real application
    logger.critical(f"CRITICAL: Database initialization failed: {e}")
    # Depending on the severity, you might want to prevent the app from starting
    # For now, we'll print and continue, but routes might fail.

# Mock data storage (to be replaced with database interactions)
# These functions will be removed/modified in subsequent tasks.
# For now, to keep routes functional at a basic level (though not saving data),
# we'll create dummy read_data and write_data or adapt routes to not call them.
# For this step, the goal is just to setup DB, so we'll keep routes as is
# but the JSON functions are removed.
# The routes will fail if they rely on read_data/write_data with the old structure.

# --- Old JSON based functions removed ---
# DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
# DATA_FILE = os.path.join(DATA_DIR, 'study_data.json')
#
# def ensure_data_file_exists():
#     ... (removed)
#
# def read_data():
#     ... (removed)
#
# def write_data(data):
#     ... (removed)
# --- End of old JSON functions ---

# --- Mock functions removed ---
# MOCK_DB_REPLACEMENT = {"kids": []}
#
# def read_data():
#     ... (removed)
#
# def write_data(data):
#     ... (removed)
# --- End of Mock functions ---

@app.route('/')
def home():
    return "Hello from Flask Backend!"

@app.route('/api/kids/register', methods=['POST'])
def register_kid():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # Basic validation
    required_fields = ['name', 'age', 'grade', 'subjects']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    if not isinstance(data['name'], str) or not data['name'].strip():
        return jsonify({"error": "Name must be a non-empty string"}), 400
    if not isinstance(data['age'], int) or data['age'] <= 0:
        return jsonify({"error": "Age must be a positive integer"}), 400
    if not isinstance(data['grade'], str) or not data['grade'].strip():
        return jsonify({"error": "Grade must be a non-empty string"}), 400
    if not isinstance(data['subjects'], list) or not data['subjects']:
        return jsonify({"error": "Subjects must be a non-empty list"}), 400

    kid_id = uuid.uuid4().hex
    kid_id = uuid.uuid4().hex
    
    # Prepare data for DB (convert lists to JSON strings)
    db_subjects = json.dumps(data['subjects'])
    db_improvement_areas = json.dumps(data.get('improvement_areas', []))
    db_preferred_subjects = json.dumps(data.get('preferred_subjects', []))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
        INSERT INTO kids (id, name, age, grade, subjects, school_name, school_timings, preferred_study_hours, improvement_areas, preferred_subjects)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (
            kid_id, data['name'], data['age'], data['grade'], db_subjects,
            data.get('school_name'), data.get('school_timings'), data.get('preferred_study_hours'),
            db_improvement_areas, db_preferred_subjects
        ))
        conn.commit()

        # Construct the response object (matching original structure where possible)
        new_kid_response = {
            "id": kid_id,
            "name": data['name'],
            "age": data['age'],
            "grade": data['grade'],
            "subjects": data['subjects'], # Return as list
            "school_name": data.get('school_name'),
            "school_timings": data.get('school_timings'),
            "preferred_study_hours": data.get('preferred_study_hours'),
            "improvement_areas": data.get('improvement_areas', []), # Return as list
            "preferred_subjects": data.get('preferred_subjects', []), # Return as list
            "exams": [], # New kid has no exams yet
            "ai_insights": {} # New kid has no insights yet
        }
        return jsonify(new_kid_response), 201

    except Exception as e:
        logger.error(f"Error registering kid: {e}")
        if conn:
            conn.rollback()
        return jsonify({"error": "Failed to register kid", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/kids/<kid_id>/exams', methods=['POST'])
def add_exam_data(kid_id):
    exam_data = request.get_json()
    if not exam_data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # Basic validation for required fields
    required_fields = ['exam_name', 'exam_date', 'subject', 'marks_obtained_percentage']
    for field in required_fields:
        if field not in exam_data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Validate marks_obtained_percentage
    marks = exam_data.get('marks_obtained_percentage')
    if not isinstance(marks, (int, float)) or not (0 <= marks <= 100):
        return jsonify({"error": "marks_obtained_percentage must be a number between 0 and 100"}), 400

    # Validate class_top_percentage if present
    class_top = exam_data.get('class_top_percentage')
    if class_top is not None:
        if not isinstance(class_top, (int, float)) or not (0 <= class_top <= 100):
            return jsonify({"error": "class_top_percentage must be a number between 0 and 100"}), 400
    
    # Basic check for exam_date format (YYYY-MM-DD)
    # This is a basic check, a more robust validation might be needed for production
    exam_date_str = exam_data.get('exam_date')
    if not isinstance(exam_date_str, str) or len(exam_date_str) != 10 or exam_date_str[4] != '-' or exam_date_str[7] != '-':
        return jsonify({"error": "exam_date must be a string in YYYY-MM-DD format"}), 400
    try:
        year, month, day = map(int, exam_date_str.split('-'))
        datetime(year, month, day) # Validate date components
    except ValueError:
        return jsonify({"error": "Invalid date in exam_date. Ensure YYYY-MM-DD format and valid day/month."}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if kid exists
        cursor.execute("SELECT id FROM kids WHERE id = ?", (kid_id,))
        kid_record = cursor.fetchone()
        if not kid_record:
            return jsonify({"error": "Kid not found"}), 404

        exam_id = uuid.uuid4().hex
        sql = """
        INSERT INTO exams (exam_id, kid_id, exam_name, exam_date, subject, marks_obtained_percentage, class_top_percentage)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (
            exam_id, kid_id, exam_data['exam_name'], exam_date_str, exam_data['subject'],
            exam_data['marks_obtained_percentage'], exam_data.get('class_top_percentage')
        ))
        conn.commit()

        new_exam_response = {
            "exam_id": exam_id,
            "kid_id": kid_id, # Often useful to return the parent ID
            "exam_name": exam_data['exam_name'],
            "exam_date": exam_date_str,
            "subject": exam_data['subject'],
            "marks_obtained_percentage": exam_data['marks_obtained_percentage'],
            "class_top_percentage": exam_data.get('class_top_percentage')
        }
        return jsonify(new_exam_response), 201

    except Exception as e:
        logger.error(f"Error adding exam data for kid {kid_id}: {e}")
        if conn:
            conn.rollback()
        return jsonify({"error": "Failed to add exam data", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/kids', methods=['GET'])
def get_all_kids():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, age, grade, subjects, school_name, school_timings, preferred_study_hours, improvement_areas, preferred_subjects FROM kids")
        
        kids_list = []
        columns = [desc[0].lower() for desc in cursor.description]
        for row in cursor.fetchall():
            kid_data = dict(zip(columns, row))
            
            # Convert JSON strings back to Python lists
            try:
                kid_data['subjects'] = json.loads(kid_data['subjects']) if kid_data['subjects'] else []
                kid_data['improvement_areas'] = json.loads(kid_data['improvement_areas']) if kid_data['improvement_areas'] else []
                kid_data['preferred_subjects'] = json.loads(kid_data['preferred_subjects']) if kid_data['preferred_subjects'] else []
            except json.JSONDecodeError as je:
                logger.warning(f"JSON decode error for kid {kid_data['id']}: {je}. Returning empty lists for affected fields.")
                kid_data['subjects'] = []
                kid_data['improvement_areas'] = []
                kid_data['preferred_subjects'] = []
            
            # Add placeholders for exams and ai_insights, as per original structure
            kid_data['exams'] = [] # Will be fetched in get_kid_data for individual kid
            kid_data['ai_insights'] = {} # Will be fetched in get_kid_data for individual kid
            kids_list.append(kid_data)
            
        return jsonify({"kids": kids_list}), 200

    except Exception as e:
        logger.error(f"Error getting all kids: {e}")
        return jsonify({"error": "Failed to retrieve kids", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()

def _safe_json_loads(json_string, default_value=None):
    """Safely loads a JSON string, returning a default value on error or if None."""
    if json_string is None:
        return default_value if default_value is not None else {} # Or [] based on context
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        logger.warning(f"Failed to decode JSON string: {json_string}")
        return default_value if default_value is not None else {}


@app.route('/api/kids/<kid_id>', methods=['GET'])
def get_kid_data(kid_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch kid's details
        cursor.execute("SELECT id, name, age, grade, subjects, school_name, school_timings, preferred_study_hours, improvement_areas, preferred_subjects FROM kids WHERE id = ?", (kid_id,))
        kid_row = cursor.fetchone()

        if not kid_row:
            return jsonify({"error": "Kid not found"}), 404

        columns = [desc[0].lower() for desc in cursor.description]
        kid_data = dict(zip(columns, kid_row))

        # Convert JSON strings from kid_data
        kid_data['subjects'] = _safe_json_loads(kid_data.get('subjects'), [])
        kid_data['improvement_areas'] = _safe_json_loads(kid_data.get('improvement_areas'), [])
        kid_data['preferred_subjects'] = _safe_json_loads(kid_data.get('preferred_subjects'), [])

        # Fetch exams for the kid
        cursor.execute("SELECT exam_id, exam_name, exam_date, subject, marks_obtained_percentage, class_top_percentage FROM exams WHERE kid_id = ?", (kid_id,))
        exams_list = []
        exam_columns = [desc[0].lower() for desc in cursor.description]
        for exam_row in cursor.fetchall():
            exams_list.append(dict(zip(exam_columns, exam_row)))
        kid_data['exams'] = exams_list

        # Fetch AI insights for the kid
        cursor.execute("SELECT insight_id, last_updated, progress_analysis, daily_schedule, weekly_schedule, monthly_schedule, suggestions FROM ai_insights WHERE kid_id = ?", (kid_id,))
        insight_row = cursor.fetchone()
        if insight_row:
            insight_columns = [desc[0].lower() for desc in cursor.description]
            ai_insight_data = dict(zip(insight_columns, insight_row))
            ai_insight_data['daily_schedule'] = _safe_json_loads(ai_insight_data.get('daily_schedule'), [])
            ai_insight_data['weekly_schedule'] = _safe_json_loads(ai_insight_data.get('weekly_schedule'), [])
            ai_insight_data['monthly_schedule'] = _safe_json_loads(ai_insight_data.get('monthly_schedule'), [])
            ai_insight_data['suggestions'] = _safe_json_loads(ai_insight_data.get('suggestions'), [])
            kid_data['ai_insights'] = ai_insight_data
        else:
            kid_data['ai_insights'] = {}
            
        return jsonify(kid_data), 200

    except Exception as e:
        logger.error(f"Error getting data for kid {kid_id}: {e}")
        return jsonify({"error": "Failed to retrieve kid data", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/kids/<kid_id>/ai-insights', methods=['POST'])
def generate_ai_insights(kid_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Fetch Kid's Data
        cursor.execute("SELECT id, name, age, grade, subjects, preferred_subjects, improvement_areas FROM kids WHERE id = ?", (kid_id,))
        kid_row = cursor.fetchone()
        if not kid_row:
            return jsonify({"error": "Kid not found"}), 404
        
        kid_columns = [desc[0].lower() for desc in cursor.description]
        kid_details = dict(zip(kid_columns, kid_row))

        kid_details['subjects'] = _safe_json_loads(kid_details.get('subjects'), [])
        kid_details['preferred_subjects'] = _safe_json_loads(kid_details.get('preferred_subjects'), [])
        kid_details['improvement_areas'] = _safe_json_loads(kid_details.get('improvement_areas'), [])

        cursor.execute("SELECT exam_name, exam_date, subject, marks_obtained_percentage, class_top_percentage FROM exams WHERE kid_id = ?", (kid_id,))
        exams_list = []
        exam_columns = [desc[0].lower() for desc in cursor.description]
        for exam_row in cursor.fetchall():
            exams_list.append(dict(zip(exam_columns, exam_row)))

        # 2. Environment Variables for AI Model
        colab_model_url = os.environ.get('COLAB_MODEL_URL')
        colab_api_key = os.environ.get('COLAB_API_KEY')
        
        use_placeholder_url = False
        if not colab_model_url:
            # Using a public test API that echoes POST data.
            # The "create" endpoint will return what we send it, encapsulated in a "data" field.
            colab_model_url = 'https://dummy.restapiexample.com/api/v1/create' 
            use_placeholder_url = True
            logger.warning("COLAB_MODEL_URL not set. Using placeholder URL for AI insights.")

        # 3. Prepare Payload for AI Model
        ai_payload = {
            "kid_id": kid_details['id'],
            "age": kid_details['age'],
            "grade": kid_details['grade'],
            "subjects": kid_details['subjects'],
            "preferred_subjects": kid_details['preferred_subjects'],
            "improvement_areas": kid_details['improvement_areas'],
            "exams": exams_list
        }

        # 4. Make API Call to Colab Model
        headers = {'Content-Type': 'application/json'}
        if colab_api_key:
            headers['Authorization'] = f'Bearer {colab_api_key}'
        
        ai_response_data = None
        try:
            logger.info(f"Sending request to AI model at {colab_model_url} with payload: {json.dumps(ai_payload, indent=2)}")
            response = requests.post(colab_model_url, json=ai_payload, headers=headers, timeout=30) # 30-second timeout
            response.raise_for_status()  # Raises HTTPError for bad responses (4XX or 5XX)
            
            raw_ai_response = response.json()
            logger.info(f"Received raw response from AI model: {json.dumps(raw_ai_response, indent=2)}")

            if use_placeholder_url:
                # The dummy.restapiexample.com/api/v1/create returns the sent data under a 'data' key
                # and adds its own 'id' and 'message'. We need to extract our original payload.
                # It also stringifies the nested objects if not careful, but requests.post(json=...) handles it.
                if 'data' in raw_ai_response and isinstance(raw_ai_response['data'], dict) and 'kid_id' in raw_ai_response['data']:
                     # This is a very basic mock, actual model would return progress_analysis etc.
                    ai_response_data = {
                        "progress_analysis": f"Placeholder analysis for {kid_details['name']}. Model echoed: {raw_ai_response['data'].get('subjects', [])[0] if raw_ai_response['data'].get('subjects') else 'N/A'}.",
                        "schedules": {
                            "daily": ["Placeholder daily task 1", "Placeholder daily task 2"],
                            "weekly": ["Placeholder weekly task 1"],
                            "monthly": ["Placeholder monthly task 1"]
                        },
                        "suggestions": ["Placeholder suggestion 1", "Placeholder suggestion 2"]
                    }
                else: # Unexpected response from placeholder
                    logger.error(f"Placeholder AI model response format unexpected: {raw_ai_response}")
                    return jsonify({"error": "AI model (placeholder) returned unexpected data format"}), 500
            else: # Actual model response
                 ai_response_data = raw_ai_response # Assume it matches our desired structure

        except requests.exceptions.RequestException as e:
            logger.error(f"AI model request failed: {e}")
            return jsonify({"error": "Failed to get insights from AI model due to connection or server error", "details": str(e)}), 502 # Bad Gateway
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON response from AI model")
            return jsonify({"error": "AI model returned non-JSON response"}), 500

        if not ai_response_data or not all(k in ai_response_data for k in ["progress_analysis", "schedules", "suggestions"]):
            logger.error(f"AI model response missing required fields. Received: {ai_response_data}")
            return jsonify({"error": "AI model response format incorrect"}), 500

        # 5. Store Insights
        insight_id = uuid.uuid4().hex
        last_updated = datetime.now(timezone.utc).isoformat()
        
        # Ensure schedules exist and are dicts before accessing keys
        schedules = ai_response_data.get("schedules", {})
        db_daily_schedule = json.dumps(schedules.get("daily", []))
        db_weekly_schedule = json.dumps(schedules.get("weekly", []))
        db_monthly_schedule = json.dumps(schedules.get("monthly", []))
        db_suggestions = json.dumps(ai_response_data.get("suggestions", []))

        cursor.execute("DELETE FROM ai_insights WHERE kid_id = ?", (kid_id,))
        sql = """
        INSERT INTO ai_insights (insight_id, kid_id, last_updated, progress_analysis, daily_schedule, weekly_schedule, monthly_schedule, suggestions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (
            insight_id, kid_id, last_updated, ai_response_data['progress_analysis'],
            db_daily_schedule, db_weekly_schedule, db_monthly_schedule, db_suggestions
        ))
        conn.commit()
        
        # 6. Return Response
        final_response = {
            "insight_id": insight_id,
            "kid_id": kid_id,
            "last_updated": last_updated,
            "progress_analysis": ai_response_data['progress_analysis'],
            "daily_schedule": schedules.get("daily", []), # Return as list
            "weekly_schedule": schedules.get("weekly", []), # Return as list
            "monthly_schedule": schedules.get("monthly", []), # Return as list
            "suggestions": ai_response_data.get("suggestions", []) # Return as list
        }
        return jsonify(final_response), 200

    except Exception as e:
        logger.error(f"Error in generate_ai_insights for kid {kid_id}: {e}")
        if conn:
            conn.rollback()
        # Check if it's an HTTPError from response.raise_for_status()
        if isinstance(e, requests.exceptions.HTTPError):
            return jsonify({"error": "AI model request failed", "status_code": e.response.status_code, "details": e.response.text}), e.response.status_code
        return jsonify({"error": "Internal server error while generating AI insights", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/kids/<kid_id>/exams/upload_image', methods=['POST'])
def upload_exam_image(kid_id):
    conn = None
    try:
        # 1. Kid Existence Check
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM kids WHERE id = ?", (kid_id,))
        kid_record = cursor.fetchone()
        if not kid_record:
            return jsonify({"error": "Kid not found"}), 404

        # 2. File Handling
        if 'marks_sheet_image' not in request.files:
            return jsonify({"error": "No image file provided (expected 'marks_sheet_image')"}), 400
        
        file = request.files['marks_sheet_image']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Generate a secure temporary filename
        _, file_extension = os.path.splitext(file.filename)
        if file_extension.lower() not in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            return jsonify({"error": "Invalid file type. Allowed types: png, jpg, jpeg, tiff, bmp"}), 400
            
        temp_filename = f"{uuid.uuid4().hex}{file_extension}"
        image_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        
        try:
            file.save(image_path)
            logger.info(f"Image saved temporarily to {image_path}")

            # 3. OCR Processing
            try:
                extracted_text = pytesseract.image_to_string(Image.open(image_path))
                logger.info(f"OCR extracted text: \n---\n{extracted_text}\n---")
                
                # 4. Simple Text Parsing (Very Basic Placeholder)
                extracted_data = {
                    "exam_name": "Unknown Exam",
                    "subject": "Unknown Subject",
                    "marks_obtained_percentage": "0.0",
                    "raw_text": extracted_text # Include raw text for debugging/manual review
                }
                
                lines = extracted_text.lower().splitlines()
                for line in lines:
                    if "exam name:" in line or "exam:" in line:
                        extracted_data["exam_name"] = line.split(":", 1)[1].strip().title()
                    if "subject:" in line:
                        extracted_data["subject"] = line.split(":", 1)[1].strip().title()
                    if "marks:" in line or "percentage:" in line:
                        # Attempt to find a number in the line
                        found_marks = [word for word in line.split() if word.replace('.', '', 1).isdigit()]
                        if found_marks:
                             extracted_data["marks_obtained_percentage"] = found_marks[0]
                
                # Basic validation for marks (if found)
                try:
                    marks_float = float(extracted_data["marks_obtained_percentage"])
                    if not (0 <= marks_float <= 100):
                        logger.warning(f"Extracted marks {marks_float} out of range. Resetting to 0.0.")
                        extracted_data["marks_obtained_percentage"] = "0.0" # Or handle as error
                except ValueError:
                    logger.warning(f"Could not convert extracted marks '{extracted_data['marks_obtained_percentage']}' to float. Resetting to 0.0.")
                    extracted_data["marks_obtained_percentage"] = "0.0" # Or handle as error

                return jsonify({"extracted_data": extracted_data}), 200

            except pytesseract.TesseractNotFoundError:
                logger.error("Tesseract OCR engine not found. Please ensure it is installed and in PATH.")
                # This is where we would mock if Tesseract was not installed.
                # Since it was installed, a real error here means something else is wrong.
                return jsonify({"error": "OCR processing failed: Tesseract not found or not configured."}), 500
            except Exception as ocr_error:
                logger.error(f"OCR processing error: {ocr_error}")
                return jsonify({"error": "OCR processing failed", "details": str(ocr_error)}), 500
        finally:
            # Ensure temporary image is deleted
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    logger.info(f"Temporary image {image_path} deleted.")
                except Exception as e_remove:
                    logger.error(f"Failed to delete temporary image {image_path}: {e_remove}")
                    
    except Exception as e:
        logger.error(f"Error in upload_exam_image for kid {kid_id}: {e}")
        # Ensure connection is closed if opened
        if conn:
            conn.rollback() # Rollback any potential transaction, though none explicitly started here
        return jsonify({"error": "Internal server error during image upload", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    # ensure_data_file_exists() # Removed, init_db() handles database creation
    app.run(debug=True, use_reloader=False) # use_reloader=False can be helpful for DB init issues
