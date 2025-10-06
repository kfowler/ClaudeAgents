#!/usr/bin/env python3
"""
Integration tests for agent validation and system integrity.

This test suite ensures the Claude Code Agent System maintains quality
and consistency across all agent definitions, commands, and documentation.

Test Coverage:
    - Agent file parsing and YAML frontmatter validation
    - Required metadata fields (name, description)
    - Name/filename consistency
    - No duplicate agent names
    - Agent references in commands are valid
    - Validator error tracking accuracy

Usage:
    # Run all tests
    python3 tests/test_agent_integration.py -v

    # Run specific test class
    python3 -m pytest tests/test_agent_integration.py::TestAgentIntegration -v

    # Run with pytest
    pytest tests/ -v --cov=tools

These tests run automatically in CI/CD on every push and pull request.
"""

import os
import sys
from pathlib import Path
import unittest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import yaml
except ImportError:
    print("Warning: PyYAML not installed. Install with: pip install -r tools/requirements.txt")
    sys.exit(1)

from tools.validate_agents import AgentValidator


class TestAgentIntegration(unittest.TestCase):
    """
    Integration tests for agent system integrity.

    Validates that all agents follow required structure and that
    cross-references between agents and commands are valid.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up test fixtures that are shared across all test methods.

        Establishes paths to agents/ and commands/ directories
        for validation throughout the test suite.
        """
        cls.repo_root = Path(__file__).parent.parent
        cls.agents_dir = cls.repo_root / 'agents'
        cls.commands_dir = cls.repo_root / 'commands'

    def test_all_agents_parse(self):
        """Test that all agent files can be parsed."""
        validator = AgentValidator(str(self.agents_dir))

        for agent_file in self.agents_dir.glob('*.md'):
            # Skip special files
            if agent_file.name in ['AGENT_PROFESSIONAL_BEHAVIOR.md', 'AGENT_TEMPLATE.md']:
                continue

            with self.subTest(agent=agent_file.name):
                is_valid, metadata = validator.validate_agent_file(agent_file)
                self.assertTrue(
                    is_valid,
                    f"Agent {agent_file.name} failed validation: {validator.errors}"
                )
                self.assertIsNotNone(metadata)
                self.assertIn('name', metadata)
                self.assertIn('description', metadata)

    def test_required_frontmatter_fields(self):
        """Test that all agents have required frontmatter fields."""
        required_fields = {'name', 'description'}

        for agent_file in self.agents_dir.glob('*.md'):
            if agent_file.name in ['AGENT_PROFESSIONAL_BEHAVIOR.md', 'AGENT_TEMPLATE.md']:
                continue

            with self.subTest(agent=agent_file.name):
                with open(agent_file, 'r') as f:
                    content = f.read()

                # Extract frontmatter
                parts = content.split('---', 2)
                self.assertGreaterEqual(len(parts), 3, f"{agent_file.name} missing frontmatter")

                metadata = yaml.safe_load(parts[1])
                for field in required_fields:
                    self.assertIn(
                        field,
                        metadata,
                        f"{agent_file.name} missing required field: {field}"
                    )

    def test_agent_name_matches_filename(self):
        """Test that agent names match their filenames."""
        for agent_file in self.agents_dir.glob('*.md'):
            if agent_file.name in ['AGENT_PROFESSIONAL_BEHAVIOR.md', 'AGENT_TEMPLATE.md']:
                continue

            with self.subTest(agent=agent_file.name):
                with open(agent_file, 'r') as f:
                    content = f.read()

                parts = content.split('---', 2)
                metadata = yaml.safe_load(parts[1])

                expected_name = agent_file.stem
                actual_name = metadata.get('name')

                self.assertEqual(
                    expected_name,
                    actual_name,
                    f"Name mismatch in {agent_file.name}: expected '{expected_name}', got '{actual_name}'"
                )

    def test_no_duplicate_agent_names(self):
        """Test that there are no duplicate agent names."""
        agent_names = []

        for agent_file in self.agents_dir.glob('*.md'):
            if agent_file.name in ['AGENT_PROFESSIONAL_BEHAVIOR.md', 'AGENT_TEMPLATE.md']:
                continue

            with open(agent_file, 'r') as f:
                content = f.read()

            parts = content.split('---', 2)
            if len(parts) >= 3:
                metadata = yaml.safe_load(parts[1])
                if 'name' in metadata:
                    agent_names.append(metadata['name'])

        # Check for duplicates
        duplicates = [name for name in agent_names if agent_names.count(name) > 1]
        self.assertEqual(
            len(duplicates),
            0,
            f"Found duplicate agent names: {set(duplicates)}"
        )

    def test_agent_references_in_commands_are_valid(self):
        """Test that all agent references in commands exist."""
        # Get list of valid agent names
        valid_agents = set()
        for agent_file in self.agents_dir.glob('*.md'):
            if agent_file.name in ['AGENT_PROFESSIONAL_BEHAVIOR.md', 'AGENT_TEMPLATE.md']:
                continue
            valid_agents.add(agent_file.stem)

        # Check command files for agent references
        for command_file in self.commands_dir.rglob('*.md'):
            # Skip template files
            if command_file.name == 'COMMAND_TEMPLATE.md':
                continue

            with self.subTest(command=command_file.name):
                with open(command_file, 'r') as f:
                    content = f.read()

                # Look for agent references in backticks like `agent-name`
                import re
                agent_refs = re.findall(r'`([a-z][a-z0-9-]*(?:-[a-z0-9]+)*)`', content)

                for ref in agent_refs:
                    # Only check if it looks like an agent name (contains hyphen or is a known agent)
                    if '-' in ref or ref in valid_agents:
                        # Skip known non-agent references
                        skip_patterns = [
                            'git-', 'npm-', 'yarn-', 'docker-', 'kubectl-',
                            'react-', 'next-', 'vue-', 'python-', 'node-'
                        ]
                        if any(ref.startswith(pattern) for pattern in skip_patterns):
                            continue

                        # Check if it's a valid agent
                        if ref not in valid_agents:
                            # Only fail if it looks very much like an agent name
                            if any(keyword in ref for keyword in ['agent', 'engineer', 'specialist', 'expert', 'developer', 'architect', 'orchestrator']):
                                self.assertIn(
                                    ref,
                                    valid_agents,
                                    f"Command {command_file.name} references non-existent agent: {ref}"
                                )

    def test_description_not_empty(self):
        """Test that all agent descriptions are not empty."""
        for agent_file in self.agents_dir.glob('*.md'):
            if agent_file.name in ['AGENT_PROFESSIONAL_BEHAVIOR.md', 'AGENT_TEMPLATE.md']:
                continue

            with self.subTest(agent=agent_file.name):
                with open(agent_file, 'r') as f:
                    content = f.read()

                parts = content.split('---', 2)
                metadata = yaml.safe_load(parts[1])

                description = metadata.get('description', '')
                self.assertGreater(
                    len(description),
                    0,
                    f"{agent_file.name} has empty description"
                )

    def test_agent_content_body_exists(self):
        """Test that all agents have actual content beyond frontmatter."""
        for agent_file in self.agents_dir.glob('*.md'):
            if agent_file.name in ['AGENT_PROFESSIONAL_BEHAVIOR.md', 'AGENT_TEMPLATE.md']:
                continue

            with self.subTest(agent=agent_file.name):
                with open(agent_file, 'r') as f:
                    content = f.read()

                parts = content.split('---', 2)
                self.assertGreaterEqual(len(parts), 3, f"{agent_file.name} has no content body")

                content_body = parts[2].strip()
                self.assertGreater(
                    len(content_body),
                    0,
                    f"{agent_file.name} has empty content body"
                )


class TestValidatorErrorTracking(unittest.TestCase):
    """
    Test validator error tracking accuracy.

    Ensures the validator correctly reports validation status
    on a per-file basis and aggregates errors properly.
    """

    def setUp(self):
        """
        Set up test fixtures for each test method.

        Creates paths needed for validator testing.
        """
        self.repo_root = Path(__file__).parent.parent
        self.agents_dir = self.repo_root / 'agents'

    def test_validator_reports_correct_error_count(self):
        """Test that validator returns correct validation status."""
        validator = AgentValidator(str(self.agents_dir))

        # Validate all agents
        validator.validate_all_agents()

        # If there were errors, the error list should not be empty
        if validator.errors:
            self.assertGreater(len(validator.errors), 0)

        # The validation should pass (no critical errors currently)
        self.assertEqual(len(validator.errors), 0, f"Found unexpected errors: {validator.errors}")


if __name__ == '__main__':
    unittest.main()
