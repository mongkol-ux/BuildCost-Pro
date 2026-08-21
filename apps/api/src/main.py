"""BuildCost Pro API bootstrap.

First executable vertical slice: a deterministic health endpoint and
configuration boundary. Business modules are intentionally kept out of this
bootstrap so they can be added behind explicit contracts.
"""

from fastapi import FastAPI

app = FastAPI(title="BuildCost Pro API", version="1.0.0")


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "buildcost-pro-api", "version": "1.0.0"}
