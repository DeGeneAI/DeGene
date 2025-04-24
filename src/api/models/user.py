from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
import bcrypt
import uuid

class User(BaseModel):
    id: str
    email: EmailStr
    password_hash: str
    name: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
    
    @classmethod
    async def create(cls, email: str, password: str, name: str) -> "User":
        """Create a new user"""
        # Hash password
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt)
        
        # Create user
        now = datetime.utcnow()
        user = cls(
            id=str(uuid.uuid4()),
            email=email,
            password_hash=password_hash.decode(),
            name=name,
            created_at=now,
            updated_at=now
        )
        
        # Save to database (implementation needed)
        await user.save()
        
        return user
    
    @classmethod
    async def find_by_email(cls, email: str) -> Optional["User"]:
        """Find user by email"""
        # Database query implementation needed
        pass
    
    @classmethod
    async def authenticate(cls, email: str, password: str) -> Optional["User"]:
        """Authenticate user"""
        user = await cls.find_by_email(email)
        if not user:
            return None
            
        if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            return None
            
        return user
    
    async def save(self):
        """Save user to database"""
        # Database save implementation needed
        pass
    
    async def update(self, **kwargs):
        """Update user"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
        await self.save() 