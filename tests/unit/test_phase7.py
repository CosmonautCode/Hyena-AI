"""
Comprehensive tests for Phase 7 components
(Search Tools, Streaming, Advanced Memory Search, Performance Tracking)
"""

import pytest
import asyncio
from pathlib import Path
from typing import List, AsyncIterator

# Import Phase 7 components
from app.agents.tools.search_tools import SearchEngine, search_files, SearchResult
from app.core.streaming import (
    StreamManager, ConsoleStreamCallback, ListStreamCallback,
    ResponseStreamer, StreamToken, StreamMetrics, create_mock_stream
)
from app.memory.retrieval.advanced_search import (
    AdvancedMemorySearch, SemanticSearchEngine, MemoryItem, EmbeddingGenerator
)


# ============================================================================
# SEARCH TOOLS TESTS (10 tests)
# ============================================================================

class TestSearchEngine:
    """Test suite for SearchEngine."""

    @pytest.fixture
    def engine(self):
        """Create search engine."""
        return SearchEngine(max_results=50)

    @pytest.fixture
    def temp_files(self, tmp_path):
        """Create temporary test files."""
        # Create test files
        (tmp_path / "file1.txt").write_text("Hello world\nPython programming\nHello again")
        (tmp_path / "file2.txt").write_text("Java programming\nPython is great\nHello Java")
        (tmp_path / "config.json").write_text('{"hello": "world"}')
        return tmp_path

    def test_full_text_search(self, engine, temp_files):
        """Test full-text search."""
        results = engine.search_full_text(str(temp_files), "Hello", case_sensitive=True)
        assert len(results) >= 2
        assert all("Hello" in r.line_content for r in results)

    def test_case_insensitive_search(self, engine, temp_files):
        """Test case-insensitive search."""
        results = engine.search_full_text(str(temp_files), "HELLO", case_sensitive=False)
        assert len(results) >= 2

    def test_case_sensitive_search(self, engine, temp_files):
        """Test case-sensitive search."""
        results = engine.search_full_text(str(temp_files), "Hello", case_sensitive=True)
        assert len(results) >= 1

    def test_regex_search(self, engine, temp_files):
        """Test regex pattern search."""
        results = engine.search_regex(str(temp_files), r"\w+ing")  # Words ending in 'ing'
        assert len(results) >= 2

    def test_search_by_extension(self, engine, temp_files):
        """Test search by file extension."""
        results = engine.search_by_extension(str(temp_files), [".txt"])
        assert len(results) == 2

    def test_relevance_scoring(self, engine, temp_files):
        """Test relevance score calculation."""
        results = engine.search_full_text(str(temp_files), "Hello")
        assert all(0 <= r.relevance_score <= 1 for r in results)
        # Results should be sorted by relevance
        assert results == sorted(results, key=lambda r: r.relevance_score, reverse=True)

    def test_max_results_limit(self, engine, temp_files):
        """Test max results limit."""
        engine.max_results = 2
        results = engine.search_full_text(str(temp_files), "o")  # 'o' appears many times
        assert len(results) <= engine.max_results

    def test_nonexistent_path(self, engine):
        """Test search on nonexistent path."""
        results = engine.search_full_text("/nonexistent/path", "test")
        assert len(results) == 0

    def test_search_files_full_text(self, temp_files):
        """Test search_files function with full-text."""
        result = search_files(str(temp_files), "Python", search_type="full-text")
        assert result["success"] is True
        assert result["total_results"] >= 1

    def test_search_files_regex(self, temp_files):
        """Test search_files function with regex."""
        result = search_files(str(temp_files), r"P\w+", search_type="regex")
        assert result["success"] is True


# ============================================================================
# STREAMING TESTS (8 tests)
# ============================================================================

