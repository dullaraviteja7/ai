# routes/exam_routes.py
from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
import uuid
from datetime import datetime

exam_bp = Blueprint('exam_bp', __name__)

# Helper to get MongoDB collection
def get_exam_collection():
    mongo = current_app.extensions['pymongo']
    return mongo.db.exams

@exam_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Exam Service is running"}), 200

@exam_bp.route('/kids/<kid_id>/exams', methods=['POST'])
def create_exam(kid_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    required_fields = ["exam_name", "exam_date", "subject", "marks_obtained_percentage"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        marks = float(data["marks_obtained_percentage"])
        if not (0 <= marks <= 100):
            return jsonify({"error": "marks_obtained_percentage must be between 0 and 100"}), 400
    except ValueError:
        return jsonify({"error": "marks_obtained_percentage must be a valid number"}), 400

    if "class_top_percentage" in data and data["class_top_percentage"] is not None:
        try:
            top_marks = float(data["class_top_percentage"])
            if not (0 <= top_marks <= 100):
                return jsonify({"error": "class_top_percentage must be between 0 and 100"}), 400
        except ValueError:
            return jsonify({"error": "class_top_percentage must be a valid number"}), 400
    
    try:
        # Validate exam_date format
        datetime.strptime(data["exam_date"], "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "exam_date must be in YYYY-MM-DD format"}), 400


    exam = {
        "_id": ObjectId(), # MongoDB's primary key
        "exam_id": uuid.uuid4().hex, # Application-specific unique ID
        "kid_id": kid_id,
        "exam_name": data["exam_name"],
        "exam_date": data["exam_date"],
        "subject": data["subject"],
        "marks_obtained_percentage": marks,
        "class_top_percentage": data.get("class_top_percentage"), # Optional field
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    try:
        exam_collection = get_exam_collection()
        result = exam_collection.insert_one(exam)
        exam_id_str = str(result.inserted_id) # MongoDB _id
        
        # Prepare response: convert ObjectId to string for JSON serialization
        exam_to_return = exam.copy()
        exam_to_return["_id"] = exam_id_str # Use the string version of MongoDB's _id
        # exam_id field (application specific uuid) is already in exam_to_return

        # Send message to Kafka
        kafka_producer = current_app.extensions.get('kafka_producer')
        if kafka_producer:
            kafka_topic = current_app.config.get("KAFKA_EXAM_TOPIC", "exam_events")
            message = {
                "event_type": "exam_created",
                "exam_id": exam_to_return["exam_id"], # Application-specific UUID
                "mongodb_id": exam_id_str,
                "kid_id": exam_to_return["kid_id"],
                "subject": exam_to_return["subject"],
                "marks_obtained_percentage": exam_to_return["marks_obtained_percentage"],
                "exam_date": exam_to_return["exam_date"],
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            try:
                future = kafka_producer.send(kafka_topic, value=message)
                # Optional: wait for message to be sent
                # future.get(timeout=5) # Block for 'timeout' seconds.
                current_app.logger.info(f"Sent exam event to Kafka topic {kafka_topic}: {message['exam_id']}")
            except Exception as ke:
                current_app.logger.error(f"Failed to send exam event to Kafka: {ke}")
                # Decide if this should be a critical failure. For now, just log.
        else:
            current_app.logger.warning("Kafka producer not available. Skipping message send.")

        return jsonify(exam_to_return), 201
    except Exception as e:
        current_app.logger.error(f"Error creating exam: {e}")
        return jsonify({"error": "Could not create exam"}), 500


@exam_bp.route('/kids/<kid_id>/exams', methods=['GET'])
def get_exams_for_kid(kid_id):
    try:
        exam_collection = get_exam_collection()
        exams_cursor = exam_collection.find({"kid_id": kid_id})
        exams_list = []
        for exam in exams_cursor:
            exam["_id"] = str(exam["_id"]) # Convert ObjectId
            exams_list.append(exam)
        return jsonify(exams_list), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching exams for kid {kid_id}: {e}")
        return jsonify({"error": "Could not fetch exams"}), 500

@exam_bp.route('/exams/<exam_id_param>', methods=['GET'])
def get_exam_by_id(exam_id_param):
    try:
        exam_collection = get_exam_collection()
        # Try to find by application-specific exam_id first, then by MongoDB's _id
        exam = exam_collection.find_one({"exam_id": exam_id_param})
        if not exam and ObjectId.is_valid(exam_id_param): # Check if it could be an ObjectId
             exam = exam_collection.find_one({"_id": ObjectId(exam_id_param)})

        if exam:
            exam["_id"] = str(exam["_id"])
            return jsonify(exam), 200
        else:
            return jsonify({"error": "Exam not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching exam by id {exam_id_param}: {e}")
        return jsonify({"error": "Could not fetch exam"}), 500

@exam_bp.route('/exams/<exam_id_param>', methods=['PUT'])
def update_exam(exam_id_param):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    updates = {}
    if "exam_name" in data:
        updates["exam_name"] = data["exam_name"]
    if "exam_date" in data:
        try:
            datetime.strptime(data["exam_date"], "%Y-%m-%d")
            updates["exam_date"] = data["exam_date"]
        except ValueError:
            return jsonify({"error": "exam_date must be in YYYY-MM-DD format"}), 400
    if "subject" in data:
        updates["subject"] = data["subject"]
    if "marks_obtained_percentage" in data:
        try:
            marks = float(data["marks_obtained_percentage"])
            if not (0 <= marks <= 100):
                return jsonify({"error": "marks_obtained_percentage must be between 0 and 100"}), 400
            updates["marks_obtained_percentage"] = marks
        except ValueError:
            return jsonify({"error": "marks_obtained_percentage must be a valid number"}), 400
    if "class_top_percentage" in data: # Allows setting it to null or a value
        if data["class_top_percentage"] is not None:
            try:
                top_marks = float(data["class_top_percentage"])
                if not (0 <= top_marks <= 100):
                    return jsonify({"error": "class_top_percentage must be between 0 and 100"}), 400
                updates["class_top_percentage"] = top_marks
            except ValueError:
                return jsonify({"error": "class_top_percentage must be a valid number"}), 400
        else:
             updates["class_top_percentage"] = None


    if not updates:
        return jsonify({"error": "No update fields provided"}), 400

    updates["updated_at"] = datetime.utcnow()

    try:
        exam_collection = get_exam_collection()
        # Find by application-specific exam_id
        result = exam_collection.find_one_and_update(
            {"exam_id": exam_id_param},
            {"$set": updates},
            return_document=True # Requires PyMongo 3.0+
        )
        if result:
            result["_id"] = str(result["_id"])
            return jsonify(result), 200
        else:
            # If not found by exam_id, try by _id if valid ObjectId
            if ObjectId.is_valid(exam_id_param):
                result_by_oid = exam_collection.find_one_and_update(
                    {"_id": ObjectId(exam_id_param)},
                    {"$set": updates},
                    return_document=True
                )
                if result_by_oid:
                    result_by_oid["_id"] = str(result_by_oid["_id"])
                    return jsonify(result_by_oid), 200
            return jsonify({"error": "Exam not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error updating exam {exam_id_param}: {e}")
        return jsonify({"error": "Could not update exam"}), 500

@exam_bp.route('/exams/<exam_id_param>', methods=['DELETE'])
def delete_exam(exam_id_param):
    try:
        exam_collection = get_exam_collection()
        # Find by application-specific exam_id
        result = exam_collection.delete_one({"exam_id": exam_id_param})
        
        if result.deleted_count > 0:
            return jsonify({"message": "Exam deleted successfully"}), 200 # Or 204 No Content
        else:
            # If not found by exam_id, try by _id if valid ObjectId
            if ObjectId.is_valid(exam_id_param):
                 result_by_oid = exam_collection.delete_one({"_id": ObjectId(exam_id_param)})
                 if result_by_oid.deleted_count > 0:
                     return jsonify({"message": "Exam deleted successfully"}), 200
            return jsonify({"error": "Exam not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error deleting exam {exam_id_param}: {e}")
        return jsonify({"error": "Could not delete exam"}), 500

# --- OCR Endpoint ---
import pytesseract
from PIL import Image
import os
import re

UPLOAD_FOLDER = 'uploads' 
# Ensure UPLOAD_FOLDER is created at the root of exam-service, 
# or adjust path accordingly e.g. os.path.join(current_app.root_path, 'uploads')
# For simplicity here, assuming it's relative to where app.py is run from or an absolute path.
# A better approach might be to configure this in app.config.

if not os.path.exists(UPLOAD_FOLDER):
    try:
        os.makedirs(UPLOAD_FOLDER)
    except OSError as e:
        # This might happen if the script is run in an environment where it can't create directories
        # or if there's a race condition (though less likely for a simple startup).
        current_app.logger.error(f"Could not create upload folder: {UPLOAD_FOLDER} - {e}")
        pass # Continue, but uploads will likely fail


def parse_ocr_text(text):
    """
    A very basic parser for exam text.
    This should be significantly improved for real-world use.
    """
    parsed_data = {
        "exam_name": None,
        "subject": None,
        "marks_obtained_percentage": None,
        # "total_marks": None, # Not in current User model for exam directly
        # "grade": None, # Grade is part of User, not exam directly
    }

    # Extremely simplified regex - these would need to be much more robust
    exam_match = re.search(r"(?:Exam|Test|Assessment)[:\s]+([\w\s]+)", text, re.IGNORECASE)
    if exam_match:
        parsed_data["exam_name"] = exam_match.group(1).strip()

    subject_match = re.search(r"Subject[:\s]+([\w\s]+)", text, re.IGNORECASE)
    if subject_match:
        parsed_data["subject"] = subject_match.group(1).strip()
    
    # Look for percentage first
    marks_percentage_match = re.search(r"Marks.*?(\d{1,2}\.?\d*)\s*%", text, re.IGNORECASE)
    if marks_percentage_match:
        try:
            parsed_data["marks_obtained_percentage"] = float(marks_percentage_match.group(1))
        except ValueError:
            pass # Could not convert to float
    else:
        # Fallback: Look for "Marks: XX/YY" or "Score: XX/YY"
        marks_match = re.search(r"(?:Marks|Score)[:\s]+(\d{1,3}(?:\.\d{1,2})?)\s*(?:/|out of)\s*(\d{1,3}(?:\.\d{1,2})?)", text, re.IGNORECASE)
        if marks_match:
            try:
                obtained = float(marks_match.group(1))
                total = float(marks_match.group(2))
                if total > 0:
                    parsed_data["marks_obtained_percentage"] = round((obtained / total) * 100, 2)
            except ValueError:
                pass # Could not convert

    return parsed_data


@exam_bp.route('/kids/<kid_id>/exams/upload_image', methods=['POST'])
def upload_exam_image(kid_id): # kid_id is available if needed for context, not directly used in OCR parsing here
    if 'marks_sheet_image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['marks_sheet_image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        try:
            # Ensure upload folder exists (it might not if app started before mkdir command ran)
            if not os.path.exists(UPLOAD_FOLDER):
                 os.makedirs(UPLOAD_FOLDER)
                 current_app.logger.info(f"Created upload folder at: {os.path.abspath(UPLOAD_FOLDER)}")


            filename = str(uuid.uuid4()) + "_" + file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            current_app.logger.info(f"File saved to {filepath}")
            
            raw_text = pytesseract.image_to_string(Image.open(filepath))
            current_app.logger.info(f"Raw OCR Text: {raw_text}")
            
            parsed_data = parse_ocr_text(raw_text)
            
            return jsonify({
                "message": "Image processed successfully",
                "kid_id": kid_id,
                "extracted_data": {**parsed_data, "raw_text": raw_text}
            }), 200

        except pytesseract.TesseractNotFoundError:
            current_app.logger.error("Tesseract is not installed or not in PATH.")
            return jsonify({"error": "OCR processing unavailable: Tesseract not found on server."}), 500
        except Exception as e:
            current_app.logger.error(f"Error processing image: {e}")
            return jsonify({"error": f"Could not process image: {str(e)}"}), 500
        finally:
            if 'filepath' in locals() and os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    current_app.logger.info(f"Temporary file {filepath} deleted.")
                except Exception as e:
                    current_app.logger.error(f"Error deleting temporary file {filepath}: {e}")
    
    return jsonify({"error": "File processing failed"}), 500
