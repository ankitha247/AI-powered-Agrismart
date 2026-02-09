from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    language: str = "en"

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str  # This is the important field - should match what you're returning
    name: str
    email: EmailStr
    phone: str
    language: str
    created_at: datetime
    farms: List[dict] = []

    class Config:
        from_attributes = True


class FarmCreate(BaseModel):
    name: str
    location: str
    size_acres: float
    soil_type: str

class FarmResponse(BaseModel):
    id: str
    name: str
    location: str
    size_acres: float
    soil_type: str

class YieldPredictionInput(BaseModel):
    crop_name: str
    soil_type: str
    season: str
    irrigation_source: str
    state: str
    district: str

class YieldPredictionResponse(BaseModel):
    prediction_id: str
    predicted_yield: float
    confidence: float
    recommendations: List[str]
    timestamp: datetime
    message: str

class CropRecommendationInput(BaseModel):
    state: str
    district: str
    soil_type: str
    season: str
    irrigation_source: str

class CropRecommendationResponse(BaseModel):
    prediction_id: str
    recommendations: List[dict]
    message: str
    form_options: dict