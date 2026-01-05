"""Main entry point for running the Holon Engine server."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "holon_engine.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
