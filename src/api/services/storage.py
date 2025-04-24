import logging
from typing import Dict, Optional, BinaryIO
import json
import ipfshttpclient
from datetime import datetime

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, ipfs_host: str = "/ip4/127.0.0.1/tcp/5001"):
        """Initialize IPFS storage service"""
        try:
            self.client = ipfshttpclient.connect(ipfs_host)
        except Exception as e:
            logger.error(f"Failed to connect to IPFS: {str(e)}")
            raise
            
    async def store_genome(self, file_content: BinaryIO, metadata: Dict, user_id: str) -> str:
        """Store genome data and metadata in IPFS"""
        try:
            # Create storage object
            storage_obj = {
                "content": file_content.read().decode(),
                "metadata": metadata,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0"
            }
            
            # Convert to JSON and upload to IPFS
            json_data = json.dumps(storage_obj)
            result = self.client.add_json(json_data)
            
            logger.info(f"Successfully stored genome data with hash: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to store genome data: {str(e)}")
            raise
            
    async def get_genome(self, storage_id: str) -> Optional[Dict]:
        """Retrieve genome data from IPFS"""
        try:
            # Get data from IPFS
            json_data = self.client.get_json(storage_id)
            
            if not json_data:
                logger.warning(f"No data found for storage ID: {storage_id}")
                return None
                
            return json_data
            
        except Exception as e:
            logger.error(f"Failed to retrieve genome data: {str(e)}")
            raise
            
    async def delete_genome(self, storage_id: str) -> bool:
        """Delete genome data from IPFS (unpin)"""
        try:
            # Note: IPFS doesn't support true deletion
            # We can only unpin the data
            self.client.pin.rm(storage_id)
            logger.info(f"Successfully unpinned genome data: {storage_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unpin genome data: {str(e)}")
            raise
            
    async def update_metadata(self, storage_id: str, new_metadata: Dict) -> str:
        """Update metadata for existing genome data"""
        try:
            # Get existing data
            existing_data = await self.get_genome(storage_id)
            if not existing_data:
                raise ValueError(f"No data found for storage ID: {storage_id}")
                
            # Update metadata
            existing_data['metadata'] = new_metadata
            existing_data['timestamp'] = datetime.utcnow().isoformat()
            
            # Store updated data
            json_data = json.dumps(existing_data)
            result = self.client.add_json(json_data)
            
            # Unpin old version
            self.client.pin.rm(storage_id)
            
            logger.info(f"Successfully updated metadata with new hash: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update metadata: {str(e)}")
            raise
            
    def __del__(self):
        """Cleanup IPFS client connection"""
        try:
            if hasattr(self, 'client'):
                self.client.close()
        except Exception as e:
            logger.error(f"Error closing IPFS client: {str(e)}") 