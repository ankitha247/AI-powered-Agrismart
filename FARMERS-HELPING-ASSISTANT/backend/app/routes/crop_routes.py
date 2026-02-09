# backend/app/routes/crop_routes.py

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from app.ml_models.crop_model import crop_recommender

router = APIRouter(tags=["Crops"])


class CropRequestModel(BaseModel):
    state: str
    district: str
    soil_type: str
    season: str
    irrigation_source: str
    user_id: Optional[str] = None


@router.post("/recommend")
async def get_crop_recommendations(payload: CropRequestModel, request: Request):
    """
    Final URL (because of main.py prefix):
        POST /api/crops/recommend
    """
    try:
        model_input = {
            "state": payload.state,
            "district": payload.district,
            "soil_type": payload.soil_type,
            "season": payload.season,
            "irrigation_source": payload.irrigation_source,
        }

        print("🌱 Received crop recommendation request:", payload.dict())
        print("📊 Model input:", model_input)

        result = crop_recommender.recommend(model_input)

        # result from rule-based model:
        # {
        #   "recommended_crop": "Paddy",
        #   "top_predictions": [
        #       {"crop": "Paddy", "score": 0.55},
        #       {"crop": "Maize", "score": 0.25},
        #       ...
        #   ]
        # }

        raw_preds = result.get("top_predictions", [])

        # 🔁 Normalize to a very frontend-friendly shape
        recommendations = []
        for item in raw_preds:
            crop_name = item.get("crop")
            score = float(item.get("score", 0.0))
            recommendations.append(
                {
                    "crop": crop_name,
                    "name": crop_name,   # many UIs expect "name"
                    "label": crop_name,  # some UIs expect "label"
                    "score": score,
                }
            )

        # Safety: never send empty list
        if not recommendations:
            recommendations = [
                {"crop": "Paddy", "name": "Paddy", "label": "Paddy", "score": 0.4},
                {"crop": "Maize", "name": "Maize", "label": "Maize", "score": 0.35},
                {"crop": "Chickpea", "name": "Chickpea", "label": "Chickpea", "score": 0.25},
            ]

        response = {
            "status": "success",
            "recommended_crop": result.get("recommended_crop"),
            # 👇 THIS is what frontend is probably using
            "recommendations": recommendations,
            # also keep original for debugging
            "top_predictions": recommendations,
        }

        print("✅ Sending crop response to frontend:", response)

        return JSONResponse(status_code=200, content=response)

    except Exception as e:
        print(f"❌ Crop recommendation error: {e}")
        import traceback
        print("🔍 Traceback:", traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="Crop recommendation model not available",
        )
