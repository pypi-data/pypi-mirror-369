#!/usr/bin/env python3
"""
Command Line Interface for Vector Store Client.

Provides CLI commands for interacting with Vector Store services.
Supports all operations: create, search, delete, health check, etc.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
import json
import sys
from typing import Optional
import os

import click

from .client import VectorStoreClient
from .models import SemanticChunk


@click.group()
@click.option('--url', '-u', default='http://localhost:8007', help='Vector Store server URL')
@click.option('--timeout', '-t', default=30.0, type=float, help='Request timeout in seconds')
@click.pass_context
def cli(ctx: click.Context, url: str, timeout: float) -> None:
    """Vector Store Client CLI."""
    ctx.ensure_object(dict)
    ctx.obj['url'] = url
    ctx.obj['timeout'] = timeout


@cli.command()
@click.pass_context
def health(ctx: click.Context) -> None:
    """Check server health."""
    async def _health():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            health_data = await client.health_check()
            click.echo("Server Health Status:")
            click.echo(f"  Status: {health_data.status}")
            click.echo(f"  Version: {health_data.version}")
            click.echo(f"  Uptime: {health_data.uptime}")
            await client.close()
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_health())


@cli.command()
@click.option('--command', '-c', help='Specific command to get help for')
@click.pass_context
def help(ctx: click.Context, command: Optional[str]) -> None:
    """Get help information."""
    async def _help():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            if command:
                help_data = await client.get_help(command)
                click.echo(f"Help for '{command}':")
                click.echo(json.dumps(help_data, indent=2))
            else:
                help_data = await client.get_help()
                click.echo("Available commands:")
                click.echo(json.dumps(help_data, indent=2))
            await client.close()
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_help())


@cli.command()
@click.option('--path', '-p', help='Configuration path')
@click.pass_context
def config(ctx: click.Context, path: Optional[str]) -> None:
    """Get server configuration."""
    async def _config():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            if path:
                config_value = await client.get_config(path)
                click.echo(f"{path}: {config_value}")
            else:
                config_data = await client.get_config()
                click.echo("Server configuration:")
                click.echo(json.dumps(config_data, indent=2))
            await client.close()
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_config())


@cli.command()
@click.option('--file', '-f', help='JSON file with chunk data')
@click.option('--text', '-t', help='Text content for single chunk')
@click.option('--type', '-y', default='DocBlock', help='Chunk type')
@click.option('--language', '-l', default='en', help='Language code')
@click.option('--tags', help='Comma-separated tags')
@click.pass_context
def create(ctx: click.Context, file: Optional[str], text: Optional[str], type: str, language: str, tags: Optional[str]) -> None:
    """Create chunks from file or text."""
    async def _create():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            
            if file:
                # Create from file
                if not os.path.exists(file):
                    click.echo(f"Error: File {file} not found", err=True)
                    sys.exit(1)
                
                with open(file, 'r') as f:
                    chunks_data = json.load(f)
                
                if not chunks_data:
                    click.echo("Error: Empty file", err=True)
                    sys.exit(1)
                
                # Convert to SemanticChunk objects
                chunks = []
                for chunk_data in chunks_data:
                    chunk = SemanticChunk(**chunk_data)
                    chunks.append(chunk)
                
                result = await client.create_chunks(chunks)
                click.echo(f"Created {len(result.uuids)} chunks")
                for uuid in result.uuids:
                    click.echo(f"  {uuid}")
            
            elif text:
                # Create from text
                tags_list = tags.split(',') if tags else []
                chunk = await client.create_text_chunk(
                    text=text,
                    chunk_type=type,
                    language=language,
                    tags=tags_list
                )
                click.echo(f"Created chunk: {chunk.uuid}")
            
            else:
                click.echo("Error: Must provide either --file or --text", err=True)
                sys.exit(1)
            
            await client.close()
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_create())


@cli.command()
@click.option('--query', '-q', required=True, help='Search query')
@click.option('--limit', '-l', default=10, type=int, help='Maximum results')
@click.option('--filter', '-f', help='Metadata filter (JSON string)')
@click.option('--relevance', '-r', default=0.0, type=float, help='Minimum relevance threshold')
@click.pass_context
def search(ctx: click.Context, query: str, limit: int, filter: Optional[str], relevance: float) -> None:
    """Search for chunks."""
    async def _search():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            
            metadata_filter = None
            if filter:
                try:
                    metadata_filter = json.loads(filter)
                except json.JSONDecodeError:
                    click.echo("Error: Invalid JSON in filter", err=True)
                    sys.exit(1)
            
            results = await client.search_chunks(
                search_str=query,
                metadata_filter=metadata_filter,
                limit=limit,
                level_of_relevance=relevance
            )
            
            if results:
                click.echo(f"Found {len(results)} results:")
                for chunk in results:
                    click.echo(f"  {chunk.uuid}: {chunk.body[:100]}...")
            else:
                click.echo("No results found. Try adjusting search parameters.")
                click.echo("Suggestions:")
                click.echo("  - Lower the relevance threshold (--relevance 0.0)")
                click.echo("  - Increase the limit (--limit 20)")
                click.echo("  - Try different search terms")
            
            await client.close()
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_search())


@cli.command()
@click.option('--uuids', '-u', required=True, help='Comma-separated list of UUIDs to delete')
@click.pass_context
def delete(ctx: click.Context, uuids: str) -> None:
    """Delete chunks by UUIDs."""
    async def _delete():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            
            uuid_list = [u.strip() for u in uuids.split(',') if u.strip()]
            if not uuid_list:
                click.echo("Error: No valid UUIDs provided", err=True)
                sys.exit(1)
            
            result = await client.delete_chunks(uuids=uuid_list)
            
            if result.success:
                click.echo(f"Successfully deleted {result.deleted_count} chunks")
                if result.deleted_uuids:
                    click.echo("Deleted UUIDs:")
                    for uuid in result.deleted_uuids:
                        click.echo(f"  {uuid}")
            else:
                click.echo(f"Error: {result.error}", err=True)
                sys.exit(1)
            
            await client.close()
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_delete())


@cli.command()
@click.option('--ast-filter', '-a', help='AST filter (JSON string)')
@click.option('--limit', '-l', default=10, type=int, help='Maximum results')
@click.option('--relevance', '-r', default=0.0, type=float, help='Minimum relevance threshold')
@click.pass_context
def search_ast(ctx: click.Context, ast_filter: str, limit: int, relevance: float) -> None:
    """Search for chunks using AST filter."""
    async def _search_ast():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            
            if not ast_filter:
                click.echo("Error: AST filter is required", err=True)
                sys.exit(1)
            
            try:
                ast_data = json.loads(ast_filter)
            except json.JSONDecodeError:
                click.echo("Error: Invalid JSON in AST filter", err=True)
                sys.exit(1)
            
            results = await client.search_chunks(
                ast_filter=ast_data,
                limit=limit,
                level_of_relevance=relevance
            )
            
            if not results:
                click.echo("No results found for AST filter.")
                return
            
            click.echo(f"Found {len(results)} results:")
            click.echo()
            
            for i, chunk in enumerate(results, 1):
                click.echo(f"Result {i}:")
                click.echo(f"  UUID: {chunk.uuid}")
                click.echo(f"  Type: {chunk.type}")
                click.echo(f"  Language: {chunk.language}")
                click.echo(f"  Text: {chunk.text[:100]}...")
                if chunk.tags:
                    click.echo(f"  Tags: {', '.join(chunk.tags)}")
                click.echo()
            
            await client.close()
            
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_search_ast())


@cli.command()
@click.option('--query', '-q', help='Search query')
@click.option('--ast-filter', '-a', help='AST filter (JSON string)')
@click.option('--limit', '-l', default=10, type=int, help='Maximum results')
@click.option('--relevance', '-r', default=0.0, type=float, help='Minimum relevance threshold')
@click.pass_context
def search_advanced(ctx: click.Context, query: Optional[str], ast_filter: Optional[str], limit: int, relevance: float) -> None:
    """Advanced search with both text and AST filters."""
    async def _search_advanced():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            
            ast_data = None
            if ast_filter:
                try:
                    ast_data = json.loads(ast_filter)
                except json.JSONDecodeError:
                    click.echo("Error: Invalid JSON in AST filter", err=True)
                    sys.exit(1)
            
            results = await client.search_chunks(
                search_str=query,
                ast_filter=ast_data,
                limit=limit,
                level_of_relevance=relevance
            )
            
            if not results:
                click.echo("No results found.")
                return
            
            click.echo(f"Found {len(results)} results:")
            click.echo()
            
            for i, chunk in enumerate(results, 1):
                click.echo(f"Result {i}:")
                click.echo(f"  UUID: {chunk.uuid}")
                click.echo(f"  Type: {chunk.type}")
                click.echo(f"  Language: {chunk.language}")
                click.echo(f"  Text: {chunk.text[:100]}...")
                if chunk.tags:
                    click.echo(f"  Tags: {', '.join(chunk.tags)}")
                click.echo()
            
            await client.close()
            
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_search_advanced())


@cli.command()
@click.option('--text', '-t', required=True, help='Text content')
@click.option('--source-id', '-s', required=True, help='Source identifier')
@click.option('--type', '-y', default='DocBlock', help='Chunk type')
@click.option('--language', '-l', default='en', help='Language code')
@click.pass_context
def create_with_embedding(ctx: click.Context, text: str, source_id: str, type: str, language: str) -> None:
    """Create a chunk with automatic embedding generation."""
    async def _create():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            
            # Create chunk with embedding
            chunk = await client.create_chunk_with_embedding(
                text=text,
                source_id=source_id,
                chunk_type=type,
                language=language
            )
            
            # Save chunk to database
            result = await client.create_chunks([chunk])
            
            if result.success and result.uuids:
                created_uuid = result.uuids[0]
                click.echo(f"Created chunk:")
                click.echo(f"  UUID: {created_uuid}")
                click.echo(f"  Type: {chunk.type}")
                click.echo(f"  Language: {chunk.language}")
                click.echo(f"  Text: {chunk.text[:100]}...")
                if chunk.embedding:
                    click.echo(f"  Embedding: {len(chunk.embedding)} dimensions")
            else:
                click.echo(f"Failed to create chunk: {result.error}")
            
            await client.close()
            
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_create())


@cli.command()
@click.option('--uuid', '-u', required=True, help='Chunk UUID')
@click.pass_context
def delete(ctx: click.Context, uuid: str) -> None:
    """Delete a chunk by UUID."""
    async def _delete():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            
            result = await client.delete_chunks(uuids=[uuid])
            
            if result.success:
                click.echo(f"Successfully deleted chunk: {uuid}")
            else:
                click.echo(f"Failed to delete chunk: {result.error}")
            
            await client.close()
            
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_delete())


@cli.command()
@click.option('--ast-filter', '-a', help='AST filter (JSON string)')
@click.pass_context
def delete_ast(ctx: click.Context, ast_filter: str) -> None:
    """Delete chunks using AST filter."""
    async def _delete_ast():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            
            if not ast_filter:
                click.echo("Error: AST filter is required", err=True)
                sys.exit(1)
            
            try:
                ast_data = json.loads(ast_filter)
            except json.JSONDecodeError:
                click.echo("Error: Invalid JSON in AST filter", err=True)
                sys.exit(1)
            
            result = await client.delete_chunks(ast_filter=ast_data)
            
            if result.success:
                click.echo(f"Successfully deleted {result.deleted_count} chunks")
            else:
                click.echo(f"Failed to delete chunks: {result.error}")
            
            await client.close()
            
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_delete_ast())


@cli.command()
@click.pass_context
def count(ctx: click.Context) -> None:
    """Get total number of chunks."""
    async def _count():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            
            result = await client.execute_command("count", {})
            count_value = result.get('data', {}).get('count', 0)
            click.echo(f"Total chunks: {count_value}")
            
            await client.close()
            
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_count())


@cli.command()
@click.option('--ast-filter', '-a', help='AST filter (JSON string)')
@click.pass_context
def count_ast(ctx: click.Context, ast_filter: Optional[str]) -> None:
    """Count chunks using AST filter."""
    async def _count_ast():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            
            params = {}
            if ast_filter:
                try:
                    ast_data = json.loads(ast_filter)
                    params['ast_filter'] = ast_data
                except json.JSONDecodeError:
                    click.echo("Error: Invalid JSON in AST filter", err=True)
                    sys.exit(1)
            
            result = await client.execute_command("count", params)
            count_value = result.get('data', {}).get('count', 0)
            click.echo(f"Chunks matching filter: {count_value}")
            
            await client.close()
            
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_count_ast())


@cli.command()
@click.pass_context
def duplicates(ctx: click.Context) -> None:
    """Find duplicate UUIDs."""
    async def _duplicates():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            
            result = await client.find_duplicate_uuids()
            
            if result.duplicates:
                click.echo(f"Found {len(result.duplicates)} duplicate UUIDs:")
                for duplicate in result.duplicates:
                    click.echo(f"  {duplicate}")
            else:
                click.echo("No duplicate UUIDs found")
            
            await client.close()
            
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_duplicates())


@cli.command()
@click.option('--uuids', '-u', help='Comma-separated list of UUIDs to delete')
@click.option('--filter', '-f', help='Metadata filter (JSON string)')
@click.option('--ast-filter', '-a', help='AST filter (JSON string)')
@click.option('--confirm', is_flag=True, help='Confirm hard deletion')
@click.pass_context
def hard_delete(ctx: click.Context, uuids: Optional[str], filter: Optional[str], ast_filter: Optional[str], confirm: bool) -> None:
    """Hard delete chunks from the database."""
    async def _hard_delete():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            
            if not confirm:
                click.echo("Error: Hard delete requires --confirm flag", err=True)
                sys.exit(1)
            
            # Parse UUIDs
            uuid_list = None
            if uuids:
                uuid_list = [uuid.strip() for uuid in uuids.split(',')]
            
            # Parse filters
            metadata_filter = None
            if filter:
                try:
                    metadata_filter = json.loads(filter)
                except json.JSONDecodeError:
                    click.echo("Error: Invalid JSON in filter parameter", err=True)
                    sys.exit(1)
            
            ast_data = None
            if ast_filter:
                try:
                    ast_data = json.loads(ast_filter)
                except json.JSONDecodeError:
                    click.echo("Error: Invalid JSON in AST filter parameter", err=True)
                    sys.exit(1)
            
            result = await client.chunk_hard_delete(
                uuids=uuid_list,
                metadata_filter=metadata_filter,
                ast_filter=ast_data,
                confirm=True
            )
            
            if result.success:
                click.echo(f"✅ Successfully hard deleted {result.deleted_count} chunks")
            else:
                click.echo(f"❌ Hard delete failed: {result.error}")
            
            await client.close()
            
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_hard_delete())


@cli.command()
@click.option('--uuids', '-u', required=True, help='Comma-separated list of UUIDs to force delete')
@click.pass_context
def force_delete(ctx: click.Context, uuids: str) -> None:
    """Force delete chunks by UUIDs."""
    async def _force_delete():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            
            # Parse UUIDs
            uuid_list = [uuid.strip() for uuid in uuids.split(',')]
            
            result = await client.force_delete_by_uuids(
                uuids=uuid_list
            )
            
            if result.success:
                click.echo(f"✅ Successfully force deleted {result.deleted_count} chunks")
                if result.deleted_uuids:
                    click.echo(f"📋 Deleted UUIDs: {', '.join(result.deleted_uuids)}")
            else:
                click.echo(f"❌ Force delete failed: {result.error}")
            
            await client.close()
            
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_force_delete())


@cli.command()
@click.pass_context
def cleanup(ctx: click.Context) -> None:
    """Clean up deferred chunks."""
    async def _cleanup():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            
            result = await client.chunk_deferred_cleanup()
            
            if result.success:
                click.echo(f"Cleaned {result.cleaned_count} chunks")
            else:
                click.echo(f"Error: {result.error}", err=True)
                sys.exit(1)
            
            await client.close()
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_cleanup())


@cli.command()
@click.pass_context
def reindex(ctx: click.Context) -> None:
    """Reindex chunks with missing embeddings."""
    async def _reindex():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            
            result = await client.reindex_missing_embeddings()
            
            if result.success:
                click.echo(f"Reindexed {result.reindexed_count} chunks")
            else:
                click.echo(f"Error: {result.error}", err=True)
                sys.exit(1)
            
            await client.close()
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_reindex())


@cli.command()
@click.pass_context
def info(ctx: click.Context) -> None:
    """Get server information."""
    async def _info():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            
            info_data = await client.get_server_info()
            click.echo("Server Information:")
            click.echo(json.dumps(info_data, indent=2))
            
            await client.close()
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_info())


@cli.command()
@click.pass_context
def clean_orphans(ctx: click.Context) -> None:
    """Clean orphaned FAISS entries."""
    async def _clean_orphans():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            
            result = await client.clean_faiss_orphans()
            
            if result.success:
                click.echo(f"✅ Cleaned {result.cleaned_count} orphaned entries")
                click.echo(f"📊 Total processed: {result.total_processed}")
            else:
                click.echo(f"❌ Clean orphans failed: {result.error}")
            
            await client.close()
            
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_clean_orphans())


@cli.command()
@click.pass_context
def ast_examples(ctx: click.Context) -> None:
    """Show AST filter examples."""
    examples = {
        "Simple AND": {
            "operator": "AND",
            "left": {"field": "type", "operator": "=", "value": "DocBlock"},
            "right": {"field": "language", "operator": "=", "value": "en"}
        },
        "Complex OR": {
            "operator": "OR",
            "left": {"field": "type", "operator": "=", "value": "DocBlock"},
            "right": {"field": "type", "operator": "=", "value": "CodeBlock"}
        },
        "Range query": {
            "operator": "AND",
            "left": {"field": "quality_score", "operator": ">=", "value": 0.8},
            "right": {"field": "year", "operator": ">=", "value": 2023}
        },
        "NOT condition": {
            "operator": "NOT",
            "operand": {"field": "category", "operator": "=", "value": "test"}
        },
        "Nested AND/OR": {
            "operator": "AND",
            "left": {
                "operator": "OR",
                "left": {"field": "type", "operator": "=", "value": "DocBlock"},
                "right": {"field": "type", "operator": "=", "value": "CodeBlock"}
            },
            "right": {"field": "language", "operator": "=", "value": "en"}
        }
    }
    
    click.echo("AST Filter Examples:")
    click.echo("=" * 50)
    
    for name, example in examples.items():
        click.echo(f"\n{name}:")
        click.echo(json.dumps(example, indent=2))
    
    click.echo("\nUsage examples:")
    click.echo("  # Search with AST filter")
    click.echo('  python -m vector_store_client.cli search-ast -a \'{"operator": "AND", "left": {"field": "type", "operator": "=", "value": "DocBlock"}, "right": {"field": "language", "operator": "=", "value": "en"}}\'')
    click.echo("  # Count with AST filter")
    click.echo('  python -m vector_store_client.cli count-ast -a \'{"field": "quality_score", "operator": ">=", "value": 0.8}\'')
    click.echo("  # Delete with AST filter")
    click.echo('  python -m vector_store_client.cli delete-ast -a \'{"field": "category", "operator": "=", "value": "test"}\'')


def main() -> None:
    """Main CLI entry point."""
    cli()


if __name__ == "__main__":
    main() 