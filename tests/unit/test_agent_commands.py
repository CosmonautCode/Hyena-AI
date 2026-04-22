"""Tests for agent commands."""

import pytest
import asyncio
import shutil
from pathlib import Path
from datetime import datetime

from app.cli.commands.agents import (
    InitAgentCommand,
    ListAgentsCommand,
    LoadAgentCommand,
    RunAgentCommand,
    EditAgentCommand,
    DeleteAgentCommand,
    CloneAgentCommand,
    ExportAgentCommand,
)
from app.cli.commands.base import CommandContext


@pytest.fixture(autouse=True)
def cleanup_agents():
    """Clean up agents directory before and after each test."""
    agents_dir = Path("app/data/agents")
    try:
        if agents_dir.exists():
            shutil.rmtree(agents_dir)
    except:
        pass
    yield
    try:
        if agents_dir.exists():
            shutil.rmtree(agents_dir)
    except:
        pass


class TestInitAgentCommand:
    """Test /agent init command."""

    @pytest.mark.asyncio
    async def test_init_basic(self):
        """Test basic agent initialization."""
        cmd = InitAgentCommand()
        context = CommandContext(
            "agent init test_agent",
            {"name": "test_agent", "description": "Test Agent"}
        )

        result = await cmd.execute(context)
        assert result.success
        assert "test_agent" in result.message

    @pytest.mark.asyncio
    async def test_init_with_type(self):
        """Test agent initialization with type."""
        cmd = InitAgentCommand()
        context = CommandContext(
            "agent init advanced_agent --type advanced",
            {"name": "advanced_agent", "type": "advanced"}
        )

        result = await cmd.execute(context)
        assert result.success

    @pytest.mark.asyncio
    async def test_init_duplicate(self):
        """Test initializing duplicate agent fails."""
        cmd = InitAgentCommand()
        context1 = CommandContext(
            "agent init test_agent",
            {"name": "test_agent"}
        )
        context2 = CommandContext(
            "agent init test_agent",
            {"name": "test_agent"}
        )

        result1 = await cmd.execute(context1)
        assert result1.success

        result2 = await cmd.execute(context2)
        assert not result2.success

    @pytest.mark.asyncio
    async def test_init_missing_name(self):
        """Test initialization without agent name fails."""
        cmd = InitAgentCommand()
        context = CommandContext("agent init", {})

        result = await cmd.execute(context)
        assert not result.success


class TestListAgentsCommand:
    """Test /agent list command."""

    @pytest.mark.asyncio
    async def test_list_empty(self):
        """Test listing agents when none exist."""
        cmd = ListAgentsCommand()
        context = CommandContext("agent list", {})

        result = await cmd.execute(context)
        assert result.success

    @pytest.mark.asyncio
    async def test_list_multiple(self):
        """Test listing multiple agents."""
        init_cmd = InitAgentCommand()
        list_cmd = ListAgentsCommand()

        # Create agents
        for i in range(3):
            ctx = CommandContext(
                f"agent init agent_{i}",
                {"name": f"agent_{i}"}
            )
            await init_cmd.execute(ctx)

        context = CommandContext("agent list", {})
        result = await list_cmd.execute(context)

        assert result.success

    @pytest.mark.asyncio
    async def test_list_filter_by_type(self):
        """Test listing agents filtered by type."""
        init_cmd = InitAgentCommand()
        list_cmd = ListAgentsCommand()

        # Create agents with different types
        await init_cmd.execute(
            CommandContext("agent init simple_agent", {"name": "simple_agent"})
        )
        await init_cmd.execute(
            CommandContext(
                "agent init advanced_agent --type advanced", 
                {"name": "advanced_agent", "type": "advanced"}
            )
        )

        context = CommandContext(
            "agent list --type advanced", 
            {"type": "advanced"}
        )
        result = await list_cmd.execute(context)

        assert result.success


class TestLoadAgentCommand:
    """Test /agent load command."""

    @pytest.mark.asyncio
    async def test_load_existing(self):
        """Test loading an existing agent."""
        init_cmd = InitAgentCommand()
        load_cmd = LoadAgentCommand()

        await init_cmd.execute(
            CommandContext(
                "agent init test_agent",
                {"name": "test_agent", "description": "Test Agent"}
            )
        )

        context = CommandContext("agent load test_agent", {"name": "test_agent"})
        result = await load_cmd.execute(context)

        assert result.success

    @pytest.mark.asyncio
    async def test_load_nonexistent(self):
        """Test loading a nonexistent agent."""
        cmd = LoadAgentCommand()
        context = CommandContext("agent load nonexistent", {"name": "nonexistent"})

        result = await cmd.execute(context)
        assert not result.success

    @pytest.mark.asyncio
    async def test_load_missing_name(self):
        """Test load without agent name fails."""
        cmd = LoadAgentCommand()
        context = CommandContext("agent load", {})

        result = await cmd.execute(context)
        assert not result.success


class TestRunAgentCommand:
    """Test /agent run command."""

    @pytest.mark.asyncio
    async def test_run_existing(self):
        """Test running an existing agent."""
        init_cmd = InitAgentCommand()
        run_cmd = RunAgentCommand()

        await init_cmd.execute(
            CommandContext("agent init test_agent", {"name": "test_agent"})
        )

        context = CommandContext(
            "agent run test_agent",
            {"name": "test_agent", "input": "test_input"}
        )
        result = await run_cmd.execute(context)

        assert result.success

    @pytest.mark.asyncio
    async def test_run_nonexistent(self):
        """Test running a nonexistent agent."""
        cmd = RunAgentCommand()
        context = CommandContext("agent run nonexistent", {"name": "nonexistent"})

        result = await cmd.execute(context)
        assert not result.success


