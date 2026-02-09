from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import auth_routes, yield_routes, crop_routes, disease_routes, dashboard_routes


import os

app = FastAPI(title="AgriSmart API", version="1.0.0")

# Use the existing app/uploads directory
os.makedirs("app/uploads", exist_ok=True)
print("✅ Using app/uploads directory for images")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the existing app/uploads directory
app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")

# Include routers
# Include routers (ONLY ONCE each)
app.include_router(auth_routes.router, prefix="/api/auth")
app.include_router(yield_routes.router, prefix="/api/yield")
app.include_router(crop_routes.router, prefix="/api/crops")
app.include_router(disease_routes.router, prefix="/api/disease")
app.include_router(dashboard_routes.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/")
def read_root():
    return {"message": "AgriSmart Backend API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Backend is working!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)