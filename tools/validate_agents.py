#!/usr/bin/env python3
"""
Agent Validation Script
Validates consistency and completeness of agent definitions in the agents/ directory.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

try:
    import yaml
except ImportError:
    print("❌ Error: PyYAML library is not installed.", file=sys.stderr)
    print("Please install it by running:", file=sys.stderr)
    print("  pip install -r tools/requirements.txt", file=sys.stderr)
    sys.exit(1)

class AgentValidator:
    """Validates agent definitions for consistency and completeness."""
    
    REQUIRED_FIELDS = {'name', 'description'}
    OPTIONAL_FIELDS = {'color'}
    VALID_COLORS = {
        'blue', 'green', 'yellow', 'red', 'purple', 'cyan', 'orange', 'pink',
        'gray', 'grey', 'brown', 'indigo', 'teal', 'lime', 'amber', 'emerald',
        'violet', 'fuchsia', 'rose', 'slate', 'zinc', 'neutral', 'stone',
        'crimson', 'lavender', 'navy', 'silver'
    }
    
    def __init__(self, agents_dir: str = 'agents'):
        self.agents_dir = Path(agents_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.stats: Dict = defaultdict(int)
        
    def validate_agent_file(self, filepath: Path) -> Tuple[bool, Dict]:
        """Validate a single agent file."""
        filename = filepath.name
        file_errors = []  # Track errors for this file only

        # Skip non-agent files
        if filename == 'AGENT_PROFESSIONAL_BEHAVIOR.md':
            return True, {}

        # Skip template file
        if filename == 'AGENT_TEMPLATE.md':
            return True, {}

        try:
            with open(filepath, 'r') as f:
                content = f.read()

            # Check for YAML frontmatter
            if not content.startswith('---'):
                file_errors.append(f"{filename}: Missing YAML frontmatter")
                self.errors.extend(file_errors)
                return False, {}

            # Extract frontmatter
            parts = content.split('---', 2)
            if len(parts) < 3:
                file_errors.append(f"{filename}: Invalid YAML frontmatter format")
                self.errors.extend(file_errors)
                return False, {}

            # Parse YAML
            try:
                metadata = yaml.safe_load(parts[1])
            except yaml.YAMLError as e:
                file_errors.append(f"{filename}: YAML parsing error: {e}")
                self.errors.extend(file_errors)
                return False, {}

            # Validate required fields
            for field in self.REQUIRED_FIELDS:
                if field not in metadata:
                    file_errors.append(f"{filename}: Missing required field '{field}'")

            # Validate name matches filename
            expected_name = filename.replace('.md', '')
            if metadata.get('name') != expected_name:
                file_errors.append(
                    f"{filename}: Name mismatch. Expected '{expected_name}', "
                    f"got '{metadata.get('name')}'"
                )

            # Validate description length
            desc = metadata.get('description', '')
            if len(desc) < 50:
                self.warnings.append(
                    f"{filename}: Description too short ({len(desc)} chars, minimum 50)"
                )
            elif len(desc) > 500:
                self.warnings.append(
                    f"{filename}: Description too long ({len(desc)} chars, maximum 500)"
                )

            # Validate color if present
            if 'color' in metadata:
                color = metadata['color'].lower()
                if color not in self.VALID_COLORS:
                    self.warnings.append(
                        f"{filename}: Invalid color '{color}'. "
                        f"Valid colors: {', '.join(sorted(self.VALID_COLORS))}"
                    )

            # Check for unexpected fields
            all_fields = self.REQUIRED_FIELDS | self.OPTIONAL_FIELDS
            unexpected = set(metadata.keys()) - all_fields
            if unexpected:
                self.warnings.append(
                    f"{filename}: Unexpected fields: {', '.join(unexpected)}"
                )

            # Check content structure
            content_body = parts[2].strip()
            if len(content_body) < 100:
                self.warnings.append(
                    f"{filename}: Agent content body too short ({len(content_body)} chars)"
                )

            # Update stats
            self.stats['total_agents'] += 1
            if 'color' in metadata:
                self.stats['agents_with_color'] += 1
            if 'examples' in metadata:
                self.stats['agents_with_examples'] += 1

            # Add file errors to global error list
            self.errors.extend(file_errors)

            # Return True only if this file had no errors
            return len(file_errors) == 0, metadata
            
        except Exception as e:
            self.errors.append(f"{filename}: Unexpected error: {e}")
            return False, {}
            
    def validate_all_agents(self) -> bool:
        """Validate all agent files in the directory."""
        if not self.agents_dir.exists():
            self.errors.append(f"Agents directory '{self.agents_dir}' does not exist")
            return False
            
        agent_files = sorted(self.agents_dir.glob('*.md'))
        
        if not agent_files:
            self.errors.append("No agent files found")
            return False
            
        all_metadata = {}
        for filepath in agent_files:
            valid, metadata = self.validate_agent_file(filepath)
            if metadata:
                all_metadata[filepath.name] = metadata
                
        # Check for duplicate names
        names = [m.get('name') for m in all_metadata.values() if m.get('name')]
        duplicates = [name for name in names if names.count(name) > 1]
        if duplicates:
            self.errors.append(f"Duplicate agent names found: {', '.join(set(duplicates))}")
            
        # Check for color distribution
        colors = [m.get('color') for m in all_metadata.values() if m.get('color')]
        color_counts = defaultdict(int)
        for color in colors:
            color_counts[color] += 1
            
        # Report statistics
        self.stats['unique_colors'] = len(color_counts)
        self.stats['most_used_color'] = max(color_counts.items(), key=lambda x: x[1])[0] if color_counts else None
        
        return len(self.errors) == 0
        
    def print_report(self):
        """Print validation report."""
        print("=" * 60)
        print("AGENT VALIDATION REPORT")
        print("=" * 60)
        
        if self.errors:
            print("\n❌ ERRORS (must fix):")
            for error in self.errors:
                print(f"  • {error}")
                
        if self.warnings:
            print("\n⚠️  WARNINGS (should fix):")
            for warning in self.warnings:
                print(f"  • {warning}")
                
        print("\n📊 STATISTICS:")
        print(f"  • Total agents: {self.stats['total_agents']}")
        print(f"  • Agents with color: {self.stats['agents_with_color']}")
        print(f"  • Agents with examples: {self.stats['agents_with_examples']}")
        print(f"  • Unique colors used: {self.stats['unique_colors']}")
        if self.stats['most_used_color']:
            print(f"  • Most used color: {self.stats['most_used_color']}")
            
        if not self.errors and not self.warnings:
            print("\n✅ All agents are valid and consistent!")
        elif not self.errors:
            print("\n✅ No critical errors found, but there are warnings to address.")
        else:
            print(f"\n❌ Found {len(self.errors)} error(s) and {len(self.warnings)} warning(s)")
            
        print("=" * 60)
        
        return len(self.errors) == 0


def main():
    """Main entry point."""
    # Change to repository root if needed
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    validator = AgentValidator()
    valid = validator.validate_all_agents()
    validator.print_report()
    
    # Exit with appropriate code
    sys.exit(0 if valid else 1)


if __name__ == '__main__':
    main()