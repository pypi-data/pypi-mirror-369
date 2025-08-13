#!/usr/bin/env python3
"""
ZMP Knowledge Store MCP Server

Following the standard FastMCP pattern from the Medium article
"""

import asyncio
import logging
from datetime import datetime, timezone
import json

# Add FastAPI for health check endpoint
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

# Import FastMCP
from fastmcp import FastMCP, Context

# from mcp.server.fastmcp import FastMCP
from zmp_knowledge_store.knowledge_store import ZmpKnowledgeStore
from zmp_knowledge_store.config import Config

# Load environment variables first
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Configure logging for all package modules
logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")
logger = logging.getLogger("zmp-knowledge-store")

# Ensure all zmp_knowledge_store module loggers are visible
package_logger = logging.getLogger("zmp_knowledge_store")
package_logger.setLevel(logging.INFO)


# Create the FastMCP server with standard variable name
mcp = FastMCP(
    name="zmp-knowledge-store",
    instructions="""
               This server provides ZMP knowledge store tools.
               Call ingest_documents() to ingest documents into the knowledge store.
               Call search_knowledge() to search the knowledge store for relevant information.
            """,
)

# Add /healthz endpoint to the main FastMCP app (on port 5371)
if hasattr(mcp, "app") and isinstance(mcp.app, FastAPI):

    @mcp.app.get("/healthz")
    def healthz():
        return PlainTextResponse("ok", status_code=200)


# Global knowledge store - initialize at module level for mcp dev
knowledge_store = None


async def get_knowledge_store():
    """Initialize and return knowledge store"""
    global knowledge_store
    if knowledge_store is None:
        logger.info("🔧 Creating ZmpKnowledgeStore instance...")
        knowledge_store = ZmpKnowledgeStore()

    # Always ensure async initialization is run
    if not getattr(knowledge_store, "initialized", False):
        logger.info("🔌 Initializing Knowledge Store (async)...")
        await knowledge_store.initialize()

        logger.info("✅ Knowledge store initialized successfully (async)")

    return knowledge_store


@mcp.tool()
async def ingest_documents(
    documents: list, solution: str = None, collection: str = None, ctx: Context = None
):
    """
    Ingest documents into the ZMP knowledge store.

    Args:
        documents: List of documents to ingest
        solution: Solution identifier (optional)
        collection: Target collection name. If not provided, uses default collection.
                   If collection doesn't exist, it will be created with same vector configs as existing collections.
        ctx: MCP context (internal use)
    """
    # logger.info(f"[REQUEST] ingest_documents input: {json.dumps({'documents': documents, 'solution': solution}, ensure_ascii=False, indent=2)}")
    ingest_timestamp = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    try:
        if not documents:
            result = {
                "success": False,
                "error": "No documents provided for ingestion",
                "results": [],
            }
            if ctx:
                await ctx.error("No documents provided for ingestion")
            return result

        # Validate collection parameter
        if collection is not None:
            if not collection or not collection.strip():
                result = {
                    "success": False,
                    "error": "Collection name cannot be empty",
                    "results": [],
                }
                if ctx:
                    await ctx.error("Collection name cannot be empty")
                return result
        ks = await get_knowledge_store()
        results = []
        ingest_results = await ks.ingest_documents(
            documents,
            ingest_timestamp=ingest_timestamp,
            solution=solution,
            collection=collection,
        )
        results = ingest_results.get("results", [])
        response = {"success": True, "results": results}
        if "total_page_count" in ingest_results:
            response["total_page_count"] = ingest_results["total_page_count"]
        logger.info(
            f"##### Ingest Document Job completed with {len(results)} results successfully! #####"
        )
        return response
    except Exception as e:
        if ctx:
            await ctx.error(f"💥 Document ingestion failed: {e}")
        logger.error(f"##### Ingest Document Job failed: {e} #####")
        return {"success": False, "error": f"Ingestion failed: {str(e)}", "results": []}


