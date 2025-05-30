from pymongo.database import Database
from bson import ObjectId
from typing import List, Optional
from datetime import datetime, timezone

from models.insight_models import AIInsightCreate, AIInsightInDB, AIInsightUpdate
from db.mongodb import get_db # Ensure get_db is correctly providing the database instance

# Helper to get the collection; can be called by each CRUD function
def get_insights_collection():
    db = get_db()
    return db.ai_insights # "ai_insights" is the collection name

def create_insight(insight_data: AIInsightCreate) -> AIInsightInDB:
    collection = get_insights_collection()
    # Pydantic model to dict, ready for MongoDB
    # AIInsightCreate now includes default factories for insight_id and last_updated
    insight_dict = insight_data.model_dump(by_alias=True, exclude_none=True) 
    
    # Ensure last_updated is correctly set to current UTC time at the moment of creation,
    # overriding any default that might have been set when Pydantic model was initialized earlier.
    insight_dict["last_updated"] = datetime.now(timezone.utc)
    
    # Logic for "create or replace latest for kid": delete any existing insight(s) for this kid_id first.
    # This ensures only one active insight document per kid_id after generation.
    deleted_count = delete_insights_by_kid_id(insight_data.kid_id)
    if deleted_count > 0:
        print(f"Deleted {deleted_count} existing insight(s) for kid_id: {insight_data.kid_id} before creating new one.")

    insert_result = collection.insert_one(insight_dict)
    created_insight = collection.find_one({"_id": insert_result.inserted_id})
    
    if created_insight:
        # Convert MongoDB document to AIInsightInDB Pydantic model
        return AIInsightInDB.parse_obj(created_insight)
    return None # Should not happen if insert was successful

def get_insight_by_kid_id(kid_id: str) -> Optional[AIInsightInDB]:
    collection = get_insights_collection()
    # Assuming we want the latest insight if multiple could exist (e.g. by last_updated)
    # For now, assuming one active insight per kid_id or the most recently created one.
    insight_data = collection.find_one({"kid_id": kid_id}, sort=[("last_updated", -1)])
    if insight_data:
        return AIInsightInDB(**insight_data)
    return None

def get_insight_by_insight_id(insight_id: str) -> Optional[AIInsightInDB]:
    collection = get_insights_collection()
    insight_data = collection.find_one({"insight_id": insight_id})
    if insight_data:
        return AIInsightInDB(**insight_data)
    return None

def update_insight(insight_id: str, insight_data: AIInsightUpdate) -> Optional[AIInsightInDB]:
    collection = get_insights_collection()
    update_data = insight_data.model_dump(exclude_unset=True) # only include fields that are set
    
    # Ensure last_updated is set to current UTC time for the update
    update_data["last_updated"] = datetime.now(timezone.utc)

    result = collection.find_one_and_update(
        {"insight_id": insight_id},
        {"$set": update_data},
        return_document=True # Requires PyMongo >= 3.0
    )
    if result:
        return AIInsightInDB.parse_obj(result)
    return None

def delete_insight(insight_id: str) -> bool:
    collection = get_insights_collection()
    result = collection.delete_one({"insight_id": insight_id})
    return result.deleted_count > 0

def delete_insights_by_kid_id(kid_id: str) -> int:
    """Deletes all insights associated with a specific kid_id. Returns count of deleted documents."""
    collection = get_insights_collection()
    result = collection.delete_many({"kid_id": kid_id})
    return result.deleted_count

```
