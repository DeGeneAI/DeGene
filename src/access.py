from typing import Dict, List, Optional
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
import base58
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AccessManager:
    """Genome data access control"""
    
    def __init__(self, rpc_url: str, program_id: str, private_key: str):
        self.client = AsyncClient(rpc_url)
        self.keypair = Keypair.from_secret_key(base58.b58decode(private_key))
        self.program_id = program_id
        
    async def grant_access(self, genome_id: str, user_address: str) -> bool:
        """Grant access to genome data"""
        try:
            # Create instruction data
            instruction_data = {
                "method": "grant_access",
                "genome_id": genome_id,
                "user_address": user_address
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
            logger.error(f"Error granting access: {e}")
            return False
            
    async def revoke_access(self, genome_id: str, user_address: str) -> bool:
        """Revoke access to genome data"""
        try:
            # Create instruction data
            instruction_data = {
                "method": "revoke_access",
                "genome_id": genome_id,
                "user_address": user_address
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
            logger.error(f"Error revoking access: {e}")
            return False
            
    async def set_public(self, genome_id: str, is_public: bool) -> bool:
        """Set genome data public/private"""
        try:
            # Create instruction data
            instruction_data = {
                "method": "set_public",
                "genome_id": genome_id,
                "is_public": is_public
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
            logger.error(f"Error setting public status: {e}")
            return False
            
    async def get_access_list(self, genome_id: str) -> List[str]:
        """Get list of users with access"""
        try:
            # Get account data
            account_info = await self.client.get_account_info(self.program_id)
            if not account_info:
                return []
                
            # Parse account data
            data = account_info.value.data
            # Implement data parsing logic based on program structure
            
            return data.get("access_list", [])
            
        except Exception as e:
            logger.error(f"Error getting access list: {e}")
            return []
            
    async def has_access(self, genome_id: str, user_address: str) -> bool:
        """Check if user has access"""
        try:
            # Get account data
            account_info = await self.client.get_account_info(self.program_id)
            if not account_info:
                return False
                
            # Parse account data
            data = account_info.value.data
            # Implement data parsing logic based on program structure
            
            return user_address in data.get("access_list", [])
            
        except Exception as e:
            logger.error(f"Error checking access: {e}")
            return False 