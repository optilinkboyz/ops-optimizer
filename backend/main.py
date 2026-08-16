"""
Operations & Supply Chain Optimizer — Backend
================================================
FastAPI application entry point.

Combines:
- Route Optimization (OR-Tools VRP solver)
- Staffing/Capacity Planning (M/M/s queueing theory)
- What-If Scenario Analysis

Author: Andrew Nelson Enoh
Version: 1.0.0
"""
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from routes.route import router as route_router
from routes.scenario import router as scenario_router
from routes.staffing import router as staffing_router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Operations & Supply Chain Optimizer",
    description="""
    A business optimization tool combining:
    
    - **Route Optimization** — minimize delivery distance/cost using OR-Tools VRP solver
    - **Staffing Calculator** — determine optimal staffing using M/M/s queueing theory
    - **What-If Analysis** — test demand scenarios and get staffing recommendations
    
    Built for operations analysts and business decision-makers.
    """,
    version="1.0.0",
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(route_router)
app.include_router(staffing_router)
app.include_router(scenario_router)


class HealthResponse(BaseModel):
    status: str
    version: str
    message: str


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        message="Operations Optimizer API is running."
    )


@app.get("/", tags=["System"], include_in_schema=False)
async def root():
    return {
        "message": "Operations & Supply Chain Optimizer API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True, log_level="info")
