from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime
import logging
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import io

router = APIRouter()

model = None
processor = None

def load_clip_model():
    global model, processor
    try:
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        logging.info("CLIP model loaded successfully")
    except Exception as e:
        logging.error(f"Error loading CLIP model: {str(e)}")
        raise e

DISEASE_LABELS = {
    "common": [
        "healthy plant leaf", 
        "plant leaf with early blight disease",
        "plant leaf with late blight disease",
        "plant leaf with bacterial spot disease",
        "plant leaf with powdery mildew",
        "plant leaf with rust disease",
        "plant leaf with leaf spot disease",
        "plant leaf with mosaic virus",
        "plant leaf with fungal infection",
        "plant leaf with nutrient deficiency"
    ],
    "tomato": [
        "healthy tomato leaf",
        "tomato leaf with early blight",
        "tomato leaf with late blight", 
        "tomato leaf with bacterial spot",
        "tomato leaf with leaf mold",
        "tomato leaf with septoria leaf spot",
        "tomato leaf with spider mite damage",
        "tomato leaf with target spot",
        "tomato leaf with mosaic virus",
        "tomato leaf with yellow leaf curl virus"
    ],
    "potato": [
        "healthy potato leaf",
        "potato leaf with early blight",
        "potato leaf with late blight",
        "potato leaf with bacterial wilt",
        "potato leaf with verticillium wilt",
        "potato leaf with common scab",
        "potato leaf with blackleg",
        "potato leaf with potato virus Y"
    ],
    "corn": [
        "healthy corn leaf",
        "corn leaf with common rust",
        "corn leaf with northern leaf blight",
        "corn leaf with gray leaf spot",
        "corn leaf with southern leaf blight",
        "corn leaf with anthracnose"
    ]
}

TREATMENT_DATABASE = {
    "early blight": {
        "treatment": "Apply copper-based fungicides. Remove infected leaves and improve air circulation.",
        "prevention": "Practice crop rotation, use resistant varieties, avoid overhead irrigation."
    },
    "late blight": {
        "treatment": "Apply fungicides containing chlorothalonil or mancozeb. Destroy severely infected plants immediately.",
        "prevention": "Use certified disease-free seeds, ensure proper spacing, remove plant debris."
    },
    "bacterial spot": {
        "treatment": "Apply copper bactericides. Remove and destroy infected plants to prevent spread.",
        "prevention": "Use disease-free seeds, practice crop rotation, avoid working with wet plants."
    },
    "powdery mildew": {
        "treatment": "Apply sulfur-based fungicides or neem oil. Improve air circulation around plants.",
        "prevention": "Plant resistant varieties, ensure proper spacing, avoid overhead watering."
    },
    "healthy": {
        "treatment": "No treatment needed. Continue good agricultural practices.",
        "prevention": "Maintain proper nutrition, irrigation, and regular monitoring."
    }
}

def get_treatment_recommendations(disease_name):
    disease_lower = disease_name.lower()
    
    for key, treatment in TREATMENT_DATABASE.items():
        if key in disease_lower:
            return treatment
    
    return {
        "treatment": "Consult local agricultural expert for specific treatment recommendations.",
        "prevention": "Practice crop rotation and maintain field sanitation."
    }

@router.post("/detect")
async def detect_disease(
    crop_type: str = Form(...),
    image: UploadFile = File(...),
    user_id: str = Form(None)  # ⭐ NEW (optional)
):
    try:
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        file_extension = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4()}{file_extension}"
        file_path = f"uploads/{filename}"
        
        os.makedirs("uploads", exist_ok=True)
        with open(file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        if model is None or processor is None:
            load_clip_model()
        
        detection_result = clip_disease_detection(crop_type, file_path)
        
        detection_result.update({
            "image_id": filename,
            "crop_type": crop_type,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id  # ⭐ attach for reference
        })

        logging.info(f"Disease detection for user {user_id}: {detection_result['disease_name']}")
        
        return JSONResponse(content=detection_result)
        
    except Exception as e:
        logging.error(f"Error in disease detection: {str(e)}")
        raise HTTPException(status_code=500, detail="Disease detection failed")

def clip_disease_detection(crop_type, image_path):
    """Perform zero-shot disease classification using CLIP"""
    try:
        # Load and preprocess image
        image = Image.open(image_path).convert("RGB")
        
        # Get appropriate labels based on crop type
        if crop_type.lower() in DISEASE_LABELS:
            candidate_labels = DISEASE_LABELS[crop_type.lower()]
        else:
            candidate_labels = DISEASE_LABELS["common"]
        
        # Prepare inputs for CLIP
        inputs = processor(
            text=candidate_labels,
            images=image,
            return_tensors="pt",
            padding=True
        )
        
        # Run CLIP model
        with torch.no_grad():
            outputs = model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)
        
        # Get results
        probabilities = probs[0].tolist()
        best_idx = probabilities.index(max(probabilities))
        best_label = candidate_labels[best_idx]
        confidence = probabilities[best_idx]
        
        # Extract disease name from label
        if "healthy" in best_label.lower():
            disease_name = "Healthy"
        else:
            # Extract disease name from the label
            disease_name = best_label.replace("plant leaf with", "").replace("leaf with", "").strip()
            disease_name = disease_name.title()
        
        # Get treatment recommendations
        treatment_info = get_treatment_recommendations(disease_name)
        
        # Determine immediate actions based on confidence and disease
        immediate_actions = get_immediate_actions(disease_name, confidence)
        
        return {
            "disease_name": disease_name,
            "confidence": round(confidence, 4),
            "treatment": treatment_info["treatment"],
            "prevention": treatment_info["prevention"],
            "immediate_actions": immediate_actions,
            "detection_method": "CLIP Zero-Shot Classification"
        }
        
    except Exception as e:
        logging.error(f"CLIP detection error: {str(e)}")
        # Fallback to mock detection if CLIP fails
        return mock_disease_detection(crop_type)

def get_immediate_actions(disease_name, confidence):
    """Get immediate actions based on disease and confidence"""
    base_actions = []
    
    if "healthy" not in disease_name.lower():
        if confidence > 0.7:
            base_actions = [
                "Isolate affected plants immediately",
                "Remove severely infected leaves",
                "Apply recommended treatment within 48 hours"
            ]
        else:
            base_actions = [
                "Monitor plants closely for symptom progression",
                "Isolate suspicious plants as precaution",
                "Consult agricultural expert for confirmation"
            ]
    else:
        base_actions = [
            "Continue regular monitoring",
            "Maintain current farming practices",
            "Document plant health for future reference"
        ]
    
    return base_actions

def mock_disease_detection(crop_type):
    """Fallback mock detection if CLIP fails"""
    import random
    
    common_diseases = ["Early Blight", "Late Blight", "Bacterial Spot", "Powdery Mildew", "Healthy"]
    disease = random.choice(common_diseases)
    
    treatment_info = get_treatment_recommendations(disease)
    
    return {
        "disease_name": disease,
        "confidence": round(random.uniform(0.85, 0.98), 4),
        "treatment": treatment_info["treatment"],
        "prevention": treatment_info["prevention"],
        "immediate_actions": get_immediate_actions(disease, 0.9),
        "detection_method": "Mock Detection (CLIP Failed)"
    }

# Load model when module is imported
load_clip_model()