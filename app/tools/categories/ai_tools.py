"""AI and ML tools."""

from typing import Any, Dict, List, Optional
import re
from app.tools.base import BaseTool, ToolMetadata


class TextClassifyTool(BaseTool):
    """Classify text."""
    
    metadata = ToolMetadata(
        name="text_classify",
        category="ai",
        description="Classify text into categories",
        parameters={
            "text": {"type": "string", "description": "Text to classify"},
            "categories": {"type": "array", "description": "Possible categories"},
        },
        returns={"category": {"type": "string"}, "confidence": {"type": "number"}},
        permissions=["ai.classify"],
    )
    
    async def execute(self, text: str, categories: List[str], **kwargs: Any) -> Dict[str, Any]:
        """Classify text."""
        try:
            # Simple keyword-based classification
            text_lower = text.lower()
            scores = {}
            
            for category in categories:
                # Score based on keyword presence
                keywords = category.lower().split()
                score = sum(1 for kw in keywords if kw in text_lower) / len(keywords) if keywords else 0
                scores[category] = score
            
            best_category = max(scores, key=scores.get)
            confidence = scores[best_category]
            
            return {
                "success": True,
                "category": best_category,
                "confidence": round(confidence, 2),
                "scores": scores,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "text" in kwargs and "categories" in kwargs


class SentimentAnalysisTool(BaseTool):
    """Analyze sentiment."""
    
    metadata = ToolMetadata(
        name="sentiment_analysis",
        category="ai",
        description="Analyze text sentiment",
        parameters={
            "text": {"type": "string", "description": "Text to analyze"},
        },
        returns={"sentiment": {"type": "string"}, "score": {"type": "number"}},
        permissions=["ai.analyze"],
    )
    
    async def execute(self, text: str, **kwargs: Any) -> Dict[str, Any]:
        """Analyze sentiment."""
        try:
            text_lower = text.lower()
            
            # Simple sentiment scoring
            positive_words = ["good", "great", "excellent", "amazing", "love", "perfect", "wonderful", "fantastic"]
            negative_words = ["bad", "terrible", "awful", "hate", "horrible", "poor", "worst"]
            
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            
            sentiment = "positive" if pos_count > neg_count else "negative" if neg_count > pos_count else "neutral"
            score = (pos_count - neg_count) / (pos_count + neg_count if pos_count + neg_count > 0 else 1)
            
            return {
                "success": True,
                "sentiment": sentiment,
                "score": round(score, 2),
                "positive_count": pos_count,
                "negative_count": neg_count,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "text" in kwargs


class EntityExtractionTool(BaseTool):
    """Extract entities from text."""
    
    metadata = ToolMetadata(
        name="entity_extraction",
        category="ai",
        description="Extract named entities from text",
        parameters={
            "text": {"type": "string", "description": "Text to analyze"},
            "entity_types": {"type": "array", "description": "Entity types: person, location, organization"},
        },
        returns={"entities": {"type": "array"}},
        permissions=["ai.extract"],
    )
    
    async def execute(self, text: str, entity_types: Optional[List[str]] = None, **kwargs: Any) -> Dict[str, Any]:
        """Extract entities."""
        try:
            entity_types = entity_types or ["person", "location", "organization"]
            entities = []
            
            # Simple pattern-based extraction
            # Names (capitalized words)
            names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
            if "person" in entity_types:
                entities.extend([{"type": "person", "value": name} for name in set(names)])
            
            # Email addresses
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            entities.extend([{"type": "email", "value": email} for email in emails])
            
            # URLs
            urls = re.findall(r'https?://[^\s]+', text)
            entities.extend([{"type": "url", "value": url} for url in urls])
            
            return {
                "success": True,
                "entity_count": len(entities),
                "entities": entities[:50],
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "text" in kwargs


class TextSummarizationTool(BaseTool):
    """Summarize text."""
    
    metadata = ToolMetadata(
        name="text_summarize",
        category="ai",
        description="Generate text summary",
        parameters={
            "text": {"type": "string", "description": "Text to summarize"},
            "max_length": {"type": "integer", "description": "Maximum summary length"},
        },
        returns={"summary": {"type": "string"}, "reduction": {"type": "number"}},
        permissions=["ai.summarize"],
    )
    
    async def execute(self, text: str, max_length: int = 200, **kwargs: Any) -> Dict[str, Any]:
        """Summarize text."""
        try:
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Score sentences by word presence
            words = re.findall(r'\w+', text.lower())
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            scored = []
            for sentence in sentences:
                score = sum(word_freq.get(word.lower(), 0) for word in re.findall(r'\w+', sentence))
                scored.append((sentence, score))
            
            # Get top sentences
            top_sentences = sorted(scored, key=lambda x: x[1], reverse=True)[:3]
            summary = ". ".join([s[0] for s in sorted(top_sentences, key=lambda x: sentences.index(x[0]))])
            
            if len(summary) > max_length:
                summary = summary[:max_length - 3] + "..."
            
            reduction = 1 - len(summary) / len(text) if text else 0
            
            return {
                "success": True,
                "summary": summary,
                "original_length": len(text),
                "summary_length": len(summary),
                "reduction_ratio": round(reduction, 2),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "text" in kwargs


class TranslationTool(BaseTool):
    """Translate text."""
    
    metadata = ToolMetadata(
        name="translate",
        category="ai",
        description="Translate text between languages",
        parameters={
            "text": {"type": "string", "description": "Text to translate"},
            "source_lang": {"type": "string", "description": "Source language code"},
            "target_lang": {"type": "string", "description": "Target language code"},
        },
        returns={"translation": {"type": "string"}},
        permissions=["ai.translate"],
    )
    
    async def execute(self, text: str, source_lang: str = "en", target_lang: str = "es", **kwargs: Any) -> Dict[str, Any]:
        """Translate text."""
        try:
            # Simulate translation - in real use, call translation API
            translation_map = {
                ("en", "es"): "Hola",
                ("en", "fr"): "Bonjour",
                ("en", "de"): "Hallo",
            }
            
            key = (source_lang, target_lang)
            if key in translation_map:
                translated = translation_map[key]
            else:
                translated = f"[Translation from {source_lang} to {target_lang}]"
            
            return {
                "success": True,
                "text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "translation": translated,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "text" in kwargs


class SemanticSearchTool(BaseTool):
    """Semantic search."""
    
    metadata = ToolMetadata(
        name="semantic_search",
        category="ai",
        description="Search using semantic similarity",
        parameters={
            "query": {"type": "string", "description": "Search query"},
            "documents": {"type": "array", "description": "Documents to search"},
        },
        returns={"results": {"type": "array"}, "scores": {"type": "array"}},
        permissions=["ai.search"],
    )
    
    async def execute(self, query: str, documents: List[str], **kwargs: Any) -> Dict[str, Any]:
        """Semantic search."""
        try:
            # Simple keyword matching for semantic search
            query_words = set(query.lower().split())
            results = []
            
            for i, doc in enumerate(documents):
                doc_words = set(doc.lower().split())
                # Jaccard similarity
                intersection = len(query_words & doc_words)
                union = len(query_words | doc_words)
                similarity = intersection / union if union > 0 else 0
                
                results.append({
                    "index": i,
                    "document": doc[:100],
                    "similarity": round(similarity, 2),
                })
            
            # Sort by similarity
            results = sorted(results, key=lambda x: x["similarity"], reverse=True)
            
            return {
                "success": True,
                "query": query,
                "result_count": len(results),
                "results": results[:10],
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "query" in kwargs and "documents" in kwargs


class EmbeddingGenerationTool(BaseTool):
    """Generate embeddings."""
    
    metadata = ToolMetadata(
        name="embedding_gen",
        category="ai",
        description="Generate text embeddings",
        parameters={
            "text": {"type": "string", "description": "Text to embed"},
            "model": {"type": "string", "description": "Embedding model"},
        },
        returns={"embedding": {"type": "array"}, "dimension": {"type": "integer"}},
        permissions=["ai.embed"],
    )
    
    async def execute(self, text: str, model: str = "default", **kwargs: Any) -> Dict[str, Any]:
        """Generate embeddings."""
        try:
            import hashlib
            
            # Generate simple hash-based embedding
            hash_val = hashlib.md5(text.encode()).hexdigest()
            embedding = [int(hash_val[i:i+2], 16) / 255.0 for i in range(0, len(hash_val), 2)]
            
            return {
                "success": True,
                "text": text[:100],
                "model": model,
                "dimension": len(embedding),
                "embedding": embedding[:10],  # First 10 dimensions
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "text" in kwargs
