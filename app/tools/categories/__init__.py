"""Tools categories module - all available tools."""

# File tools
from app.tools.categories.file_tools import (
    ReadFileTool,
    WriteFileTool,
    ListDirectoryTool,
    DeleteFileTool,
    CopyFileTool,
    MoveFileTool,
    SearchFilesTool,
    WatchFilesTool,
)

# Code tools
from app.tools.categories.code_tools import (
    ParseCodeTool,
    AnalyzeImportsTool,
    FindSymbolsTool,
    DetectComplexityTool,
    LintCodeTool,
    GenerateTestsTool,
    GenerateDocsTool,
    RefactorCodeTool,
)

# Git tools
from app.tools.categories.git_tools import (
    GitStatusTool,
    GitLogTool,
    GitBranchesTool,
    GitDiffTool,
    GitCommitTool,
    GitMergeTool,
    GitCreateBranchTool,
    GitStashTool,
)

# Web tools
from app.tools.categories.web_tools import (
    HttpGetTool,
    HttpPostTool,
    UrlValidateTool,
    JsonProcessTool,
    ParseHtmlTool,
    ExtractDataTool,
    ApiSchemaTool,
    CacheDataTool,
)

# AI tools
from app.tools.categories.ai_tools import (
    TextClassifyTool,
    SentimentAnalysisTool,
    EntityExtractionTool,
    TextSummarizationTool,
    TranslationTool,
    SemanticSearchTool,
    EmbeddingGenerationTool,
)

__all__ = [
    # File tools (8)
    "ReadFileTool",
    "WriteFileTool",
    "ListDirectoryTool",
    "DeleteFileTool",
    "CopyFileTool",
    "MoveFileTool",
    "SearchFilesTool",
    "WatchFilesTool",
    # Code tools (8)
    "ParseCodeTool",
    "AnalyzeImportsTool",
    "FindSymbolsTool",
    "DetectComplexityTool",
    "LintCodeTool",
    "GenerateTestsTool",
    "GenerateDocsTool",
    "RefactorCodeTool",
    # Git tools (8)
    "GitStatusTool",
    "GitLogTool",
    "GitBranchesTool",
    "GitDiffTool",
    "GitCommitTool",
    "GitMergeTool",
    "GitCreateBranchTool",
    "GitStashTool",
    # Web tools (8)
    "HttpGetTool",
    "HttpPostTool",
    "UrlValidateTool",
    "JsonProcessTool",
    "ParseHtmlTool",
    "ExtractDataTool",
    "ApiSchemaTool",
    "CacheDataTool",
    # AI tools (7)
    "TextClassifyTool",
    "SentimentAnalysisTool",
    "EntityExtractionTool",
    "TextSummarizationTool",
    "TranslationTool",
    "SemanticSearchTool",
    "EmbeddingGenerationTool",
]

# Tool count: 8 + 8 + 8 + 8 + 7 = 39 tools total
