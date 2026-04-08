"""Disease detection placeholder - accepts image, returns mock until CNN model is trained."""
import base64
import io
from typing import Optional

# Placeholder: In production, load TensorFlow/PyTorch model and run inference
# For now return mock based on common AP/TG crops
COMMON_DISEASES = {
    "default": {
        "disease": "Analysis pending",
        "confidence": 0.0,
        "treatment": "Upload a clear image of the affected leaf/plant. Ensure good lighting.",
        "prevention": "Maintain crop hygiene; use resistant varieties; timely irrigation.",
    },
}


def detect_disease_from_image(image_base64: Optional[str] = None, crop_hint: Optional[str] = None) -> dict:
    """Placeholder: Real implementation would use CNN (ResNet/EfficientNet) on PlantVillage + custom dataset."""
    if not image_base64:
        return {"error": "No image provided", "disease": None}
    try:
        data = base64.b64decode(image_base64)
        if len(data) < 100:
            return {"error": "Invalid image", "disease": None}
    except Exception:
        return {"error": "Invalid base64 image", "disease": None}
    # Mock response until model is deployed
    return {
        "disease": "Early Blight (Alternaria)" if (crop_hint or "").lower() in ("tomato", "potato") else "Leaf Spot",
        "confidence": 0.72,
        "treatment": "Apply Mancozeb 2g/l or Copper Oxychloride. Remove infected leaves. Avoid overhead irrigation.",
        "prevention": "Use disease-free seeds; crop rotation; avoid water stress.",
        "note": "This is a placeholder. Train CNN on PlantVillage + local dataset for production.",
    }
