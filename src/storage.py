from typing import Dict, List, Optional
import hashlib
import json
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
import base58
import logging
import ipfshttpclient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlockchainStorage:
    """Blockchain-based genome storage"""
    
    def __init__(self, rpc_url: str, program_id: str, private_key: str):
        self.client = AsyncClient(rpc_url)
        self.keypair = Keypair.from_secret_key(base58.b58decode(private_key))
        self.program_id = program_id
        self.ipfs_client = ipfshttpclient.connect()
        
    async def store_genome(self, sequence: str, metadata: Dict, is_public: bool = False) -> str:
        """Store genome data on blockchain"""
        # Generate unique ID
        genome_id = hashlib.sha256(sequence.encode()).hexdigest()
        
        # Store sequence on IPFS
        ipfs_hash = self._store_on_ipfs(sequence)
        
        # Prepare metadata
        metadata_json = json.dumps(metadata)
        
        # Create instruction data
        instruction_data = {
            "method": "store_genome",
            "genome_id": genome_id,
            "ipfs_hash": ipfs_hash,
            "metadata": metadata_json,
            "is_public": is_public
        }
        
        # Create transaction
        transaction = Transaction()
        transaction.add(
            transfer(
                TransferParams(
                    from_pubkey=self.keypair.public_key,
                    to_pubkey=self.program_id,
                    lamports=1000000  # Adjust based on program requirements
                )
            )
        )
        
        # Sign and send transaction
        try:
            result = await self.client.send_transaction(transaction, self.keypair)
            logger.info(f"Genome stored with ID: {genome_id}")
            return genome_id
        except Exception as e:
            logger.error(f"Error storing genome: {e}")
            return None
            
    async def retrieve_genome(self, genome_id: str) -> Optional[Dict]:
        """Retrieve genome data from blockchain"""
        try:
            # Get account data
            account_info = await self.client.get_account_info(self.program_id)
            if not account_info:
                return None
                
            # Parse account data
            data = account_info.value.data
            # Implement data parsing logic based on program structure
            
            # Retrieve from IPFS
            sequence = self._retrieve_from_ipfs(data["ipfs_hash"])
            
            return {
                'sequence': sequence,
                'owner': data["owner"],
                'timestamp': data["timestamp"],
                'metadata': json.loads(data["metadata"]),
                'is_public': data["is_public"]
            }
        except Exception as e:
            logger.error(f"Error retrieving genome: {e}")
            return None
            
    async def grant_access(self, genome_id: str, user_address: str) -> bool:
        """Grant access to genome data"""
        try:
            # Create instruction data
            instruction_data = {
                "method": "grant_access",
                "genome_id": genome_id,
                "user_address": user_address
            }
            
            # Create and send transaction
            transaction = Transaction()
            # Add instruction based on program requirements
            
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
            
            # Create and send transaction
            transaction = Transaction()
            # Add instruction based on program requirements
            
            result = await self.client.send_transaction(transaction, self.keypair)
            return True
        except Exception as e:
            logger.error(f"Error revoking access: {e}")
            return False
            
    def _store_on_ipfs(self, data: str) -> str:
        """Store data on IPFS"""
        result = self.ipfs_client.add_str(data)
        return result['Hash']
        
    def _retrieve_from_ipfs(self, ipfs_hash: str) -> str:
        """Retrieve data from IPFS"""
        return self.ipfs_client.cat(ipfs_hash).decode() 