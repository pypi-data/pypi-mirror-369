#!/usr/bin/env python3
"""
Simple Vector Store Client CLI.

Usage:
    python -m vector_store_client.cli_client health
    python -m vector_store_client.cli_client search "machine learning"
    python -m vector_store_client.cli_client embed "Hello world"
    python -m vector_store_client.cli_client create-chunk "Text content" --source-id test
"""

import asyncio
import sys
import json
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .client import VectorStoreClient
from .exceptions import ServerError


class SimpleCLI:
    """Simple CLI for Vector Store Client."""
    
    def __init__(self):
        self.console = Console()
        self.client: Optional[VectorStoreClient] = None
    
    async def connect(self, url: str = "http://localhost:8007") -> None:
        """Connect to server."""
        try:
            self.client = await VectorStoreClient.create(url)
            self.console.print(f"✅ Connected to {url}")
        except Exception as e:
            self.console.print(f"❌ Connection failed: {e}")
            sys.exit(1)
    
    async def health(self) -> None:
        """Check server health."""
        await self.connect()
        
        try:
            health = await self.client.health_check()
            self.console.print(f"✅ Server health: {health.status}")
            if health.version:
                self.console.print(f"   Version: {health.version}")
            if health.uptime:
                self.console.print(f"   Uptime: {health.uptime}s")
        except Exception as e:
            self.console.print(f"❌ Health check failed: {e}")
            sys.exit(1)
    
    async def search(self, query: str, limit: int = 10) -> None:
        """Search chunks."""
        await self.connect()
        
        try:
            results = await self.client.search_chunks(search_str=query, limit=limit)
            
            if not results:
                self.console.print("📭 No results found")
                return
            
            table = Table(title=f"Search Results ({len(results)} found)")
            table.add_column("UUID", style="cyan")
            table.add_column("Text", style="white")
            table.add_column("Type", style="green")
            
            for chunk in results:
                text = chunk.text[:50] + "..." if len(chunk.text) > 50 else chunk.text
                table.add_row(chunk.uuid[:8], text, str(chunk.type))
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"❌ Search failed: {e}")
            sys.exit(1)
    
    async def embed(self, text: str) -> None:
        """Generate embedding for short text."""
        await self.connect()
        
        try:
            embedding = await self.client.embedding_adapter.embed_text(text)
            self.console.print(f"✅ Generated embedding")
            self.console.print(f"   Vector length: {len(embedding)}")
            self.console.print(f"   Vector: {embedding[:5]}...")
            
        except Exception as e:
            self.console.print(f"❌ Embedding failed: {e}")
            sys.exit(1)
    
    async def vectorize(self, text: str) -> None:
        """Vectorize short text for search."""
        await self.connect()
        
        try:
            embedding = await self.client.embedding_adapter.embed_text(text)
            self.console.print(f"✅ Vectorized text")
            self.console.print(f"   Text: {text}")
            self.console.print(f"   Vector length: {len(embedding)}")
            
        except Exception as e:
            self.console.print(f"❌ Vectorization failed: {e}")
            sys.exit(1)
    
    async def create_chunk(self, text: str, source_id: str) -> None:
        """Create chunks using SVO chunker and save to Vector Store."""
        await self.connect()
        
        try:
            # Step 1: Create chunks using SVO chunker (8009)
            self.console.print("🔄 Creating chunks with SVO chunker...")
            chunks = await self.client.svo_adapter.chunk_text(text)
            
            if not chunks:
                self.console.print("📭 No chunks created by SVO")
                return
            
            self.console.print(f"✅ SVO created {len(chunks)} chunks")
            
            # Step 2: Save chunks to Vector Store (8007)
            self.console.print("🔄 Saving chunks to Vector Store...")
            result = await self.client.create_chunks(chunks)
            
            if result.success:
                self.console.print(f"✅ Saved {len(result.uuids or [])} chunks to Vector Store:")
                for uuid in (result.uuids or []):
                    self.console.print(f"  - {uuid}")
            else:
                self.console.print(f"❌ Failed to save chunks: {result.error}")
            
        except Exception as e:
            self.console.print(f"❌ Failed to create chunks: {e}")
            sys.exit(1)
    
    async def models(self) -> None:
        """List embedding models."""
        await self.connect()
        
        try:
            models = await self.client.embedding_adapter.get_embedding_models()
            self.console.print(f"✅ Available models:")
            self.console.print(f"   {models}")
            
        except Exception as e:
            self.console.print(f"❌ Failed to get models: {e}")
            sys.exit(1)
    
    async def help(self) -> None:
        """Show help."""
        help_text = """
Vector Store Client CLI

Commands:
  health                    - Check server health
  search <query>           - Search chunks
  embed <text>             - Generate embedding for short text
  vectorize <text>         - Vectorize text for search
  create-chunk <text> <id> - Create chunks using SVO chunker
  models                   - List embedding models
  help                     - Show this help

Examples:
  python -m vector_store_client.cli_client health
  python -m vector_store_client.cli_client search "machine learning"
  python -m vector_store_client.cli_client embed "Hello world"
  python -m vector_store_client.cli_client vectorize "search query"
  python -m vector_store_client.cli_client create-chunk "Long text content" test-id
        """
        self.console.print(Panel(help_text, title="Help"))


async def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m vector_store_client.cli_client <command> [args...]")
        print("Commands: health, search, embed, vectorize, create-chunk, models, help")
        sys.exit(1)
    
    cli = SimpleCLI()
    command = sys.argv[1]
    
    if command == "health":
        await cli.health()
    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: search <query>")
            sys.exit(1)
        await cli.search(sys.argv[2])
    elif command == "embed":
        if len(sys.argv) < 3:
            print("Usage: embed <text>")
            sys.exit(1)
        await cli.embed(sys.argv[2])
    elif command == "vectorize":
        if len(sys.argv) < 3:
            print("Usage: vectorize <text>")
            sys.exit(1)
        await cli.vectorize(sys.argv[2])
    elif command == "create-chunk":
        if len(sys.argv) < 4:
            print("Usage: create-chunk <text> <source-id>")
            sys.exit(1)
        await cli.create_chunk(sys.argv[2], sys.argv[3])
    elif command == "models":
        await cli.models()
    elif command == "help":
        await cli.help()
    else:
        print(f"Unknown command: {command}")
        print("Use 'help' for available commands")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 