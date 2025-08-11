from __future__ import annotations
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.handlers.pipeline import pipeline
from src.common.types import PipelineRequest

app = FastAPI(title="Research GNN Agent Local")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/pipeline")
async def run_pipeline(req: PipelineRequest):
    return pipeline(req)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)