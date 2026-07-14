"""RAG Engine for retrieval and context management."""

import logging
import json
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from app.services.embeddings import get_embeddings_service
from app.services.qdrant_service import QdrantService

logger = logging.getLogger(__name__)


class RAGEngine:
    """Retrieval-Augmented Generation engine for fetching relevant context."""

    def __init__(self, qdrant_service: QdrantService, collection_name: str = "document_embeddings"):
        """Initialize RAG engine."""
        self.qdrant_service = qdrant_service
        self.embeddings_service = get_embeddings_service()
        self.collection_name = collection_name

    def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        user_id: Optional[str] = None,
        source_type: Optional[str] = None,
        score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a query.

        Args:
            query: User's query or topic
            top_k: Number of results to return
            user_id: Optional user ID for filtering
            source_type: Optional source type filter ("user_document" or "internet")
            score_threshold: Minimum similarity score

        Returns:
            List of relevant chunks with metadata and scores
        """
        try:
            # Generate embedding for query
            query_embedding = self.embeddings_service.embed_text(query)
            
            # Build filter conditions if provided
            filter_conditions = {}
            if user_id:
                filter_conditions["user_id"] = str(user_id)
            if source_type:
                filter_conditions["source_type"] = source_type

            # Search in Qdrant
            results = self.qdrant_service.search_vectors(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                limit=top_k,
                score_threshold=score_threshold,
                filter_conditions=filter_conditions if filter_conditions else None
            )

            logger.info(f"✅ Retrieved {len(results)} relevant chunks for query")
            return results

        except Exception as e:
            logger.error(f"❌ Error retrieving context: {e}")
            raise

    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        user_id: Optional[str] = None,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search (keyword + semantic).

        Args:
            query: Search query
            top_k: Number of results
            user_id: Optional user ID
            keyword_weight: Weight for keyword search (0-1)
            semantic_weight: Weight for semantic search (0-1)

        Returns:
            Combined and ranked results
        """
        try:
            # For now, just do semantic search (keyword search would require Elasticsearch or similar)
            # TODO: Implement full-text keyword search with BM25
            results = self.retrieve_context(query, top_k, user_id)
            return results

        except Exception as e:
            logger.error(f"❌ Error in hybrid search: {e}")
            raise

    def combine_context(
        self,
        chunks: List[Dict[str, Any]],
        max_tokens: int = 2000
    ) -> Tuple[str, List[str]]:
        """
        Combine multiple chunks into a single context string.

        Args:
            chunks: List of chunk dictionaries from retrieval
            max_tokens: Maximum tokens for context

        Returns:
            Tuple of (combined_text, source_urls)
        """
        try:
            combined_text = ""
            source_urls = []
            token_count = 0

            for chunk in chunks:
                chunk_text = chunk.get("payload", {}).get("chunk_text", "")
                chunk_tokens = len(chunk_text) // 4  # Rough token estimate

                # Check if adding this chunk would exceed max tokens
                if token_count + chunk_tokens > max_tokens:
                    break

                combined_text += f"{chunk_text}\n\n"
                token_count += chunk_tokens

                # Extract source URL if available
                source_url = chunk.get("payload", {}).get("source_url")
                if source_url and source_url not in source_urls:
                    source_urls.append(source_url)

            logger.info(f"✅ Combined {len(chunks)} chunks into context (~{token_count} tokens)")
            return combined_text, source_urls

        except Exception as e:
            logger.error(f"❌ Error combining context: {e}")
            raise

    def rerank_results(
        self,
        results: List[Dict[str, Any]],
        query: str,
        model: str = "cross-encoder"  # Could use cross-encoder for reranking
    ) -> List[Dict[str, Any]]:
        """
        Re-rank search results for better relevance.

        Args:
            results: Original search results
            query: Original query
            model: Reranking model to use

        Returns:
            Re-ranked results
        """
        # TODO: Implement cross-encoder based reranking
        # For now, return results as-is sorted by score
        return sorted(results, key=lambda x: x.get("score", 0), reverse=True)

    def extract_sources(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract and deduplicate sources from chunks."""
        sources = {}
        for chunk in chunks:
            payload = chunk.get("payload", {})
            source_url = payload.get("source_url")
            source_title = payload.get("source_title")
            
            if source_url:
                if source_url not in sources:
                    sources[source_url] = {
                        "title": source_title or "Unknown",
                        "type": payload.get("source_type", "unknown"),
                        "score": chunk.get("score", 0)
                    }
        return sources
