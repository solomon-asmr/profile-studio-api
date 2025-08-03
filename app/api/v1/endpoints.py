# In app/api/v1/endpoints.py

from fastapi import APIRouter, Body, HTTPException
from app.models.models import TryOnRequest, TryOnResponse, FitAnalysis, StyleAdvice
# Import our new service
from app.services import measurement_service

router = APIRouter()

@router.post("/generate-try-on", response_model=TryOnResponse)
async def generate_try_on(request: TryOnRequest = Body(...)):
    """
    Accepts user data and a product SKU, and returns a virtual try-on
    image, fit analysis, and style advice.
    """
    # --- NEW LOGIC ---
    if not request.user_photo_base64 or not request.user_height:
        raise HTTPException(
            status_code=400,
            detail="A user photo and height are required for virtual try-on."
        )

    # Call our computer vision service
    estimated_measurements, error = measurement_service.estimate_measurements_from_photo(
        photo_base64=request.user_photo_base64,
        user_height_cm=request.user_height
    )

    if error:
        raise HTTPException(status_code=400, detail=error)

    print(f"Estimated Measurements: {estimated_measurements}")

    # --- DUMMY LOGIC (for now) ---
    # We will replace this with a real call to the commentary service later
    fit_reasoning = f"Based on your photo, we estimated your chest to be ~{estimated_measurements['chest_circumference_cm']} cm. Size M is a good fit."

    dummy_fit = FitAnalysis(
        recommended_size="M",
        confidence_score=0.80, # Confidence is lower as it's an estimation
        reasoning=fit_reasoning
    )
    dummy_style = StyleAdvice(
        comment="This item's cut should complement your frame well."
    )
    dummy_response = TryOnResponse(
        try_on_image_url="https://via.placeholder.com/400x600.png?text=Try-On+(Processing...)",
        fit_analysis=dummy_fit,
        style_advice=dummy_style
    )
    # --- END DUMMY LOGIC ---

    return dummy_response