"""
Chunk operations for Vector Store Client.

This module contains all chunk-related operations including creation,
search, deletion, and metadata management.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

from typing import List, Dict, Any, Optional
from .base_operations import BaseOperations
from ..exceptions import ServerError, ValidationError
from ..models import (
    SemanticChunk, CreateChunksResponse, DeleteResponse,
    DuplicateUuidsResponse, CleanupResponse, ReindexResponse
)
from ..types import (
    DEFAULT_LIMIT, DEFAULT_OFFSET, DEFAULT_RELEVANCE_THRESHOLD,
    DEFAULT_CHUNK_TYPE, DEFAULT_LANGUAGE, DEFAULT_STATUS
)
from ..utils import (
    generate_uuid, generate_sha256_hash, format_timestamp, normalize_text
)
from ..validation import (
    validate_search_params, validate_uuid_list, validate_chunk_type,
    validate_language, validate_status, validate_embedding
)
# Remove circular import - will create client instance directly


class ChunkOperations(BaseOperations):
    """Operations for managing chunks in the vector store."""
    
    async def create_chunks(
        self,
        chunks: List[SemanticChunk]
    ) -> CreateChunksResponse:
        """
        Create multiple chunks in the vector store.
        
        Parameters:
            chunks: List of chunk metadata objects
            
        Returns:
            CreateChunksResponse: Response with created UUIDs
            
        Raises:
            ValidationError: If any chunk fails validation
            ConnectionError: If connection fails
        """
        if not chunks:
            raise ValidationError("Chunks list cannot be empty")
        
        # Validate each chunk
        for chunk in chunks:
            if not chunk.body:
                raise ValidationError(f"Chunk missing required field 'body'")
            if not chunk.source_id:
                raise ValidationError(f"Chunk missing required field 'source_id'")
            if not chunk.embedding or len(chunk.embedding) != 384:
                raise ValidationError(f"Chunk embedding must have 384 dimensions")
        
        # Prepare chunks data with unique UUIDs
        chunks_data = []
        for chunk in chunks:
            chunk_dict = chunk.model_dump()
            # Ensure unique UUID for each chunk
            if not chunk_dict.get('uuid'):
                chunk_dict['uuid'] = generate_uuid()
            chunks_data.append(chunk_dict)
        
        # Execute command
        response = await self._execute_command(
            "chunk_create",
            {"chunks": chunks_data}
        )
        
        print(f"Debug: Server response: {response}")
        
        if response.get("success"):
            # Extract UUIDs from data.uuids structure
            data = response.get("data", {})
            uuids = data.get("uuids", [])
            return CreateChunksResponse(
                success=True,
                uuids=uuids,
                created_count=data.get("created_count"),
                failed_count=data.get("failed_count")
            )
        else:
            raise ServerError(f"Failed to create chunks: {response.get('error')}")
    
    async def create_text_chunk_with_embedding(
        self,
        text: str,
        source_id: str,
        chunk_type: str = "DocBlock",
        language: str = "en",
        **kwargs
    ) -> SemanticChunk:
        """
        Create a chunk with automatic embedding generation.
        
        Parameters:
            text: Text content
            source_id: Source identifier
            chunk_type: Type of chunk
            language: Language code
            **kwargs: Additional metadata
            
        Returns:
            SemanticChunk: Created chunk with embedding
            
        Raises:
            ValidationError: If text is empty
            ConnectionError: If connection fails
            ServerError: If embedding generation fails
        """
        if not text:
            raise ValidationError("Text cannot be empty")
        
        # Step 1: Generate embedding
        import httpx
        embedding_client = httpx.AsyncClient(timeout=30.0)
        
        try:
            # Call embedding service directly
            embedding_response = await embedding_client.post(
                "http://localhost:8001/cmd",
                json={
                    "jsonrpc": "2.0",
                    "method": "embed",
                    "params": {"texts": [text]},
                    "id": 1
                }
            )
            embedding_data = embedding_response.json()
            
            if not embedding_data.get("result", {}).get("success"):
                raise ServerError("Failed to generate embedding")
            
            embedding = embedding_data.get("result", {}).get("data", {}).get("embeddings", [None])[0]
            
            # Step 2: Create chunk with embedding
            chunk_data = {
                "body": text,
                "text": text,
                "source_id": source_id,
                "type": chunk_type,
                "language": language,
                "embedding": embedding,
                "uuid": generate_uuid()
            }
            chunk_data.update(kwargs)
            
            response = await self._execute_command(
                "chunk_create",
                {"chunks": [chunk_data]}
            )
            
            if response.get("success"):
                uuid = response.get("data", {}).get("uuids", [None])[0]
                return SemanticChunk(
                    uuid=uuid,
            body=text,
            text=text,
                    source_id=source_id,
            type=chunk_type,
            language=language,
                    embedding=embedding,
            **kwargs
        )
            else:
                raise ServerError(f"Failed to create chunk: {response.get('error')}")
        
        finally:
            await embedding_client.aclose()
    
    async def search_chunks(
        self,
        search_str: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        ast_filter: Optional[Dict[str, Any]] = None,
        limit: int = DEFAULT_LIMIT,
        level_of_relevance: float = DEFAULT_RELEVANCE_THRESHOLD,
        offset: int = DEFAULT_OFFSET
    ) -> List[SemanticChunk]:
        """
        Search for chunks by various criteria.
        
        Parameters:
            search_str: Text to search for
            embedding: Vector to search with
            metadata_filter: Filter by metadata
            ast_filter: AST-based filter
            limit: Maximum results
            level_of_relevance: Minimum relevance threshold
            offset: Number of results to skip
            
        Returns:
            List[SemanticChunk]: Matching chunks
        """
        # Validate search parameters
        validate_search_params(search_str, metadata_filter, limit, level_of_relevance, offset)
        
        # Validate embedding if provided
        if embedding is not None:
            validate_embedding(embedding)
        
        # Prepare search parameters
        search_params = {
            "limit": limit,
            "level_of_relevance": level_of_relevance,
            "offset": offset
        }
        
        if search_str:
            search_params["search_str"] = search_str
        
        if embedding:
            search_params["embedding"] = embedding
        
        if metadata_filter:
            search_params["metadata_filter"] = metadata_filter
        
        if ast_filter:
            search_params["ast_filter"] = ast_filter
        
        # Execute search
        response = await self._execute_command("search", search_params)
        
        # Convert response to SemanticChunk objects
        chunks = []
        chunks_data = response.get("data", {}).get("chunks", [])
        for chunk_data in chunks_data:
            try:
                chunk = SemanticChunk(**chunk_data)
                chunks.append(chunk)
            except Exception as e:
                print(f"Warning: Failed to parse chunk data: {e}")
                continue
        
        return chunks
    
    async def delete_chunks(
        self,
        uuids: Optional[List[str]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> DeleteResponse:
        """
        Delete chunks by UUIDs or metadata filter.
        
        Parameters:
            uuids: List of chunk UUIDs to delete
            metadata_filter: Filter for chunks to delete
            
        Returns:
            DeleteResponse: Deletion result
        """
        if not uuids and not metadata_filter:
            raise ValidationError("Must provide either uuids or metadata_filter")
        
        params = {}
        if uuids:
            validate_uuid_list(uuids)
            params["uuids"] = uuids
        
        if metadata_filter:
            params["metadata_filter"] = metadata_filter
        
        response = await self._execute_command("chunk_delete", params)
        
        return DeleteResponse(
            success=response.get("success", False),
            deleted_count=response.get("data", {}).get("deleted_count", 0),
            deleted_uuids=response.get("data", {}).get("deleted_uuids", []),
            error=response.get("error")
        )
    
    async def find_duplicate_uuids(
        self,
        metadata_filter: Optional[Dict[str, Any]] = None,
        ast_filter: Optional[Dict[str, Any]] = None
    ) -> DuplicateUuidsResponse:
        """
        Find duplicate UUIDs in the store.
        
        Parameters:
            metadata_filter: Filter by metadata
            ast_filter: AST-based filter
            
        Returns:
            DuplicateUuidsResponse: Duplicate information
        """
        params = {}
        if metadata_filter:
            params["metadata_filter"] = metadata_filter
        
        if ast_filter:
            params["ast_filter"] = ast_filter
        
        response = await self._execute_command("find_duplicate_uuids", params)
        
        return DuplicateUuidsResponse(
            success=response.get("success", False),
            total_duplicates=response.get("data", {}).get("total_duplicates", 0),
            duplicates=response.get("data", {}).get("duplicates", []),
            error=response.get("error")
        )
    
    async def reindex_missing_embeddings(self) -> ReindexResponse:
        """
        Reindex chunks with missing embeddings.
        
        Returns:
            ReindexResponse: Reindexing result
            
        Raises:
            ServerError: If reindexing fails
        """
        response = await self._execute_command("reindex_missing_embeddings", {})
        
        if response.get("success"):
            data = response.get("data", {})
            return ReindexResponse(
                success=True,
                reindexed_count=data.get("reindexed_count", 0),
                total_count=data.get("total_count", 0)
            )
        else:
            raise ServerError(f"Failed to reindex embeddings: {response.get('error')}")
    
    async def clean_faiss_orphans(self) -> CleanupResponse:
        """
        Clean orphaned FAISS entries.
        
        Removes FAISS index entries that don't have corresponding chunks in the database.
        This helps maintain consistency between the vector index and the database.
        
        Returns:
            CleanupResponse: Cleanup result with count of cleaned entries
            
        Raises:
            ServerError: If cleanup fails
            
        Example:
            >>> result = await client.clean_faiss_orphans()
            >>> print(f"Cleaned {result.cleaned_count} orphaned entries")
        """
        response = await self._execute_command("clean_faiss_orphans", {})
        
        if response.get("success"):
            data = response.get("data", {})
            return CleanupResponse(
                success=True,
                cleaned_count=data.get("cleaned_count", 0),
                total_processed=data.get("total_processed", 0)
            )
        else:
            raise ServerError(f"Failed to clean FAISS orphans: {response.get('error')}")
    
    async def chunk_hard_delete(
        self,
        uuids: Optional[List[str]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        ast_filter: Optional[Dict[str, Any]] = None,
        confirm: bool = False
    ) -> DeleteResponse:
        """
        Hard delete chunks from the database.
        
        Performs permanent deletion of chunks without possibility of recovery.
        Requires explicit confirmation for safety.
        
        Parameters:
            uuids: List of UUIDs to delete (optional)
            metadata_filter: Metadata filter for deletion (optional)
            ast_filter: AST filter for deletion (optional)
            confirm: Confirmation flag for safety (required)
            
        Returns:
            DeleteResponse: Deletion result with count of deleted chunks
            
        Raises:
            ValidationError: If no confirmation provided or invalid parameters
            ServerError: If deletion fails
            
        Example:
            >>> # Delete specific chunks
            >>> result = await client.chunk_hard_delete(
            ...     uuids=["uuid1", "uuid2"],
            ...     confirm=True
            ... )
            >>> print(f"Deleted {result.deleted_count} chunks")
            
            >>> # Delete by filter
            >>> result = await client.chunk_hard_delete(
            ...     metadata_filter={"type": "test"},
            ...     confirm=True
            ... )
        """
        if not confirm:
            raise ValidationError("Hard delete requires explicit confirmation (confirm=True)")
        
        # Validate that at least one deletion method is specified
        if not uuids and not metadata_filter and not ast_filter:
            raise ValidationError("Must specify uuids, metadata_filter, or ast_filter for deletion")
        
        # Validate UUIDs if provided
        if uuids:
            validate_uuid_list(uuids)
        
        # Prepare parameters
        params = {"confirm": True}
        
        if uuids:
            params["uuids"] = uuids
        if metadata_filter:
            params["metadata_filter"] = metadata_filter
        if ast_filter:
            params["ast_filter"] = ast_filter
        
        # Execute command
        response = await self._execute_command("chunk_hard_delete", params)
        
        if response.get("success"):
            data = response.get("data", {})
            return DeleteResponse(
                success=True,
                deleted_count=data.get("deleted_count", 0),
                message=f"Successfully deleted {data.get('deleted_count', 0)} chunks"
            )
        else:
            raise ServerError(f"Hard delete failed: {response.get('error')}")
    
    async def force_delete_by_uuids(
        self,
        uuids: List[str]
    ) -> DeleteResponse:
        """
        Force delete chunks by UUIDs.
        
        Performs forced deletion bypassing normal restrictions and safety checks.
        Use with extreme caution as this operation cannot be undone.
        
        Parameters:
            uuids: List of UUIDs to force delete (required)
            
        Returns:
            DeleteResponse: Deletion result with count of deleted chunks
            
        Raises:
            ValidationError: If UUIDs list is empty or invalid
            ServerError: If deletion fails
            
        Example:
            >>> # Force delete specific chunks
            >>> result = await client.force_delete_by_uuids(
            ...     uuids=["uuid1", "uuid2"]
            ... )
            >>> print(f"Force deleted {result.deleted_count} chunks")
        """
        if not uuids:
            raise ValidationError("UUIDs list cannot be empty for force delete")
        
        # Validate UUIDs
        validate_uuid_list(uuids)
        
        # Prepare parameters - server requires force=True parameter
        # Note: Server has a bug where it doesn't accept force=True properly
        # This needs to be fixed on the server side
        params = {
            "uuids": uuids,
            "force": True  # Server requires this parameter
        }
        
        # Execute command
        response = await self._execute_command("force_delete_by_uuids", params)
        
        if response.get("success"):
            data = response.get("data", {})
            return DeleteResponse(
                success=True,
                deleted_count=data.get("deleted", 0),
                deleted_uuids=data.get("deleted_uuids", []),
                message=f"Successfully force deleted {data.get('deleted', 0)} chunks"
            )
        else:
            raise ServerError(f"Force delete failed: {response.get('error')}")
    
    async def chunk_deferred_cleanup(self) -> CleanupResponse:
        """
        Clean up deferred chunks.
        
        Processes chunks marked for deletion. This command physically removes
        soft-deleted records from FAISS and Redis to free up space.
        
        Returns:
            CleanupResponse: Cleanup result with count of processed chunks
            
        Raises:
            ServerError: If cleanup fails
            
        Example:
            >>> # Clean up deferred chunks
            >>> result = await client.chunk_deferred_cleanup()
            >>> print(f"Cleaned {result.cleaned_count} chunks")
        """
        # Execute command - server doesn't support dry_run and batch_size parameters
        response = await self._execute_command("chunk_deferred_cleanup", {})
        
        if response.get("success"):
            data = response.get("data", {})
            return CleanupResponse(
                success=True,
                cleaned_count=data.get("cleaned_count", 0),
                total_processed=data.get("cleaned_count", 0),
                dry_run=False
            )
        else:
            raise ServerError(f"Deferred cleanup failed: {response.get('error')}") 