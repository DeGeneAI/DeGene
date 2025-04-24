from typing import Dict, Optional, List
import logging
import os
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solana.transaction import Transaction, TransactionInstruction
from solana.system_program import TransferParams, transfer
from solana.keypair import Keypair
from solana.publickey import PublicKey
import base58
from anchorpy import Program, Provider, Wallet
import json

logger = logging.getLogger(__name__)

class BlockchainService:
    def __init__(self, rpc_url: str, keypair: Keypair):
        """Initialize Solana blockchain service"""
        self.client = AsyncClient(rpc_url)
        self.keypair = keypair
        
    async def create_genome_record(self, genome_data: Dict) -> str:
        """Create a new genome record on Solana blockchain"""
        try:
            # Create transaction
            transaction = Transaction()
            
            # Add genome data to transaction
            encoded_data = json.dumps(genome_data).encode()
            instruction = self._create_data_instruction(encoded_data)
            transaction.add(instruction)
            
            # Sign and send transaction
            result = await self.client.send_transaction(
                transaction, 
                self.keypair,
            )
            
            return result['result']
            
        except Exception as e:
            logger.error(f"Failed to create genome record: {str(e)}")
            raise
            
    async def mark_genome_deleted(self, genome_id: str) -> bool:
        """Mark a genome record as deleted on Solana"""
        try:
            # Create deletion transaction
            transaction = Transaction()
            instruction = self._create_deletion_instruction(genome_id)
            transaction.add(instruction)
            
            # Sign and send transaction
            result = await self.client.send_transaction(
                transaction,
                self.keypair,
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark genome as deleted: {str(e)}")
            raise
            
    async def verify_genome_ownership(self, genome_id: str, user_pubkey: str) -> bool:
        """Verify ownership of a genome record"""
        try:
            # Get account info
            account_info = await self.client.get_account_info(b58decode(genome_id))
            
            if not account_info['result']['value']:
                return False
                
            # Parse account data and verify owner
            data = json.loads(account_info['result']['value']['data'][0])
            return data['owner'] == user_pubkey
            
        except Exception as e:
            logger.error(f"Failed to verify genome ownership: {str(e)}")
            raise
            
    async def get_genome_account(self, genome_id: str) -> Optional[Dict]:
        """Retrieve genome account data from Solana"""
        try:
            # Get account info
            account_info = await self.client.get_account_info(b58decode(genome_id))
            
            if not account_info['result']['value']:
                return None
                
            # Parse and return account data
            data = json.loads(account_info['result']['value']['data'][0])
            return data
            
        except Exception as e:
            logger.error(f"Failed to get genome account: {str(e)}")
            raise
            
    async def get_user_genomes(self, user_pubkey: str) -> List[Dict]:
        """Get all genome records owned by a user"""
        try:
            # Get program accounts filtered by owner
            accounts = await self.client.get_program_accounts(
                self.program_id,
                encoding="jsonParsed",
                filters=[
                    {"memcmp": {"offset": 0, "bytes": user_pubkey}}
                ]
            )
            
            return [json.loads(acc['account']['data'][0]) for acc in accounts['result']]
            
        except Exception as e:
            logger.error(f"Failed to get user genomes: {str(e)}")
            raise
            
    def _create_data_instruction(self, data: bytes):
        """Create instruction for storing genome data"""
        # Implementation needed based on specific program
        pass
        
    def _create_deletion_instruction(self, genome_id: str):
        """Create instruction for marking genome as deleted"""
        # Implementation needed based on specific program
        pass

    async def verify_ownership(self, tx_hash: str, owner: str) -> bool:
        """Verify genome ownership on blockchain"""
        try:
            # Get transaction info
            tx_info = await self.client.get_transaction(tx_hash)
            genome_pubkey = PublicKey(tx_info.value.transaction.message.account_keys[1])
            
            # Get genome account data
            genome_account = await self.program.account["Genome"].fetch(genome_pubkey)
            
            # Verify ownership
            return str(genome_account.owner) == owner
            
        except Exception as e:
            logger.error(f"Failed to verify ownership: {str(e)}")
            raise
            
    async def get_genome_accounts(self, owner: str) -> List[Dict]:
        """Get all genome accounts owned by user"""
        try:
            owner_pubkey = PublicKey(owner)
            accounts = await self.program.account["Genome"].all([
                {"memcmp": {"offset": 8, "bytes": str(owner_pubkey)}}
            ])
            
            return [
                {
                    "address": str(account.public_key),
                    "storage_id": account.account.storage_id,
                    "metadata": json.loads(account.account.metadata),
                    "created_at": account.account.created_at,
                    "deleted": account.account.deleted
                }
                for account in accounts
            ]
            
        except Exception as e:
            logger.error(f"Failed to get genome accounts: {str(e)}")
            raise 
