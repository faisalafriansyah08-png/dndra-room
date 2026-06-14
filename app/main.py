from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.database import Base, engine
from app.api.v1 import auth, rooms, bookings, payments, promos, support, users
import os

settings = get_settings()

# Buat folder uploads kalau belum ada
os.makedirs("uploads/rooms", exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Hotel Booking System API with Online Payment",
    version="1.0.0",
    docs_url=f"/api/{settings.API_VERSION}/docs",
    redoc_url=f"/api/{settings.API_VERSION}/redoc",
    openapi_url=f"/api/{settings.API_VERSION}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (gambar yang diupload)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
@app.get("/")
async def root():
    return {
        "message": "Hotel Booking System API",
        "version": "1.0.0",
        "status": "running",
        "docs": f"/api/{settings.API_VERSION}/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(auth.router, prefix=f"/api/{settings.API_VERSION}", tags=["Authentication"])
app.include_router(rooms.router, prefix=f"/api/{settings.API_VERSION}", tags=["Rooms"])
app.include_router(bookings.router, prefix=f"/api/{settings.API_VERSION}", tags=["Bookings"])
app.include_router(payments.router, prefix=f"/api/{settings.API_VERSION}", tags=["Payments"])
app.include_router(promos.router, prefix=f"/api/{settings.API_VERSION}", tags=["Promos"])
app.include_router(support.router, prefix=f"/api/{settings.API_VERSION}", tags=["Support"])
app.include_router(users.router, prefix=f"/api/{settings.API_VERSION}", tags=["Users"])
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)