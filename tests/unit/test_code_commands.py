"""Tests for code and diff commands."""

import pytest
import asyncio
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from app.cli.commands.base import CommandContext, CommandResult
from app.cli.commands.code import (
    CodeAnalyzeCommand,
    CodeExplainCommand,
    CodeSuggestCommand,
    CodeRefactorCommand,
    CodeTestCommand,
    CodeDocumentCommand,
    DiffCommand,
    MergeCommand,
    RevertCommand,
    ApplyCommand,
)


class TestCodeAnalyzeCommand:
    """Test code analysis command."""

    @pytest.fixture
    def command(self):
        return CodeAnalyzeCommand()

    @pytest.fixture
    def temp_file(self):
        """Create temporary Python file."""
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""# Sample Python file
def hello(name):
    '''Say hello'''
    print(f"Hello, {name}!")
    
def calculate(a, b):
    return a + b

class Calculator:
    \"\"\"Simple calculator\"\"\"
    def __init__(self):
        self.result = 0
""")
            f.flush()
            yield f.name
        Path(f.name).unlink()

    @pytest.mark.asyncio
    async def test_analyze_basic(self, command, temp_file):
        """Test basic code analysis."""
        context = CommandContext(
            user_input=f"code analyze {temp_file}",
            args={"_positional": [temp_file]}
        )
        result = await command.execute(context)
        
        assert result.success
        assert result.data["lines_of_code"] > 0
        assert result.data["language"] == "python"
        assert "complexity" in result.data

    @pytest.mark.asyncio
    async def test_analyze_nonexistent_file(self, command):
        """Test analysis of nonexistent file."""
        context = CommandContext(
            user_input="code analyze /nonexistent/file.py",
            args={"_positional": ["/nonexistent/file.py"]}
        )
        result = await command.execute(context)
        
        assert not result.success
        assert "not found" in result.message.lower()

    @pytest.mark.asyncio
    async def test_analyze_validation(self, command):
        """Test validation fails without file."""
        context = CommandContext(
            user_input="code analyze",
            args={}
        )
        result = await command.execute(context)
        
        assert not result.success

    @pytest.mark.asyncio
    async def test_analyze_js_file(self, command):
        """Test analyzing JavaScript file."""
        import tempfile
        import time
        fd, path = tempfile.mkstemp(suffix=".js", text=True)
        try:
            import os
            os.write(fd, b"function hello() { console.log('hi'); }")
            os.close(fd)
            
            context = CommandContext(
                user_input=f"code analyze {path}",
                args={"_positional": [path]}
            )
            result = await command.execute(context)
            
            assert result.success
            assert result.data["language"] == "javascript"
        finally:
            try:
                Path(path).unlink()
            except (OSError, PermissionError):
                # On Windows, file might still be locked
                time.sleep(0.1)
                try:
                    Path(path).unlink()
                except (OSError, PermissionError):
                    pass  # Give up, file will be cleaned by temp cleanup


class TestCodeExplainCommand:
    """Test code explanation command."""

    @pytest.fixture
    def command(self):
        return CodeExplainCommand()

    @pytest.fixture
    def temp_file(self):
        """Create temporary file."""
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("async def process(): pass\ndef handler(): pass")
            f.flush()
            yield f.name
        Path(f.name).unlink()

    @pytest.mark.asyncio
    async def test_explain_basic(self, command, temp_file):
        """Test basic code explanation."""
        context = CommandContext(
            user_input=f"code explain {temp_file}",
            args={"_positional": [temp_file]}
        )
        result = await command.execute(context)
        
        assert result.success
        assert "summary" in result.data
        assert result.data["language"] == "python"

    @pytest.mark.asyncio
    async def test_explain_with_section(self, command, temp_file):
        """Test explanation with section limit."""
        context = CommandContext(
            user_input=f"code explain {temp_file} --section 5",
            args={"_positional": [temp_file], "section": "5"}
        )
        result = await command.execute(context)
        
        assert result.success

    @pytest.mark.asyncio
    async def test_explain_detects_concepts(self, command, temp_file):
        """Test concept detection."""
        context = CommandContext(
            user_input=f"code explain {temp_file}",
            args={"_positional": [temp_file]}
        )
        result = await command.execute(context)
        
        assert result.success
        assert "key_concepts" in result.data
        assert len(result.data["key_concepts"]) > 0


class TestCodeSuggestCommand:
    """Test code suggestion command."""

    @pytest.fixture
    def command(self):
        return CodeSuggestCommand()

    @pytest.fixture
    def temp_file(self):
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("x = [i for i in range(100) if i % 2 == 0]")
            f.flush()
            yield f.name
        Path(f.name).unlink()

    @pytest.mark.asyncio
    async def test_suggest_improvements(self, command, temp_file):
        """Test improvement suggestions."""
        context = CommandContext(
            user_input=f"code suggest {temp_file}",
            args={"_positional": [temp_file]}
        )
        result = await command.execute(context)
        
        assert result.success
        assert "improvements" in result.data
        assert len(result.data["improvements"]) > 0
        assert any(i["category"] for i in result.data["improvements"])


class TestCodeRefactorCommand:
    """Test code refactoring command."""

    @pytest.fixture
    def command(self):
        return CodeRefactorCommand()

    @pytest.fixture
    def temp_file(self):
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""if x > 0:
    if y > 0:
        if z > 0:
            print('positive')
""")
            f.flush()
            yield f.name
        Path(f.name).unlink()

    @pytest.mark.asyncio
    async def test_refactor_suggestions(self, command, temp_file):
        """Test refactoring suggestions."""
        context = CommandContext(
            user_input=f"code refactor {temp_file}",
            args={"_positional": [temp_file]}
        )
        result = await command.execute(context)
        
        assert result.success
        assert "changes" in result.data
        assert len(result.data["changes"]) > 0

    @pytest.mark.asyncio
    async def test_refactor_with_pattern(self, command, temp_file):
        """Test refactoring with specific pattern."""
        context = CommandContext(
            user_input=f"code refactor {temp_file} --pattern simplify",
            args={"_positional": [temp_file], "pattern": "simplify"}
        )
        result = await command.execute(context)
        
        assert result.success
        assert result.data["pattern"] == "simplify"


