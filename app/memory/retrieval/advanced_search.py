"""
Advanced memory search with vector-based semantic capabilities.

Provides semantic similarity search using embeddings (mock) and ranking.
Enhances memory retrieval with context-aware matching.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import math
import logging


logger = logging.getLogger(__name__)


@dataclass
class MemoryItem:
    """Represents searchable memory item."""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict] = None
    relevance_score: float = 0.0


class EmbeddingGenerator:
    """Generates simple embeddings for text (mock implementation)."""

    def __init__(self, dimension: int = 128):
        """Initialize embedding generator.

        Args:
            dimension: Dimension of embedding vectors
        """
        self.dimension = dimension

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text.

        Note: This is a mock implementation using simple hashing.
        In production, use actual embeddings (e.g., sentence-transformers)

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        # Simple hash-based embedding (deterministic, fast)
        embedding = []
        text_lower = text.lower()

        for i in range(self.dimension):
            # Use hash and character frequencies
            seed = i * 73 + 17  # Prime numbers for variation
            hash_val = seed

            for j, char in enumerate(text_lower):
                hash_val = (hash_val * 31 + ord(char) + j) % (2**31)

            # Normalize to 0-1
            normalized = (hash_val % 1000) / 1000.0
            embedding.append(normalized * 2.0 - 1.0)  # Scale to -1 to 1

        # L2 normalize
        norm = math.sqrt(sum(x**2 for x in embedding))
        if norm > 0:
            embedding = [x / norm for x in embedding]

        return embedding

    def batch_generate(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts

        Returns:
            List of embeddings
        """
        return [self.generate_embedding(text) for text in texts]


class SemanticSearchEngine:
    """Performs semantic search using vector similarity."""

    def __init__(self, embedding_dim: int = 128):
        """Initialize semantic search engine.

        Args:
            embedding_dim: Dimension of embeddings
        """
        self.embedder = EmbeddingGenerator(embedding_dim)
        self.memory_items: List[MemoryItem] = []

    def index_memory(self, items: List[MemoryItem]) -> None:
        """Index memory items for search.

        Args:
            items: Memory items to index
        """
        for item in items:
            if not item.embedding:
                item.embedding = self.embedder.generate_embedding(item.content)
        self.memory_items = items

    def search_semantic(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.3
    ) -> List[MemoryItem]:
        """Perform semantic search.

        Args:
            query: Search query
            top_k: Number of top results
            score_threshold: Minimum similarity score

        Returns:
            Ranked list of memory items
        """
        if not self.memory_items:
            return []

        # Generate query embedding
        query_embedding = self.embedder.generate_embedding(query)

        # Calculate similarities
        results = []
        for item in self.memory_items:
            if not item.embedding:
                item.embedding = self.embedder.generate_embedding(item.content)

            similarity = self._cosine_similarity(query_embedding, item.embedding)

            if similarity >= score_threshold:
                item.relevance_score = similarity
                results.append(item)

        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        return results[:top_k]

    def search_hybrid(
        self,
        query: str,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.7,
        top_k: int = 5
    ) -> List[MemoryItem]:
        """Perform hybrid search (keyword + semantic).

        Args:
            query: Search query
            keyword_weight: Weight for keyword matching (0-1)
            semantic_weight: Weight for semantic matching (0-1)
            top_k: Number of top results

        Returns:
            Ranked list of memory items
        """
        if not self.memory_items:
            return []

        results = {}

        # Keyword search
        query_lower = query.lower()
        for item in self.memory_items:
            keyword_score = self._keyword_relevance(query_lower, item.content)
            if keyword_score > 0:
                results[item.id] = keyword_score * keyword_weight

        # Semantic search
        semantic_results = self.search_semantic(query, top_k=len(self.memory_items))
        for item in semantic_results:
            current_score = results.get(item.id, 0.0)
            results[item.id] = current_score + (item.relevance_score * semantic_weight)

        # Convert to sorted list
        scored_items = []
        for item in self.memory_items:
            if item.id in results:
                item.relevance_score = results[item.id]
                scored_items.append(item)

        scored_items.sort(key=lambda x: x.relevance_score, reverse=True)

        return scored_items[:top_k]

    def search_contextual(
        self,
        query: str,
        context_items: Optional[List[MemoryItem]] = None,
        top_k: int = 5
    ) -> List[MemoryItem]:
        """Search with optional context.

        Args:
            query: Search query
            context_items: Optional context memory items
            top_k: Number of top results

        Returns:
            Ranked list of memory items
        """
        # Enhance query with context
        if context_items:
            context_text = " ".join(item.content for item in context_items)
            enhanced_query = f"{query} {context_text}"
        else:
            enhanced_query = query

        # Perform semantic search with enhanced query
        return self.search_semantic(enhanced_query, top_k)

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between vectors.

        Args:
            a: First vector
            b: Second vector

        Returns:
            Similarity score (0-1)
        """
        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = math.sqrt(sum(x**2 for x in a))
        magnitude_b = math.sqrt(sum(x**2 for x in b))

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return (dot_product + 1) / (magnitude_a * magnitude_b + 1)  # Normalize to 0-1

    @staticmethod
    def _keyword_relevance(query: str, text: str) -> float:
        """Calculate keyword relevance.

        Args:
            query: Query text
            text: Text to check

        Returns:
            Relevance score (0-1)
        """
        query_terms = query.lower().split()
        text_lower = text.lower()

        if not query_terms:
            return 0.0

        matched_terms = sum(1 for term in query_terms if term in text_lower)

        return matched_terms / len(query_terms)


class AdvancedMemorySearch:
    """High-level interface for advanced memory search."""

    def __init__(self):
        """Initialize advanced memory search."""
        self.search_engine = SemanticSearchEngine()

    def index_memory(self, items: List[Dict]) -> None:
        """Index memory for search.

        Args:
            items: Memory items with 'id', 'content', optional 'metadata'
        """
        memory_items = [
            MemoryItem(
                id=item.get('id', str(i)),
                content=item.get('content', ''),
                metadata=item.get('metadata', {})
            )
            for i, item in enumerate(items)
        ]
        self.search_engine.index_memory(memory_items)

    def search(
        self,
        query: str,
        search_type: str = "hybrid",
        top_k: int = 5,
        **kwargs
    ) -> List[Dict]:
        """Search memory.

        Args:
            query: Search query
            search_type: Type of search ("semantic", "keyword", "hybrid", "contextual")
            top_k: Number of top results
            **kwargs: Additional options

        Returns:
            List of matching memory items with scores
        """
        if search_type == "semantic":
            results = self.search_engine.search_semantic(query, top_k)
        elif search_type == "hybrid":
            results = self.search_engine.search_hybrid(query, top_k=top_k)
        elif search_type == "contextual":
            context = kwargs.get('context', [])
            context_items = [MemoryItem(id=c.get('id'), content=c.get('content')) for c in context]
            results = self.search_engine.search_contextual(query, context_items, top_k)
        else:
            results = self.search_engine.search_semantic(query, top_k)

        return [
            {
                'id': item.id,
                'content': item.content,
                'score': round(item.relevance_score, 3),
                'metadata': item.metadata or {}
            }
            for item in results
        ]
