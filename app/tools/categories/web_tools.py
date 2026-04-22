"""Web and API tools."""

from typing import Any, Dict, List, Optional
import json
import hashlib
from urllib.parse import urlparse
from app.tools.base import BaseTool, ToolMetadata


class HttpGetTool(BaseTool):
    """Make HTTP GET request."""
    
    metadata = ToolMetadata(
        name="http_get",
        category="web",
        description="Make HTTP GET request",
        parameters={
            "url": {"type": "string", "description": "URL to fetch"},
            "timeout": {"type": "integer", "description": "Timeout in seconds"},
            "headers": {"type": "object", "description": "HTTP headers"},
        },
        returns={"status": {"type": "integer"}, "data": {"type": "string"}, "size": {"type": "integer"}},
        permissions=["http.get"],
    )
    
    async def execute(self, url: str, timeout: int = 10, headers: Optional[Dict] = None, **kwargs: Any) -> Dict[str, Any]:
        """Make GET request."""
        try:
            import httpx
            headers = headers or {}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=timeout, headers=headers)
            
            return {
                "success": True,
                "url": url,
                "status": response.status_code,
                "content_length": len(response.text),
                "content_type": response.headers.get("content-type", ""),
                "preview": response.text[:500],
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "url" in kwargs


class HttpPostTool(BaseTool):
    """Make HTTP POST request."""
    
    metadata = ToolMetadata(
        name="http_post",
        category="web",
        description="Make HTTP POST request",
        parameters={
            "url": {"type": "string", "description": "URL to post to"},
            "data": {"type": "object", "description": "Data to post"},
            "json": {"type": "boolean", "description": "Send as JSON"},
        },
        returns={"status": {"type": "integer"}, "response": {"type": "string"}},
        permissions=["http.post"],
    )
    
    async def execute(self, url: str, data: Optional[Dict] = None, json: bool = True, **kwargs: Any) -> Dict[str, Any]:
        """Make POST request."""
        try:
            import httpx
            data = data or {}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data if json else None, data=data if not json else None)
            
            return {
                "success": True,
                "url": url,
                "status": response.status_code,
                "response": response.text[:500],
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "url" in kwargs


class UrlValidateTool(BaseTool):
    """Validate URL format."""
    
    metadata = ToolMetadata(
        name="url_validate",
        category="web",
        description="Validate and parse URL",
        parameters={
            "url": {"type": "string", "description": "URL to validate"},
        },
        returns={"valid": {"type": "boolean"}, "components": {"type": "object"}},
        permissions=["http.read"],
    )
    
    async def execute(self, url: str, **kwargs: Any) -> Dict[str, Any]:
        """Validate URL."""
        try:
            parsed = urlparse(url)
            
            is_valid = all([parsed.scheme, parsed.netloc])
            
            return {
                "success": True,
                "url": url,
                "valid": is_valid,
                "scheme": parsed.scheme,
                "netloc": parsed.netloc,
                "path": parsed.path,
                "query": parsed.query,
                "fragment": parsed.fragment,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "url" in kwargs


class JsonProcessTool(BaseTool):
    """Process JSON data."""
    
    metadata = ToolMetadata(
        name="json_process",
        category="web",
        description="Process and validate JSON",
        parameters={
            "data": {"type": "string", "description": "JSON string or object"},
            "operation": {"type": "string", "description": "Operation: validate, format, minify"},
        },
        returns={"valid": {"type": "boolean"}, "result": {"type": "string"}},
        permissions=["data.read"],
    )
    
    async def execute(self, data: Any, operation: str = "validate", **kwargs: Any) -> Dict[str, Any]:
        """Process JSON."""
        try:
            if isinstance(data, str):
                parsed = json.loads(data)
            else:
                parsed = data
            
            if operation == "format":
                result = json.dumps(parsed, indent=2)
            elif operation == "minify":
                result = json.dumps(parsed, separators=(',', ':'))
            else:  # validate
                result = json.dumps(parsed)
            
            return {
                "success": True,
                "operation": operation,
                "valid": True,
                "result": result[:1000],
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "valid": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "data" in kwargs


class ParseHtmlTool(BaseTool):
    """Parse HTML content."""
    
    metadata = ToolMetadata(
        name="html_parse",
        category="web",
        description="Parse HTML and extract elements",
        parameters={
            "html": {"type": "string", "description": "HTML content"},
            "selector": {"type": "string", "description": "CSS selector (optional)"},
        },
        returns={"elements": {"type": "array"}},
        permissions=["data.read"],
    )
    
    async def execute(self, html: str, selector: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Parse HTML."""
        try:
            # Simple HTML parsing without external dependencies
            elements = []
            
            # Find tags like <tag>...</tag>
            import re
            tags = re.findall(r'<(\w+)[^>]*>(.*?)</\1>', html, re.DOTALL)
            
            for tag_name, content in tags:
                elements.append({
                    "tag": tag_name,
                    "content": content[:100],
                })
            
            return {
                "success": True,
                "element_count": len(elements),
                "elements": elements[:20],
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "html" in kwargs


class ExtractDataTool(BaseTool):
    """Extract structured data from text."""
    
    metadata = ToolMetadata(
        name="data_extract",
        category="web",
        description="Extract structured data using patterns",
        parameters={
            "text": {"type": "string", "description": "Text to extract from"},
            "pattern": {"type": "string", "description": "Regex pattern"},
        },
        returns={"matches": {"type": "array"}},
        permissions=["data.read"],
    )
    
    async def execute(self, text: str, pattern: str, **kwargs: Any) -> Dict[str, Any]:
        """Extract data."""
        try:
            import re
            regex = re.compile(pattern)
            matches = regex.findall(text)
            
            return {
                "success": True,
                "pattern": pattern,
                "match_count": len(matches),
                "matches": matches[:50],
            }
        except re.error as e:
            return {
                "success": False,
                "error": f"Regex error: {str(e)}",
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "text" in kwargs and "pattern" in kwargs


class ApiSchemaTool(BaseTool):
    """Inspect API schema."""
    
    metadata = ToolMetadata(
        name="api_schema",
        category="web",
        description="Inspect OpenAPI/Swagger schema",
        parameters={
            "schema": {"type": "object", "description": "OpenAPI schema"},
            "endpoint": {"type": "string", "description": "Specific endpoint (optional)"},
        },
        returns={"endpoints": {"type": "array"}},
        permissions=["api.read"],
    )
    
    async def execute(self, schema: Dict, endpoint: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Inspect API schema."""
        try:
            endpoints = []
            
            if "paths" in schema:
                for path, methods in schema["paths"].items():
                    for method, details in methods.items():
                        if method.lower() in ["get", "post", "put", "delete", "patch"]:
                            endpoints.append({
                                "path": path,
                                "method": method.upper(),
                                "description": details.get("description", ""),
                                "summary": details.get("summary", ""),
                            })
            
            return {
                "success": True,
                "endpoint_count": len(endpoints),
                "endpoints": endpoints[:20],
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "schema" in kwargs


class CacheDataTool(BaseTool):
    """Cache data with TTL."""
    
    metadata = ToolMetadata(
        name="cache_data",
        category="web",
        description="Cache data with time-to-live",
        parameters={
            "key": {"type": "string", "description": "Cache key"},
            "data": {"type": "string", "description": "Data to cache"},
            "ttl": {"type": "integer", "description": "Time to live in seconds"},
        },
        returns={"cached": {"type": "boolean"}, "key": {"type": "string"}},
        permissions=["cache.write"],
    )
    
    # Simple in-memory cache
    _cache: Dict[str, tuple] = {}
    
    async def execute(self, key: str, data: str, ttl: int = 3600, **kwargs: Any) -> Dict[str, Any]:
        """Cache data."""
        try:
            import time
            expiry = time.time() + ttl
            
            # Store with expiry
            self._cache[key] = (data, expiry)
            
            return {
                "success": True,
                "key": key,
                "cached": True,
                "ttl": ttl,
                "hash": hashlib.md5(data.encode()).hexdigest(),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "key" in kwargs and "data" in kwargs