class TestEditAgentCommand:
    """Test /agent edit command."""

    @pytest.mark.asyncio
    async def test_edit_description(self):
        """Test editing agent description."""
        init_cmd = InitAgentCommand()
        edit_cmd = EditAgentCommand()

        await init_cmd.execute(
            CommandContext("agent init test_agent", {"name": "test_agent"})
        )

        context = CommandContext(
            "agent edit test_agent",
            {"name": "test_agent", "description": "Updated Description"}
        )
        result = await edit_cmd.execute(context)

        assert result.success

    @pytest.mark.asyncio
    async def test_edit_type(self):
        """Test editing agent type."""
        init_cmd = InitAgentCommand()
        edit_cmd = EditAgentCommand()

        await init_cmd.execute(
            CommandContext("agent init test_agent", {"name": "test_agent"})
        )

        context = CommandContext(
            "agent edit test_agent --type advanced",
            {"name": "test_agent", "type": "advanced"}
        )
        result = await edit_cmd.execute(context)

        assert result.success

    @pytest.mark.asyncio
    async def test_edit_nonexistent(self):
        """Test editing a nonexistent agent."""
        cmd = EditAgentCommand()
        context = CommandContext("agent edit nonexistent", {"name": "nonexistent"})

        result = await cmd.execute(context)
        assert not result.success


class TestDeleteAgentCommand:
    """Test /agent delete command."""

    @pytest.mark.asyncio
    async def test_delete_existing(self):
        """Test deleting an existing agent."""
        init_cmd = InitAgentCommand()
        delete_cmd = DeleteAgentCommand()

        await init_cmd.execute(
            CommandContext("agent init test_agent", {"name": "test_agent"})
        )

        context = CommandContext("agent delete test_agent", {"name": "test_agent"})
        result = await delete_cmd.execute(context)

        assert result.success

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self):
        """Test deleting a nonexistent agent."""
        cmd = DeleteAgentCommand()
        context = CommandContext("agent delete nonexistent", {"name": "nonexistent"})

        result = await cmd.execute(context)
        assert not result.success


class TestCloneAgentCommand:
    """Test /agent clone command."""

    @pytest.mark.asyncio
    async def test_clone_existing(self):
        """Test cloning an existing agent."""
        init_cmd = InitAgentCommand()
        clone_cmd = CloneAgentCommand()

        await init_cmd.execute(
            CommandContext("agent init source_agent", {"name": "source_agent"})
        )

        context = CommandContext(
            "agent clone source_agent cloned_agent",
            {"source": "source_agent", "target": "cloned_agent", "_positional": ["source_agent", "cloned_agent"]}
        )
        result = await clone_cmd.execute(context)

        assert result.success

    @pytest.mark.asyncio
    async def test_clone_nonexistent_source(self):
        """Test cloning from nonexistent source."""
        cmd = CloneAgentCommand()
        context = CommandContext(
            "agent clone nonexistent target",
            {"source": "nonexistent", "target": "target", "_positional": ["nonexistent", "target"]}
        )

        result = await cmd.execute(context)
        assert not result.success

    @pytest.mark.asyncio
    async def test_clone_to_existing_target(self):
        """Test cloning to an existing target."""
        init_cmd = InitAgentCommand()
        clone_cmd = CloneAgentCommand()

        await init_cmd.execute(
            CommandContext("agent init agent1", {"name": "agent1"})
        )
        await init_cmd.execute(
            CommandContext("agent init agent2", {"name": "agent2"})
        )

        context = CommandContext(
            "agent clone agent1 agent2",
            {"source": "agent1", "target": "agent2", "_positional": ["agent1", "agent2"]}
        )
        result = await clone_cmd.execute(context)

        assert not result.success


class TestExportAgentCommand:
    """Test /agent export command."""

    @pytest.mark.asyncio
    async def test_export_json(self):
        """Test exporting agent as JSON."""
        init_cmd = InitAgentCommand()
        export_cmd = ExportAgentCommand()

        await init_cmd.execute(
            CommandContext("agent init test_agent", {"name": "test_agent"})
        )

        context = CommandContext(
            "agent export test_agent --format json",
            {"name": "test_agent", "format": "json"}
        )
        result = await export_cmd.execute(context)

        assert result.success

    @pytest.mark.asyncio
    async def test_export_yaml(self):
        """Test exporting agent as YAML."""
        init_cmd = InitAgentCommand()
        export_cmd = ExportAgentCommand()

        await init_cmd.execute(
            CommandContext("agent init test_agent", {"name": "test_agent"})
        )

        context = CommandContext(
            "agent export test_agent --format yaml",
            {"name": "test_agent", "format": "yaml"}
        )
        result = await export_cmd.execute(context)

        assert result.success

    @pytest.mark.asyncio
    async def test_export_nonexistent(self):
        """Test exporting a nonexistent agent."""
        cmd = ExportAgentCommand()
        context = CommandContext("agent export nonexistent", {"name": "nonexistent"})

        result = await cmd.execute(context)
        assert not result.success
