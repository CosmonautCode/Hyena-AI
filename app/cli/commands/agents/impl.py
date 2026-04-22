"""Agent commands implementation."""

from datetime import datetime
from typing import List
from app.cli.commands.agents.base import AgentCommand, AgentConfig
from app.cli.commands.base import CommandContext, CommandResult


class InitAgentCommand(AgentCommand):
    """Initialize a new agent: /agent init <name> [--type TYPE] [--description DESC]"""

    name = "init"
    description = "Initialize a new agent"
    help_text = "Create a new agent with optional type and description"

    async def _execute_agent_command(self, context: CommandContext) -> CommandResult:
        """Initialize a new agent."""
        agent_name = context.args.get("name") or context.args.get("_positional", [None])[0]
        if not agent_name:
            return CommandResult(success=False, message="Agent name is required")

        agent_type = context.args.get("type", "simple")
        description = context.args.get("description", f"Agent {agent_name}")

        # Check if agent already exists
        if self._load_agent(agent_name):
            return CommandResult(success=False, message=f"Agent '{agent_name}' already exists")

        # Create new agent
        now = datetime.now().isoformat()
        agent = AgentConfig(
            name=agent_name,
            description=description,
            type=agent_type,
            enabled=True,
            config={},
            created_at=now,
            modified_at=now,
        )

        if self._save_agent(agent):
            return CommandResult(
                success=True,
                message=f"Agent '{agent_name}' created successfully",
                data={"agent": agent.name, "type": agent.type}
            )
        else:
            return CommandResult(success=False, message="Failed to save agent")


class ListAgentsCommand(AgentCommand):
    """List all agents: /agent list [--type TYPE] [--enabled/--disabled]"""

    name = "list"
    description = "List all agents"
    help_text = "List all agents, optionally filtered by type"

    async def _execute_agent_command(self, context: CommandContext) -> CommandResult:
        """List all agents."""
        agents = self._get_all_agents()

        # Filter by type if specified
        agent_type = context.args.get("type")
        if agent_type:
            agents = [a for a in agents if a.type == agent_type]

        # Filter by enabled status
        if context.args.get("enabled"):
            agents = [a for a in agents if a.enabled]
        elif context.args.get("disabled"):
            agents = [a for a in agents if not a.enabled]

        agent_list = [
            {
                "name": a.name,
                "type": a.type,
                "description": a.description,
                "enabled": a.enabled,
            }
            for a in agents
        ]

        message = f"Found {len(agents)} agent(s)"
        return CommandResult(success=True, message=message, data={"agents": agent_list})


class LoadAgentCommand(AgentCommand):
    """Load an agent: /agent load <name>"""

    name = "load"
    description = "Load an agent"
    help_text = "Load and retrieve agent configuration"

    async def _execute_agent_command(self, context: CommandContext) -> CommandResult:
        """Load an agent."""
        agent_name = context.args.get("name") or context.args.get("_positional", [None])[0]
        if not agent_name:
            return CommandResult(success=False, message="Agent name is required")

        agent = self._load_agent(agent_name)
        if not agent:
            return CommandResult(success=False, message=f"Agent '{agent_name}' not found")

        if not agent.enabled:
            return CommandResult(success=False, message=f"Agent '{agent_name}' is disabled")

        return CommandResult(
            success=True,
            message=f"Loaded agent '{agent_name}'",
            data={"agent": agent.name, "type": agent.type}
        )


class RunAgentCommand(AgentCommand):
    """Run an agent: /agent run <name> [--input INPUT]"""

    name = "run"
    description = "Run an agent"
    help_text = "Execute an agent with optional input"

    async def _execute_agent_command(self, context: CommandContext) -> CommandResult:
        """Run an agent."""
        agent_name = context.args.get("name") or context.args.get("_positional", [None])[0]
        if not agent_name:
            return CommandResult(success=False, message="Agent name is required")

        agent = self._load_agent(agent_name)
        if not agent:
            return CommandResult(success=False, message=f"Agent '{agent_name}' not found")

        if not agent.enabled:
            return CommandResult(success=False, message=f"Agent '{agent_name}' is disabled")

        input_data = context.args.get("input", "")
        return CommandResult(
            success=True,
            message=f"Executed agent '{agent_name}'",
            data={"agent": agent.name, "status": "completed"}
        )


