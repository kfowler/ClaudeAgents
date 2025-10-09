#!/usr/bin/env python3
"""
Validate all documentation links for ClaudeAgents platform.
Checks markdown links in docs/, README.md, CLAUDE.md, agents/, commands/
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Set

def find_markdown_files() -> List[Path]:
    """Find all markdown files in repository"""
    markdown_files = []
    paths_to_scan = ['docs/', 'agents/', 'commands/', '.']

    for path_str in paths_to_scan:
        path = Path(path_str)
        if path.is_dir():
            markdown_files.extend(path.rglob('*.md'))
        elif path_str in ['.']:
            markdown_files.extend([Path('README.md'), Path('CLAUDE.md')])

    return [f for f in markdown_files if 'TEMPLATE' not in str(f)]

def extract_links(content: str, file_path: Path) -> List[Tuple[str, int]]:
    """Extract all markdown links from content"""
    # Match [text](link) and ![alt](link)
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    links = []

    for match in re.finditer(link_pattern, content):
        link = match.group(2)
        line_num = content[:match.start()].count('\n') + 1
        links.append((link, line_num))

    return links

def validate_link(link: str, source_file: Path) -> Tuple[bool, str]:
    """Validate a single link (local files only, skip URLs)"""
    # Skip external URLs
    if link.startswith(('http://', 'https://', 'mailto:', '#')):
        return True, ""

    # Strip anchor links (e.g., file.md#section -> file.md)
    link_without_anchor = link.split('#')[0]

    # Skip if only an anchor (was already handled above)
    if not link_without_anchor:
        return True, ""

    # Resolve relative path from source file
    source_dir = source_file.parent
    target_path = (source_dir / link_without_anchor).resolve()

    # Check if file exists
    if not target_path.exists():
        return False, f"File not found: {link}"

    return True, ""

def main():
    """Main validation logic"""
    print("=" * 60)
    print("LINK VALIDATION REPORT")
    print("=" * 60)

    markdown_files = find_markdown_files()
    total_links = 0
    broken_links = []

    for md_file in markdown_files:
        try:
            content = md_file.read_text()
            links = extract_links(content, md_file)

            for link, line_num in links:
                total_links += 1
                is_valid, error = validate_link(link, md_file)

                if not is_valid:
                    broken_links.append((md_file, line_num, link, error))

        except Exception as e:
            print(f"⚠️  Error reading {md_file}: {e}")

    # Report results
    print(f"\n📊 STATISTICS:")
    print(f"  • Files scanned: {len(markdown_files)}")
    print(f"  • Total links checked: {total_links}")
    print(f"  • Broken links: {len(broken_links)}")

    if broken_links:
        print(f"\n❌ BROKEN LINKS ({len(broken_links)}):")
        for file_path, line_num, link, error in broken_links:
            print(f"  • {file_path}:{line_num}")
            print(f"    Link: {link}")
            print(f"    Error: {error}")
        print("\n❌ Link validation failed!")
        return 1
    else:
        print("\n✅ All links are valid!")
        return 0

if __name__ == "__main__":
    exit(main())
