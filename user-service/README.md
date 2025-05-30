# User Service

This is the User Service for the Kids Study Planner application. It handles user-related operations and data.

## Prerequisites

*   Java 11 or higher
*   Maven
*   MongoDB (running locally or accessible)

## Setup

1.  **Configure MongoDB:**
    Open `src/main/resources/application.properties` and update the `spring.data.mongodb.uri` if your MongoDB instance is not running on `mongodb://localhost:27017/user_service_db`.

2.  **Build the project:**
    ```bash
    mvn clean install
    ```

## Running the server

1.  **Run the application:**
    ```bash
    mvn spring-boot:run
    ```
    Alternatively, you can run the packaged jar:
    ```bash
    java -jar target/user-service-0.0.1-SNAPSHOT.jar
    ```

The server will start on port 8080 by default (this can be changed in `application.properties` by adding `server.port=NEW_PORT_NUMBER`).

## Endpoints

*   **`GET /api/users/health`**: Health check endpoint to verify if the User Service is running.
*   **`POST /api/users/register`**: Registers a new user.
    *   Request Body: User object (JSON) - see `User.java` for fields like `name`, `age`, `grade`, `subjects`.
    *   Response: Created user object (JSON) with HTTP 201 status.
*   **`GET /api/users`**: Retrieves a list of all registered users.
    *   Response: List of user objects (JSON).
*   **`GET /api/users/{id}`**: Retrieves a specific user by their ID.
    *   Response: User object (JSON) or HTTP 404 if not found.
