"""
Service layer for the Art & Technology Knowledge Miner API.
"""

import asyncio
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime
from loguru import logger

from .config import Settings
from .models import SearchResult, TrendData, CooccurrenceData

# Import pipeline modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../pipeline'))

from ingest import WebIngester
from preprocess import BatchPreprocessor
from embed_store import EmbeddingStore
from trends import TrendAnalyzer


class IngestService:
    """Service for content ingestion."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.ingester = WebIngester(settings.pipeline_config_path)
        self.preprocessor = BatchPreprocessor()
        self.embedding_store = EmbeddingStore(
            collection_name=settings.collection_name,
            persist_directory=settings.chroma_persist_directory,
            embedding_model=settings.embedding_model
        )
        self.tasks: Dict[str, Dict[str, Any]] = {}
    
    async def start_ingestion(self, queries: List[str], max_pages: int) -> str:
        """Start background ingestion task."""
        task_id = str(uuid.uuid4())
        
        # Initialize task status
        self.tasks[task_id] = {
            'status': 'pending',
            'progress': 0.0,
            'message': 'Task created',
            'result': None,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Start background task
        asyncio.create_task(self._run_ingestion(task_id, queries, max_pages))
        
        return task_id
    
    async def _run_ingestion(self, task_id: str, queries: List[str], max_pages: int):
        """Run the ingestion process."""
        try:
            # Update status
            self._update_task_status(task_id, 'running', 0.1, 'Starting web crawling')
            
            # Crawl web pages
            pages = await self.ingester.search_and_crawl(queries, max_pages)
            
            if not pages:
                self._update_task_status(task_id, 'completed', 1.0, 'No pages found')
                return
            
            # Update status
            self._update_task_status(task_id, 'running', 0.3, f'Crawled {len(pages)} pages, processing content')
            
            # Convert pages to documents
            documents = [
                {
                    'url': page.url,
                    'title': page.title,
                    'content': page.content,
                    'publish_date': page.publish_date,
                    'domain': page.domain
                }
                for page in pages
            ]
            
            # Preprocess documents
            chunks = self.preprocessor.process_documents(documents)
            chunks = self.preprocessor.filter_chunks(chunks, min_length=100)
            
            # Update status
            self._update_task_status(task_id, 'running', 0.7, f'Created {len(chunks)} chunks, indexing')
            
            # Add to vector store
            added_count = self.embedding_store.add_chunks(chunks)
            
            # Update status
            self._update_task_status(
                task_id, 
                'completed', 
                1.0, 
                f'Successfully indexed {added_count} chunks from {len(pages)} pages'
            )
            
            # Store result
            self.tasks[task_id]['result'] = {
                'pages_crawled': len(pages),
                'chunks_created': len(chunks),
                'chunks_indexed': added_count,
                'queries': queries
            }
            
        except Exception as e:
            logger.error(f"Ingestion task {task_id} failed: {e}")
            self._update_task_status(task_id, 'failed', None, f'Task failed: {str(e)}')
    
    def _update_task_status(self, task_id: str, status: str, progress: Optional[float], message: str):
        """Update task status."""
        if task_id in self.tasks:
            self.tasks[task_id].update({
                'status': status,
                'progress': progress,
                'message': message,
                'updated_at': datetime.now()
            })
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        return self.tasks[task_id]


class SearchService:
    """Service for content search."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.embedding_store = EmbeddingStore(
            collection_name=settings.collection_name,
            persist_directory=settings.chroma_persist_directory,
            embedding_model=settings.embedding_model
        )
    
    async def search(self, query: str, n_results: int = 10, hybrid: bool = True) -> List[SearchResult]:
        """Search the knowledge base."""
        try:
            if hybrid:
                results = self.embedding_store.hybrid_search(query, n_results=n_results)
            else:
                results = self.embedding_store.search(query, n_results=n_results)
            
            # Convert to SearchResult objects
            search_results = []
            for result in results:
                metadata = result['metadata']
                search_results.append(SearchResult(
                    content=result['content'],
                    title=metadata.get('title', 'Untitled'),
                    url=metadata.get('url', ''),
                    domain=metadata.get('domain', ''),
                    publish_date=metadata.get('publish_date'),
                    relevance_score=result.get('combined_score', result.get('distance', 0)),
                    chunk_index=metadata.get('chunk_index', 0),
                    total_chunks=metadata.get('total_chunks', 1)
                ))
            
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        try:
            stats = self.embedding_store.get_collection_stats()
            
            # Get additional stats
            all_data = self.embedding_store.collection.get()
            unique_domains = set()
            unique_dates = set()
            
            for metadata in all_data['metadatas']:
                if metadata.get('domain'):
                    unique_domains.add(metadata['domain'])
                if metadata.get('publish_date'):
                    unique_dates.add(metadata['publish_date'])
            
            return {
                'total_chunks': stats.get('total_chunks', 0),
                'total_documents': len(unique_domains),
                'collection_name': stats.get('collection_name', ''),
                'embedding_model': stats.get('embedding_model', ''),
                'unique_domains': len(unique_domains),
                'date_range': {
                    'min': min(unique_dates) if unique_dates else None,
                    'max': max(unique_dates) if unique_dates else None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}


class TrendsService:
    """Service for trend analysis."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.embedding_store = EmbeddingStore(
            collection_name=settings.collection_name,
            persist_directory=settings.chroma_persist_directory,
            embedding_model=settings.embedding_model
        )
        self.trend_analyzer = TrendAnalyzer(self.embedding_store)
    
    async def analyze_trends(self, 
                           facet: str = "all",
                           from_date: Optional[str] = None,
                           to_date: Optional[str] = None,
                           granularity: str = "year") -> List[TrendData]:
        """Analyze temporal trends."""
        try:
            trends = self.trend_analyzer.analyze_temporal_trends(
                facet=facet,
                from_date=from_date,
                to_date=to_date,
                granularity=granularity
            )
            
            # Convert to TrendData objects
            trend_data = []
            for trend in trends:
                trend_data.append(TrendData(
                    time_period=trend.time_period,
                    count=trend.count,
                    trend_slope=trend.trend_slope,
                    trend_significance=trend.trend_significance,
                    r_squared=trend.r_squared
                ))
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            raise
    
    async def analyze_cooccurrence(self, min_cooccurrence: int = 2) -> List[CooccurrenceData]:
        """Analyze tag co-occurrence."""
        try:
            cooccurrence = self.trend_analyzer.analyze_tag_cooccurrence(
                min_cooccurrence=min_cooccurrence
            )
            
            # Convert to CooccurrenceData objects
            cooccurrence_data = []
            for cooc in cooccurrence:
                cooccurrence_data.append(CooccurrenceData(
                    tag1=cooc.tag1,
                    tag2=cooc.tag2,
                    count=cooc.count,
                    correlation=cooc.correlation
                ))
            
            return cooccurrence_data
            
        except Exception as e:
            logger.error(f"Co-occurrence analysis failed: {e}")
            raise
