# Exam Service

This service is responsible for managing exams for kids in the Kids Study Planner application.

## Prerequisites

*   Python 3
*   MongoDB (running locally or accessible)
*   **Tesseract OCR Engine**: This service uses Pytesseract for OCR. You must have Tesseract installed on the system where the service is running. Refer to the official Tesseract documentation for installation instructions for your OS (e.g., `sudo apt-get install tesseract-ocr` on Debian/Ubuntu).

## Setup

1.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    The `requirements.txt` file includes `Flask`, `Flask-PyMongo`, `python-dotenv`, `Werkzeug`, `Pytesseract`, `Pillow`, and `kafka-python`.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    Create a `.env` file in the `exam-service` directory by copying `.env.example`:
    ```bash
    cp .env.example .env
    ```
    Update the `.env` file with your MongoDB connection details and Kafka broker information if they differ from the defaults.
    Key environment variables:
    *   `MONGO_URI`: MongoDB connection string.
    *   `KAFKA_BOOTSTRAP_SERVERS`: Comma-separated list of Kafka brokers (e.g., `localhost:9092`).
    *   `KAFKA_EXAM_TOPIC`: Kafka topic for exam events (e.g., `exam_events`).

## Running the Service

1.  **Ensure your virtual environment is activated.**
2.  **Set the Flask app environment variable (if not set in `.env` or if you want to override):**
    ```bash
    export FLASK_APP=app.py  # On Windows use `set FLASK_APP=app.py`
    export FLASK_ENV=development # Optional: for development mode
    ```
3.  **Run the Flask development server:**
    ```bash
    flask run
    ```
    The service will typically start on `http://127.0.0.1:5000/`.

## API Endpoints

*   **`GET /api/exams/health`**: Health check for the service.
*   **`POST /api/kids/<kid_id>/exams`**: Create a new exam for a kid.
    *   Request Body: Exam data (JSON) - see `models/exam.py` for fields like `exam_name`, `exam_date`, `subject`, `marks_obtained_percentage`.
    *   Response: Created exam object (JSON) with HTTP 201 status.
*   **`GET /api/kids/<kid_id>/exams`**: Retrieves a list of all exams for a specific kid.
    *   Response: List of exam objects (JSON).
*   **`POST /api/kids/<kid_id>/exams/upload_image`**: Uploads an image of a marks sheet for OCR processing.
    *   Request Body: Multipart form data with an image file under the key `marks_sheet_image`.
    *   Response: JSON object with extracted text and parsed data (e.g., `exam_name`, `subject`, `marks_obtained_percentage`).
*   **`GET /api/exams/<exam_id>`**: Retrieves a specific exam by its `exam_id`.
    *   Response: Exam object (JSON) or HTTP 404 if not found.
*   **`PUT /api/exams/<exam_id>`**: Update an existing exam.
    *   Request Body: Exam data (JSON) with fields to update.
    *   Response: Updated exam object (JSON) or HTTP 404 if not found.
*   **`DELETE /api/exams/<exam_id>`**: Delete an exam.
    *   Response: Success message with HTTP 200 or HTTP 204 (No Content), or HTTP 404 if not found.

## Kafka Integration
*   When a new exam is created via `POST /api/kids/<kid_id>/exams`, an event is sent to a Kafka topic (configured by `KAFKA_EXAM_TOPIC`).
*   This requires a running Kafka instance accessible via `KAFKA_BOOTSTRAP_SERVERS`. If Kafka is unavailable, the service will log a warning, but the exam creation will still succeed.
```
