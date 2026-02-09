from fastapi import APIRouter, HTTPException
from app.models.user_models import YieldPredictionInput
from app.ml_models.yield_model import yield_predictor
from app.utils.database import get_predictions_collection
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/predict")
async def predict_yield_route(yield_data: dict):
    try:
        print("📊 Received yield prediction request:", yield_data)

        # Validate required fields
        required_fields = ['crop_name', 'soil_type', 'season', 'irrigation_source', 'state', 'district']
        for field in required_fields:
            if field not in yield_data or not yield_data[field]:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        # Extract only the features the model was trained on
        model_features = ['state', 'district', 'crop_name', 'soil_type', 'season', 'irrigation_source']
        model_input = {feature: yield_data[feature] for feature in model_features if feature in yield_data}
        
        print(f"📊 Model input: {model_input}")

        # Get prediction from ML model (without user_id)
        prediction_result = yield_predictor.predict(model_input)
        
        if prediction_result is None:
            raise HTTPException(status_code=500, detail="Prediction model not available")

        print("🎯 Prediction result:", prediction_result)

        # Get predictions collection
        predictions_collection = get_predictions_collection()

        # Create prediction document
        prediction_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": yield_data.get("user_id", "anonymous"),
            "type": "yield_prediction",
            "crop_name": yield_data.get("crop_name"),
            "state": yield_data.get("state"),
            "district": yield_data.get("district"),
            "soil_type": yield_data.get("soil_type"),
            "season": yield_data.get("season"),
            "irrigation_source": yield_data.get("irrigation_source"),
            "predicted_yield": prediction_result.get("predicted_yield"),
            "confidence": prediction_result.get("confidence", 0.85),
            "recommendations": prediction_result.get("recommendations", []),
            "data_source": prediction_result.get("data_source", "sample"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Insert into MongoDB
        result = predictions_collection.insert_one(prediction_doc)
        print("💾 Stored in MongoDB with ID:", result.inserted_id)

        # Return response with MongoDB ID
        return {
            **prediction_result,
            "prediction_id": str(result.inserted_id),
            "success": True,
            "stored_in_db": True
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Yield prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")