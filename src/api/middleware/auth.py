from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

# Configuration
JWT_SECRET = "your-secret-key"  # Should be loaded from environment variables
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

async def auth_middleware(request: Request, call_next):
    try:
        # Skip auth for certain endpoints
        if request.url.path in ["/api/health", "/api/auth/login", "/api/auth/register"]:
            return await call_next(request)

        # Verify JWT token
        credentials: HTTPAuthorizationCredentials = await security(request)
        if not credentials:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

        try:
            payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            # Add user info to request state
            request.state.user = payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

        response = await call_next(request)
        return response

    except HTTPException as e:
        logger.warning(f"Authentication failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in auth middleware: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 
