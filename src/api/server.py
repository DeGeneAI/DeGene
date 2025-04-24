from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional
from datetime import datetime
import logging

from .routes import auth, genome

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DeGene API",
    description="Decentralized Genome Data Storage and Analysis Platform API on Solana",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(genome.router, prefix="/api/genome", tags=["Genome Management"])

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "data": None,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "path": request.url.path
            }
        }
    )

@app.get("/api/health")
async def health_check():
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "version": "1.0.0",
            "blockchain": "Solana"
        },
        "error": None,
        "metadata": {
            "timestamp": datetime.now().isoformat()
        }
    }

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True) 