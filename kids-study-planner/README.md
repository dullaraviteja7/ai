# Kids Study Planner

## Overview

The Kids Study Planner is a comprehensive web application designed to empower parents in managing their children's educational journey. It facilitates tracking academic progress, organizing study schedules, and leveraging AI-driven insights for personalized learning strategies. The application supports multiple children, detailed exam logging, OCR for quick exam data entry from images, and rich data visualizations.

## Features

*   **Kid Registration:** Register children with details like name, age, grade, subjects, school information, and learning preferences.
*   **Exam Data Management:** Record exam results including exam name, date, subject, marks obtained, and class top performance.
*   **HSQLDB Data Persistence:** All application data (kid details, exam results, AI insights) is stored reliably in an HSQLDB database.
*   **Exam Result Image Upload with OCR:** Upload images of exam mark sheets; the system uses Pytesseract OCR to extract data (exam name, subject, marks) and pre-fill the form, saving manual entry time.
*   **AI-Powered Study Insights:** Connects to an external AI model (e.g., deployed on Colab or another platform) to generate personalized study schedules (daily, weekly, monthly) and actionable learning suggestions based on the child's data.
*   **Parent Dashboard with Enhanced Visualizations:**
    *   View detailed information for each registered child.
    *   Visualize academic progress through interactive charts:
        *   Average marks per subject (Bar Chart).
        *   Exam performance over time (Line Chart) with filtering options (date range, subject).
        *   Marks vs. Class Top Percentage (Scatter Plot) for comparative analysis.
    *   Tooltips on charts provide detailed information for each data point.

## Technology Stack

*   **Backend:**
    *   Python 3.8+
    *   Flask (for RESTful API development)
    *   Flask-CORS (for Cross-Origin Resource Sharing)
    *   HSQLDB (for database storage, accessed via JayDeBeApi)
    *   Pytesseract (for Optical Character Recognition - OCR)
    *   Pillow (for image manipulation with Pytesseract)
    *   Requests (for making HTTP requests to the external AI model)
    *   python-dotenv (for managing environment variables)
*   **Frontend:**
    *   React (with functional components and hooks)
    *   React Router (for client-side navigation)
    *   Recharts (for interactive charts)
*   **Testing (Backend):**
    *   Pytest (for unit and integration testing)
    *   Pytest-Mock (for mocking dependencies)

## Project Structure

```
kids-study-planner/
├── backend/                     # Flask application root
│   ├── data/                    # Stores HSQLDB database file (e.g., study_planner.db.script)
│   ├── lib/                     # For HSQLDB JAR file (hsqldb.jar)
│   ├── uploads/                 # Temporary storage for uploaded exam images
│   ├── tests/                   # Pytest unit and integration tests
│   │   ├── __init__.py
│   │   ├── test_app.py
│   │   └── test_database.py
│   ├── .env                     # Environment variable configuration (gitignored)
│   ├── .gitignore
│   ├── app.py                   # Main Flask application logic and API endpoints
│   ├── database.py              # Database connection and initialization logic
│   └── requirements.txt         # Python dependencies
├── frontend/                    # React application root
│   └── client/
│       ├── public/                # Static assets and index.html
│       ├── src/                   # React components, pages, services, etc.
│       │   ├── pages/             # Page components (KidRegistrationPage, ParentViewPage, etc.)
│       │   ├── App.js             # Main App component with routing
│       │   └── ...
│       └── package.json           # Frontend dependencies and scripts
└── README.md                    # This file
```

## Setup and Installation

### Prerequisites

