"""
Pydantic models for the Art & Technology Knowledge Miner API.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    """Request model for content ingestion."""
    queries: List[str] = Field(..., description="Search queries to crawl")
    max_pages: int = Field(10, ge=1, le=100, description="Maximum pages to crawl per query")


class IngestResponse(BaseModel):
    """Response model for content ingestion."""
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Task status")
    message: str = Field(..., description="Status message")


class TaskStatus(BaseModel):
    """Task status model."""
    task_id: str
    status: str  # pending, running, completed, failed
    progress: Optional[float] = None  # 0.0 to 1.0
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class SearchRequest(BaseModel):
    """Request model for content search."""
    query: str = Field(..., description="Search query")
    n_results: int = Field(10, ge=1, le=100, description="Number of results to return")
    hybrid: bool = Field(True, description="Use hybrid search (vector + keyword)")


class SearchResult(BaseModel):
    """Individual search result."""
    content: str = Field(..., description="Content text")
    title: str = Field(..., description="Document title")
    url: str = Field(..., description="Source URL")
    domain: str = Field(..., description="Source domain")
    publish_date: Optional[str] = Field(None, description="Publication date")
    relevance_score: float = Field(..., description="Relevance score")
    chunk_index: int = Field(..., description="Chunk index within document")
    total_chunks: int = Field(..., description="Total chunks in document")


class SearchResponse(BaseModel):
    """Response model for content search."""
    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")


class TrendsRequest(BaseModel):
    """Request model for trend analysis."""
    facet: str = Field("all", description="Facet to analyze trends for")
    from_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    to_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    granularity: str = Field("year", description="Time granularity (year, month, quarter)")
    min_cooccurrence: int = Field(2, ge=1, description="Minimum co-occurrence count")


class TrendData(BaseModel):
    """Individual trend data point."""
    time_period: str = Field(..., description="Time period")
    count: int = Field(..., description="Document count")
    trend_slope: Optional[float] = Field(None, description="Trend slope")
    trend_significance: Optional[float] = Field(None, description="Statistical significance")
    r_squared: Optional[float] = Field(None, description="R-squared value")


class CooccurrenceData(BaseModel):
    """Tag co-occurrence data."""
    tag1: str = Field(..., description="First tag")
    tag2: str = Field(..., description="Second tag")
    count: int = Field(..., description="Co-occurrence count")
    correlation: Optional[float] = Field(None, description="Correlation coefficient")


class TrendsResponse(BaseModel):
    """Response model for trend analysis."""
    facet: str = Field(..., description="Analyzed facet")
    trends: List[TrendData] = Field(..., description="Trend data points")
    cooccurrence: List[CooccurrenceData] = Field(..., description="Tag co-occurrence data")


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Overall health status")
    services: Dict[str, bool] = Field(..., description="Service status")
    database: bool = Field(..., description="Database connectivity")
    version: str = Field(..., description="API version")


class StatsResponse(BaseModel):
    """Statistics response model."""
    total_chunks: int = Field(..., description="Total number of chunks")
    total_documents: int = Field(..., description="Total number of documents")
    collection_name: str = Field(..., description="Collection name")
    embedding_model: str = Field(..., description="Embedding model used")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")


# Error models
class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


# RAG models (for future use)
class RAGRequest(BaseModel):
    """Request model for RAG queries."""
    question: str = Field(..., description="Question to answer")
    n_sources: int = Field(5, ge=1, le=20, description="Number of sources to use")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")


class RAGResponse(BaseModel):
    """Response model for RAG queries."""
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="Generated answer")
    sources: List[SearchResult] = Field(..., description="Source documents")
    confidence_score: Optional[float] = Field(None, description="Confidence score")