class TestCodeTestCommand:
    """Test test generation command."""

    @pytest.fixture
    def command(self):
        return CodeTestCommand()

    @pytest.fixture
    def temp_file(self):
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def add(a, b):\n    return a + b")
            f.flush()
            yield f.name
        Path(f.name).unlink()

    @pytest.mark.asyncio
    async def test_generate_tests(self, command, temp_file):
        """Test test generation."""
        context = CommandContext(
            user_input=f"code test {temp_file}",
            args={"_positional": [temp_file]}
        )
        result = await command.execute(context)
        
        assert result.success
        assert "generated_tests" in result.data
        assert len(result.data["generated_tests"]) > 0

    @pytest.mark.asyncio
    async def test_test_file_naming(self, command, temp_file):
        """Test generated test file naming."""
        context = CommandContext(
            user_input=f"code test {temp_file}",
            args={"_positional": [temp_file]}
        )
        result = await command.execute(context)
        
        assert result.success
        test_file = result.data["test_file"]
        assert "_test" in test_file or ".test" in test_file


class TestCodeDocumentCommand:
    """Test documentation generation command."""

    @pytest.fixture
    def command(self):
        return CodeDocumentCommand()

    @pytest.fixture
    def temp_file(self):
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""class MyClass:
    def method1(self): pass
    def method2(self): pass
    
