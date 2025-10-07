"""
Web content ingestion module for art-tech knowledge mining.
Handles DuckDuckGo search, respectful crawling, and content extraction.
"""

import asyncio
import hashlib
import time
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass

import httpx
import yaml
from duckduckgo_search import DDGS
from loguru import logger
from robotexclusionrulesparser import RobotExclusionRulesParser
from trafilatura import extract

# Configuration loading function will be defined below


@dataclass
class WebPage:
    """Represents a crawled web page."""
    url: str
    title: str
    content: str
    publish_date: Optional[str] = None
    domain: Optional[str] = None
    content_hash: Optional[str] = None
    
    def __post_init__(self):
        if self.domain is None:
            self.domain = urlparse(self.url).netloc
        if self.content_hash is None:
            self.content_hash = hashlib.md5(self.content.encode()).hexdigest()


class ContentFilter:
    """Filters content based on art-tech relevance."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.art_terms = set(term.lower() for term in config['art_terms'])
        self.tech_terms = set(term.lower() for term in config['tech_terms'])
        self.filters = config['content_filters']
    
    def is_relevant(self, content: str) -> bool:
        """Check if content contains both art and tech terms."""
        content_lower = content.lower()
        
        # Check minimum/maximum length
        if len(content) < self.filters['min_content_length']:
            return False
        if len(content) > self.filters['max_content_length']:
            return False
        
        # Count art and tech terms
        art_count = sum(1 for term in self.art_terms if term in content_lower)
        tech_count = sum(1 for term in self.tech_terms if term in content_lower)
        
        if self.filters['require_both_art_and_tech']:
            return (art_count >= self.filters['min_art_terms'] and 
                   tech_count >= self.filters['min_tech_terms'])
        
        return art_count >= self.filters['min_art_terms'] or tech_count >= self.filters['min_tech_terms']


class RobotsChecker:
    """Checks robots.txt compliance."""
    
    def __init__(self):
        self.parser = RobotExclusionRulesParser()
        self.cache: Dict[str, bool] = {}
    
    async def can_crawl(self, url: str, user_agent: str) -> bool:
        """Check if URL can be crawled according to robots.txt."""
        domain = urlparse(url).netloc
        
        if domain in self.cache:
            return self.cache[domain]
        
        try:
            robots_url = f"https://{domain}/robots.txt"
            async with httpx.AsyncClient() as client:
                response = await client.get(robots_url, timeout=10)
                if response.status_code == 200:
                    self.parser.set_url(robots_url)
                    self.parser.read(response.text)
                    can_crawl = self.parser.can_fetch(user_agent, url)
                    self.cache[domain] = can_crawl
                    return can_crawl
        except Exception as e:
            logger.warning(f"Failed to check robots.txt for {domain}: {e}")
        
        # Default to allowing if robots.txt is not accessible
        self.cache[domain] = True
        return True


class WebIngester:
    """Main web ingestion class."""
    
    def __init__(self, config_path: str = "pipeline/config/terms.yaml"):
        self.config = load_config(config_path)
        self.crawl_config = self.config['crawl_config']
        self.content_filter = ContentFilter(self.config)
        self.robots_checker = RobotsChecker()
        self.seen_urls: Set[str] = set()
        self.seen_hashes: Set[str] = set()
    
    async def search_and_crawl(self, queries: List[str], max_pages: Optional[int] = None) -> List[WebPage]:
        """Search for queries and crawl relevant pages."""
        max_pages = max_pages or self.crawl_config['max_total_pages']
        pages: List[WebPage] = []
        
        logger.info(f"Starting ingestion with {len(queries)} queries, max {max_pages} pages")
        
        for query in queries:
            if len(pages) >= max_pages:
                break
                
            logger.info(f"Searching for: {query}")
            search_results = await self._search_query(query)
            
            for result in search_results:
                if len(pages) >= max_pages:
                    break
                    
                if result['href'] in self.seen_urls:
                    continue
                
                page = await self._crawl_page(result['href'], result.get('title', ''))
                if page and self.content_filter.is_relevant(page.content):
                    pages.append(page)
                    self.seen_urls.add(page.url)
                    self.seen_hashes.add(page.content_hash)
                    logger.info(f"Added page: {page.title[:50]}...")
                
                # Respectful delay
                await asyncio.sleep(self.crawl_config['request_delay'])
        
        logger.info(f"Ingestion complete: {len(pages)} pages collected")
        return pages
    
    async def _search_query(self, query: str) -> List[Dict]:
        """Search DuckDuckGo for a query."""
        try:
            ddgs = DDGS()
            results = []
            
            for result in ddgs.text(query, max_results=self.crawl_config['max_pages_per_query']):
                results.append({
                    'title': result.get('title', ''),
                    'href': result.get('href', ''),
                    'body': result.get('body', '')
                })
            
            return results
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            return []
    
    async def _crawl_page(self, url: str, title: str) -> Optional[WebPage]:
        """Crawl a single page and extract content."""
        try:
            # Check robots.txt compliance
            if self.crawl_config['respect_robots_txt']:
                can_crawl = await self.robots_checker.can_crawl(url, self.crawl_config['user_agent'])
                if not can_crawl:
                    logger.info(f"Skipping {url} due to robots.txt")
                    return None
            
            # Fetch page content
            async with httpx.AsyncClient(
                timeout=self.crawl_config['timeout'],
                headers={'User-Agent': self.crawl_config['user_agent']}
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Extract content using trafilatura
                content = extract(response.text, include_comments=False, include_tables=True)
                
                if not content:
                    logger.warning(f"No content extracted from {url}")
                    return None
                
                # Extract publish date (simplified)
                publish_date = self._extract_publish_date(response.text)
                
                return WebPage(
                    url=url,
                    title=title or self._extract_title(response.text),
                    content=content,
                    publish_date=publish_date
                )
                
        except Exception as e:
            logger.error(f"Failed to crawl {url}: {e}")
            return None
    
    def _extract_title(self, html: str) -> str:
        """Extract title from HTML."""
        import re
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if title_match:
            return title_match.group(1).strip()
        return "Untitled"
    
    def _extract_publish_date(self, html: str) -> Optional[str]:
        """Extract publish date from HTML (simplified)."""
        import re
        from datetime import datetime
        
        # Look for common date patterns
        date_patterns = [
            r'<meta[^>]*property="article:published_time"[^>]*content="([^"]*)"',
            r'<meta[^>]*name="date"[^>]*content="([^"]*)"',
            r'<meta[^>]*name="pubdate"[^>]*content="([^"]*)"',
            r'<time[^>]*datetime="([^"]*)"',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(1)
                    # Try to parse and normalize the date
                    parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    return parsed_date.strftime('%Y-%m-%d')
                except:
                    continue
        
        return None


def load_config(config_path: str) -> Dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
        return {}


# CLI interface
async def main():
    """CLI entry point for ingestion."""
    ingester = WebIngester()
    queries = ["artificial intelligence in art", "computer vision museums"]
    pages = await ingester.search_and_crawl(queries, max_pages=20)
    
    print(f"Collected {len(pages)} pages:")
    for page in pages:
        print(f"- {page.title}: {page.url}")


if __name__ == "__main__":
    asyncio.run(main())


def load_config(config_path: str = "pipeline/config/terms.yaml"):
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
        return {}
