import os
import json
import httpx
from fastmcp import FastMCP


COPY_AI_API_KEY = os.getenv("COPY_AI_API_KEY")
COPY_AI_BASE_URL = "https://api.copy.ai/api"

if not COPY_AI_API_KEY:
    raise ValueError("COPY_AI_API_KEY environment variable is required")

# Create an HTTP client for your API
client = httpx.AsyncClient(
    base_url=COPY_AI_BASE_URL,
    headers={
        "x-copy-ai-api-key": COPY_AI_API_KEY
    }
)

# Load your OpenAPI spec
with open(os.path.join(os.path.dirname(__file__), 'schema.json'), ) as f:
    openapi_spec = json.load(f)

# Create the MCP server
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="COpy.ai MCP Server"
)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
