"""Code analysis and manipulation tools."""

from typing import Any, Dict, List, Optional
import ast
import re
from pathlib import Path
from app.tools.base import BaseTool, ToolMetadata


class ParseCodeTool(BaseTool):
    """Parse code using AST."""
    
    metadata = ToolMetadata(
        name="code_parse",
        category="code",
        description="Parse Python code and extract AST information",
        parameters={
            "code": {"type": "string", "description": "Code to parse"},
            "language": {"type": "string", "description": "Programming language (default: python)"},
        },
        returns={"functions": {"type": "array"}, "classes": {"type": "array"}},
        permissions=["code.read"],
    )
    
    async def execute(self, code: str, language: str = "python", **kwargs: Any) -> Dict[str, Any]:
        """Parse code."""
        if language != "python":
            return {
                "success": False,
                "error": f"Language {language} not supported. Use 'python'",
            }
        
        try:
            tree = ast.parse(code)
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                    })
            
            return {
                "success": True,
                "language": language,
                "functions": functions,
                "classes": classes,
                "lines": len(code.split("\n")),
            }
        except SyntaxError as e:
            return {
                "success": False,
                "error": f"Syntax error: {str(e)}",
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "code" in kwargs


class AnalyzeImportsTool(BaseTool):
    """Analyze imports in code."""
    
    metadata = ToolMetadata(
        name="code_imports",
        category="code",
        description="Analyze and extract imports from code",
        parameters={
            "code": {"type": "string", "description": "Code to analyze"},
        },
        returns={"imports": {"type": "array"}, "from_imports": {"type": "array"}},
        permissions=["code.read"],
    )
    
    async def execute(self, code: str, **kwargs: Any) -> Dict[str, Any]:
        """Analyze imports."""
        import_pattern = r"^import\s+(.+)$"
        from_pattern = r"^from\s+(.+?)\s+import\s+(.+)$"
        
        imports = []
        from_imports = []
        
        for line in code.split("\n"):
            line = line.strip()
            
            import_match = re.match(import_pattern, line)
            if import_match:
                imports.append(import_match.group(1))
            
            from_match = re.match(from_pattern, line)
            if from_match:
                from_imports.append({
                    "module": from_match.group(1),
                    "names": from_match.group(2).split(","),
                })
        
        return {
            "success": True,
            "imports": imports,
            "from_imports": from_imports,
            "total_imports": len(imports) + len(from_imports),
        }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "code" in kwargs


class FindSymbolsTool(BaseTool):
    """Find symbols in code."""
    
    metadata = ToolMetadata(
        name="code_symbols",
        category="code",
        description="Find and list all symbols (functions, classes, variables)",
        parameters={
            "code": {"type": "string", "description": "Code to search"},
            "symbol_type": {"type": "string", "description": "Type: function, class, variable, all"},
        },
        returns={"symbols": {"type": "array"}},
        permissions=["code.read"],
    )
    
    async def execute(self, code: str, symbol_type: str = "all", **kwargs: Any) -> Dict[str, Any]:
        """Find symbols."""
        try:
            tree = ast.parse(code)
            symbols = []
            
            for node in ast.walk(tree):
                if symbol_type in ["function", "all"] and isinstance(node, ast.FunctionDef):
                    symbols.append({"name": node.name, "type": "function", "line": node.lineno})
                elif symbol_type in ["class", "all"] and isinstance(node, ast.ClassDef):
                    symbols.append({"name": node.name, "type": "class", "line": node.lineno})
                elif symbol_type in ["variable", "all"] and isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            symbols.append({"name": target.id, "type": "variable", "line": node.lineno})
            
            return {
                "success": True,
                "symbol_count": len(symbols),
                "symbols": symbols,
            }
        except SyntaxError as e:
            return {
                "success": False,
                "error": f"Syntax error: {str(e)}",
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "code" in kwargs


class DetectComplexityTool(BaseTool):
    """Detect code complexity."""
    
    metadata = ToolMetadata(
        name="code_complexity",
        category="code",
        description="Analyze code complexity (cyclomatic complexity, nesting)",
        parameters={
            "code": {"type": "string", "description": "Code to analyze"},
        },
        returns={"complexity": {"type": "integer"}, "nesting_depth": {"type": "integer"}},
        permissions=["code.read"],
    )
    
    async def execute(self, code: str, **kwargs: Any) -> Dict[str, Any]:
        """Detect complexity."""
        try:
            tree = ast.parse(code)
            
            # Cyclomatic complexity: count decision points
            complexity = 1
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With)):
                    complexity += 1
            
            # Nesting depth
            max_depth = self._calc_nesting_depth(code)
            
            return {
                "success": True,
                "cyclomatic_complexity": complexity,
                "max_nesting_depth": max_depth,
                "complexity_level": "low" if complexity < 5 else "medium" if complexity < 15 else "high",
            }
        except SyntaxError as e:
            return {
                "success": False,
                "error": f"Syntax error: {str(e)}",
            }
    
    def _calc_nesting_depth(self, code: str) -> int:
        """Calculate max nesting depth."""
        max_depth = 0
        current_depth = 0
        for char in code:
            if char in "{([":
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in "})]":
                current_depth -= 1
        return max_depth
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "code" in kwargs


