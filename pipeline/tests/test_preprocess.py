"""
Tests for the preprocess module.
"""

import pytest
from pipeline.preprocess import ContentPreprocessor, ProcessedChunk, BatchPreprocessor


def test_content_preprocessor():
    """Test ContentPreprocessor functionality."""
    preprocessor = ContentPreprocessor(chunk_size=500, chunk_overlap=100)
    
    # Test content cleaning
    dirty_content = "This is a test   with   excessive    whitespace. [Bracketed text] (Parenthetical text) http://example.com"
    cleaned = preprocessor.clean_content(dirty_content)
    
    assert "   " not in cleaned
    assert "[Bracketed text]" not in cleaned
    assert "(Parenthetical text)" not in cleaned
    assert "http://example.com" not in cleaned
    
    # Test chunking
    long_text = "This is a test sentence. " * 100
    chunks = preprocessor.chunk_content(long_text, {'url': 'http://test.com', 'title': 'Test'})
    
    assert len(chunks) > 1
    assert all(isinstance(chunk, ProcessedChunk) for chunk in chunks)
    assert all(chunk.source_url == 'http://test.com' for chunk in chunks)


def test_metadata_normalization():
    """Test metadata normalization."""
    preprocessor = ContentPreprocessor()
    
    metadata = {
        'title': '  Test Title  ',
        'publish_date': '2023-01-15',
        'url': 'https://example.com/page'
    }
    
    normalized = preprocessor.normalize_metadata(metadata)
    
    assert normalized['title'] == 'Test Title'
    assert normalized['publish_date'] == '2023-01-15'
    assert normalized['domain'] == 'example.com'
    assert 'processed_at' in normalized


def test_batch_preprocessor():
    """Test BatchPreprocessor functionality."""
    preprocessor = BatchPreprocessor(chunk_size=500, chunk_overlap=100)
    
    documents = [
        {
            'content': 'This is a test document about art and technology.',
            'url': 'http://test1.com',
            'title': 'Test 1'
        },
        {
            'content': 'Another document discussing AI in creative applications.',
            'url': 'http://test2.com',
            'title': 'Test 2'
        }
    ]
    
    chunks = preprocessor.process_documents(documents)
    
    assert len(chunks) >= 2
    assert all(isinstance(chunk, ProcessedChunk) for chunk in chunks)
    
    # Test filtering
    filtered_chunks = preprocessor.filter_chunks(chunks, min_length=10)
    assert len(filtered_chunks) <= len(chunks)


if __name__ == "__main__":
    pytest.main([__file__])
