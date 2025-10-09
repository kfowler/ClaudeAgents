#!/usr/bin/env python3
"""
Command Generator - Interactive tool for creating new ClaudeAgents workflow commands.

This tool guides you through creating a new workflow command with proper agent
orchestration, validation, and professional standards.

Usage:
    python3 tools/create_command.py

Features:
- Interactive prompts for all required fields
- Agent validation (ensures referenced agents exist)
- Category selection with smart defaults
- Template population with multi-phase orchestration
- Automatic file creation in correct directory
- Validation check before completion
"""

import os
import sys
import re
from pathlib import Path
from typing import Optional, List, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    from rich import print as rprint
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


class CommandGenerator:
    """Interactive command generator"""

    CATEGORIES = {
        "development": "Code-focused workflows (implementation, design, refactoring)",
        "quality": "Testing, security, performance, accessibility workflows",
        "deployment": "Infrastructure, deployment, CI/CD workflows",
        "specialized": "Language or framework-specific workflows",
        "workflows": "Complex multi-agent orchestration workflows"
    }

    def __init__(self):
        self.console = Console() if HAS_RICH else None
        self.commands_dir = Path(__file__).parent.parent / "commands"
        self.agents_dir = Path(__file__).parent.parent / "agents"
        self.template_path = self.commands_dir / "COMMAND_TEMPLATE.md"

        # Load available agents
        self.available_agents = self._load_available_agents()

    def _load_available_agents(self) -> List[str]:
        """Load list of available agents"""
        agents = []
        for agent_file in self.agents_dir.glob("*.md"):
            if agent_file.stem not in ["AGENT_TEMPLATE", "AGENT_PROFESSIONAL_BEHAVIOR"]:
                agents.append(agent_file.stem)
        return sorted(agents)

    def _print(self, message: str, style: str = ""):
        """Print with optional rich formatting"""
        if self.console and HAS_RICH:
            self.console.print(message, style=style)
        else:
            print(message)

    def _prompt(self, message: str, choices: Optional[List[str]] = None, default: Optional[str] = None) -> str:
        """Prompt for input with optional choices"""
        if self.console and HAS_RICH:
            if choices:
                return Prompt.ask(message, choices=choices, default=default)
            else:
                return Prompt.ask(message, default=default or "")
        else:
            # Fallback to basic input
            prompt_text = message
            if choices:
                prompt_text += f" ({'/'.join(choices)})"
            if default:
                prompt_text += f" [{default}]"
            prompt_text += ": "

            response = input(prompt_text).strip()
            return response or default or ""

    def _confirm(self, message: str, default: bool = True) -> bool:
        """Confirm with yes/no"""
        if self.console and HAS_RICH:
            return Confirm.ask(message, default=default)
        else:
            response = input(f"{message} (y/n) [{('y' if default else 'n')}]: ").strip().lower()
            if not response:
                return default
            return response in ['y', 'yes']

    def validate_name(self, name: str, category: str) -> bool:
        """Validate command name format"""
        # Must be lowercase with hyphens
        if not re.match(r'^[a-z][a-z0-9\-]*[a-z0-9]$', name):
            return False

        # Check for existing command in this category
        command_file = self.commands_dir / category / f"{name}.md"
        if command_file.exists():
            self._print(f"❌ Command '{name}' already exists in {category}/!", style="bold red")
            return False

        return True

    def validate_agent(self, agent_name: str) -> bool:
        """Validate that agent exists"""
        return agent_name in self.available_agents

    def prompt_category(self) -> str:
        """Prompt for command category"""
        self._print("\n📁 Command Category", style="bold cyan")

        for i, (category, description) in enumerate(self.CATEGORIES.items(), 1):
            self._print(f"  {i}. {category}: {description}", style="dim")

        while True:
            category = self._prompt("Category", choices=list(self.CATEGORIES.keys()), default="development")

            if category in self.CATEGORIES:
                return category

            self._print(f"❌ Invalid category. Choose from: {', '.join(self.CATEGORIES.keys())}", style="red")

    def prompt_name(self, category: str) -> str:
        """Prompt for command name"""
        while True:
            self._print("\n📝 Command Name", style="bold cyan")
            self._print(f"Category: {category}/")
            self._print("Format: lowercase-with-hyphens (e.g., 'api-security-audit')")

            name = self._prompt("Command name")

            if not name:
                self._print("❌ Name cannot be empty", style="red")
                continue

            if not self.validate_name(name, category):
                self._print("❌ Invalid name format or command already exists", style="red")
                self._print("Requirements:", style="yellow")
                self._print("  • Lowercase letters, numbers, and hyphens only")
                self._print("  • Must start with letter, end with letter or number")
                self._print("  • Cannot start/end with hyphen")
                continue

            return name

    def prompt_description(self) -> str:
        """Prompt for command description"""
        while True:
            self._print("\n📝 Command Description", style="bold cyan")
            self._print("Brief description of what this command accomplishes and when to use it")
            self._print("Example: 'Comprehensive security audit combining vulnerability scanning, code review, and compliance checks'")

            description = self._prompt("Description")

            if not description:
                self._print("❌ Description cannot be empty", style="red")
                continue

            if len(description) < 30:
                self._print(f"❌ Description too short (min 30 characters, currently: {len(description)})", style="red")
                continue

            return description

    def prompt_agents(self) -> List[Dict[str, str]]:
        """Prompt for agents to use in workflow phases"""
        phases = []

        self._print("\n🤖 Agent Orchestration", style="bold cyan")
        self._print("Define the workflow phases and agents")
        self._print(f"Available agents: {', '.join(self.available_agents[:10])}...\n", style="dim")

        phase_num = 1
        while True:
            self._print(f"\n--- Phase {phase_num} ---", style="bold yellow")

            # Agent selection
            while True:
                agent = self._prompt(f"Agent for Phase {phase_num} (or 'done' to finish)")

                if agent.lower() == 'done':
                    if phase_num < 2:
                        self._print("❌ At least 2 phases required", style="red")
                        continue
                    return phases

                if not self.validate_agent(agent):
                    self._print(f"❌ Agent '{agent}' not found", style="red")
                    self._print(f"Available: {', '.join(self.available_agents[:20])}...", style="dim")
                    continue

                break

            # Phase description
            phase_desc = self._prompt(f"What will {agent} do in this phase?")
            if not phase_desc:
                phase_desc = "Complete the assigned tasks"

            # Rationale
            rationale = self._prompt(f"Why use {agent} for this phase?")
            if not rationale:
                rationale = f"Best suited for these specific tasks"

            phases.append({
                "phase_num": phase_num,
                "agent": agent,
                "description": phase_desc,
                "rationale": rationale
            })

            phase_num += 1

            if not self._confirm(f"Add Phase {phase_num}?", default=True):
                if phase_num < 3:  # At least 2 phases required
                    self._print("⚠️  At least 2 phases required", style="yellow")
                    continue
                break

        return phases

    def create_command_content(self, metadata: Dict) -> str:
        """Create command file content from metadata"""
        # Read template
        with open(self.template_path, 'r') as f:
            template = f.read()

        # Replace basic placeholders
        content = template.replace("command-name", metadata["name"])
        content = content.replace("Brief description of what this command accomplishes and when to use it", metadata["description"])

        # Generate phase sections
        phases_text = ""
        for phase in metadata["phases"]:
            phase_template = f"""
### **Phase {phase['phase_num']}: {phase['description'][:50]}**
Deploy `{phase['agent']}` to:
- {phase['description']}
- [Add specific deliverables]
- [Add quality criteria]
- [Add integration points]

**Why this agent:** {phase['rationale']}
"""
            phases_text += phase_template

        # Replace multi-agent orchestration section
        orchestration_pattern = r"### \*\*Phase 1:.*?### \*\*Phase 3:.*?\n\n\*\*Why this agent:\*\* Justification for using this agent\."
        content = re.sub(orchestration_pattern, phases_text.strip(), content, flags=re.DOTALL)

        # Generate execution flow diagram
        flow_text = "```\n"
        for i, phase in enumerate(metadata["phases"]):
            flow_text += f"Phase {phase['phase_num']} ({phase['agent']})\n"
            if i < len(metadata["phases"]) - 1:
                flow_text += "    ↓\n"
        flow_text += "    ↓\n"
        flow_text += "Deliverables\n```"

        # Replace execution flow section
        flow_pattern = r"```\nPhase 1 \(agent-name\).*?```"
        content = re.sub(flow_pattern, flow_text, content, flags=re.DOTALL)

        return content

    def run(self):
        """Run interactive command generator"""
        if self.console and HAS_RICH:
            self.console.clear()

        self._print("\n" + "="*70, style="bold blue")
        self._print("⚡  CLAUDEAGENTS COMMAND GENERATOR", style="bold blue")
        self._print("="*70 + "\n", style="bold blue")

        self._print("This tool will guide you through creating a new workflow command.", style="dim")
        self._print("Press Ctrl+C at any time to cancel.\n", style="dim")

        try:
            # Collect metadata
            category = self.prompt_category()
            name = self.prompt_name(category)
            description = self.prompt_description()
            phases = self.prompt_agents()

            # Summary
            self._print("\n" + "="*70, style="bold cyan")
            self._print("📋 COMMAND SUMMARY", style="bold cyan")
            self._print("="*70, style="bold cyan")
            self._print(f"Category: {category}/")
            self._print(f"Name: {name}")
            self._print(f"Description: {description}")
            self._print(f"\nPhases ({len(phases)}):")
            for phase in phases:
                self._print(f"  Phase {phase['phase_num']}: {phase['agent']} - {phase['description'][:60]}...")
            self._print("="*70 + "\n", style="bold cyan")

            # Confirm creation
            if not self._confirm("Create this command?", default=True):
                self._print("\n❌ Command creation cancelled", style="yellow")
                return

            # Create command file
            metadata = {
                "category": category,
                "name": name,
                "description": description,
                "phases": phases
            }

            content = self.create_command_content(metadata)

            # Ensure category directory exists
            category_dir = self.commands_dir / category
            category_dir.mkdir(exist_ok=True)

            command_file = category_dir / f"{name}.md"

            with open(command_file, 'w') as f:
                f.write(content)

            self._print(f"\n✅ Command created: {command_file}", style="bold green")

            # Next steps
            self._print("\n" + "="*70, style="bold blue")
            self._print("📝 NEXT STEPS", style="bold blue")
            self._print("="*70, style="bold blue")
            self._print(f"1. Edit {command_file} to complete the template")
            self._print("2. Add specific deliverables for each phase")
            self._print("3. Define success criteria")
            self._print("4. Add any prerequisites or common issues")
            self._print("5. Test the command with Claude Code: /{category}:{name}")
            self._print(f"6. Commit: git add commands/{category}/{name}.md && git commit -m 'Add {name} command'")
            self._print("="*70 + "\n", style="bold blue")

        except KeyboardInterrupt:
            self._print("\n\n❌ Command creation cancelled", style="yellow")
            sys.exit(1)
        except Exception as e:
            self._print(f"\n\n❌ Error creating command: {e}", style="bold red")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Main entry point"""
    generator = CommandGenerator()
    generator.run()


if __name__ == "__main__":
    main()
