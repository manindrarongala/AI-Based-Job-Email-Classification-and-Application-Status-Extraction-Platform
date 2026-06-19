from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.email_routes import router

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "running"}


if __name__ == "__main__":
    import uvicorn
    # Run from parent directory: python -m app.main
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
