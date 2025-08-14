"""
SVO chunker adapter for Vector Store Client.

Provides interface to SVO chunking service using svo_client library.
"""

import logging
from typing import List, Optional, Dict, Any
from svo_client.chunker_client import ChunkerClient

from ..models import SemanticChunk
from ..exceptions import VectorStoreError, ConnectionError, ServerError
from chunk_metadata_adapter.data_types import ChunkRole, ChunkType, LanguageEnum

logger = logging.getLogger(__name__)


class SVOChunkerAdapter:
    """
    Adapter for SVO chunking service using svo_client library.
    
    Provides interface to SVO chunking service for semantic text chunking.
    """
    
    def __init__(self, base_url: str = "http://localhost", port: int = 8009):
        """
        Initialize SVO chunker adapter.
        
        Parameters:
            base_url: Base URL of SVO chunking service
            port: Port of SVO chunking service
        """
        self.base_url = base_url
        self.port = port
        self.client: Optional[ChunkerClient] = None
    
    async def _create_client(self) -> None:
        """Create and initialize chunker client."""
        if not self.client:
            self.client = ChunkerClient(
                url=self.base_url,
                port=self.port
            )
            await self.client.__aenter__()
    
    async def _close_client(self) -> None:
        """Close chunker client."""
        if self.client:
            await self.client.__aexit__(None, None, None)
            self.client = None
    
    async def chunk_text(self, text: str) -> List[SemanticChunk]:
        """
        Chunk text using SVO semantic chunking.
        
        Parameters:
            text: Text to chunk
            
        Returns:
            List[SemanticChunk]: List of semantic chunks
            
        Raises:
            ConnectionError: If connection fails
            ServerError: If server returns error
        """
        try:
            await self._create_client()
            
            # Call chunking service
            chunks = await self.client.chunk_text(text)
            
            # Convert to SemanticChunk objects
            semantic_chunks = []
            for chunk in chunks:
                # Parse chunk data
                chunk_data = self._parse_chunk_data(chunk)
                semantic_chunks.append(SemanticChunk(**chunk_data))
            
            return semantic_chunks
            
        except Exception as e:
            logger.error(f"Chunking error: {e}")
            raise ConnectionError(f"Failed to chunk text: {e}")
        finally:
            await self._close_client()
    
    def _parse_chunk_data(self, chunk) -> Dict[str, Any]:
        """
        Parse chunk data from SVO service response.
        
        Parameters:
            chunk: Raw chunk data from service
            
        Returns:
            Dict[str, Any]: Parsed chunk data for SemanticChunk
        """
        # Extract basic fields
        chunk_data = {
            "uuid": chunk.uuid if hasattr(chunk, 'uuid') else None,
            "source_id": chunk.source_id if hasattr(chunk, 'source_id') else None,
            "body": chunk.text if hasattr(chunk, 'text') else "",
            "text": chunk.text if hasattr(chunk, 'text') else "",
            "embedding": chunk.embedding if hasattr(chunk, 'embedding') else [],
            "type": ChunkType.from_string(chunk.type) if hasattr(chunk, 'type') else ChunkType.from_string("DocBlock"),
            "language": LanguageEnum.from_string(chunk.language) if hasattr(chunk, 'language') else LanguageEnum.from_string("ru"),
            "role": ChunkRole.from_string(chunk.role) if hasattr(chunk, 'role') else ChunkRole.from_string("USER"),
            "block_meta": chunk.block_meta if hasattr(chunk, 'block_meta') else {}
        }
        
        return chunk_data
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check SVO chunking service health.
        
        Returns:
            Dict[str, Any]: Health status
            
        Raises:
            ConnectionError: If connection fails
            ServerError: If server returns error
        """
        try:
            await self._create_client()
            
            result = await self.client.health()
            
            if "result" in result:
                return result["result"]
            else:
                raise ServerError("No result in health response")
                
        except Exception as e:
            logger.error(f"Health check error: {e}")
            raise ConnectionError(f"Failed to check health: {e}")
        finally:
            await self._close_client()
    
    async def get_help(self) -> Dict[str, Any]:
        """
        Get SVO chunking service help.
        
        Returns:
            Dict[str, Any]: Help information
            
        Raises:
            ConnectionError: If connection fails
            ServerError: If server returns error
        """
        try:
            await self._create_client()
            
            result = await self.client.get_help()
            
            if "result" in result:
                return result["result"]
            else:
                raise ServerError("No result in help response")
                
        except Exception as e:
            logger.error(f"Help error: {e}")
            raise ConnectionError(f"Failed to get help: {e}")
        finally:
            await self._close_client()
    
    async def get_chunker_info(self) -> Dict[str, Any]:
        """
        Get SVO chunking service information.
        
        Returns:
            Dict[str, Any]: Service information
            
        Raises:
            ConnectionError: If connection fails
            ServerError: If server returns error
        """
        try:
            await self._create_client()
            
            result = await self.client.get_openapi_schema()
            
            if "result" in result:
                return result["result"]
            else:
                raise ServerError("No result in info response")
                
        except Exception as e:
            logger.error(f"Info error: {e}")
            raise ConnectionError(f"Failed to get info: {e}")
        finally:
            await self._close_client()
    
    async def close(self) -> None:
        """Close the adapter and release resources."""
        await self._close_client() 