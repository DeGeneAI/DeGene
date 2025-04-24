from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import logging
from typing import Optional

from ..models.user import User
from ..schemas.auth import UserCreate, UserLogin, TokenResponse

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Configuration (should be moved to config file)
JWT_SECRET = "your-secret-key"
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    try:
        # Check if user exists
        if await User.find_by_email(user_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        user = await User.create(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )
        
        # Generate token
        token = create_access_token({"sub": str(user.id), "email": user.email})
        
        return {
            "access_token": token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    try:
        # Verify credentials
        user = await User.authenticate(credentials.email, credentials.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Generate token
        token = create_access_token({"sub": str(user.id), "email": user.email})
        
        return {
            "access_token": token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM) 
