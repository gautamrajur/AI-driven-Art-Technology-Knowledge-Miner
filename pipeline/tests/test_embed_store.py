"""
Tests for the embed_store module.
"""

import pytest
import tempfile
import shutil
from pipeline.embed_store import EmbeddingStore
from pipeline.preprocess import ProcessedChunk


@pytest.fixture
def temp_store():
    """Create a temporary embedding store for testing."""
    temp_dir = tempfile.mkdtemp()
    store = EmbeddingStore(
        collection_name="test_collection",
        persist_directory=temp_dir
    )
    yield store
    shutil.rmtree(temp_dir)


def test_embedding_store_creation(temp_store):
    """Test EmbeddingStore creation."""
    assert temp_store.collection_name == "test_collection"
    assert temp_store.embedding_model_name == "sentence-transformers/all-MiniLM-L6-v2"


def test_add_chunks(temp_store):
    """Test adding chunks to the store."""
    chunks = [
        ProcessedChunk(
            content="This is a test document about art and technology.",
            metadata={'url': 'http://test.com', 'title': 'Test'},
            chunk_id="test_0",
            source_url="http://test.com",
            chunk_index=0,
            total_chunks=1
        )
    ]
    
    added_count = temp_store.add_chunks(chunks)
    assert added_count == 1
    
    stats = temp_store.get_collection_stats()
    assert stats['total_chunks'] == 1


def test_search(temp_store):
    """Test search functionality."""
    # Add test chunks
    chunks = [
        ProcessedChunk(
            content="Artificial intelligence is revolutionizing art creation.",
            metadata={'url': 'http://test1.com', 'title': 'AI Art'},
            chunk_id="test1_0",
            source_url="http://test1.com",
            chunk_index=0,
            total_chunks=1
        ),
        ProcessedChunk(
            content="Computer vision helps museums analyze visitor behavior.",
            metadata={'url': 'http://test2.com', 'title': 'Museum Tech'},
            chunk_id="test2_0",
            source_url="http://test2.com",
            chunk_index=0,
            total_chunks=1
        )
    ]
    
    temp_store.add_chunks(chunks)
    
    # Test vector search
    results = temp_store.search("artificial intelligence", n_results=2)
    assert len(results) >= 1
    assert "artificial intelligence" in results[0]['content'].lower()
    
    # Test hybrid search
    hybrid_results = temp_store.hybrid_search("computer vision", n_results=2)
    assert len(hybrid_results) >= 1


def test_collection_stats(temp_store):
    """Test collection statistics."""
    stats = temp_store.get_collection_stats()
    assert 'total_chunks' in stats
    assert 'collection_name' in stats
    assert 'embedding_model' in stats


if __name__ == "__main__":
    pytest.main([__file__])
