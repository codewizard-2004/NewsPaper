from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import editions, settings

app = FastAPI(
    title="Daily Dispatch Backend",
    description="Backend API and Multi-Agent Newsroom for the Daily Dispatch newspaper.",
    version="1.0.0",
)

# Configure CORS so the frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(editions.router)
app.include_router(settings.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Daily Dispatch Backend"}
