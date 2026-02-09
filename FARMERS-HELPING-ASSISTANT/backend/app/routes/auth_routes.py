from fastapi import APIRouter, HTTPException
from app.models.user_models import UserCreate, UserLogin, UserResponse
from app.utils.database import get_users_collection
from app.utils.translations import translator
from datetime import datetime
import bcrypt
import uuid
import hashlib 

router = APIRouter()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserCreate):
    try:
        print(f"🔐 Signup attempt for: {user_data.email}")
        
        users_collection = get_users_collection()
        
        if users_collection is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Check if user already exists
        existing_user = users_collection.find_one({"email": user_data.email})
        if existing_user:
            print(f"❌ User already exists: {user_data.email}")
            raise HTTPException(
                status_code=400, 
                detail=translator.translate('auth.email_exists', user_data.language)
            )
        
        user_id = str(uuid.uuid4())
        user_dict = {
            "_id": user_id,
            "name": user_data.name,
            "email": user_data.email,
            "phone": user_data.phone,
            "language": user_data.language,
            "password": hash_password(user_data.password),
            "created_at": datetime.utcnow(),
            "farms": []
        }
        
        print(f"💾 Attempting to save user: {user_data.email}")
        result = users_collection.insert_one(user_dict)
        print(f"✅ User saved with ID: {result.inserted_id}")
        
        # 🔽 FIX: Convert MongoDB document to UserResponse format
        user_dict.pop("password")
        
        # Convert _id to id for the response model
        response_data = {
            "id": user_dict["_id"],  # Map _id to id
            "name": user_dict["name"],
            "email": user_dict["email"],
            "phone": user_dict["phone"],
            "language": user_dict["language"],
            "created_at": user_dict["created_at"],
            "farms": user_dict["farms"]
        }
        
        return UserResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"🚨 Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login")
async def login(login_data: UserLogin):
    users_collection = get_users_collection()
    
    user = users_collection.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user.pop("password")
    
    # 🔽 FIX: Convert _id to id for the response
    user_response = {
        "id": user["_id"],
        "name": user["name"],
        "email": user["email"],
        "phone": user["phone"],
        "language": user["language"],
        "created_at": user["created_at"],
        "farms": user["farms"]
    }
    
    return {
        "message": translator.translate('auth.login_success', user['language']),
        "user": UserResponse(**user_response),
        "access_token": "mock_jwt_token_here"
    }