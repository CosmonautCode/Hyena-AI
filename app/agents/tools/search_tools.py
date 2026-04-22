"""
Advanced file search tools with full-text and regex support.

Implements comprehensive file searching functionality across workspaces.
Supports full-text search, regex patterns, and result ranking.
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import logging


logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a single search result."""
    file_path: str
    line_number: int
    line_content: str
    match_start: int
    match_end: int
    relevance_score: float

    def __str__(self) -> str:
        return f"{self.file_path}:{self.line_number} - {self.line_content.strip()}"


class SearchEngine:
    """Advanced file search engine with regex and full-text support."""

    def __init__(self, max_results: int = 100, context_lines: int = 2):
        """Initialize search engine.

        Args:
            max_results: Maximum number of results to return
            context_lines: Lines of context around matches
        """
        self.max_results = max_results
        self.context_lines = context_lines

    def search_full_text(
        self,
        root_path: str,
        pattern: str,
        file_pattern: Optional[str] = None,
        case_sensitive: bool = False
    ) -> List[SearchResult]:
        """Search for pattern in files using full-text matching.

        Args:
            root_path: Root directory to search
            pattern: Text pattern to search for
            file_pattern: Optional glob pattern for files (e.g., "*.py")
            case_sensitive: Whether search is case-sensitive

        Returns:
            List of SearchResult objects ranked by relevance
        """
        results: List[SearchResult] = []
        root = Path(root_path)

        if not root.exists():
            logger.warning(f"Search path does not exist: {root_path}")
            return results

        # Prepare search flags
        flags = 0 if case_sensitive else re.IGNORECASE
        search_re = re.compile(re.escape(pattern), flags)

        try:
            for file_path in self._get_files(root, file_pattern):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            for match in search_re.finditer(line):
                                score = self._calculate_relevance(
                                    line, pattern, match.span()
                                )
                                results.append(SearchResult(
                                    file_path=str(file_path.relative_to(root)),
                                    line_number=line_num,
                                    line_content=line,
                                    match_start=match.start(),
                                    match_end=match.end(),
                                    relevance_score=score
                                ))
                                if len(results) >= self.max_results:
                                    return sorted(
                                        results,
                                        key=lambda r: r.relevance_score,
                                        reverse=True
                                    )
                except (OSError, UnicodeDecodeError) as e:
                    logger.warning(f"Could not read {file_path}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Search error: {e}")

        return sorted(results, key=lambda r: r.relevance_score, reverse=True)

    def search_regex(
        self,
        root_path: str,
        regex_pattern: str,
        file_pattern: Optional[str] = None
    ) -> List[SearchResult]:
        """Search for regex pattern in files.

        Args:
            root_path: Root directory to search
            regex_pattern: Regex pattern to search for
            file_pattern: Optional glob pattern for files

        Returns:
            List of SearchResult objects ranked by relevance
        """
        results: List[SearchResult] = []
        root = Path(root_path)

        if not root.exists():
            logger.warning(f"Search path does not exist: {root_path}")
            return results

        try:
            regex = re.compile(regex_pattern)
        except re.error as e:
            logger.error(f"Invalid regex pattern: {e}")
            return results

        try:
            for file_path in self._get_files(root, file_pattern):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            for match in regex.finditer(line):
                                score = len(match.group())  # Score by match length
                                results.append(SearchResult(
                                    file_path=str(file_path.relative_to(root)),
                                    line_number=line_num,
                                    line_content=line,
                                    match_start=match.start(),
                                    match_end=match.end(),
                                    relevance_score=score
                                ))
                                if len(results) >= self.max_results:
                                    return sorted(
                                        results,
                                        key=lambda r: r.relevance_score,
                                        reverse=True
                                    )
                except (OSError, UnicodeDecodeError) as e:
                    logger.warning(f"Could not read {file_path}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Regex search error: {e}")

        return sorted(results, key=lambda r: r.relevance_score, reverse=True)

    def search_by_extension(
        self,
        root_path: str,
        extensions: List[str]
    ) -> List[SearchResult]:
        """Find all files with given extensions.

        Args:
            root_path: Root directory to search
            extensions: List of file extensions (e.g., [".py", ".js"])

        Returns:
            List of files (as SearchResult objects)
        """
        results: List[SearchResult] = []
        root = Path(root_path)

        if not root.exists():
            return results

        for file_path in root.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                # Store as SearchResult for consistency
                results.append(SearchResult(
                    file_path=str(file_path.relative_to(root)),
                    line_number=0,
                    line_content=str(file_path),
                    match_start=0,
                    match_end=0,
                    relevance_score=1.0
                ))

        return results[:self.max_results]

    @staticmethod
    def _get_files(root: Path, pattern: Optional[str]) -> List[Path]:
        """Get files matching pattern."""
        if pattern:
            return list(root.rglob(pattern))
        return [f for f in root.rglob('*') if f.is_file()]

    @staticmethod
    def _calculate_relevance(line: str, pattern: str, match_span: Tuple[int, int]) -> float:
        """Calculate relevance score for a match.

        Scoring factors:
        - Match position (earlier in line = higher score)
        - Match length (longer = higher relevance)
        - Line length (shorter line with match = higher relevance)
        """
        match_start, match_end = match_span
        match_length = match_end - match_start
        
        # Normalize match position (0-1, with 1 being start of line)
        position_score = 1.0 - (match_start / max(len(line), 1))
        
        # Length score (prefer longer matches)
        length_score = min(match_length / len(pattern) if pattern else 1, 2.0)
        
        # Line compactness (shorter lines with matches = higher relevance)
        compactness_score = 1.0 / (1.0 + len(line) / 50.0)
        
        # Combined score
        return (position_score * 0.3 + length_score * 0.4 + compactness_score * 0.3)


def search_files(
    root_path: str,
    pattern: str,
    search_type: str = "full-text",
    file_pattern: Optional[str] = None,
    max_results: int = 100
) -> Dict:
    """Search files using specified search type.

    Args:
        root_path: Root directory to search
        pattern: Search pattern (text or regex)
        search_type: Type of search ("full-text", "regex", or "extension")
        file_pattern: Optional glob pattern for files
        max_results: Maximum results to return

    Returns:
        Dictionary with search results and metadata
    """
    engine = SearchEngine(max_results=max_results)

    try:
        if search_type == "full-text":
            results = engine.search_full_text(
                root_path, pattern, file_pattern, case_sensitive=False
            )
            search_method = "Full-text"
        elif search_type == "regex":
            results = engine.search_regex(root_path, pattern, file_pattern)
            search_method = "Regex"
        elif search_type == "extension":
            results = engine.search_by_extension(root_path, [pattern])
            search_method = "Extension"
        else:
            return {"error": f"Unknown search type: {search_type}"}

        return {
            "success": True,
            "search_method": search_method,
            "pattern": pattern,
            "total_results": len(results),
            "results": [
                {
                    "file": r.file_path,
                    "line": r.line_number,
                    "content": r.line_content.strip(),
                    "score": round(r.relevance_score, 2)
                }
                for r in results[:max_results]
            ]
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return {"success": False, "error": str(e)}
