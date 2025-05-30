from pydantic import BaseModel, Field, validator
from typing import List, Optional, Any
from datetime import datetime, timezone
import uuid
from bson import ObjectId # For MongoDB _id handling

# Helper for ObjectId validation and serialization if needed directly in models
# Pydantic V2 has better built-in support for this.
# For this setup, we'll handle ObjectId conversion in CRUD/routes primarily.
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field: Any = None): # field added for Pydantic v1 compatibility
        if ObjectId.is_valid(v):
            return ObjectId(v)
        # Try to convert if it's a string representation of ObjectId
        if isinstance(v, str):
            try:
                return ObjectId(v)
            except Exception:
                raise ValueError("Not a valid ObjectId string")
        raise ValueError("Invalid ObjectId")


    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class AIInsightBase(BaseModel):
    kid_id: str = Field(..., description="Identifier for the kid this insight pertains to")
    progress_analysis: Optional[str] = "No analysis generated yet."
    daily_schedule: List[str] = Field(default_factory=list)
    weekly_schedule: List[str] = Field(default_factory=list)
    monthly_schedule: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    
    class Config:
        # For Pydantic V2, use `model_config = {"populate_by_name": True}`
        # For Pydantic V1:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str, datetime: lambda dt: dt.isoformat()}


class AIInsightCreate(AIInsightBase):
    # insight_id and last_updated will be set by the application logic before saving
    insight_id: str = Field(default_factory=lambda: uuid.uuid4().hex, description="Unique identifier for the AI insight, auto-generated.")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of when the insight was created/updated.")


class AIInsightUpdate(BaseModel): # For PUT requests, allow partial updates
    progress_analysis: Optional[str] = None
    daily_schedule: Optional[List[str]] = None
    weekly_schedule: Optional[List[str]] = None
    monthly_schedule: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None
    # last_updated will be set automatically on update
    
    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat()}


class AIInsightInDBBase(AIInsightBase):
    # Represents the structure in MongoDB, including MongoDB's _id
    # and our application-specific insight_id
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id") # MongoDB's primary key
    insight_id: str = Field(...) # Our application-specific unique ID
    last_updated: datetime = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True # For PyObjectId
        json_encoders = {ObjectId: str, datetime: lambda dt: dt.isoformat()}

# This model will be used for reading data from the DB and converting to AIInsightResponse
class AIInsightInDB(AIInsightInDBBase): 
    pass


class AIInsightResponse(AIInsightBase):
    insight_id: str
    last_updated: datetime

    @validator("last_updated", pre=True, always=True)
    def ensure_datetime_is_aware(cls, v):
        if isinstance(v, str):
            try:
                # Attempt to parse ISO format string
                v_dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                if v_dt.tzinfo is None: # If still naive, assume UTC
                    return v_dt.replace(tzinfo=timezone.utc)
                return v_dt
            except ValueError:
                raise ValueError("Invalid datetime format string")
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v
    
    class Config:
        # For Pydantic V2, use `model_config = {"from_attributes": True}`
        # For Pydantic V1:
        orm_mode = True 
        json_encoders = {datetime: lambda dt: dt.isoformat()}


# Request model for generating insights
class GenerateInsightRequest(BaseModel):
    kid_id: str = Field(..., description="The ID of the kid for whom to generate insights.")
    # Example of other data that might be needed for the AI model, not used yet
    # current_goals: Optional[List[str]] = None
    # specific_focus_areas: Optional[List[str]] = None

# Response from external AI model (example structure)
class AIModelResponse(BaseModel):
    progress_analysis: str
    daily_schedule: List[str]
    weekly_schedule: List[str]
    monthly_schedule: List[str]
    suggestions: List[str]

# Data to be sent to the AI model
class AIModelInput(BaseModel):
    kid_id: str
    user_details: Optional[dict] = None # From User Service
    exam_data: Optional[List[dict]] = None # From Exam Service
    # Add any other relevant data
```
