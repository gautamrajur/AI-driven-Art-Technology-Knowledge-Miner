"""
FastAPI main application for Art & Technology Knowledge Miner.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import uvicorn

from .models import (
    IngestRequest, IngestResponse, 
    SearchRequest, SearchResponse,
    TrendsRequest, TrendsResponse,
    HealthResponse
)
from .services import IngestService, SearchService, TrendsService
from .config import Settings


# Global services
ingest_service: Optional[IngestService] = None
search_service: Optional[SearchService] = None
trends_service: Optional[TrendsService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global ingest_service, search_service, trends_service
    
    # Startup
    logger.info("Starting Art & Technology Knowledge Miner API")
    
    try:
        settings = Settings()
        
        # Initialize services
        ingest_service = IngestService(settings)
        search_service = SearchService(settings)
        trends_service = TrendsService(settings)
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Art & Technology Knowledge Miner API")


# Create FastAPI app
app = FastAPI(
    title="Art & Technology Knowledge Miner API",
    description="API for mining and exploring art-technology intersections",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/ingest", response_model=IngestResponse)
async def ingest_content(
    request: IngestRequest,
    background_tasks: BackgroundTasks
):
    """Ingest new content into the knowledge base."""
    try:
        if not ingest_service:
            raise HTTPException(status_code=500, detail="Ingest service not initialized")
        
        # Start background ingestion task
        task_id = await ingest_service.start_ingestion(
            queries=request.queries,
            max_pages=request.max_pages
        )
        
        return IngestResponse(
            task_id=task_id,
            status="started",
            message="Ingestion started in background"
        )
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ingest/{task_id}/status")
async def get_ingestion_status(task_id: str):
    """Get the status of an ingestion task."""
    try:
        if not ingest_service:
            raise HTTPException(status_code=500, detail="Ingest service not initialized")
        
        status = await ingest_service.get_task_status(task_id)
        return status
        
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=SearchResponse)
async def search_content(request: SearchRequest):
    """Search the knowledge base."""
    try:
        if not search_service:
            raise HTTPException(status_code=500, detail="Search service not initialized")
        
        results = await search_service.search(
            query=request.query,
            n_results=request.n_results,
            hybrid=request.hybrid
        )
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results)
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search")
async def search_content_get(
    q: str,
    n_results: int = 10,
    hybrid: bool = True
):
    """Search the knowledge base (GET endpoint)."""
    try:
        if not search_service:
            raise HTTPException(status_code=500, detail="Search service not initialized")
        
        results = await search_service.search(
            query=q,
            n_results=n_results,
            hybrid=hybrid
        )
        
        return SearchResponse(
            query=q,
            results=results,
            total_results=len(results)
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/trends", response_model=TrendsResponse)
async def analyze_trends(request: TrendsRequest):
    """Analyze trends in the knowledge base."""
    try:
        if not trends_service:
            raise HTTPException(status_code=500, detail="Trends service not initialized")
        
        trends = await trends_service.analyze_trends(
            facet=request.facet,
            from_date=request.from_date,
            to_date=request.to_date,
            granularity=request.granularity
        )
        
        cooccurrence = await trends_service.analyze_cooccurrence(
            min_cooccurrence=request.min_cooccurrence
        )
        
        return TrendsResponse(
            facet=request.facet,
            trends=trends,
            cooccurrence=cooccurrence
        )
        
    except Exception as e:
        logger.error(f"Trends analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trends")
async def analyze_trends_get(
    facet: str = "all",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    granularity: str = "year",
    min_cooccurrence: int = 2
):
    """Analyze trends in the knowledge base (GET endpoint)."""
    try:
        if not trends_service:
            raise HTTPException(status_code=500, detail="Trends service not initialized")
        
        trends = await trends_service.analyze_trends(
            facet=facet,
            from_date=from_date,
            to_date=to_date,
            granularity=granularity
        )
        
        cooccurrence = await trends_service.analyze_cooccurrence(
            min_cooccurrence=min_cooccurrence
        )
        
        return TrendsResponse(
            facet=facet,
            trends=trends,
            cooccurrence=cooccurrence
        )
        
    except Exception as e:
        logger.error(f"Trends analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check if services are initialized
        services_status = {
            "ingest_service": ingest_service is not None,
            "search_service": search_service is not None,
            "trends_service": trends_service is not None
        }
        
        # Check database connectivity
        db_status = True
        if search_service:
            try:
                stats = search_service.get_stats()
                db_status = stats.get('total_chunks', 0) >= 0
            except:
                db_status = False
        
        overall_status = "healthy" if all(services_status.values()) and db_status else "unhealthy"
        
        return HealthResponse(
            status=overall_status,
            services=services_status,
            database=db_status,
            version="0.1.0"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            services={},
            database=False,
            version="0.1.0"
        )


@app.get("/stats")
async def get_stats():
    """Get knowledge base statistics."""
    try:
        if not search_service:
            raise HTTPException(status_code=500, detail="Search service not initialized")
        
        stats = search_service.get_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
