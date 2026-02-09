from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Global variables
_client = None
_db = None

def get_database():
    global _client, _db
    try:
        if _db is not None:
            return _db
            
        # Use the exact database name that exists
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        _client = MongoClient(mongo_uri)
        _db = _client["AgriSmart"]  # Exact case matching your existing DB
        
        # Test the connection
        _db.command('ping')
        print("✅ Connected to MongoDB successfully!")
        return _db
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        _db = None
        _client = None
        return None

def get_users_collection():
    db = get_database()
    if db is None:
        return None
    return db.users

def get_predictions_collection():
    db = get_database()
    if db is None:
        return None
    return db.predictions

def get_recommendations_collection():
    db = get_database()
    if db is None:
        return None
    return db.recommendations

def get_disease_reports_collection():
    db = get_database()
    if db is None:
        return None
    return db.disease_reports