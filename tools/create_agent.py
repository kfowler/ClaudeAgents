#!/usr/bin/env python3
"""
Agent Generator - Interactive tool for creating new ClaudeAgents agents.

This tool guides you through creating a new agent with proper structure,
validation, and professional standards.

Usage:
    python3 tools/create_agent.py

Features:
- Interactive prompts for all required fields
- Validation of agent metadata
- Model/complexity recommendations
- Template population
- Automatic file creation
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


class AgentGenerator:
    """Interactive agent generator"""

    VALID_COLORS = [
        "blue", "green", "purple", "red", "orange", "cyan", "teal",
        "indigo", "violet", "crimson", "amber", "emerald", "lavender",
        "rose", "navy", "gold", "silver", "bronze"
    ]

    VALID_MODELS = ["haiku", "sonnet", "opus"]
    VALID_COMPLEXITY = ["low", "medium", "high"]

    MODEL_DESCRIPTIONS = {
        "haiku": "Fast, low-cost. Best for creative tasks, simple patterns, quick operations.",
        "sonnet": "Balanced. Best for standard development, code review, implementation.",
        "opus": "Maximum reasoning. Best for complex analysis, critical decisions, security."
    }

    COMPLEXITY_DESCRIPTIONS = {
        "low": "Single-step tasks, <30s execution, minimal context (<4K tokens)",
        "medium": "Multi-step workflows, 1-5 min tasks, standard development (4K-32K tokens)",
        "high": "Complex analysis, 5+ min tasks, large codebase analysis (32K+ tokens)"
    }

    def __init__(self):
        self.console = Console() if HAS_RICH else None
        self.agents_dir = Path(__file__).parent.parent / "agents"
        self.template_path = self.agents_dir / "AGENT_TEMPLATE.md"

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

    def validate_name(self, name: str) -> bool:
        """Validate agent name format"""
        # Must be lowercase with hyphens
        if not re.match(r'^[a-z][a-z0-9\-]*[a-z0-9]$', name):
            return False

        # Check for existing agent
        agent_file = self.agents_dir / f"{name}.md"
        if agent_file.exists():
            self._print(f"❌ Agent '{name}' already exists!", style="bold red")
            return False

        return True

    def validate_description(self, description: str) -> bool:
        """Validate description length"""
        return 50 <= len(description) <= 500

    def prompt_name(self) -> str:
        """Prompt for agent name"""
        while True:
            self._print("\n📝 Agent Name", style="bold cyan")
            self._print("Format: lowercase-with-hyphens (e.g., 'data-visualization-specialist')")

            name = self._prompt("Agent name")

            if not name:
                self._print("❌ Name cannot be empty", style="red")
                continue

            if not self.validate_name(name):
                self._print("❌ Invalid name format or agent already exists", style="red")
                self._print("Requirements:", style="yellow")
                self._print("  • Lowercase letters, numbers, and hyphens only")
                self._print("  • Must start with letter, end with letter or number")
                self._print("  • Cannot start/end with hyphen")
                continue

            return name

    def prompt_description(self) -> str:
        """Prompt for agent description"""
        while True:
            self._print("\n📝 Agent Description", style="bold cyan")
            self._print("50-500 characters describing the agent's purpose and expertise")
            self._print("Example: 'Expert in React/Next.js development, full-stack architecture, and modern web applications'")

            description = self._prompt("Description")

            if not description:
                self._print("❌ Description cannot be empty", style="red")
                continue

            if not self.validate_description(description):
                self._print(f"❌ Description must be 50-500 characters (currently: {len(description)})", style="red")
                continue

            return description

    def prompt_color(self) -> str:
        """Prompt for agent color"""
        self._print("\n🎨 Agent Color", style="bold cyan")
        self._print(f"Available colors: {', '.join(self.VALID_COLORS[:10])}...")

        while True:
            color = self._prompt("Color", choices=self.VALID_COLORS, default="blue")

            if color in self.VALID_COLORS:
                return color

            self._print(f"❌ Invalid color. Choose from: {', '.join(self.VALID_COLORS)}", style="red")

    def prompt_model(self) -> str:
        """Prompt for model tier"""
        self._print("\n🧠 Model Selection", style="bold cyan")

        for model, desc in self.MODEL_DESCRIPTIONS.items():
            self._print(f"  • {model.upper()}: {desc}", style="dim")

        while True:
            model = self._prompt("Model tier", choices=self.VALID_MODELS, default="sonnet")

            if model in self.VALID_MODELS:
                return model

            self._print(f"❌ Invalid model. Choose from: {', '.join(self.VALID_MODELS)}", style="red")

    def prompt_complexity(self) -> str:
        """Prompt for computational complexity"""
        self._print("\n⚙️ Computational Complexity", style="bold cyan")

        for complexity, desc in self.COMPLEXITY_DESCRIPTIONS.items():
            self._print(f"  • {complexity.upper()}: {desc}", style="dim")

        while True:
            complexity = self._prompt("Complexity", choices=self.VALID_COMPLEXITY, default="medium")

            if complexity in self.VALID_COMPLEXITY:
                return complexity

            self._print(f"❌ Invalid complexity. Choose from: {', '.join(self.VALID_COMPLEXITY)}", style="red")

    def get_recommendations(self, description: str) -> Dict[str, str]:
        """Get model/complexity recommendations based on description"""
        description_lower = description.lower()

        # Model recommendations
        if any(word in description_lower for word in ["creative", "writing", "design", "artistic", "comedy", "visual"]):
            model_rec = "haiku"
            model_reason = "Creative tasks work well with Haiku"
        elif any(word in description_lower for word in ["security", "audit", "critical", "architecture review", "complex analysis"]):
            model_rec = "opus"
            model_reason = "Critical analysis requires Opus"
        else:
            model_rec = "sonnet"
            model_reason = "Standard development tasks use Sonnet"

        # Complexity recommendations
        if any(word in description_lower for word in ["simple", "quick", "fast", "basic", "format"]):
            complexity_rec = "low"
            complexity_reason = "Simple tasks have low complexity"
        elif any(word in description_lower for word in ["complex", "analysis", "large", "deep", "comprehensive"]):
            complexity_rec = "high"
            complexity_reason = "Complex analysis requires high complexity"
        else:
            complexity_rec = "medium"
            complexity_reason = "Standard tasks have medium complexity"

        return {
            "model": model_rec,
            "model_reason": model_reason,
            "complexity": complexity_rec,
            "complexity_reason": complexity_reason
        }

    def create_agent_content(self, metadata: Dict) -> str:
        """Create agent file content from metadata"""
        # Read template
        with open(self.template_path, 'r') as f:
            template = f.read()

        # Replace placeholders
        content = template.replace("agent-name-here", metadata["name"])
        content = content.replace('Brief description (50-500 chars) of agent\'s purpose and expertise. Use quotes if description contains colons or special characters.', metadata["description"])
        content = content.replace("color: blue", f"color: {metadata['color']}")
        content = content.replace("model: sonnet", f"model: {metadata['model']}")
        content = content.replace("computational_complexity: medium", f"computational_complexity: {metadata['complexity']}")

        return content

    def run(self):
        """Run interactive agent generator"""
        if self.console and HAS_RICH:
            self.console.clear()

        self._print("\n" + "="*70, style="bold blue")
        self._print("🤖  CLAUDEAGENTS AGENT GENERATOR", style="bold blue")
        self._print("="*70 + "\n", style="bold blue")

        self._print("This tool will guide you through creating a new agent.", style="dim")
        self._print("Press Ctrl+C at any time to cancel.\n", style="dim")

        try:
            # Collect metadata
            name = self.prompt_name()
            description = self.prompt_description()

            # Get recommendations
            recommendations = self.get_recommendations(description)

            self._print("\n💡 Recommendations", style="bold green")
            self._print(f"  Model: {recommendations['model'].upper()} - {recommendations['model_reason']}")
            self._print(f"  Complexity: {recommendations['complexity'].upper()} - {recommendations['complexity_reason']}")

            use_recommendations = self._confirm("\nUse these recommendations?", default=True)

            if use_recommendations:
                model = recommendations["model"]
                complexity = recommendations["complexity"]
            else:
                model = self.prompt_model()
                complexity = self.prompt_complexity()

            color = self.prompt_color()

            # Summary
            self._print("\n" + "="*70, style="bold cyan")
            self._print("📋 AGENT SUMMARY", style="bold cyan")
            self._print("="*70, style="bold cyan")
            self._print(f"Name: {name}")
            self._print(f"Description: {description}")
            self._print(f"Color: {color}")
            self._print(f"Model: {model}")
            self._print(f"Complexity: {complexity}")
            self._print("="*70 + "\n", style="bold cyan")

            # Confirm creation
            if not self._confirm("Create this agent?", default=True):
                self._print("\n❌ Agent creation cancelled", style="yellow")
                return

            # Create agent file
            metadata = {
                "name": name,
                "description": description,
                "color": color,
                "model": model,
                "complexity": complexity
            }

            content = self.create_agent_content(metadata)
            agent_file = self.agents_dir / f"{name}.md"

            with open(agent_file, 'w') as f:
                f.write(content)

            self._print(f"\n✅ Agent created: {agent_file}", style="bold green")

            # Validate
            self._print("\n🔍 Validating agent...", style="cyan")
            validation_result = os.system("python3 tools/validate_agents.py")

            if validation_result == 0:
                self._print("✅ Agent validation passed!", style="bold green")
            else:
                self._print("⚠️  Agent validation found issues. Please fix before committing.", style="yellow")

            # Next steps
            self._print("\n" + "="*70, style="bold blue")
            self._print("📝 NEXT STEPS", style="bold blue")
            self._print("="*70, style="bold blue")
            self._print(f"1. Edit {agent_file} to fill in the template")
            self._print("2. Update the Professional Manifesto Commitment section")
            self._print("3. Define Responsibilities and Technical Implementation")
            self._print("4. Add deliverables, limitations, and key considerations")
            self._print("5. Test the agent with a simple task")
            self._print(f"6. Run validation: python3 tools/validate_agents.py")
            self._print(f"7. Commit: git add agents/{name}.md && git commit -m 'Add {name} agent'")
            self._print("="*70 + "\n", style="bold blue")

        except KeyboardInterrupt:
            self._print("\n\n❌ Agent creation cancelled", style="yellow")
            sys.exit(1)
        except Exception as e:
            self._print(f"\n\n❌ Error creating agent: {e}", style="bold red")
            sys.exit(1)


def main():
    """Main entry point"""
    generator = AgentGenerator()
    generator.run()


if __name__ == "__main__":
    main()
