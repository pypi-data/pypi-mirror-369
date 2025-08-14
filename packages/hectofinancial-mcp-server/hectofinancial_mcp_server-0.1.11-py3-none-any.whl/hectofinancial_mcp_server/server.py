from fastmcp import FastMCP

from .core import documents
from .core.document_repository import initialize_repository
from .tools import get_docs, list_docs, search_docs


def main():
    instructions = documents.get("instructions.md", "")
    initialize_repository(documents)

    mcp = FastMCP(
        "hectofinancial-mcp",
        instructions=instructions,
    )

    mcp.tool(list_docs)
    mcp.tool(get_docs)
    mcp.tool(search_docs)

    mcp.run("stdio")
