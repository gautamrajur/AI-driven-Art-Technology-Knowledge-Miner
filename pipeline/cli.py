"""
Command-line interface for the art-tech knowledge miner.
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional

import typer
from loguru import logger

from .ingest import WebIngester
from .preprocess import BatchPreprocessor
from .embed_store import EmbeddingStore
from .summarize import ContentSummarizer
from .rag import ArtTechRAG
from .trends import TrendAnalyzer


app = typer.Typer(help="Art & Technology Knowledge Miner CLI")


@app.command()
def crawl(
    queries: List[str] = typer.Option(
        ["artificial intelligence in art", "computer vision museums"],
        "--query", "-q",
        help="Search queries to crawl"
    ),
    max_pages: int = typer.Option(
        20,
        "--max-pages", "-m",
        help="Maximum number of pages to crawl"
    ),
    output_file: Optional[str] = typer.Option(
        None,
        "--output", "-o",
        help="Output file for crawled data (JSON)"
    )
):
    """Crawl web pages for art-technology content."""
    async def _crawl():
        ingester = WebIngester()
        pages = await ingester.search_and_crawl(queries, max_pages)
        
        if output_file:
            import json
            data = [
                {
                    'url': page.url,
                    'title': page.title,
                    'content': page.content,
                    'publish_date': page.publish_date,
                    'domain': page.domain
                }
                for page in pages
            ]
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(pages)} pages to {output_file}")
        else:
            logger.info(f"Crawled {len(pages)} pages")
            for page in pages:
                logger.info(f"- {page.title}: {page.url}")
    
    asyncio.run(_crawl())


@app.command()
def index(
    input_file: str = typer.Argument(..., help="Input file with crawled data (JSON)"),
    collection_name: str = typer.Option(
        "art_tech_knowledge",
        "--collection", "-c",
        help="ChromaDB collection name"
    ),
    chunk_size: int = typer.Option(
        1000,
        "--chunk-size",
        help="Chunk size for text processing"
    ),
    chunk_overlap: int = typer.Option(
        200,
        "--chunk-overlap",
        help="Chunk overlap for text processing"
    )
):
    """Index crawled data into vector store."""
    import json
    
    # Load data
    with open(input_file, 'r') as f:
        documents = json.load(f)
    
    logger.info(f"Loaded {len(documents)} documents from {input_file}")
    
    # Preprocess documents
    preprocessor = BatchPreprocessor(chunk_size, chunk_overlap)
    chunks = preprocessor.process_documents(documents)
    
    # Filter chunks
    chunks = preprocessor.filter_chunks(chunks, min_length=100)
    
    # Create embedding store
    store = EmbeddingStore(collection_name=collection_name)
    
    # Add chunks to store
    added_count = store.add_chunks(chunks)
    
    logger.info(f"Successfully indexed {added_count} chunks")
    
    # Print stats
    stats = store.get_collection_stats()
    logger.info(f"Collection stats: {stats}")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    n_results: int = typer.Option(
        10,
        "--results", "-n",
        help="Number of results to return"
    ),
    collection_name: str = typer.Option(
        "art_tech_knowledge",
        "--collection", "-c",
        help="ChromaDB collection name"
    ),
    hybrid: bool = typer.Option(
        True,
        "--hybrid/--vector-only",
        help="Use hybrid search (vector + keyword)"
    )
):
    """Search the knowledge base."""
    store = EmbeddingStore(collection_name=collection_name)
    
    if hybrid:
        results = store.hybrid_search(query, n_results=n_results)
    else:
        results = store.search(query, n_results=n_results)
    
    logger.info(f"Found {len(results)} results for query: {query}")
    
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        logger.info(f"\n{i}. {metadata.get('title', 'Untitled')}")
        logger.info(f"   URL: {metadata.get('url', 'N/A')}")
        logger.info(f"   Domain: {metadata.get('domain', 'N/A')}")
        logger.info(f"   Content: {result['content'][:200]}...")
        
        if 'combined_score' in result:
            logger.info(f"   Score: {result['combined_score']:.3f}")


@app.command()
def trends(
    facet: str = typer.Option(
        "all",
        "--facet", "-f",
        help="Facet to analyze trends for"
    ),
    from_date: Optional[str] = typer.Option(
        None,
        "--from",
        help="Start date (YYYY-MM-DD)"
    ),
    to_date: Optional[str] = typer.Option(
        None,
        "--to",
        help="End date (YYYY-MM-DD)"
    ),
    granularity: str = typer.Option(
        "year",
        "--granularity", "-g",
        help="Time granularity (year, month, quarter)"
    ),
    collection_name: str = typer.Option(
        "art_tech_knowledge",
        "--collection", "-c",
        help="ChromaDB collection name"
    )
):
    """Analyze trends in the knowledge base."""
    store = EmbeddingStore(collection_name=collection_name)
    analyzer = TrendAnalyzer(store)
    
    # Analyze temporal trends
    trends = analyzer.analyze_temporal_trends(
        facet=facet,
        from_date=from_date,
        to_date=to_date,
        granularity=granularity
    )
    
    logger.info(f"Trend analysis for facet: {facet}")
    logger.info(f"Time range: {from_date or 'start'} to {to_date or 'end'}")
    logger.info(f"Granularity: {granularity}")
    
    if not trends:
        logger.info("No trend data found")
        return
    
    # Print trend data
    for trend in trends:
        logger.info(f"\n{trend.time_period}: {trend.count} documents")
        if trend.trend_slope is not None:
            logger.info(f"  Trend slope: {trend.trend_slope:.3f}")
            logger.info(f"  R-squared: {trend.r_squared:.3f}")
            logger.info(f"  Significance: {trend.trend_significance:.3f}")
    
    # Analyze tag co-occurrence
    cooccurrence = analyzer.analyze_tag_cooccurrence()
    if cooccurrence:
        logger.info(f"\nTop tag co-occurrences:")
        for i, cooc in enumerate(cooccurrence[:10], 1):
            logger.info(f"{i}. {cooc.tag1} + {cooc.tag2}: {cooc.count} occurrences")


@app.command()
def demo(
    collection_name: str = typer.Option(
        "art_tech_knowledge",
        "--collection", "-c",
        help="ChromaDB collection name"
    ),
    openai_api_key: Optional[str] = typer.Option(
        None,
        "--openai-key",
        help="OpenAI API key for RAG demo"
    )
):
    """Run a demonstration of the knowledge miner."""
    store = EmbeddingStore(collection_name=collection_name)
    
    # Check if collection has data
    stats = store.get_collection_stats()
    if stats.get('total_chunks', 0) == 0:
        logger.error("No data found in collection. Please run 'crawl' and 'index' first.")
        return
    
    logger.info(f"Demo with {stats['total_chunks']} chunks in collection")
    
    # Test search
    logger.info("\n=== Search Demo ===")
    test_queries = [
        "artificial intelligence in art",
        "computer vision museums",
        "robotics performance art"
    ]
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        results = store.hybrid_search(query, n_results=3)
        
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            logger.info(f"{i}. {metadata.get('title', 'Untitled')}")
            logger.info(f"   {result['content'][:100]}...")
    
    # Test trends
    logger.info("\n=== Trends Demo ===")
    analyzer = TrendAnalyzer(store)
    trends = analyzer.analyze_temporal_trends()
    
    if trends:
        logger.info("Recent trends:")
        for trend in trends[-5:]:  # Last 5 periods
            logger.info(f"{trend.time_period}: {trend.count} documents")
    
    # Test RAG if API key provided
    if openai_api_key:
        logger.info("\n=== RAG Demo ===")
        rag = ArtTechRAG(store, openai_api_key=openai_api_key)
        
        test_question = "How is artificial intelligence being used in art?"
        response = rag.query(test_question)
        
        logger.info(f"Question: {test_question}")
        logger.info(f"Answer: {response.answer}")
        logger.info(f"Sources: {len(response.sources)}")
        
        for i, source in enumerate(response.sources[:3], 1):
            logger.info(f"{i}. {source['title']} - {source['url']}")
    else:
        logger.info("\n=== RAG Demo (Skipped) ===")
        logger.info("Provide --openai-key to test RAG functionality")


@app.command()
def stats(
    collection_name: str = typer.Option(
        "art_tech_knowledge",
        "--collection", "-c",
        help="ChromaDB collection name"
    )
):
    """Show statistics about the knowledge base."""
    store = EmbeddingStore(collection_name=collection_name)
    stats = store.get_collection_stats()
    
    logger.info("Knowledge Base Statistics:")
    logger.info("=" * 40)
    logger.info(f"Collection: {stats.get('collection_name', 'N/A')}")
    logger.info(f"Total chunks: {stats.get('total_chunks', 0)}")
    logger.info(f"Embedding model: {stats.get('embedding_model', 'N/A')}")
    logger.info(f"Storage directory: {stats.get('persist_directory', 'N/A')}")
    
    # Get sample documents
    try:
        sample_data = store.collection.get(limit=5)
        if sample_data['documents']:
            logger.info(f"\nSample documents:")
            for i, doc in enumerate(sample_data['documents'], 1):
                metadata = sample_data['metadatas'][i-1]
                logger.info(f"{i}. {metadata.get('title', 'Untitled')}")
                logger.info(f"   Domain: {metadata.get('domain', 'N/A')}")
                logger.info(f"   Date: {metadata.get('publish_date', 'N/A')}")
    except Exception as e:
        logger.error(f"Failed to get sample data: {e}")


if __name__ == "__main__":
    app()