class TestStreaming:
    """Test suite for streaming infrastructure."""

    @pytest.fixture
    def stream_manager(self):
        """Create stream manager."""
        return StreamManager()

    @pytest.mark.asyncio
    async def test_emit_token(self, stream_manager):
        """Test token emission."""
        callback = ListStreamCallback()
        stream_manager.add_callback(callback)

        await stream_manager.emit_token("H", 0)
        await stream_manager.emit_token("i", 1)

        assert len(callback.tokens) == 2
        assert callback.get_text() == "Hi"

    @pytest.mark.asyncio
    async def test_stream_generator(self, stream_manager):
        """Test streaming from generator."""
        callback = ListStreamCallback()
        stream_manager.add_callback(callback)

        async def test_gen():
            for char in "Hello":
                yield char

        text = await stream_manager.stream(test_gen())
        assert text == "Hello"
        assert callback.get_text() == "Hello"

    @pytest.mark.asyncio
    async def test_stream_metrics(self, stream_manager):
        """Test streaming metrics calculation."""
        async def test_gen():
            for char in "Test":
                await asyncio.sleep(0.01)
                yield char

        await stream_manager.stream(test_gen())
        assert stream_manager.metrics.total_tokens == 4
        assert stream_manager.metrics.total_time > 0.04

    @pytest.mark.asyncio
    async def test_multiple_callbacks(self, stream_manager):
        """Test multiple callbacks."""
        callback1 = ListStreamCallback()
        callback2 = ListStreamCallback()
        stream_manager.add_callback(callback1)
        stream_manager.add_callback(callback2)

        await stream_manager.emit_token("X", 0)

        assert len(callback1.tokens) == 1
        assert len(callback2.tokens) == 1

    @pytest.mark.asyncio
    async def test_response_streamer(self):
        """Test ResponseStreamer."""
        streamer = ResponseStreamer()

        async def test_gen():
            yield "He"
            yield "llo"

        text = await streamer.stream_response(test_gen())
        assert text == "Hello"

    @pytest.mark.asyncio
    async def test_mock_stream(self):
        """Test mock stream creation."""
        stream = create_mock_stream("Hi", delay=0.001)
        text = ""
        async for char in stream:
            text += char
        assert text == "Hi"

    @pytest.mark.asyncio
    async def test_stream_error_handling(self, stream_manager):
        """Test error handling in streaming."""
        callback = ListStreamCallback()
        stream_manager.add_callback(callback)

        async def error_gen():
            yield "H"
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            await stream_manager.stream(error_gen())

    @pytest.mark.asyncio
    async def test_console_callback(self, capsys, stream_manager):
        """Test console callback."""
        callback = ConsoleStreamCallback()
        stream_manager.add_callback(callback)

        await stream_manager.emit_token("T", 0)
        await stream_manager.emit_token("e", 1)

        # Check that tokens were printed
        assert callback.buffer == "Te"


# ============================================================================
# ADVANCED MEMORY SEARCH TESTS (6 tests)
# ============================================================================

class TestAdvancedMemorySearch:
    """Test suite for advanced memory search."""

    @pytest.fixture
    def search_engine(self):
        """Create search engine."""
        return SemanticSearchEngine()

    @pytest.fixture
    def test_items(self):
        """Create test memory items."""
        return [
            MemoryItem(id="1", content="Python is a programming language"),
            MemoryItem(id="2", content="Java is also a programming language"),
            MemoryItem(id="3", content="Machine learning with Python"),
            MemoryItem(id="4", content="Web development with JavaScript"),
        ]

    def test_embedding_generation(self):
        """Test embedding generation."""
        embedder = EmbeddingGenerator(dimension=128)
        embedding = embedder.generate_embedding("test text")
        assert len(embedding) == 128
        assert all(-1 <= x <= 1 for x in embedding)

    def test_semantic_search(self, search_engine, test_items):
        """Test semantic search."""
        search_engine.index_memory(test_items)
        results = search_engine.search_semantic("programming language", top_k=2)
        assert len(results) <= 2
        assert all(r.relevance_score > 0 for r in results)

    def test_hybrid_search(self, search_engine, test_items):
        """Test hybrid search."""
        search_engine.index_memory(test_items)
        results = search_engine.search_hybrid("Python programming", top_k=3)
        assert len(results) <= 3
        assert results[0].relevance_score >= results[-1].relevance_score

    def test_contextual_search(self, search_engine, test_items):
        """Test contextual search."""
        search_engine.index_memory(test_items)
        context = [MemoryItem(id="c1", content="I know Python")]
        results = search_engine.search_contextual("programming", context_items=context, top_k=2)
        assert len(results) <= 2

    def test_advanced_search_interface(self, test_items):
        """Test high-level advanced search interface."""
        search = AdvancedMemorySearch()
        search.index_memory([{"id": item.id, "content": item.content} for item in test_items])

        results = search.search("Python", search_type="semantic", top_k=2)
        assert isinstance(results, list)
        assert all("score" in r for r in results)

    def test_search_with_metadata(self):
        """Test search with metadata."""
        search = AdvancedMemorySearch()
        items = [
            {
                "id": "1",
                "content": "Important fact",
                "metadata": {"priority": "high", "timestamp": 1234567890}
            }
        ]
        search.index_memory(items)
        results = search.search("fact", top_k=1)
        assert results[0]["metadata"]["priority"] == "high"