@mcp.tool()
async def search_knowledge(
    query: str, n_results: int = 5, collection: str = None, ctx: Context = None
):
    """
    Search the ZMP knowledge store for relevant information.

    Args:
        query: Search query string
        n_results: Number of results to return (1-20, default: 5)
        collection: Target collection name. If not provided, uses default collection.
                   If collection doesn't exist, it will be created with same vector configs as existing collections.
        ctx: MCP context (internal use)
    """
    logger.info(
        f"[REQUEST] search_knowledge input: {json.dumps({'query': query, 'n_results': n_results}, ensure_ascii=False, indent=2)}"
    )
    try:
        if not query or not query.strip():
            result = {
                "success": False,
                "error": "Empty search query provided",
                "query": query,
                "results": [],
            }
            if ctx:
                await ctx.error("Empty search query provided")
            return result

        # Validate collection parameter
        if collection is not None:
            if not collection or not collection.strip():
                result = {
                    "success": False,
                    "error": "Collection name cannot be empty",
                    "query": query,
                    "results": [],
                }
                if ctx:
                    await ctx.error("Collection name cannot be empty")
                return result
        n_results = max(1, min(n_results, 20))
        ks = await get_knowledge_store()
        search_results = await ks.search_knowledge(
            query, n_results, collection=collection
        )

        if "error" in search_results:
            error_message = search_results.get(
                "error", "Search failed without a specific message."
            )
            result = {
                "success": False,
                "error": error_message,
                "query": query,
                "results": [],
            }
            if ctx:
                await ctx.error(error_message)
            return result

        results = search_results.get("results", [])
        return {"query": query, "results": results}
    except Exception as e:
        if ctx:
            await ctx.error(f"💥 Knowledge search failed: {e}")
        return {
            "success": False,
            "error": f"Search failed: {str(e)}",
            "query": query,
            "results": [],
        }


@mcp.tool()
async def log_chat_history(
    query: str,
    response: str,
    user_id: str = None,
    session_id: str = None,
    doc_urls: list = None,
    citation_map: dict = None,
    ctx: Context = None,
):
    """
    Log a user query and response pair to the chat_history collection in Qdrant.

    Args:
        query: The user's query
        response: The system's response
        user_id: Optional user identifier
        session_id: Optional session identifier
        doc_urls: Optional list of document URLs referenced in the response
        citation_map: Optional dictionary mapping document IDs to citation information
    """
    logger.info(
        f"[REQUEST] log_chat_history input: {{'query': {query}, 'response': {response}, 'user_id': {user_id}, 'session_id': {session_id}, 'doc_urls': {doc_urls}, 'citation_map': {citation_map}}}"
    )
    try:
        if not query or not response:
            result = {
                "success": False,
                "error": "Both query and response are required",
                "query": query,
                "response": response,
            }
            if ctx:
                await ctx.error("Both query and response are required")
            return result
        timestamp = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        ks = await get_knowledge_store()
        record_id = await ks.log_chat_history(
            query, response, timestamp, user_id, session_id, doc_urls, citation_map
        )
        logger.info(f"✅ Chat history logged: {record_id}")
        return {"success": True, "id": record_id}
    except Exception as e:
        if ctx:
            await ctx.error(f"💥 Chat history logging failed: {e}")
        logger.error(f"##### Chat history logging failed: {e} #####")
        return {"success": False, "error": f"Chat history logging failed: {str(e)}"}


@mcp.tool()
async def search_chat_history(
    query: str, user_id: str = None, n_results: int = 5, ctx: Context = None
):
    """
    Hybrid search for chat history records using dense+sparse vectors and optional user_id filter.

    Returns search results that include all fields from log_chat_history:
    - query, response, timestamp, user_id, session_id
    - doc_urls: list of document URLs referenced in the response
    - citation_map: dictionary mapping document IDs to citation information
    """
    logger.info(
        f"[REQUEST] search_chat_history input: {{'query': {query}, 'user_id': {user_id}, 'n_results': {n_results}}}"
    )
    try:
        if not query or not query.strip():
            result = {
                "success": False,
                "error": "Empty search query provided",
                "query": query,
                "results": [],
            }
            if ctx:
                await ctx.error("Empty search query provided")
            return result
        n_results = max(1, min(n_results, 20))
        ks = await get_knowledge_store()
        search_results = await ks.search_chat_history(query, user_id, n_results)
        return {"query": query, "user_id": user_id, "results": search_results}
    except Exception as e:
        if ctx:
            await ctx.error(f"💥 Chat history search failed: {e}")
        return {
            "success": False,
            "error": f"Chat history search failed: {str(e)}",
            "query": query,
            "results": [],
        }


# Main execution
async def main():
    """Initializes the knowledge store and runs the MCP server."""
    logger.info("🚀 Starting ZMP Knowledge Store MCP Server...")
    logger.info("📋 Available tools: ingest_documents, search_knowledge")
    logger.info(
        f"⚙️  Configuration: {Config.SERVER_HOST}:{Config.SERVER_PORT} (for reference)"
    )

    # Initialize knowledge store at startup
    logger.info("🔄 Initializing knowledge store...")
    await get_knowledge_store()
    logger.info("✅ Knowledge store initialized successfully.")

    # The `run_async` method should be used within an async context.
    await mcp.run_async(
        transport="streamable-http",
        host=Config.SERVER_HOST,
        port=Config.SERVER_PORT,
        log_level=Config.LOG_LEVEL,
    )


if __name__ == "__main__":
    asyncio.run(main())
