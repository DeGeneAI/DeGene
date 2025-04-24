from typing import Dict, List, Optional
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.publickey import PublicKey
from anchorpy import Program, Provider, Wallet
import base58
import logging
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionManager:
    """Genome data transaction management"""
    
    def __init__(self):
        # Initialize Solana client
        self.client = AsyncClient(
            os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
        )
        
        # Load program ID and keypair
        self.program_id = PublicKey(os.getenv("SOLANA_PROGRAM_ID"))
        private_key = os.getenv("SOLANA_PRIVATE_KEY")
        self.keypair = Keypair.from_secret_key(base58.b58decode(private_key))
        
        # Initialize Anchor provider and program
        self.provider = Provider(
            self.client,
            Wallet(self.keypair)
        )
        
        # Load program IDL
        with open("idl/genome_program.json") as f:
            idl = json.load(f)
        self.program = Program(idl, self.program_id, self.provider)
        
    async def create_transaction(self, genome_id: str, price: int, duration: int) -> str:
        """Create genome transaction"""
        try:
            # Create transaction account
            transaction_account = Keypair()
            
            # Calculate space needed
            space = 1000  # Adjust based on your program's needs
            
            # Get rent exemption amount
            rent = await self.client.get_minimum_balance_for_rent_exemption(space)
            
            # Create transaction
            tx = Transaction()
            
            # Add create account instruction
            create_tx_ix = self.program.instruction["create_transaction"](
                {
                    "genome_id": genome_id,
                    "price": price,
                    "duration": duration
                },
                accounts={
                    "transaction": transaction_account.public_key,
                    "user": self.keypair.public_key,
                    "system_program": PublicKey("11111111111111111111111111111111")
                }
            )
            
            tx.add(create_tx_ix)
            
            # Sign and send transaction
            result = await self.client.send_transaction(
                tx,
                [self.keypair, transaction_account]
            )
            
            return result.value.signature
            
        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            raise
            
    async def execute_transaction(self, transaction_id: str) -> str:
        """Execute genome transaction"""
        try:
            # Get transaction account
            tx_pubkey = PublicKey(transaction_id)
            
            # Create transaction
            tx = Transaction()
            
            # Add execute instruction
            execute_tx_ix = self.program.instruction["execute_transaction"](
                accounts={
                    "transaction": tx_pubkey,
                    "buyer": self.keypair.public_key,
                    "system_program": PublicKey("11111111111111111111111111111111")
                }
            )
            
            tx.add(execute_tx_ix)
            
            # Sign and send transaction
            result = await self.client.send_transaction(
                tx,
                [self.keypair]
            )
            
            return result.value.signature
            
        except Exception as e:
            logger.error(f"Error executing transaction: {e}")
            raise
            
    async def get_transaction(self, transaction_id: str) -> Dict:
        """Get transaction details"""
        try:
            # Get transaction account
            tx_pubkey = PublicKey(transaction_id)
            
            # Fetch transaction data
            tx_account = await self.program.account["Transaction"].fetch(tx_pubkey)
            
            return {
                "genome_id": tx_account.genome_id,
                "seller": str(tx_account.seller),
                "buyer": str(tx_account.buyer) if tx_account.buyer else None,
                "price": tx_account.price,
                "duration": tx_account.duration,
                "status": tx_account.status,
                "created_at": tx_account.created_at,
                "executed_at": tx_account.executed_at
            }
            
        except Exception as e:
            logger.error(f"Error getting transaction: {e}")
            raise
            
    async def get_transaction_history(self, genome_id: str) -> List[Dict]:
        """Get transaction history"""
        try:
            # Query all transactions for this genome
            transactions = await self.program.account["Transaction"].all([
                {"memcmp": {"offset": 8, "bytes": genome_id}}
            ])
            
            return [
                {
                    "transaction_id": str(tx.public_key),
                    "genome_id": tx.account.genome_id,
                    "seller": str(tx.account.seller),
                    "buyer": str(tx.account.buyer) if tx.account.buyer else None,
                    "price": tx.account.price,
                    "status": tx.account.status,
                    "created_at": tx.account.created_at,
                    "executed_at": tx.account.executed_at
                }
                for tx in transactions
            ]
            
        except Exception as e:
            logger.error(f"Error getting transaction history: {e}")
            raise
            
    async def cancel_transaction(self, transaction_id: str) -> str:
        """Cancel transaction"""
        try:
            # Get transaction account
            tx_pubkey = PublicKey(transaction_id)
            
            # Create transaction
            tx = Transaction()
            
            # Add cancel instruction
            cancel_tx_ix = self.program.instruction["cancel_transaction"](
                accounts={
                    "transaction": tx_pubkey,
                    "authority": self.keypair.public_key
                }
            )
            
            tx.add(cancel_tx_ix)
            
            # Sign and send transaction
            result = await self.client.send_transaction(
                tx,
                [self.keypair]
            )
            
            return result.value.signature
            
        except Exception as e:
            logger.error(f"Error canceling transaction: {e}")
            raise
            
 