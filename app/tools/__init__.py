"""Tools module initialization."""

from app.tools.base import BaseTool, ToolMetadata
from app.tools.registry import get_tool_registry

# Import all tool categories for auto-registration
from app.tools.categories import (
    # File tools
    ReadFileTool,
    WriteFileTool,
    ListDirectoryTool,
    DeleteFileTool,
    CopyFileTool,
    MoveFileTool,
    SearchFilesTool,
    WatchFilesTool,
    # Code tools
    ParseCodeTool,
    AnalyzeImportsTool,
    FindSymbolsTool,
    DetectComplexityTool,
    LintCodeTool,
    GenerateTestsTool,
    GenerateDocsTool,
    # Git tools
    GitStatusTool,
    GitLogTool,
    GitBranchesTool,
    GitDiffTool,
    GitCommitTool,
    GitMergeTool,
    GitCreateBranchTool,
    # Web tools
    HttpGetTool,
    HttpPostTool,
    UrlValidateTool,
    JsonProcessTool,
    ParseHtmlTool,
    ExtractDataTool,
    ApiSchemaTool,
    CacheDataTool,
    # AI tools
    TextClassifyTool,
    SentimentAnalysisTool,
    EntityExtractionTool,
    TextSummarizationTool,
    TranslationTool,
    SemanticSearchTool,
    EmbeddingGenerationTool,
)


def register_all_tools():
    """Register all available tools."""
    registry = get_tool_registry()
    
    # File tools
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(ListDirectoryTool())
    registry.register(DeleteFileTool())
    registry.register(CopyFileTool())
    registry.register(MoveFileTool())
    registry.register(SearchFilesTool())
    registry.register(WatchFilesTool())
    
    # Code tools
    registry.register(ParseCodeTool())
    registry.register(AnalyzeImportsTool())
    registry.register(FindSymbolsTool())
    registry.register(DetectComplexityTool())
    registry.register(LintCodeTool())
    registry.register(GenerateTestsTool())
    registry.register(GenerateDocsTool())
    
    # Git tools
    registry.register(GitStatusTool())
    registry.register(GitLogTool())
    registry.register(GitBranchesTool())
    registry.register(GitDiffTool())
    registry.register(GitCommitTool())
    registry.register(GitMergeTool())
    registry.register(GitCreateBranchTool())
    
    # Web tools
    registry.register(HttpGetTool())
    registry.register(HttpPostTool())
    registry.register(UrlValidateTool())
    registry.register(JsonProcessTool())
    registry.register(ParseHtmlTool())
    registry.register(ExtractDataTool())
    registry.register(ApiSchemaTool())
    registry.register(CacheDataTool())
    
    # AI tools
    registry.register(TextClassifyTool())
    registry.register(SentimentAnalysisTool())
    registry.register(EntityExtractionTool())
    registry.register(TextSummarizationTool())
    registry.register(TranslationTool())
    registry.register(SemanticSearchTool())
    registry.register(EmbeddingGenerationTool())


# Auto-register all tools on import
register_all_tools()

__all__ = [
    "BaseTool",
    "ToolMetadata",
    "get_tool_registry",
    "register_all_tools",
]
