# Analytics Service (Go)

This service is responsible for collecting data from other services (like Exam Service) and generating analytics for the Kids Study Planner application.

## Prerequisites

*   Go (version 1.18 or higher recommended)
*   MongoDB (running locally or accessible)

## Setup

1.  **Navigate to the service directory:**
    ```bash
    cd analytics-service
    ```

2.  **Initialize Go Module (if not already done):**
    Replace `your_module_path` with your Go module path (e.g., `github.com/yourusername/kids-study-planner/analytics-service`).
    ```bash
    go mod init your_module_path 
    # Example: go mod init kids-study-planner/analytics-service
    ```
    (For this project, a simpler module name like `analytics-service` might be used if it's not intended for public hosting)

3.  **Install Dependencies:**
    This will fetch the necessary dependencies listed in `go.mod` (which will be created/updated by `go get` commands later or by `go mod tidy`).
    Key dependencies include:
    *   `go.mongodb.org/mongo-driver`
    *   `github.com/joho/godotenv`
    *   `github.com/segmentio/kafka-go`
    ```bash
    go mod tidy 
    # or run 'go get' for specific packages as you add them in the code
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the `analytics-service` directory by copying `.env.example`:
    ```bash
    cp .env.example .env
    ```
    Update the `.env` file with your MongoDB connection details and other service URLs as needed.

## Running the Service

1.  **Ensure your environment variables are set up (in the `.env` file).**
2.  **Run the application:**
    ```bash
    go run main.go
    ```
    The service will typically start on a configured port (e.g., 5003). Check the application output for the exact address.

## API Endpoints

*   **`GET /api/analytics/health`**: Health check for the service.
*   **`POST /api/analytics/aggregate`**: Triggers the aggregation of exam data to calculate and store subject averages.
    *   This endpoint currently uses **mocked exam data** as it assumes an internal endpoint `GET {EXAM_SERVICE_URL}/api/exams/internal/all` from the Exam Service which is not yet implemented.
    *   Returns a success message with a count of subjects processed.
*   **`GET /api/analytics/subject-averages`**: Retrieves the currently stored aggregated subject averages.
    *   Returns a list of subject average objects.

(Further endpoint details for kid-specific analytics will be added as implemented.)

## Kafka Integration
*   The service listens to a Kafka topic (defined by `KAFKA_EXAM_TOPIC` and `KAFKA_BOOTSTRAP_SERVERS`) for exam events.
*   Upon receiving an exam event, it currently triggers a full re-aggregation of analytics (by fetching all exam data, which is currently mocked).
*   This requires a running Kafka instance. If Kafka is unavailable, the consumer will log errors and attempt to reconnect.

## Environment Variables

Make sure to configure these in your `.env` file (see `.env.example`):

*   `MONGO_URI`: MongoDB connection string (e.g., `mongodb://localhost:27017`)
*   `MONGO_DB_NAME_ANALYTICS`: Database name for this service (e.g., `analytics_service_db`)
*   `SERVER_PORT`: Port for this service (e.g., `5003`)
*   `EXAM_SERVICE_URL`: Base URL for the Exam Service (e.g., `http://localhost:5001/api/exams`). Used to fetch exam data (currently mocked for the aggregation trigger).
*   `KAFKA_BOOTSTRAP_SERVERS`: Comma-separated list of Kafka brokers (e.g., `localhost:9092`).
*   `KAFKA_EXAM_TOPIC`: Kafka topic for incoming exam events (e.g., `exam_events`).
*   `KAFKA_CONSUMER_GROUP_ID`: Kafka consumer group ID for this service (e.g., `analytics_service_group`).
```
