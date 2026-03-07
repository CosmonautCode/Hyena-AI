"""Extract key insights from conversations using AI analysis."""

import json
import time
from typing import List, Dict, Optional


class MemoryExtractor:
    """
    Extracts key insights from conversation segments using the LLM.
    Creates structured memories that can be retrieved for context.
    """
    
    def __init__(self, llm):
        """
        Initialize the memory extractor.
        
        Args:
            llm: The LLM instance for analysis
        """
        self.llm = llm
        self.extraction_prompt = """Analyze this conversation segment and extract key insights.

Conversation:
{conversation}

Extract and return a JSON object with:
1. insights: List of key facts, decisions, or important information
2. decisions: List of decisions made
3. patterns: List of code patterns, architecture choices, or technical approaches
4. topics: List of topics/themes (e.g., "authentication", "api-design", "database")
5. importance: "high", "medium", or "low" based on significance

Format your response as valid JSON only, no other text:
{{
  "insights": ["insight 1", "insight 2"],
  "decisions": ["decision 1"],
  "patterns": ["pattern 1"],
  "topics": ["topic1", "topic2"],
  "importance": "high|medium|low"
}}"""
    
    def should_extract(self, messages_since_last: int, min_interval: int = 5) -> bool:
        """
        Determine if we should run memory extraction.
        
        Args:
            messages_since_last: Number of messages since last extraction
            min_interval: Minimum messages before next extraction
            
        Returns:
            True if extraction should run
        """
        return messages_since_last >= min_interval
    
    def format_messages(self, messages: List[Dict]) -> str:
        """
        Format messages for the extraction prompt.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            Formatted conversation text
        """
        formatted = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted.append(f"{role}: {content}")
        return "\n\n".join(formatted)
    
    def extract(self, messages: List[Dict]) -> Optional[Dict]:
        """
        Extract insights from a conversation segment.
        
        Args:
            messages: List of recent messages to analyze
            
        Returns:
            Extracted memory dict or None if extraction failed
        """
        if not self.llm:
            return None
        
        if len(messages) < 2:
            return None  # Need at least a user message and response
        
        conversation_text = self.format_messages(messages)
        prompt = self.extraction_prompt.format(conversation=conversation_text)
        
        try:
            # Use completion API for extraction
            output = self.llm.create_completion(
                prompt=prompt,
                max_tokens=500,
                temperature=0.2,
                stop=["\n\n"]  # Stop at double newline
            )
            
            response_text = output["choices"][0]["text"].strip()
            
            # Parse JSON response
            extracted = json.loads(response_text)
            
            # Validate required fields
            if "insights" not in extracted:
                extracted["insights"] = []
            if "topics" not in extracted:
                extracted["topics"] = []
            if "importance" not in extracted:
                extracted["importance"] = "low"
            
            # Add metadata
            extracted["extracted_at"] = time.time()
            extracted["message_count"] = len(messages)
            
            return extracted
            
        except json.JSONDecodeError:
            # LLM didn't return valid JSON
            return None
        except Exception as e:
            print(f"Memory extraction error: {e}")
            return None
    
    def extract_key_points_only(self, messages: List[Dict]) -> List[str]:
        """
        Quick extraction that just gets key points as strings.
        Fallback for when full extraction isn't needed.
        
        Args:
            messages: Messages to analyze
            
        Returns:
            List of key point strings
        """
        extracted = self.extract(messages)
        if not extracted:
            return []
        
        # Combine insights and decisions into key points
        key_points = []
        key_points.extend(extracted.get("insights", []))
        key_points.extend(extracted.get("decisions", []))
        
        return key_points