def function1(): pass
def function2(): pass""")
            f.flush()
            yield f.name
        Path(f.name).unlink()

    @pytest.mark.asyncio
    async def test_generate_docs(self, command, temp_file):
        """Test documentation generation."""
        context = CommandContext(
            user_input=f"code document {temp_file}",
            args={"_positional": [temp_file]}
        )
        result = await command.execute(context)
        
        assert result.success
        assert "sections" in result.data
        assert "api" in result.data["sections"]

    @pytest.mark.asyncio
    async def test_docs_api_section(self, command, temp_file):
        """Test API section in docs."""
        context = CommandContext(
            user_input=f"code document {temp_file}",
            args={"_positional": [temp_file]}
        )
        result = await command.execute(context)
        
        assert result.success
        api = result.data["sections"]["api"]
        assert api["classes"] > 0
        assert api["functions"] > 0


class TestDiffCommand:
    """Test diff command."""

    @pytest.fixture
    def command(self):
        return DiffCommand()

    @pytest.fixture
    def temp_files(self):
        """Create two temporary files."""
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f1:
            with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f2:
                f1.write("def hello():\n    print('hello')\n")
                f2.write("def hello():\n    print('hi')\n")
                f1.flush()
                f2.flush()
                yield f1.name, f2.name
        Path(f1.name).unlink()
        Path(f2.name).unlink()

    @pytest.mark.asyncio
    async def test_diff_basic(self, command, temp_files):
        """Test basic diff."""
        context = CommandContext(
            user_input=f"diff {temp_files[0]} {temp_files[1]}",
            args={"_positional": temp_files}
        )
        result = await command.execute(context)
        
        assert result.success
        assert result.data["file1"] == temp_files[0]
        assert result.data["file2"] == temp_files[1]

    @pytest.mark.asyncio
    async def test_diff_similarity(self, command, temp_files):
        """Test similarity calculation."""
        context = CommandContext(
            user_input=f"diff {temp_files[0]} {temp_files[1]}",
            args={"_positional": temp_files}
        )
        result = await command.execute(context)
        
        assert result.success
        assert "similarity" in result.data
        assert 0 <= result.data["similarity"] <= 100

    @pytest.mark.asyncio
    async def test_diff_validation(self, command):
        """Test validation requires two files."""
        context = CommandContext(
            user_input="diff /tmp/file1.py",
            args={"_positional": ["/tmp/file1.py"]}
        )
        result = await command.execute(context)
        
        assert not result.success


class TestMergeCommand:
    """Test merge command."""

    @pytest.fixture
    def command(self):
        return MergeCommand()

    @pytest.fixture
    def temp_files(self):
        """Create two temporary files."""
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f1:
            with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f2:
                f1.write("def func1(): pass\n")
                f2.write("def func2(): pass\n")
                f1.flush()
                f2.flush()
                yield f1.name, f2.name
        Path(f1.name).unlink()
        Path(f2.name).unlink()

    @pytest.mark.asyncio
    async def test_merge_basic(self, command, temp_files):
        """Test basic merge."""
        context = CommandContext(
            user_input=f"merge {temp_files[0]} {temp_files[1]}",
            args={"_positional": temp_files}
        )
        result = await command.execute(context)
        
        assert result.success
        assert result.data["file1"] == temp_files[0]
        assert result.data["file2"] == temp_files[1]

    @pytest.mark.asyncio
    async def test_merge_line_count(self, command, temp_files):
        """Test merged line count."""
        context = CommandContext(
            user_input=f"merge {temp_files[0]} {temp_files[1]}",
            args={"_positional": temp_files}
        )
        result = await command.execute(context)
        
        assert result.success
        assert result.data["merged_lines"] > 0
        assert result.data["merged_lines"] <= result.data["original_lines"]

    @pytest.mark.asyncio
    async def test_merge_with_output(self, command, temp_files):
        """Test merge with output file."""
        context = CommandContext(
            user_input=f"merge {temp_files[0]} {temp_files[1]} --output /tmp/merged.py",
            args={"_positional": temp_files, "output": "/tmp/merged.py"}
        )
        result = await command.execute(context)
        
        assert result.success
        assert result.data["output"] == "/tmp/merged.py"


class TestRevertCommand:
    """Test revert command."""

    @pytest.fixture
    def command(self):
        return RevertCommand()

    @pytest.fixture
    def temp_file(self):
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('hello')")
            f.flush()
            yield f.name
        Path(f.name).unlink()

    @pytest.mark.asyncio
    async def test_revert_basic(self, command, temp_file):
        """Test basic revert."""
        context = CommandContext(
            user_input=f"revert {temp_file}",
            args={"_positional": [temp_file]}
        )
        result = await command.execute(context)
        
        assert result.success
        assert result.data["file"] == temp_file
        assert result.data["status"] == "reverted"

    @pytest.mark.asyncio
    async def test_revert_to_version(self, command, temp_file):
        """Test revert to specific version."""
        context = CommandContext(
            user_input=f"revert {temp_file} --version v1.0",
            args={"_positional": [temp_file], "version": "v1.0"}
        )
        result = await command.execute(context)
        
        assert result.success
        assert result.data["version"] == "v1.0"

    @pytest.mark.asyncio
    async def test_revert_nonexistent(self, command):
        """Test revert of nonexistent file."""
        context = CommandContext(
            user_input="revert /nonexistent/file.py",
            args={"_positional": ["/nonexistent/file.py"]}
        )
        result = await command.execute(context)
        
        assert not result.success


class TestApplyCommand:
    """Test apply patch command."""

    @pytest.fixture
    def command(self):
        return ApplyCommand()

    @pytest.fixture
    def temp_file(self):
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def func(): pass")
            f.flush()
            yield f.name
        Path(f.name).unlink()

    @pytest.mark.asyncio
    async def test_apply_patch_basic(self, command, temp_file):
        """Test basic patch application."""
        context = CommandContext(
            user_input=f"apply patch {temp_file}",
            args={"_positional": ["patch", temp_file]}
        )
        result = await command.execute(context)
        
        assert result.success
        assert result.data["file"] == temp_file
        assert result.data["status"] == "applied"

    @pytest.mark.asyncio
    async def test_apply_patch_without_keyword(self, command, temp_file):
        """Test patch application without 'patch' keyword."""
        context = CommandContext(
            user_input=f"apply {temp_file}",
            args={"_positional": [temp_file]}
        )
        result = await command.execute(context)
        
        assert result.success

    @pytest.mark.asyncio
    async def test_apply_with_source(self, command, temp_file):
        """Test apply with source."""
        context = CommandContext(
            user_input=f"apply {temp_file} --source file.patch",
            args={"_positional": [temp_file], "source": "file.patch"}
        )
        result = await command.execute(context)
        
        assert result.success
        assert result.data["source"] == "file.patch"

    @pytest.mark.asyncio
    async def test_apply_patch_counts(self, command, temp_file):
        """Test patch change counts."""
        context = CommandContext(
            user_input=f"apply {temp_file}",
            args={"_positional": [temp_file]}
        )
        result = await command.execute(context)
        
        assert result.success
        data = result.data
        assert "lines_added" in data
        assert "lines_removed" in data
        assert "lines_modified" in data


class TestCodeCommandIntegration:
    """Integration tests for code commands."""

    @pytest.fixture
    def temp_file_with_complexity(self):
        """Create file with more complexity."""
        content = """
