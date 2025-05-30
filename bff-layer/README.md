# BFF Layer

This is the Backend For Frontend (BFF) layer for the Kids Study Planner application. It serves as an intermediary between the frontend and the Python backend.

## Setup

1.  **Install dependencies:**
    ```bash
    npm install
    ```

## Running the server

1.  **Start the server:**
    ```bash
    node server.js
    ```

The server will start on port 3000 by default.

## Endpoints

*   **GET /api/bff/health:** Health check endpoint to verify if the BFF is running.
*   **All requests starting with `/api/v1`:** These requests are proxied to the Python backend running on `http://localhost:5000`.
