from fastapi import FastAPI
from dotenv import load_dotenv
import uvicorn
import os

from routers import insight_routes
from db.mongodb import connect_to_mongo, close_mongo_connection

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="AI Insights Service")

@app.on_event("startup")
async def startup_db_client():
    connect_to_mongo()
    # You could add other startup tasks here, like connecting to other services
    # or initializing resources for the AI model.

@app.on_event("shutdown")
async def shutdown_db_client():
    close_mongo_connection()
    # Clean up other resources if any

# Include routers
app.include_router(insight_routes.router, prefix="/api/ai-insights", tags=["AI Insights"])

# Root endpoint (optional)
@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Insights Service. Visit /docs for API documentation."}

if __name__ == "__main__":
    # This is for direct execution, e.g., for local debugging without Uvicorn CLI.
    # Uvicorn is the recommended ASGI server for FastAPI.
    # Use: uvicorn main:app --reload --host 0.0.0.0 --port 5002
    # The port and host can also be configured via environment variables if needed.
    
    host = os.getenv("HOST", "0.0.0.0")
    try:
        port = int(os.getenv("PORT", "5002"))
    except ValueError:
        port = 5002 # Default if PORT env var is invalid

    uvicorn.run("main:app", host=host, port=port, reload=True)

```
