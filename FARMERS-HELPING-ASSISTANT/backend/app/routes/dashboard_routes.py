from fastapi import APIRouter, HTTPException
from app.utils.database import (
    get_predictions_collection,
    get_recommendations_collection,
    get_disease_reports_collection,
)

router = APIRouter()


def _safe_timestamp(doc):
    ts = doc.get("created_at")
    if ts is None:
        return None
    try:
        # Convert datetime to ISO string if needed
        return ts.isoformat() if hasattr(ts, "isoformat") else str(ts)
    except Exception:
        return str(ts)


@router.get("/{user_id}")
async def get_user_dashboard(user_id: str):
    try:
        predictions_collection = get_predictions_collection()
        recommendations_collection = get_recommendations_collection()
        disease_collection = get_disease_reports_collection()

        # Get counts for THIS USER only
        prediction_count = predictions_collection.count_documents({"user_id": user_id})
        recommendation_count = recommendations_collection.count_documents(
            {"user_id": user_id}
        )
        disease_report_count = disease_collection.count_documents({"user_id": user_id})

        # Get recent activity for THIS USER only
        recent_predictions = list(
            predictions_collection.find({"user_id": user_id})
            .sort("created_at", -1)
            .limit(5)
        )

        recent_recommendations = list(
            recommendations_collection.find({"user_id": user_id})
            .sort("created_at", -1)
            .limit(5)
        )

        recent_disease_reports = list(
            disease_collection.find({"user_id": user_id})
            .sort("created_at", -1)
            .limit(5)
        )

        # Format recent activity
        recent_activity = []

        for pred in recent_predictions:
            recent_activity.append(
                {
                    "type": "yield_prediction",
                    "title": f"{pred.get('crop_name', 'Crop')} Yield Prediction",
                    "result": f"{pred.get('predicted_yield', 'N/A')} tons/hectare",
                    "timestamp": _safe_timestamp(pred),
                    "icon": "📊",
                }
            )

        for rec in recent_recommendations:
            top_rec = rec.get("top_recommendation", {}) or {}
            recent_activity.append(
                {
                    "type": "crop_recommendation",
                    "title": "Crop Recommendation",
                    "result": top_rec.get("crop_name", top_rec.get("crop", "Crop")),
                    "timestamp": _safe_timestamp(rec),
                    "icon": "🌱",
                }
            )

        for disease in recent_disease_reports:
            recent_activity.append(
                {
                    "type": "disease_detection",
                    "title": f"{disease.get('crop_type', 'Crop')} Disease Detection",
                    "result": disease.get("disease_name", "Disease"),
                    "timestamp": _safe_timestamp(disease),
                    "icon": "🦠",
                }
            )

        # Sort by timestamp (None goes last) and get top 5
        recent_activity.sort(
            key=lambda x: (x["timestamp"] is None, x["timestamp"]), reverse=True
        )
        recent_activity = recent_activity[:5]

        return {
            "user_id": user_id,
            "stats": {
                "total_predictions": prediction_count,
                "total_recommendations": recommendation_count,
                "total_disease_reports": disease_report_count,
                "success_rate": 0,  # placeholder
            },
            "recent_activity": recent_activity,
        }

    except Exception as e:
        print("❌ Dashboard error:", e)
        import traceback

        print("🔍 Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")
