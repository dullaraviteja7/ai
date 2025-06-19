# Kids Study Planner

## Overview/Description

The Kids Study Planner is a web application designed to help parents manage their children's study schedules, track academic progress, and gain AI-driven insights for personalized learning. It allows for registration of multiple children, logging exam results, and viewing performance trends.

## Features

*   **Kid Registration:** Register children with details like name, age, grade, subjects, school information, and learning preferences.
*   **Exam Data Management:** Record exam results for each child, including exam name, date, subject, marks obtained, and class top performance.
*   **Parent Dashboard with Progress Charts:**
    *   View detailed information for each registered child.
    *   Visualize academic progress through charts:
        *   Average marks per subject.
        *   Exam performance over time.
*   **Personalized Study Schedules and Suggestions (via Mock AI):** Generate mock AI-driven insights, including personalized study schedules (daily, weekly, monthly) and actionable suggestions based on the child's data.

## Technical Stack

*   **Frontend:** React, React Router (for navigation), Recharts (for charts)
*   **Backend:** Python (Flask), Flask-CORS (for handling cross-origin requests)
*   **Data Storage:** JSON files (for simplicity in this version)

## Project Structure

```
kids-study-planner/
├── backend/         # Flask application
│   ├── data/        # JSON data storage (study_data.json)
│   ├── app.py       # Main Flask application logic and API endpoints
│   └── requirements.txt # Python dependencies
├── frontend/        # React application (created using create-react-app)
│   └── client/
│       ├── public/    # Static assets and index.html
│       ├── src/       # React components, pages, services, etc.
│       │   ├── pages/ # Page components (HomePage, KidRegistrationPage, etc.)
│       │   ├── App.js # Main App component with routing
│       │   └── ...
│       └── package.json # Frontend dependencies and scripts
└── README.md        # This file
```

## Setup and Installation

### Prerequisites

*   Node.js and npm (or yarn)
*   Python 3.x and pip

### Backend Setup

1.  Navigate to the `backend` directory:
    ```bash
    cd kids-study-planner/backend
    ```
2.  Create a virtual environment (recommended):
    ```bash
    python -m venv venv
    ```
3.  Activate the virtual environment:
    *   On macOS/Linux: `source venv/bin/activate`
    *   On Windows: `venv\Scripts\activate`
4.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Frontend Setup

1.  Navigate to the `frontend/client` directory:
    ```bash
    cd kids-study-planner/frontend/client
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
    (or `yarn install` if you prefer yarn)

## Running the Application

### Backend

1.  Ensure you are in the `kids-study-planner/backend` directory.
2.  Activate the virtual environment (if you created one).
3.  Run the Flask server:
    ```bash
    python app.py
    ```
    (Alternatively, you might use `flask run` if your environment is configured for it).
4.  The backend will typically start on `http://localhost:5000`. You should see output in the terminal indicating it's running.

### Frontend

1.  Ensure you are in the `kids-study-planner/frontend/client` directory.
2.  Run the React development server:
    ```bash
    npm start
    ```
    (or `yarn start`)
3.  The frontend development server will typically start on `http://localhost:3000` and automatically open the application in your default web browser.

## API Endpoints

The backend provides the following main API endpoints:

*   `POST /api/kids/register`: Register a new kid.
*   `GET /api/kids`: Get a list of all registered kids.
*   `GET /api/kids/<kid_id>`: Get detailed information for a specific kid.
*   `POST /api/kids/<kid_id>/exams`: Add exam data for a specific kid.
*   `POST /api/kids/<kid_id>/ai-insights`: Generate (mock) AI-driven study insights for a specific kid.

## Future Enhancements

*   **Real AI Model Integration:** Connect to a more sophisticated AI model (e.g., deployed on Google Colab or a cloud platform) for generating insights.
*   **User Authentication:** Implement user accounts and authentication to secure data.
*   **Database Integration:** Replace JSON file storage with a relational or NoSQL database for better scalability and data management.
*   **More Detailed Charting Options:** Add more interactive charts and filtering options.
*   **UI/UX Improvements:** Enhance the user interface and user experience.
*   **Testing:** Add comprehensive unit and integration tests for both frontend and backend.
*   **Offline Capabilities:** Implement service workers for basic offline access to the frontend.
*   **Deployment:** Scripts and configurations for deploying to a cloud platform.
