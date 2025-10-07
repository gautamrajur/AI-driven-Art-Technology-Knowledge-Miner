"""
Tests for the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "services" in data
    assert "database" in data
    assert "version" in data


def test_search_get():
    """Test search endpoint (GET)."""
    response = client.get("/search", params={"q": "artificial intelligence"})
    assert response.status_code == 200
    
    data = response.json()
    assert "query" in data
    assert "results" in data
    assert "total_results" in data


def test_search_post():
    """Test search endpoint (POST)."""
    response = client.post("/search", json={
        "query": "computer vision",
        "n_results": 5,
        "hybrid": True
    })
    assert response.status_code == 200
    
    data = response.json()
    assert "query" in data
    assert "results" in data
    assert "total_results" in data


def test_trends_get():
    """Test trends endpoint (GET)."""
    response = client.get("/trends")
    assert response.status_code == 200
    
    data = response.json()
    assert "facet" in data
    assert "trends" in data
    assert "cooccurrence" in data


def test_trends_post():
    """Test trends endpoint (POST)."""
    response = client.post("/trends", json={
        "facet": "all",
        "granularity": "year",
        "min_cooccurrence": 2
    })
    assert response.status_code == 200
    
    data = response.json()
    assert "facet" in data
    assert "trends" in data
    assert "cooccurrence" in data


def test_ingest_post():
    """Test ingest endpoint."""
    response = client.post("/ingest", json={
        "queries": ["artificial intelligence art"],
        "max_pages": 5
    })
    assert response.status_code == 200
    
    data = response.json()
    assert "task_id" in data
    assert "status" in data
    assert "message" in data


def test_stats():
    """Test stats endpoint."""
    response = client.get("/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_chunks" in data
    assert "total_documents" in data


if __name__ == "__main__":
    pytest.main([__file__])
