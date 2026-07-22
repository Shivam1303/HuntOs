"""Minimal FastAPI application for the Lead Hunting MVP."""

from fastapi import FastAPI

app = FastAPI(title="Lead Hunting MVP")


@app.get("/health")
def health() -> dict[str, str]:
    """Report that the API process is ready to receive requests."""

    return {"status": "ok"}
