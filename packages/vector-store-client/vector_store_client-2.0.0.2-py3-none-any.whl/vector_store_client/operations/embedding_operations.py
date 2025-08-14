"""
Embedding operations for Vector Store Client.

This module contains all embedding-related operations including
text embedding, batch embedding, and model management.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import uuid
from typing import List, Optional
from .base_operations import BaseOperations
from ..models import SemanticChunk, EmbedResponse, ModelsResponse
from ..utils import generate_uuid


class EmbeddingOperations(BaseOperations):
    """Operations for managing embeddings."""
    
    async def embed_text(
        self,
        text: str,
        model: Optional[str] = None,
        **kwargs
    ) -> EmbedResponse:
        """
        Generate embedding for a single text.
        
        Parameters:
            text: Text to embed
            model: Embedding model to use (optional)
            **kwargs: Additional parameters
            
        Returns:
            EmbedResponse: Embedding response with vector
        """
        embedding = await self.client.embedding_adapter.embed_text(text)
        return EmbedResponse(
            embedding=embedding, 
            model=model or "default",
            dimension=len(embedding)
        )
    
    async def embed_batch(
        self,
        texts: List[str],
        model: Optional[str] = None,
        **kwargs
    ) -> List[EmbedResponse]:
        """
        Generate embeddings for multiple texts.
        
        Parameters:
            texts: List of texts to embed
            model: Embedding model to use (optional)
            **kwargs: Additional parameters
            
        Returns:
            List[EmbedResponse]: List of embedding responses
        """
        embeddings = await self.client.embedding_adapter.embed_batch(texts)
        return [
            EmbedResponse(
                embedding=emb, 
                model=model or "default",
                dimension=len(emb)
            ) for emb in embeddings
        ]
    
    async def get_embedding_models(self) -> ModelsResponse:
        """
        Get available embedding models.
        
        Returns:
            ModelsResponse: Available models information
        """
        raw_response = await self.client.embedding_adapter.get_embedding_models()
        
        # Convert raw response to ModelsResponse
        if isinstance(raw_response, dict):
            data = raw_response.get("data", {})
            models_data = data.get("models", [])
            
            # Extract model names from model objects
            models = []
            model_configs = {}
            
            for model_data in models_data:
                if isinstance(model_data, dict):
                    model_name = model_data.get("name", "unknown")
                    models.append(model_name)
                    model_configs[model_name] = model_data
                elif isinstance(model_data, str):
                    models.append(model_data)
                    model_configs[model_data] = {"dimension": 384}
            
            default_model = data.get("default_model", "default")
            
            return ModelsResponse(
                models=models,
                default_model=default_model,
                model_configs=model_configs
            )
        else:
            # Fallback if response is not in expected format
            return ModelsResponse(
                models=["default"],
                default_model="default",
                model_configs={"default": {"dimension": 384}}
            )
    
    async def create_chunk_with_embedding(
        self,
        text: str,
        chunk_type: str = "Draft",
        language: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> SemanticChunk:
        """
        Create a chunk with automatic embedding generation.
        
        Parameters:
            text: Text content
            chunk_type: Type of chunk
            language: Language of text
            model: Embedding model to use
            **kwargs: Additional chunk parameters
            
        Returns:
            SemanticChunk: Created chunk with embedding
        """
        # Generate embedding
        embed_response = await self.embed_text(text, model)
        
        # Create chunk with embedding
        chunk = SemanticChunk(
            body=text,
            text=text,
            source_id=generate_uuid(),  # Add required source_id
            embedding=embed_response.embedding,
            type=chunk_type,
            language=language or "en",
            **kwargs
        )
        
        return chunk
    
    async def create_chunks_with_embeddings(
        self,
        texts: List[str],
        chunk_type: str = "Draft",
        language: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> List[SemanticChunk]:
        """
        Create multiple chunks with automatic embedding generation.
        
        Parameters:
            texts: List of text contents
            chunk_type: Type of chunks
            language: Language of texts
            model: Embedding model to use
            **kwargs: Additional chunk parameters
            
        Returns:
            List[SemanticChunk]: List of created chunks with embeddings
        """
        # Generate embeddings for all texts
        embed_responses = await self.embed_batch(texts, model)
        
        # Create chunks with embeddings
        chunks = []
        for i, (text, embed_response) in enumerate(zip(texts, embed_responses)):
            chunk = SemanticChunk(
                body=text,
                text=text,
                source_id=generate_uuid(),  # Add required source_id
                embedding=embed_response.embedding,
                type=chunk_type,
                language=language or "en",
                **kwargs
            )
            chunks.append(chunk)
        
        return chunks 