*   **Python:** Version 3.8 or higher.
*   **Node.js and npm:** Node.js version 14.x or higher (which includes npm).
*   **Java Runtime Environment (JRE):** Required for HSQLDB. Version 8 or higher.
*   **HSQLDB JAR File:** Download `hsqldb.jar` (e.g., version 2.7.2 from [hsqldb.org](https://hsqldb.org/download/)).
*   **Tesseract OCR Engine:**
    *   **Linux (Debian/Ubuntu):** `sudo apt-get update && sudo apt-get install -y tesseract-ocr`
    *   **macOS:** `brew install tesseract`
    *   **Windows:** Download the installer from the [Tesseract at UB Mannheim page](https://github.com/UB-Mannheim/tesseract/wiki) and ensure Tesseract is added to your system's PATH.

### Backend Setup

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd kids-study-planner/backend
    ```
2.  **Create `lib/` Directory:**
    ```bash
    mkdir lib
    ```
3.  **Place HSQLDB JAR:**
    Download `hsqldb.jar` and place it into the `kids-study-planner/backend/lib/` directory.

4.  **Install Tesseract OCR:** Follow the instructions in the "Prerequisites" section if not already installed.

5.  **Create Python Virtual Environment:**
    ```bash
    python -m venv venv
    ```
6.  **Activate Virtual Environment:**
    *   Linux/macOS: `source venv/bin/activate`
    *   Windows: `venv\Scripts\activate`

7.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    (`python-dotenv` is included and will be installed).

8.  **Configure Environment Variables:**
    Create a `.env` file in the `kids-study-planner/backend/` directory. Add the following content (adjust as needed):
    ```env
    # kids-study-planner/backend/.env
    FLASK_APP=app.py
    FLASK_ENV=development # Use 'production' for deployment

    # Optional: Configuration for the external AI model for insights
    # If COLAB_MODEL_URL is not set, the application will use a public test API.
    # COLAB_MODEL_URL=YOUR_COLAB_MODEL_ENDPOINT_HERE
    # COLAB_API_KEY=YOUR_COLAB_API_KEY_HERE
    ```
    The `app.py` file uses `python-dotenv` to automatically load these variables when the application starts. Ensure `.env` is listed in your `backend/.gitignore` file (it has been added in this project).

9.  **Database and Uploads Directory Initialization:**
    The HSQLDB database file will be created in the `kids-study-planner/backend/data/` directory, and the `kids-study-planner/backend/uploads/` directory for temporary image uploads will be created automatically when the Flask application first runs and these features are accessed.

10. **Run Backend Server:**
    ```bash
    flask run
    ```
    The backend server will typically start on `http://localhost:5000`.

### Frontend Setup

1.  Navigate to the frontend client directory:
    ```bash
    cd kids-study-planner/frontend/client 
    ```
    (Adjust path if your current directory is different).
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the frontend development server:
    ```bash
    npm start
    ```
    The frontend application will typically open automatically in your browser at `http://localhost:3000`.

## Running Backend Tests

1.  Ensure you are in the `kids-study-planner/backend/` directory.
2.  Activate your Python virtual environment (e.g., `source venv/bin/activate`).
3.  Make sure the HSQLDB JAR (`hsqldb.jar`) is in the `kids-study-planner/backend/lib/` directory and Tesseract OCR is installed and accessible in your system's PATH.
4.  Run the tests using Pytest:
    ```bash
    pytest
    ```
    For more detailed output:
    ```bash
    pytest -v
    ```
    The tests will use dedicated test database files (e.g., `test_study_planner.db`, `test_app_study_planner.db`) in the `kids-study-planner/backend/tests/test_db_data/` directory, which are managed (created and cleaned up) by the test suite.

## Key API Endpoints

*   `GET /`: Home route, confirms backend is running.
*   `POST /api/kids/register`: Register a new kid.
    *   Payload: Kid details (name, age, grade, subjects, etc.).
*   `GET /api/kids`: Get a list of all registered kids.
*   `GET /api/kids/<kid_id>`: Get detailed information for a specific kid, including their exams and AI insights.
*   `POST /api/kids/<kid_id>/exams`: Add exam data for a specific kid.
    *   Payload: Exam details (exam name, date, subject, marks, etc.).
*   `POST /api/kids/<kid_id>/ai-insights`: Generate or refresh AI-driven study insights for a specific kid.
    *   Connects to an external AI model using `COLAB_MODEL_URL` and `COLAB_API_KEY` from `.env`.
*   `POST /api/kids/<kid_id>/exams/upload_image`: Upload an exam mark sheet image for OCR processing.
    *   Expects `multipart/form-data` with an image file under the key `marks_sheet_image`.
    *   Returns extracted text and parsed data (exam name, subject, marks).

## Troubleshooting

*   **HSQLDB JAR Not Found:** If you see errors related to `jaydebeapi` or HSQLDB, ensure `hsqldb.jar` is correctly placed in `kids-study-planner/backend/lib/`.
*   **Tesseract Not Found/Not in PATH:** If OCR fails with errors like "TesseractNotFoundError", ensure Tesseract OCR engine is installed correctly and its installation directory is included in your system's PATH environment variable. You might need to restart your terminal or system after installation.
*   **`flask run` command not found:** Ensure your virtual environment is activated and Flask is installed (`pip install Flask`).
*   **Port Conflicts:** If `localhost:5000` (backend) or `localhost:3000` (frontend) are in use, these services might fail to start or prompt you to use a different port.
*   **CORS Errors:** Ensure `Flask-CORS` is correctly configured on the backend if you encounter issues with frontend-backend communication (though it's set up in this project).
*   **Environment Variables Not Loaded:** Verify your `.env` file is in the `kids-study-planner/backend/` directory and correctly formatted. `python-dotenv` loads it at the start of `app.py`.

## Future Enhancements

*   **User Authentication & Authorization:** Secure the application with user accounts and roles.
*   **More Robust AI Model Integration:** Develop and deploy a more sophisticated AI model for generating more nuanced and accurate study insights.
*   **Direct Database Population from OCR:** Option to directly save OCR-extracted exam data after user review.
*   **Frontend Unit/Integration Tests:** Add comprehensive testing for the React components and services.
*   **CI/CD Pipeline:** Implement continuous integration and deployment.
*   **Containerization:** Dockerize the application for easier deployment and scaling.
```
