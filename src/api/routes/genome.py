from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.security import HTTPBearer
from typing import List, Optional
import logging
from datetime import datetime

from ..models.genome import Genome
from ..schemas.genome import GenomeCreate, GenomeResponse, GenomeList
from ..services.blockchain import BlockchainService
from ..services.storage import StorageService

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

blockchain_service = BlockchainService()
storage_service = StorageService()

@router.post("/upload", response_model=GenomeResponse)
async def upload_genome(
    metadata: GenomeCreate,
    file: UploadFile = File(...),
    current_user: dict = Depends(security)
):
    try:
        # Process and store genome data
        storage_id = await storage_service.store_genome(
            file_content=await file.read(),
            metadata=metadata.dict(),
            user_id=current_user["sub"]
        )
        
        # Create blockchain record
        tx_hash = await blockchain_service.create_genome_record(
            storage_id=storage_id,
            metadata=metadata.dict(),
            owner=current_user["sub"]
        )
        
        # Create database record
        genome = await Genome.create(
            storage_id=storage_id,
            tx_hash=tx_hash,
            metadata=metadata.dict(),
            owner_id=current_user["sub"]
        )
        
        return GenomeResponse(
            id=genome.id,
            storage_id=storage_id,
            tx_hash=tx_hash,
            metadata=metadata.dict(),
            created_at=genome.created_at
        )
        
    except Exception as e:
        logger.error(f"Genome upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload genome")

@router.get("/list", response_model=GenomeList)
async def list_genomes(
    current_user: dict = Depends(security),
    skip: int = 0,
    limit: int = 10
):
    try:
        genomes = await Genome.find_by_owner(
            owner_id=current_user["sub"],
            skip=skip,
            limit=limit
        )
        
        total = await Genome.count_by_owner(current_user["sub"])
        
        return GenomeList(
            items=[GenomeResponse.from_orm(g) for g in genomes],
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Failed to list genomes: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve genomes")

@router.get("/{genome_id}", response_model=GenomeResponse)
async def get_genome(
    genome_id: str,
    current_user: dict = Depends(security)
):
    try:
        genome = await Genome.find_by_id(genome_id)
        if not genome:
            raise HTTPException(status_code=404, detail="Genome not found")
            
        if genome.owner_id != current_user["sub"]:
            raise HTTPException(status_code=403, detail="Access denied")
            
        return GenomeResponse.from_orm(genome)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve genome: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve genome")

@router.delete("/{genome_id}")
async def delete_genome(
    genome_id: str,
    current_user: dict = Depends(security)
):
    try:
        genome = await Genome.find_by_id(genome_id)
        if not genome:
            raise HTTPException(status_code=404, detail="Genome not found")
            
        if genome.owner_id != current_user["sub"]:
            raise HTTPException(status_code=403, detail="Access denied")
            
        # Delete from storage
        await storage_service.delete_genome(genome.storage_id)
        
        # Update blockchain record
        await blockchain_service.mark_genome_deleted(genome.tx_hash)
        
        # Delete database record
        await genome.delete()
        
        return {"message": "Genome deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete genome: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete genome") 