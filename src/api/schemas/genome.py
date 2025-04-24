from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class GenomeBase(BaseModel):
    metadata: Dict

class GenomeCreate(GenomeBase):
    pass

class GenomeResponse(GenomeBase):
    id: str
    storage_id: str
    tx_hash: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class GenomeList(BaseModel):
    items: List[GenomeResponse]
    total: int
    skip: int
    limit: int 