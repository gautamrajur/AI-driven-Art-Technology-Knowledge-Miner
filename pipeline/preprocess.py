"""
Content preprocessing module for chunking and metadata normalization.
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import dateutil.parser

from loguru import logger


@dataclass
class ProcessedChunk:
    """Represents a processed text chunk."""
    content: str
    metadata: Dict
    chunk_id: str
    source_url: str
    chunk_index: int
    total_chunks: int


class ContentPreprocessor:
    """Handles content cleaning, chunking, and metadata normalization."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def clean_content(self, content: str) -> str:
        """Clean and normalize content."""
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove common web artifacts
        content = re.sub(r'\[.*?\]', '', content)  # Remove bracketed text
        content = re.sub(r'\(.*?\)', '', content)  # Remove parenthetical text
        
        # Remove URLs
        content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)
        
        # Remove email addresses
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', content)
        
        # Remove phone numbers
        content = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '', content)
        
        # Remove excessive punctuation
        content = re.sub(r'[.]{3,}', '...', content)
        content = re.sub(r'[!]{2,}', '!', content)
        content = re.sub(r'[?]{2,}', '?', content)
        
        return content.strip()
    
    def chunk_content(self, content: str, metadata: Dict) -> List[ProcessedChunk]:
        """Split content into overlapping chunks."""
        cleaned_content = self.clean_content(content)
        
        if len(cleaned_content) <= self.chunk_size:
            return [ProcessedChunk(
                content=cleaned_content,
                metadata=metadata,
                chunk_id=f"{metadata.get('url', 'unknown')}_0",
                source_url=metadata.get('url', ''),
                chunk_index=0,
                total_chunks=1
            )]
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(cleaned_content):
            end = start + self.chunk_size
            
            # Try to break at sentence boundaries
            if end < len(cleaned_content):
                # Look for sentence endings within the last 200 characters
                search_start = max(start + self.chunk_size - 200, start)
                sentence_end = cleaned_content.rfind('.', search_start, end)
                if sentence_end > start + self.chunk_size // 2:  # Don't make chunks too small
                    end = sentence_end + 1
            
            chunk_content = cleaned_content[start:end].strip()
            
            if chunk_content:
                chunks.append(ProcessedChunk(
                    content=chunk_content,
                    metadata=metadata,
                    chunk_id=f"{metadata.get('url', 'unknown')}_{chunk_index}",
                    source_url=metadata.get('url', ''),
                    chunk_index=chunk_index,
                    total_chunks=0  # Will be updated after all chunks are created
                ))
                chunk_index += 1
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(cleaned_content):
                break
        
        # Update total_chunks for all chunks
        for chunk in chunks:
            chunk.total_chunks = len(chunks)
        
        return chunks
    
    def normalize_metadata(self, metadata: Dict) -> Dict:
        """Normalize and clean metadata."""
        normalized = metadata.copy()
        
        # Normalize date
        if 'publish_date' in normalized and normalized['publish_date']:
            normalized['publish_date'] = self._normalize_date(normalized['publish_date'])
        
        # Normalize title
        if 'title' in normalized:
            normalized['title'] = self._clean_title(normalized['title'])
        
        # Add processing timestamp
        normalized['processed_at'] = datetime.now().isoformat()
        
        # Extract domain from URL
        if 'url' in normalized:
            from urllib.parse import urlparse
            parsed = urlparse(normalized['url'])
            normalized['domain'] = parsed.netloc
        
        return normalized
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date string to ISO format."""
        if not date_str:
            return None
        
        try:
            # Try parsing with dateutil
            parsed_date = dateutil.parser.parse(date_str)
            return parsed_date.strftime('%Y-%m-%d')
        except:
            # Try common formats
            date_formats = [
                '%Y-%m-%d',
                '%Y-%m',
                '%Y',
                '%B %d, %Y',
                '%d %B %Y',
                '%m/%d/%Y',
                '%d/%m/%Y'
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except:
                    continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def _clean_title(self, title: str) -> str:
        """Clean and normalize title."""
        if not title:
            return "Untitled"
        
        # Remove HTML tags
        title = re.sub(r'<[^>]+>', '', title)
        
        # Remove excessive whitespace
        title = re.sub(r'\s+', ' ', title)
        
        # Remove common prefixes/suffixes
        title = title.replace(' | ', ' - ')
        title = title.replace(' :: ', ' - ')
        
        return title.strip()


class BatchPreprocessor:
    """Handles batch preprocessing of multiple documents."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.preprocessor = ContentPreprocessor(chunk_size, chunk_overlap)
    
    def process_documents(self, documents: List[Dict]) -> List[ProcessedChunk]:
        """Process a batch of documents into chunks."""
        all_chunks = []
        
        for doc in documents:
            try:
                # Normalize metadata
                normalized_metadata = self.preprocessor.normalize_metadata(doc)
                
                # Create chunks
                chunks = self.preprocessor.chunk_content(doc['content'], normalized_metadata)
                all_chunks.extend(chunks)
                
                logger.info(f"Processed {doc.get('url', 'unknown')}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Failed to process document {doc.get('url', 'unknown')}: {e}")
                continue
        
        logger.info(f"Total chunks created: {len(all_chunks)}")
        return all_chunks
    
    def filter_chunks(self, chunks: List[ProcessedChunk], min_length: int = 100) -> List[ProcessedChunk]:
        """Filter chunks by minimum length."""
        filtered = [chunk for chunk in chunks if len(chunk.content) >= min_length]
        logger.info(f"Filtered chunks: {len(chunks)} -> {len(filtered)}")
        return filtered


# Utility functions
def extract_keywords(content: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from content using simple frequency analysis."""
    import re
    from collections import Counter
    
    # Simple keyword extraction
    words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
    
    # Filter common stop words
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
        'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these',
        'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
        'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
    }
    
    filtered_words = [word for word in words if word not in stop_words]
    
    # Count and return most common
    word_counts = Counter(filtered_words)
    return [word for word, count in word_counts.most_common(max_keywords)]


def calculate_readability_score(content: str) -> float:
    """Calculate a simple readability score."""
    sentences = re.split(r'[.!?]+', content)
    words = re.findall(r'\b\w+\b', content)
    
    if not sentences or not words:
        return 0.0
    
    avg_sentence_length = len(words) / len(sentences)
    avg_word_length = sum(len(word) for word in words) / len(words)
    
    # Simple readability formula (inverse of complexity)
    readability = 100 - (avg_sentence_length * 0.5) - (avg_word_length * 2)
    return max(0, min(100, readability))


if __name__ == "__main__":
    # Test the preprocessor
    test_content = """
    This is a test document about artificial intelligence in art. 
    It discusses how machine learning algorithms are being used to create 
    new forms of digital art and interactive installations.
    """
    
    preprocessor = ContentPreprocessor()
    chunks = preprocessor.chunk_content(test_content, {'url': 'http://test.com', 'title': 'Test'})
    
    print(f"Created {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i}: {chunk.content[:100]}...")
