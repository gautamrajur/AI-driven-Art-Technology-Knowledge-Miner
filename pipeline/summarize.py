"""
Content summarization module using Hugging Face transformers.
"""

import asyncio
from typing import List, Dict, Optional, Union
from dataclasses import dataclass

import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from loguru import logger

from .preprocess import ProcessedChunk


@dataclass
class Summary:
    """Represents a generated summary."""
    content: str
    source_chunks: List[str]
    confidence_score: Optional[float] = None
    model_used: Optional[str] = None


class ContentSummarizer:
    """Handles content summarization using various models."""
    
    def __init__(self, 
                 model_name: str = "facebook/bart-large-cnn",
                 max_length: int = 150,
                 min_length: int = 30,
                 device: Optional[str] = None):
        self.model_name = model_name
        self.max_length = max_length
        self.min_length = min_length
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize the summarization pipeline
        self.summarizer = None
        self._initialize_model()
        
        logger.info(f"Initialized ContentSummarizer with model: {model_name}")
        logger.info(f"Device: {self.device}")
    
    def _initialize_model(self):
        """Initialize the summarization model."""
        try:
            self.summarizer = pipeline(
                "summarization",
                model=self.model_name,
                device=0 if self.device == "cuda" else -1,
                max_length=self.max_length,
                min_length=self.min_length
            )
            logger.info(f"Successfully loaded model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            # Fallback to a smaller model
            try:
                self.summarizer = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn",
                    device=0 if self.device == "cuda" else -1,
                    max_length=self.max_length,
                    min_length=self.min_length
                )
                logger.info("Fallback to facebook/bart-large-cnn successful")
            except Exception as e2:
                logger.error(f"Fallback model also failed: {e2}")
                self.summarizer = None
    
    def summarize_text(self, text: str) -> Optional[Summary]:
        """Summarize a single text."""
        if not self.summarizer or not text.strip():
            return None
        
        try:
            # Truncate text if too long (most models have input limits)
            max_input_length = 1024  # Conservative limit
            if len(text) > max_input_length:
                text = text[:max_input_length]
            
            result = self.summarizer(text, max_length=self.max_length, min_length=self.min_length)
            
            if result and len(result) > 0:
                summary_text = result[0]['summary_text']
                confidence = result[0].get('score', None)
                
                return Summary(
                    content=summary_text,
                    source_chunks=[text],
                    confidence_score=confidence,
                    model_used=self.model_name
                )
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return None
    
    def summarize_chunks(self, chunks: List[ProcessedChunk]) -> Optional[Summary]:
        """Summarize multiple chunks."""
        if not chunks:
            return None
        
        # Combine chunks
        combined_text = " ".join(chunk.content for chunk in chunks)
        
        # Summarize
        summary = self.summarize_text(combined_text)
        if summary:
            summary.source_chunks = [chunk.content for chunk in chunks]
        
        return summary
    
    def batch_summarize(self, texts: List[str], batch_size: int = 4) -> List[Optional[Summary]]:
        """Summarize multiple texts in batches."""
        if not self.summarizer:
            return [None] * len(texts)
        
        summaries = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            try:
                # Process batch
                results = self.summarizer(
                    batch_texts,
                    max_length=self.max_length,
                    min_length=self.min_length,
                    batch_size=len(batch_texts)
                )
                
                # Convert results to Summary objects
                for j, result in enumerate(results):
                    if result and len(result) > 0:
                        summary_text = result[0]['summary_text']
                        confidence = result[0].get('score', None)
                        
                        summaries.append(Summary(
                            content=summary_text,
                            source_chunks=[batch_texts[j]],
                            confidence_score=confidence,
                            model_used=self.model_name
                        ))
                    else:
                        summaries.append(None)
                
                logger.info(f"Processed batch {i//batch_size + 1}: {len(batch_texts)} texts")
                
            except Exception as e:
                logger.error(f"Batch summarization failed for batch {i//batch_size + 1}: {e}")
                summaries.extend([None] * len(batch_texts))
        
        return summaries


