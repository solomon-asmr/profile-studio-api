# In app/models/models.py

from pydantic import BaseModel, Field
from typing import Optional

# --- Input Models ---

class TryOnRequest(BaseModel):
    product_sku: str
    user_photo_base64: Optional[str] = Field(None, description="The user's photo encoded in Base64.")
    user_height: Optional[float] = Field(None, description="User's height in cm. Crucial for scaling from photo.")

# --- Output Models ---

class FitAnalysis(BaseModel):
    recommended_size: str
    confidence_score: float
    reasoning: str

class StyleAdvice(BaseModel):
    comment: str

class TryOnResponse(BaseModel):
    try_on_image_url: str
    fit_analysis: FitAnalysis
    style_advice: StyleAdvice