class DataProcessor:
    def __init__(self):
        self.data = []
    
    async def process(self, items):
        for item in items:
            try:
                result = await self._transform(item)
                self.data.append(result)
            except Exception as e:
                print(f"Error: {e}")
    
    async def _transform(self, item):
        # TODO: Add caching
        return item * 2
"""
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            yield f.name
        Path(f.name).unlink()

    @pytest.mark.asyncio
    async def test_analyze_then_suggest(self, temp_file_with_complexity):
        """Test analyzing then suggesting improvements."""
        analyze_cmd = CodeAnalyzeCommand()
        suggest_cmd = CodeSuggestCommand()
        
        context1 = CommandContext(
            user_input=f"code analyze {temp_file_with_complexity}",
            args={"_positional": [temp_file_with_complexity]}
        )
        analysis = await analyze_cmd.execute(context1)
        
        assert analysis.success
        
        context2 = CommandContext(
            user_input=f"code suggest {temp_file_with_complexity}",
            args={"_positional": [temp_file_with_complexity]}
        )
        suggestions = await suggest_cmd.execute(context2)
        
        assert suggestions.success

    @pytest.mark.asyncio
    async def test_explain_then_document(self, temp_file_with_complexity):
        """Test explaining then documenting."""
        explain_cmd = CodeExplainCommand()
        doc_cmd = CodeDocumentCommand()
        
        context1 = CommandContext(
            user_input=f"code explain {temp_file_with_complexity}",
            args={"_positional": [temp_file_with_complexity]}
        )
        explanation = await explain_cmd.execute(context1)
        
        assert explanation.success
        
        context2 = CommandContext(
            user_input=f"code document {temp_file_with_complexity}",
            args={"_positional": [temp_file_with_complexity]}
        )
        documentation = await doc_cmd.execute(context2)
        
        assert documentation.success


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
