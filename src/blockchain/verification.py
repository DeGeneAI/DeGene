from typing import Dict, List, Optional
import hashlib
import json
from solana.rpc.async_api import AsyncClient
from solana.publickey import PublicKey
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenomeVerifier:
    """Genome data verification"""
    
    def __init__(self, rpc_url: str, program_id: str):
        self.client = AsyncClient(rpc_url)
        self.program_id = PublicKey(program_id)
        
    async def verify_genome(self, genome_id: str, sequence: str) -> bool:
        """Verify genome data integrity"""
        try:
            # Get account data
            account_info = await self.client.get_account_info(self.program_id)
            if not account_info:
                return False
                
            # Parse account data
            data = account_info.value.data
            # Implement data parsing logic based on program structure
            
            # Calculate hash of provided sequence
            provided_hash = hashlib.sha256(sequence.encode()).hexdigest()
            
            # Compare with stored hash
            return provided_hash == genome_id
            
        except Exception as e:
            logger.error(f"Error verifying genome: {e}")
            return False
            
    async def verify_metadata(self, genome_id: str, metadata: Dict) -> bool:
        """Verify genome metadata"""
        try:
            # Get account data
            account_info = await self.client.get_account_info(self.program_id)
            if not account_info:
                return False
                
            # Parse account data
            data = account_info.value.data
            # Implement data parsing logic based on program structure
            
            # Compare metadata
            stored_metadata = json.loads(data["metadata"])
            return stored_metadata == metadata
            
        except Exception as e:
            logger.error(f"Error verifying metadata: {e}")
            return False
            
    async def verify_access(self, genome_id: str, user_address: str) -> bool:
        """Verify user access to genome data"""
        try:
            # Get account data
            account_info = await self.client.get_account_info(self.program_id)
            if not account_info:
                return False
                
            # Parse account data
            data = account_info.value.data
            # Implement data parsing logic based on program structure
            
            # Check if genome is public
            if data["is_public"]:
                return True
                
            # Check if user is owner
            if data["owner"] == user_address:
                return True
                
            # Check if user has access
            return user_address in data.get("access_list", [])
            
        except Exception as e:
            logger.error(f"Error verifying access: {e}")
            return False
            
    async def verify_ownership(self, genome_id: str, user_address: str) -> bool:
        """Verify genome ownership"""
        try:
            # Get account data
            account_info = await self.client.get_account_info(self.program_id)
            if not account_info:
                return False
                
            # Parse account data
            data = account_info.value.data
            # Implement data parsing logic based on program structure
            
            # Check if user is owner
            return data["owner"] == user_address
            
        except Exception as e:
            logger.error(f"Error verifying ownership: {e}")
            return False 