# In app/main.py

from fastapi import FastAPI
from app.api.v1 import endpoints

# Create the FastAPI app instance
app = FastAPI(
    title="Profile Studio API",
    description="API for virtual try-on, fit estimation, and personalized catwalk previews.",
    version="1.0.0"
)

# Include the router from our v1 endpoints file
# All routes defined in that file will be prefixed with /v1
app.include_router(endpoints.router, prefix="/v1", tags=["Virtual Try-On"])

@app.get("/", tags=["Root"])
def read_root():
    """ A simple health check endpoint. """
    return {"message": "Welcome to the Profile Studio API"}