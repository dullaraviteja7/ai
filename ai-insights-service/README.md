# AI Insights Service

This service is responsible for generating AI-powered insights and study schedules for kids in the Kids Study Planner application.

## Prerequisites

*   Python 3
*   MongoDB (running locally or accessible)

## Setup

1.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    Create a `.env` file in the `ai-insights-service` directory by copying `.env.example`:
    ```bash
    cp .env.example .env
    ```
    Update the `.env` file with your MongoDB connection details and any external AI model URLs/API keys.

## Running the Service

1.  **Ensure your virtual environment is activated.**
2.  **Run the FastAPI application using Uvicorn:**
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 5002
    ```
    The service will typically start on `http://0.0.0.0:5002/`. The `--reload` flag enables auto-reloading for development.

## API Endpoints

*   **`GET /api/ai-insights/health`**: Health check for the service.
*   **`POST /api/ai-insights/generate/{kid_id}`**: Triggers AI insight generation for a specific kid.
    *   This endpoint fetches data from the User Service and Exam Service.
    *   It then (conceptually) calls an external AI model to get insights.
    *   The generated insight is stored in MongoDB (replaces any existing insight for the kid).
    *   Returns the newly created or updated insight.
*   **`GET /api/ai-insights/kid/{kid_id}`**: Retrieves the latest AI-generated insight for a specific kid.
*   **`GET /api/ai-insights/{insight_id}`**: Retrieves a specific insight by its unique `insight_id`.
*   **`PUT /api/ai-insights/{insight_id}`**: Updates an existing AI insight (e.g., if a user wants to manually tweak suggestions).
*   **`DELETE /api/ai-insights/{insight_id}`**: Deletes a specific AI insight.

## Environment Variables

Make sure to configure these in your `.env` file:

*   `MONGO_URI`: MongoDB connection string (e.g., `mongodb://localhost:27017/`)
*   `MONGO_DB_NAME_AI_INSIGHTS`: Database name for this service (e.g., `ai_insights_db`)
*   `USER_SERVICE_URL`: Base URL for the User Service (e.g., `http://localhost:8080/api/users`)
*   `EXAM_SERVICE_URL`: Base URL for the Exam Service (e.g., `http://localhost:5001/api/exams`)
*   `COLAB_MODEL_URL`: URL for the external AI model endpoint.
*   `COLAB_API_KEY`: API Key for the external AI model, if required.

(Refer to `.env.example` for the format.)
```