class LintCodeTool(BaseTool):
    """Find linting issues."""
    
    metadata = ToolMetadata(
        name="code_lint",
        category="code",
        description="Find basic linting issues in code",
        parameters={
            "code": {"type": "string", "description": "Code to lint"},
        },
        returns={"issues": {"type": "array"}},
        permissions=["code.read"],
    )
    
    async def execute(self, code: str, **kwargs: Any) -> Dict[str, Any]:
        """Lint code."""
        issues = []
        lines = code.split("\n")
        
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                issues.append({"line": i, "type": "long_line", "message": f"Line too long: {len(line)} chars"})
            
            if line.strip().startswith("print("):
                issues.append({"line": i, "type": "print_statement", "message": "Use logging instead of print"})
            
            if "TODO" in line or "FIXME" in line:
                issues.append({"line": i, "type": "todo_marker", "message": "Unresolved TODO/FIXME"})
        
        return {
            "success": True,
            "issue_count": len(issues),
            "issues": issues[:50],  # Limit to 50 issues
        }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "code" in kwargs


class GenerateTestsTool(BaseTool):
    """Generate test templates."""
    
    metadata = ToolMetadata(
        name="code_test_gen",
        category="code",
        description="Generate test templates for functions and classes",
        parameters={
            "code": {"type": "string", "description": "Code to generate tests for"},
        },
        returns={"tests": {"type": "array"}},
        permissions=["code.read"],
    )
    
    async def execute(self, code: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate tests."""
        try:
            tree = ast.parse(code)
            tests = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    test_name = f"test_{node.name}"
                    args = [arg.arg for arg in node.args.args]
                    tests.append({
                        "name": test_name,
                        "type": "unit",
                        "function": node.name,
                        "args": args,
                        "template": f"def {test_name}():\n    # TODO: Implement test",
                    })
                elif isinstance(node, ast.ClassDef):
                    test_name = f"Test{node.name}"
                    tests.append({
                        "name": test_name,
                        "type": "class",
                        "class": node.name,
                        "template": f"class {test_name}:\n    def test_init(self): pass",
                    })
            
            return {
                "success": True,
                "test_count": len(tests),
                "tests": tests,
            }
        except SyntaxError as e:
            return {
                "success": False,
                "error": f"Syntax error: {str(e)}",
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "code" in kwargs


class GenerateDocsTool(BaseTool):
    """Generate documentation."""
    
    metadata = ToolMetadata(
        name="code_docgen",
        category="code",
        description="Generate documentation templates for code",
        parameters={
            "code": {"type": "string", "description": "Code to document"},
            "style": {"type": "string", "description": "Doc style: google, numpy, sphinx"},
        },
        returns={"documentation": {"type": "array"}},
        permissions=["code.read"],
    )
    
    async def execute(self, code: str, style: str = "google", **kwargs: Any) -> Dict[str, Any]:
        """Generate docs."""
        try:
            tree = ast.parse(code)
            docs = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    doc_template = f'"""\n{node.name} function.\n\n'
                    doc_template += "Args:\n"
                    for arg in node.args.args:
                        doc_template += f"    {arg.arg}: Description\n"
                    doc_template += "\nReturns:\n    Description\n\"\"\""
                    
                    docs.append({
                        "name": node.name,
                        "type": "function",
                        "template": doc_template,
                    })
            
            return {
                "success": True,
                "doc_count": len(docs),
                "style": style,
                "documentation": docs,
            }
        except SyntaxError as e:
            return {
                "success": False,
                "error": f"Syntax error: {str(e)}",
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "code" in kwargs


class RefactorCodeTool(BaseTool):
    """Suggest refactoring opportunities."""
    
    metadata = ToolMetadata(
        name="code_refactor_suggest",
        category="code",
        description="Suggest code refactoring opportunities",
        parameters={
            "code": {"type": "string", "description": "Code to analyze"},
        },
        returns={"suggestions": {"type": "array"}},
        permissions=["code.read"],
    )
    
    async def execute(self, code: str, **kwargs: Any) -> Dict[str, Any]:
        """Suggest refactoring."""
        try:
            tree = ast.parse(code)
            suggestions = []
            
            # Find long functions (>20 lines)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                    if func_lines > 20:
                        suggestions.append({
                            "type": "long_function",
                            "function": node.name,
                            "lines": func_lines,
                            "suggestion": "Consider breaking this function into smaller functions",
                        })
            
            # Find duplicate code patterns
            lines = code.split("\n")
            if len(lines) > 10:
                suggestions.append({
                    "type": "potential_duplication",
                    "suggestion": "Review code for potential duplication",
                    "lines": len(lines),
                })
            
            return {
                "success": True,
                "suggestion_count": len(suggestions),
                "suggestions": suggestions,
            }
        except SyntaxError as e:
            return {
                "success": False,
                "error": f"Syntax error: {str(e)}",
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "code" in kwargs
