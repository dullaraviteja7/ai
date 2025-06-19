from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import uuid
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DATA_FILE = os.path.join(DATA_DIR, 'study_data.json')

def ensure_data_file_exists():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.isfile(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({"kids": []}, f, indent=4)

def read_data():
    ensure_data_file_exists()
    with open(DATA_FILE, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            # If file is empty or corrupted, initialize with default structure
            data = {"kids": []}
    return data

def write_data(data):
    ensure_data_file_exists()
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def home():
    return "Hello from Flask Backend!"

@app.route('/api/kids/register', methods=['POST'])
def register_kid():
    data = request.get_json()

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
    new_kid = {
        "id": kid_id,
        "name": data['name'],
        "age": data['age'],
        "grade": data['grade'],
        "subjects": data['subjects'],
        "school_name": data.get('school_name'),
        "school_timings": data.get('school_timings'),
        "preferred_study_hours": data.get('preferred_study_hours'),
        "improvement_areas": data.get('improvement_areas', []),
        "preferred_subjects": data.get('preferred_subjects', []),
        "exams": [],
        "ai_insights": {}
    }

    current_data = read_data()
    current_data['kids'].append(new_kid)
    write_data(current_data)

    return jsonify(new_kid), 201

@app.route('/api/kids/<kid_id>/exams', methods=['POST'])
def add_exam_data(kid_id):
    exam_data = request.get_json()

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
    exam_date = exam_data.get('exam_date')
    if not isinstance(exam_date, str) or len(exam_date) != 10 or exam_date[4] != '-' or exam_date[7] != '-':
        return jsonify({"error": "exam_date must be a string in YYYY-MM-DD format"}), 400
    try:
        year, month, day = map(int, exam_date.split('-'))
        if not (1 <= month <= 12 and 1 <= day <= 31): # Basic sanity check for month/day
             raise ValueError("Invalid month or day")
    except ValueError:
        return jsonify({"error": "Invalid date in exam_date. Ensure YYYY-MM-DD format and valid day/month."}), 400


    current_data = read_data()
    kid_found = None
    for kid in current_data['kids']:
        if kid['id'] == kid_id:
            kid_found = kid
            break

    if not kid_found:
        return jsonify({"error": "Kid not found"}), 404

    exam_id = uuid.uuid4().hex
    new_exam = {
        "exam_id": exam_id,
        "exam_name": exam_data['exam_name'],
        "exam_date": exam_data['exam_date'],
        "subject": exam_data['subject'],
        "marks_obtained_percentage": exam_data['marks_obtained_percentage'],
        "class_top_percentage": exam_data.get('class_top_percentage')
    }

    kid_found.setdefault('exams', []).append(new_exam)
    write_data(current_data)

    return jsonify(new_exam), 201

@app.route('/api/kids', methods=['GET'])
def get_all_kids():
    data = read_data() # This already returns a dict, e.g. {"kids": []}
    return jsonify(data), 200

@app.route('/api/kids/<kid_id>', methods=['GET'])
def get_kid_data(kid_id):
    current_data = read_data()
    kid_found = None
    for kid in current_data['kids']:
        if kid['id'] == kid_id:
            kid_found = kid
            break

    if kid_found:
        return jsonify(kid_found), 200
    else:
        return jsonify({"error": "Kid not found"}), 404

@app.route('/api/kids/<kid_id>/ai-insights', methods=['POST'])
def generate_ai_insights(kid_id):
    current_data = read_data()
    kid_to_update = None
    for kid_obj in current_data['kids']:
        if kid_obj['id'] == kid_id:
            kid_to_update = kid_obj
            break

    if not kid_to_update:
        return jsonify({"error": "Kid not found"}), 404

    # Mock data generation
    kid_name = kid_to_update.get('name', 'The student')

    # Try to get a subject from the last exam, or a preferred subject, or a general subject
    last_subject = "a subject"
    if kid_to_update.get('exams') and len(kid_to_update['exams']) > 0:
        last_subject = kid_to_update['exams'][-1].get('subject', "a subject")
    elif kid_to_update.get('preferred_subjects') and len(kid_to_update['preferred_subjects']) > 0:
        last_subject = kid_to_update['preferred_subjects'][0]
    elif kid_to_update.get('subjects') and len(kid_to_update['subjects']) > 0:
        last_subject = kid_to_update['subjects'][0]

    improvement_area_1 = "a specific area"
    if kid_to_update.get('improvement_areas') and len(kid_to_update['improvement_areas']) > 0:
        improvement_area_1 = kid_to_update['improvement_areas'][0]

    preferred_subject_1 = "a preferred subject"
    if kid_to_update.get('preferred_subjects') and len(kid_to_update['preferred_subjects']) > 0:
        preferred_subject_1 = kid_to_update['preferred_subjects'][0]
    elif kid_to_update.get('subjects') and len(kid_to_update['subjects']) > 0: # fallback to general subjects
        preferred_subject_1 = kid_to_update['subjects'][0]


    mock_insights = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "progress_analysis": f"Based on recent performance, {kid_name} is showing good progress in {last_subject}. Areas like {improvement_area_1} could benefit from more focus.",
        "schedules": {
            "daily": [f"Review {last_subject} for 45 mins", f"Practice {improvement_area_1} for 30 mins"],
            "weekly": [f"Complete project on {preferred_subject_1}", f"Read a chapter from {last_subject} textbook"],
            "monthly": [f"Prepare for upcoming {last_subject} test", f"Explore {preferred_subject_1} further"]
        },
        "suggestions": [f"Try using flashcards for {last_subject}", f"Dedicate 15 minutes daily to {improvement_area_1}"]
    }

    kid_to_update['ai_insights'] = mock_insights
    write_data(current_data)

    return jsonify(mock_insights), 200

if __name__ == '__main__':
    ensure_data_file_exists()  # Ensure it exists on startup
    app.run(debug=True)
