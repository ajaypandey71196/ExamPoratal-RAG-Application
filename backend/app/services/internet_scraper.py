"""Internet scraping service for gathering content from various sources."""

import logging
import json
from typing import List, Dict, Optional
from datetime import datetime
import asyncio

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    logging.warning("Web scraping libraries not installed")

try:
    import wikipedia
except ImportError:
    logging.warning("wikipedia library not installed")

logger = logging.getLogger(__name__)


class InternetScraperService:
    """Service for scraping content from various internet sources."""

    # Headers to avoid blocking
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    # Rate limiting (requests per second)
    RATE_LIMIT_DELAY = 1.0

    @staticmethod
    def search_google(query: str, num_results: int = 5) -> List[Dict]:
        """Search Google and extract URLs and snippets.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of dicts with 'title', 'url', 'snippet'
        """
        try:
            # Using Google's search result page scraping
            # Note: Google blocks automated requests, so this uses alternative approach
            search_url = f"https://www.google.com/search?q={query}"
            
            response = requests.get(search_url, headers=InternetScraperService.HEADERS, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Extract search results
            for item in soup.find_all('div', class_='g')[:num_results]:
                try:
                    title_elem = item.find('h3')
                    link_elem = item.find('a')
                    snippet_elem = item.find('span', class_='VwiC3b')
                    
                    if title_elem and link_elem:
                        results.append({
                            'title': title_elem.get_text(),
                            'url': link_elem.get('href'),
                            'snippet': snippet_elem.get_text() if snippet_elem else '',
                            'source': 'google',
                            'retrieved_at': datetime.utcnow().isoformat()
                        })
                except Exception as e:
                    logger.debug(f"Error parsing search result: {e}")
            
            logger.info(f"Found {len(results)} Google search results for '{query}'")
            return results
        except Exception as e:
            logger.error(f"Error searching Google: {e}")
            return []

    @staticmethod
    def scrape_wikipedia(query: str) -> Optional[Dict]:
        """Scrape Wikipedia article.
        
        Args:
            query: Article search query
            
        Returns:
            Dict with article content or None
        """
        try:
            # Search for the article
            results = wikipedia.search(query, results=1)
            if not results:
                logger.warning(f"No Wikipedia article found for '{query}'")
                return None
            
            # Get the page
            page = wikipedia.page(results[0])
            
            # Extract content
            content = {
                'title': page.title,
                'url': page.url,
                'summary': page.summary[:1000],  # First 1000 chars
                'content': page.content,
                'sections': [],
                'source': 'wikipedia',
                'retrieved_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Successfully scraped Wikipedia article: {page.title}")
            return content
        except Exception as e:
            logger.error(f"Error scraping Wikipedia: {e}")
            return None

    @staticmethod
    def search_arxiv(query: str, num_results: int = 5) -> List[Dict]:
        """Search ArXiv for academic papers.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of dicts with paper metadata
        """
        try:
            import arxiv
            
            # Search arXiv
            client = arxiv.Client()
            search = arxiv.Search(
                query=query,
                max_results=num_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            results = []
            for paper in client.results(search):
                results.append({
                    'title': paper.title,
                    'authors': [author.name for author in paper.authors],
                    'summary': paper.summary[:500],  # First 500 chars
                    'url': paper.entry_id,
                    'published': paper.published.isoformat(),
                    'source': 'arxiv',
                    'retrieved_at': datetime.utcnow().isoformat()
                })
            
            logger.info(f"Found {len(results)} ArXiv papers for '{query}'")
            return results
        except ImportError:
            logger.warning("arxiv library not installed")
            return []
        except Exception as e:
            logger.error(f"Error searching ArXiv: {e}")
            return []

    @staticmethod
    def search_github(query: str, num_results: int = 5) -> List[Dict]:
        """Search GitHub for repositories.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of dicts with repository info
        """
        try:
            api_url = "https://api.github.com/search/repositories"
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': num_results
            }
            
            response = requests.get(api_url, params=params, headers=InternetScraperService.HEADERS, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for repo in data.get('items', []):
                results.append({
                    'name': repo['name'],
                    'url': repo['html_url'],
                    'description': repo['description'] or '',
                    'stars': repo['stargazers_count'],
                    'language': repo['language'] or 'Unknown',
                    'updated_at': repo['updated_at'],
                    'source': 'github',
                    'retrieved_at': datetime.utcnow().isoformat()
                })
            
            logger.info(f"Found {len(results)} GitHub repositories for '{query}'")
            return results
        except Exception as e:
            logger.error(f"Error searching GitHub: {e}")
            return []

    @staticmethod
    def scrape_url(url: str) -> Optional[Dict]:
        """Scrape content from a generic URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dict with page content or None
        """
        try:
            response = requests.get(url, headers=InternetScraperService.HEADERS, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text() if title else ''
            
            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator='\n')
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return {
                'url': url,
                'title': title_text,
                'content': text[:5000],  # First 5000 chars
                'source': 'webpage',
                'retrieved_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {e}")
            return None

    @staticmethod
    def search_multiple_sources(query: str, sources: Optional[List[str]] = None) -> Dict:
        """Search multiple sources simultaneously.
        
        Args:
            query: Search query
            sources: List of sources to search ('google', 'wikipedia', 'arxiv', 'github')
            
        Returns:
            Dict with results from each source
        """
        if sources is None:
            sources = ['google', 'wikipedia', 'arxiv', 'github']
        
        results = {
            'query': query,
            'timestamp': datetime.utcnow().isoformat(),
            'sources': {}
        }
        
        if 'google' in sources:
            results['sources']['google'] = InternetScraperService.search_google(query)
        
        if 'wikipedia' in sources:
            wiki_result = InternetScraperService.scrape_wikipedia(query)
            if wiki_result:
                results['sources']['wikipedia'] = [wiki_result]
        
        if 'arxiv' in sources:
            results['sources']['arxiv'] = InternetScraperService.search_arxiv(query)
        
        if 'github' in sources:
            results['sources']['github'] = InternetScraperService.search_github(query)
        
        logger.info(f"Multi-source search completed for '{query}'")
        return results

    @staticmethod
    def extract_chunks_from_sources(sources_data: List[Dict], chunk_size: int = 500) -> List[Dict]:
        """Convert scraped content to chunks suitable for RAG.
        
        Args:
            sources_data: List of source data dicts
            chunk_size: Target chunk size in tokens (approx)
            
        Returns:
            List of dicts with 'text', 'source_url', 'source_type'
        """
        chunks = []
        
        for source in sources_data:
            # Get the content
            content = source.get('content') or source.get('summary', '')
            
            if not content:
                continue
            
            # Split into chunks
            words = content.split()
            current_chunk = []
            
            for word in words:
                current_chunk.append(word)
                # Rough estimate: 1 token ≈ 4 characters or ~1.3 words
                if len(current_chunk) >= chunk_size / 1.3:
                    chunk_text = ' '.join(current_chunk)
                    chunks.append({
                        'text': chunk_text,
                        'source_url': source.get('url', ''),
                        'source_type': source.get('source', 'unknown'),
                        'title': source.get('title', ''),
                        'retrieved_at': source.get('retrieved_at', '')
                    })
                    current_chunk = []
            
            # Add remaining words as final chunk
            if current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'source_url': source.get('url', ''),
                    'source_type': source.get('source', 'unknown'),
                    'title': source.get('title', ''),
                    'retrieved_at': source.get('retrieved_at', '')
                })
        
        logger.info(f"Extracted {len(chunks)} chunks from {len(sources_data)} sources")
        return chunks


# Singleton instance
_scraper_instance = None


def get_scraper_service() -> InternetScraperService:
    """Get or create singleton scraper service instance."""
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = InternetScraperService()
    return _scraper_instance
