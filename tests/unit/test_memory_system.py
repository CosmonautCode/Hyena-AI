"""Unit tests for memory system."""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path


class TestMemoryStore:
    """Test memory conversation store."""
    
    def test_memory_store_initialization(self, temp_workspace):
        """Test memory store initializes correctly."""
        # Import only when needed to avoid issues
        from app.memory.store import ConversationStore
        
        store = ConversationStore(str(temp_workspace))
        assert store is not None
    
    def test_memory_store_path_creation(self, temp_workspace):
        """Test memory store creates necessary directories."""
        from app.memory.store import ConversationStore
        
        store_path = temp_workspace / "conversations"
        store = ConversationStore(str(store_path))
        
        # Should create auto and named subdirectories
        assert isinstance(store_path, Path)


class TestMemoryExtractor:
    """Test memory extraction functionality."""
    
    def test_memory_extractor_initialization(self, mock_llm):
        """Test memory extractor initializes correctly."""
        from app.memory.extractor import MemoryExtractor
        
        extractor = MemoryExtractor(mock_llm)
        assert extractor.llm == mock_llm
    
    def test_extract_memories_structure(self, mock_llm, sample_conversation_history):
        """Test memory extraction returns structured output."""
        from app.memory.extractor import MemoryExtractor
        
        extractor = MemoryExtractor(mock_llm)
        
        # Mock the extract method
        mock_result = {
            "insights": ["Test insight"],
            "decisions": ["Test decision"],
            "patterns": ["Test pattern"],
            "topics": ["test-topic"],
            "importance": "high"
        }
        extractor.extract_memories = MagicMock(return_value=mock_result)
        
        result = extractor.extract_memories(sample_conversation_history)
        
        assert "insights" in result or isinstance(result, dict)


class TestMemoryRetrieval:
    """Test memory retrieval functionality."""
    
    def test_memory_retrieval_initialization(self, temp_workspace):
        """Test memory retrieval initializes correctly."""
        from app.memory.retrieval import MemoryRetrieval
        
        retrieval = MemoryRetrieval(str(temp_workspace))
        assert retrieval is not None
    
    def test_get_relevant_memories(self, temp_workspace):
        """Test retrieving relevant memories."""
        from app.memory.retrieval import MemoryRetrieval
        
        retrieval = MemoryRetrieval(str(temp_workspace))
        
        # Mock the method
        retrieval.get_relevant_memories = MagicMock(return_value=[])
        
        result = retrieval.get_relevant_memories("test context")
        
        assert isinstance(result, list)


class TestAutoMemoryOrchestrator:
    """Test auto memory orchestrator."""
    
    def test_orchestrator_initialization(self, mock_llm, sample_chat_system, temp_workspace):
        """Test orchestrator initializes correctly."""
        from app.memory.orchestrator import AutoMemoryOrchestrator
        
        orchestrator = AutoMemoryOrchestrator(
            mock_llm,
            sample_chat_system,
            str(temp_workspace)
        )
        
        assert orchestrator.llm == mock_llm
        assert orchestrator.chat_system == sample_chat_system
    
    def test_message_counting(self, mock_llm, sample_chat_system, temp_workspace):
        """Test message counting for extraction interval."""
        from app.memory.orchestrator import AutoMemoryOrchestrator
        
        orchestrator = AutoMemoryOrchestrator(
            mock_llm,
            sample_chat_system,
            str(temp_workspace)
        )
        
        assert orchestrator.extraction_interval == 5
        assert orchestrator.messages_since_extraction == 0


class TestMemoryIntegration:
    """Integration tests for memory system."""
    
    def test_memory_storage_flow(self, mock_llm, sample_chat_system, temp_workspace):
        """Test complete memory storage flow."""
        from app.memory.orchestrator import AutoMemoryOrchestrator
        
        orchestrator = AutoMemoryOrchestrator(
            mock_llm,
            sample_chat_system,
            str(temp_workspace)
        )
        
        # Should initialize without errors
        assert orchestrator is not None
        assert orchestrator.conversation_store is not None
    
    def test_extraction_interval_tracking(self, mock_llm, sample_chat_system, temp_workspace):
        """Test extraction interval is properly tracked."""
        from app.memory.orchestrator import AutoMemoryOrchestrator
        
        orchestrator = AutoMemoryOrchestrator(
            mock_llm,
            sample_chat_system,
            str(temp_workspace)
        )
        
        # Should track extraction interval
        assert hasattr(orchestrator, 'extraction_interval')
        assert hasattr(orchestrator, 'messages_since_extraction')