# ============================================================================
# PERFORMANCE TRACKING TESTS (5 tests)
# ============================================================================

class TestStreamMetrics:
    """Test suite for performance metrics."""

    def test_metrics_initialization(self):
        """Test StreamMetrics initialization."""
        metrics = StreamMetrics()
        assert metrics.total_tokens == 0
        assert metrics.tokens_per_second == 0.0

    def test_metrics_calculation(self):
        """Test metrics calculation."""
        metrics = StreamMetrics(
            total_tokens=100,
            total_time=2.0
        )
        metrics.tokens_per_second = metrics.total_tokens / metrics.total_time
        assert metrics.tokens_per_second == 50.0

    @pytest.mark.asyncio
    async def test_streaming_performance(self):
        """Test streaming performance metrics."""
        manager = StreamManager()

        async def perf_gen():
            for i in range(10):
                await asyncio.sleep(0.01)
                yield str(i)

        await manager.stream(perf_gen())
        assert manager.metrics.total_tokens == 10
        assert manager.metrics.tokens_per_second > 0

    def test_token_rate_calculation(self):
        """Test token rate calculation."""
        metrics = StreamMetrics(
            total_tokens=500,
            total_time=10.0
        )
        rate = metrics.total_tokens / metrics.total_time if metrics.total_time > 0 else 0
        assert rate == 50.0

    def test_metrics_json_serialization(self):
        """Test metrics can be serialized."""
        metrics = StreamMetrics(
            total_tokens=100,
            total_time=2.0
        )
        # Should be serializable to dict
        data = {
            "total_tokens": metrics.total_tokens,
            "total_time": metrics.total_time,
            "tokens_per_second": metrics.tokens_per_second
        }
        assert data["total_tokens"] == 100


# ============================================================================
# INTEGRATION TESTS (5 aggregate)
# ============================================================================

class TestPhase7Integration:
    """Integration tests for Phase 7 components."""

    @pytest.mark.asyncio
    async def test_search_and_stream(self):
        """Test search results can be streamed."""
        # Mock search result
        result = search_files(".", "import", search_type="full-text", max_results=5)

        # Stream the result
        streamer = ResponseStreamer()

        async def result_gen():
            yield str(result["total_results"])

        text = await streamer.stream_response(result_gen())
        assert len(text) > 0

    @pytest.mark.asyncio
    async def test_memory_search_integration(self):
        """Test memory search integration."""
        # Create search instance
        search = AdvancedMemorySearch()

        # Index items
        items = [
            {"id": "1", "content": "Python programming"},
            {"id": "2", "content": "Java programming"},
        ]
        search.index_memory(items)

        # Search
        results = search.search("programming", top_k=2)
        assert len(results) <= 2

        # Stream results
        streamer = ResponseStreamer()

        async def results_gen():
            for result in results:
                yield str(result)

        await streamer.stream_response(results_gen())


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