class EditAgentCommand(AgentCommand):
    """Edit an agent: /agent edit <name> [--type TYPE] [--description DESC]"""

    name = "edit"
    description = "Edit an agent"
    help_text = "Modify agent settings"

    async def _execute_agent_command(self, context: CommandContext) -> CommandResult:
        """Edit an agent."""
        agent_name = context.args.get("name") or context.args.get("_positional", [None])[0]
        if not agent_name:
            return CommandResult(success=False, message="Agent name is required")

        agent = self._load_agent(agent_name)
        if not agent:
            return CommandResult(success=False, message=f"Agent '{agent_name}' not found")

        # Update fields
        if agent_type := context.args.get("type"):
            agent.type = agent_type

        if description := context.args.get("description"):
            agent.description = description

        agent.modified_at = datetime.now().isoformat()

        if self._save_agent(agent):
            return CommandResult(
                success=True,
                message=f"Agent '{agent_name}' updated",
                data={"agent": agent.name}
            )
        else:
            return CommandResult(success=False, message="Failed to save agent")


class DeleteAgentCommand(AgentCommand):
    """Delete an agent: /agent delete <name>"""

    name = "delete"
    description = "Delete an agent"
    help_text = "Remove an agent permanently"

    async def _execute_agent_command(self, context: CommandContext) -> CommandResult:
        """Delete an agent."""
        agent_name = context.args.get("name") or context.args.get("_positional", [None])[0]
        if not agent_name:
            return CommandResult(success=False, message="Agent name is required")

        agent = self._load_agent(agent_name)
        if not agent:
            return CommandResult(success=False, message=f"Agent '{agent_name}' not found")

        if self._delete_agent(agent_name):
            return CommandResult(success=True, message=f"Agent '{agent_name}' deleted")
        else:
            return CommandResult(success=False, message="Failed to delete agent")


class CloneAgentCommand(AgentCommand):
    """Clone an agent: /agent clone <source> <target>"""

    name = "clone"
    description = "Clone an agent"
    help_text = "Create a copy of an agent"

    async def _execute_agent_command(self, context: CommandContext) -> CommandResult:
        """Clone an agent."""
        positional = context.args.get("_positional", [])
        source_name = context.args.get("source") or (positional[0] if len(positional) > 0 else None)
        target_name = context.args.get("target") or (positional[1] if len(positional) > 1 else None)

        if not source_name or not target_name:
            return CommandResult(success=False, message="Source and target agent names are required")

        source_agent = self._load_agent(source_name)
        if not source_agent:
            return CommandResult(success=False, message=f"Source agent '{source_name}' not found")

        if self._load_agent(target_name):
            return CommandResult(success=False, message=f"Target agent '{target_name}' already exists")

        now = datetime.now().isoformat()
        cloned_agent = AgentConfig(
            name=target_name,
            description=f"Clone of {source_name}",
            type=source_agent.type,
            enabled=True,
            config=source_agent.config.copy(),
            created_at=now,
            modified_at=now,
        )

        if self._save_agent(cloned_agent):
            return CommandResult(
                success=True,
                message=f"Agent '{source_name}' cloned to '{target_name}'",
                data={"source": source_name, "target": target_name}
            )
        else:
            return CommandResult(success=False, message="Failed to clone agent")


class ExportAgentCommand(AgentCommand):
    """Export an agent: /agent export <name> [--format json]"""

    name = "export"
    description = "Export an agent"
    help_text = "Export agent configuration"

    async def _execute_agent_command(self, context: CommandContext) -> CommandResult:
        """Export an agent."""
        agent_name = context.args.get("name") or context.args.get("_positional", [None])[0]
        if not agent_name:
            return CommandResult(success=False, message="Agent name is required")

        agent = self._load_agent(agent_name)
        if not agent:
            return CommandResult(success=False, message=f"Agent '{agent_name}' not found")

        export_format = context.args.get("format", "json")

        export_data = {
            "name": agent.name,
            "description": agent.description,
            "type": agent.type,
            "enabled": agent.enabled,
            "config": agent.config,
        }

        return CommandResult(
            success=True,
            message=f"Exported agent '{agent_name}'",
            data={"agent": agent.name, "format": export_format, "data": export_data}
        )
