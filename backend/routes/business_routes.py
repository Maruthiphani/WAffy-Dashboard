"""
Business-related API routes for WAffy Dashboard
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from app.models import Business, BusinessTag, UserSettings, User
from database import get_db

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["business"])

# Pydantic models for request/response
class BusinessTypeBase(BaseModel):
    name: str

class BusinessTypeResponse(BusinessTypeBase):
    id: int
    
    class Config:
        orm_mode = True

class BusinessTagBase(BaseModel):
    name: str

class BusinessTagResponse(BusinessTagBase):
    id: int
    business_type_id: int
    
    class Config:
        orm_mode = True

class BusinessTagCreate(BaseModel):
    name: str
    business_type_id: int

class UserBusinessTagsUpdate(BaseModel):
    tagIds: List[int]

# Business Type Routes
@router.get("/business/types", response_model=List[BusinessTypeResponse])
def get_business_types(db: Session = Depends(get_db)):
    """Get all business types"""
    business_types = db.query(Business).all()
    # Map business_id to id and business_type to name for the response
    return [{"id": b.business_id, "name": b.business_type} for b in business_types]

@router.post("/business/types", response_model=BusinessTypeResponse)
def add_business_type(type_data: BusinessTypeBase, db: Session = Depends(get_db)):
    """Add a new business type"""
    # Check if business type already exists
    existing_type = db.query(Business).filter(func.lower(Business.business_type) == func.lower(type_data.name)).first()
    if existing_type:
        return {"id": existing_type.business_id, "name": existing_type.business_type}
    
    # Create new business type
    new_type = Business(business_type=type_data.name)
    db.add(new_type)
    db.commit()
    db.refresh(new_type)
    
    # Return with proper field mapping
    return {"id": new_type.business_id, "name": new_type.business_type}

# Business Tag Routes
@router.get("/business/tags", response_model=List[BusinessTagResponse])
def get_business_tags(db: Session = Depends(get_db)):
    """Get all business tags"""
    business_tags = db.query(BusinessTag).all()
    # Return with proper field mapping
    return [{
        "id": t.tag_id, 
        "name": t.tag, 
        "business_type_id": t.business_type_id
    } for t in business_tags]

@router.get("/business/types/{business_type_id}/tags", response_model=List[BusinessTagResponse])
def get_business_tags_by_type(business_type_id: int, db: Session = Depends(get_db)):
    """Get business tags for a specific business type"""
    business_tags = db.query(BusinessTag).filter(BusinessTag.business_type_id == business_type_id).all()
    # Return with proper field mapping
    return [{
        "id": tag.tag_id, 
        "name": tag.tag, 
        "business_type_id": tag.business_type_id
    } for tag in business_tags]

@router.post("/business/tags", response_model=BusinessTagResponse)
def add_business_tag(tag_data: BusinessTagCreate, db: Session = Depends(get_db)):
    """Add a new business tag"""
    # Check if business type exists
    business_type = db.query(Business).filter(Business.business_id == tag_data.business_type_id).first()
    if not business_type:
        raise HTTPException(status_code=404, detail="Business type not found")
    
    # Check if tag already exists for this business type
    existing_tag = db.query(BusinessTag).filter(
        func.lower(BusinessTag.tag) == func.lower(tag_data.name),
        BusinessTag.business_type_id == tag_data.business_type_id
    ).first()
    if existing_tag:
        return {
            "id": existing_tag.tag_id,
            "name": existing_tag.tag,
            "business_type_id": existing_tag.business_type_id
        }
    
    # Create new business tag
    new_tag = BusinessTag(
        tag=tag_data.name,
        business_type_id=tag_data.business_type_id
    )
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    
    return {
        "id": new_tag.tag_id,
        "name": new_tag.tag,
        "business_type_id": new_tag.business_type_id
    }

# User Business Tags Routes
@router.get("/users/{clerk_id}/business-tags", response_model=List[int])
def get_user_business_tags(clerk_id: str, db: Session = Depends(get_db)):
    """Get business tags for a specific user"""
    # Find user by clerk_id
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user settings
    settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not settings:
        return []
    
    # Parse business tags from settings
    try:
        if settings.business_tags:
            # If business_tags is stored as a JSON string, parse it
            if isinstance(settings.business_tags, str):
                import json
                return json.loads(settings.business_tags)
            # If it's already a list, return it directly
            return settings.business_tags
        return []
    except Exception as e:
        logger.error(f"Error parsing business tags: {e}")
        return []

@router.put("/users/{clerk_id}/business-tags", response_model=List[int])
def update_user_business_tags(clerk_id: str, tags_data: UserBusinessTagsUpdate, db: Session = Depends(get_db)):
    """Update business tags for a specific user"""
    # Find user by clerk_id
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user settings
    settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="User settings not found")
    
    # Update business tags
    # Store as JSON string
    import json
    settings.business_tags = json.dumps(tags_data.tagIds)
    db.commit()
    
    return tags_data.tagIds
