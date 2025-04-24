from typing import Dict, List, Optional
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
import base58
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OwnershipManager:
    """Genome data ownership management"""
    
    def __init__(self, rpc_url: str, program_id: str, private_key: str):
        self.client = AsyncClient(rpc_url)
        self.keypair = Keypair.from_secret_key(base58.b58decode(private_key))
        self.program_id = program_id
        
    async def transfer_ownership(self, genome_id: str, new_owner: str) -> bool:
        """Transfer genome ownership"""
        try:
            # Create instruction data
            instruction_data = {
                "method": "transfer_ownership",
                "genome_id": genome_id,
                "new_owner": new_owner
            }
            
            # Create transaction
            transaction = Transaction()
            transaction.add(
                transfer(
                    TransferParams(
                        from_pubkey=self.keypair.public_key,
                        to_pubkey=self.program_id,
                        lamports=100000  # Adjust based on program requirements
                    )
                )
            )
            
            # Sign and send transaction
            result = await self.client.send_transaction(transaction, self.keypair)
            return True
            
        except Exception as e:
            logger.error(f"Error transferring ownership: {e}")
            return False
            
    async def get_owner(self, genome_id: str) -> str:
        """Get genome owner"""
        try:
            # Get account data
            account_info = await self.client.get_account_info(self.program_id)
            if not account_info:
                return ""
                
            # Parse account data
            data = account_info.value.data
            # Implement data parsing logic based on program structure
            
            return data.get("owner", "")
            
        except Exception as e:
            logger.error(f"Error getting owner: {e}")
            return ""
            
    async def is_owner(self, genome_id: str, address: str) -> bool:
        """Check if address is owner"""
        try:
            # Get account data
            account_info = await self.client.get_account_info(self.program_id)
            if not account_info:
                return False
                
            # Parse account data
            data = account_info.value.data
            # Implement data parsing logic based on program structure
            
            return data.get("owner", "") == address
            
        except Exception as e:
            logger.error(f"Error checking ownership: {e}")
            return False
            
    async def get_ownership_history(self, genome_id: str) -> List[Dict]:
        """Get ownership transfer history"""
        try:
            # Get account data
            account_info = await self.client.get_account_info(self.program_id)
            if not account_info:
                return []
                
            # Parse account data
            data = account_info.value.data
            # Implement data parsing logic based on program structure
            
            return data.get("ownership_history", [])
            
        except Exception as e:
            logger.error(f"Error getting ownership history: {e}")
            return []
            
    async def verify_ownership(self, genome_id: str, address: str) -> bool:
        """Verify ownership with proof"""
        try:
            # Get account data
            account_info = await self.client.get_account_info(self.program_id)
            if not account_info:
                return False
                
            # Parse account data
            data = account_info.value.data
            # Implement data parsing logic based on program structure
            
            # Verify ownership
            return data.get("owner", "") == address
            
        except Exception as e:
            logger.error(f"Error verifying ownership: {e}")
            return False 