class MapReduceSummarizer:
    """Map-reduce summarization for very long documents."""
    
    def __init__(self, 
                 summarizer: ContentSummarizer,
                 chunk_size: int = 1000,
                 overlap: int = 200):
        self.summarizer = summarizer
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def summarize_long_document(self, text: str) -> Optional[Summary]:
        """Summarize a very long document using map-reduce approach."""
        if not text.strip():
            return None
        
        # Step 1: Split into chunks
        chunks = self._split_into_chunks(text)
        
        if len(chunks) == 1:
            # Short enough for direct summarization
            return self.summarizer.summarize_text(text)
        
        # Step 2: Summarize each chunk (map)
        chunk_summaries = []
        for chunk in chunks:
            summary = self.summarizer.summarize_text(chunk)
            if summary:
                chunk_summaries.append(summary.content)
        
        if not chunk_summaries:
            return None
        
        # Step 3: Combine summaries
        combined_summaries = " ".join(chunk_summaries)
        
        # Step 4: Summarize the combined summaries (reduce)
        final_summary = self.summarizer.summarize_text(combined_summaries)
        
        if final_summary:
            final_summary.source_chunks = chunks
        
        return final_summary
    
    def _split_into_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                sentence_end = text.rfind('.', start + self.chunk_size - 200, end)
                if sentence_end > start + self.chunk_size // 2:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.overlap
            if start >= len(text):
                break
        
        return chunks


class MultiModelSummarizer:
    """Summarizer that can use multiple models and select the best result."""
    
    def __init__(self, model_names: List[str] = None):
        self.model_names = model_names or [
            "facebook/bart-large-cnn",
            "google/pegasus-xsum",
            "t5-small"
        ]
        self.summarizers = []
        
        # Initialize all models
        for model_name in self.model_names:
            try:
                summarizer = ContentSummarizer(model_name=model_name)
                if summarizer.summarizer:
                    self.summarizers.append(summarizer)
                    logger.info(f"Successfully initialized: {model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize {model_name}: {e}")
        
        logger.info(f"Initialized {len(self.summarizers)} summarizers")
    
    def summarize_with_best_model(self, text: str) -> Optional[Summary]:
        """Summarize using the best available model."""
        if not self.summarizers:
            return None
        
        # Try each model and return the first successful result
        for summarizer in self.summarizers:
            try:
                summary = summarizer.summarize_text(text)
                if summary:
                    return summary
            except Exception as e:
                logger.warning(f"Summarization failed with {summarizer.model_name}: {e}")
                continue
        
        return None


# Utility functions
def extract_key_sentences(text: str, num_sentences: int = 3) -> List[str]:
    """Extract key sentences using simple heuristics."""
    import re
    
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= num_sentences:
        return sentences
    
    # Simple scoring based on length and position
    scored_sentences = []
    for i, sentence in enumerate(sentences):
        score = len(sentence) * 0.5  # Longer sentences
        score += (len(sentences) - i) * 0.3  # Earlier sentences
        scored_sentences.append((score, sentence))
    
    # Sort by score and return top sentences
    scored_sentences.sort(key=lambda x: x[0], reverse=True)
    return [sentence for _, sentence in scored_sentences[:num_sentences]]


def calculate_summary_quality(summary: str, original: str) -> float:
    """Calculate a simple quality score for a summary."""
    if not summary or not original:
        return 0.0
    
    # Compression ratio (should be reasonable)
    compression_ratio = len(summary) / len(original)
    
    # Coverage (how many words from original appear in summary)
    original_words = set(original.lower().split())
    summary_words = set(summary.lower().split())
    coverage = len(original_words.intersection(summary_words)) / len(original_words)
    
    # Combine metrics
    quality_score = coverage * 0.7 + (1 - abs(compression_ratio - 0.1)) * 0.3
    return min(1.0, max(0.0, quality_score))


if __name__ == "__main__":
    # Test the summarizer
    test_text = """
    Artificial intelligence is revolutionizing the art world in unprecedented ways. 
    Artists are using machine learning algorithms to create new forms of digital art, 
    while museums are implementing computer vision systems to enhance visitor experiences. 
    The intersection of technology and creativity is producing innovative installations 
    that challenge traditional notions of artistic expression.
    """
    
    summarizer = ContentSummarizer()
    summary = summarizer.summarize_text(test_text)
    
    if summary:
        print(f"Summary: {summary.content}")
        print(f"Model: {summary.model_used}")
        print(f"Confidence: {summary.confidence_score}")
    else:
        print("Summarization failed")
