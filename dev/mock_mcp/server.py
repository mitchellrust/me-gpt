"""Mock MCP server for testing."""

from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Mock MCP Server")


class CompletionRequest(BaseModel):
    """Completion request model."""

    model: str
    input: str
    max_tokens: int = 1024
    stream: bool = False
    temperature: Optional[float] = None


class TokenUsage(BaseModel):
    """Token usage model."""

    prompt: int
    completion: int


class CompletionResponse(BaseModel):
    """Completion response model."""

    id: str
    output: str
    token_usage: TokenUsage


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Mock MCP Server", "version": "0.1.0"}


@app.post("/v1/completions")
async def create_completion(request: CompletionRequest) -> CompletionResponse:
    """Create a completion (mock implementation)."""
    # Simple echo response with mock token usage
    output = f"Mock response to: {request.input}"

    # Calculate mock token usage
    prompt_tokens = len(request.input.split())
    completion_tokens = len(output.split())

    return CompletionResponse(
        id=f"mock-{hash(request.input) % 10000}",
        output=output,
        token_usage=TokenUsage(prompt=prompt_tokens, completion=completion_tokens),
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
