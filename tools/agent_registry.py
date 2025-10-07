#!/usr/bin/env python3
"""
ClaudeAgents Registry - Fast Agent Discovery and Selection

Provides O(1) capability-based agent lookup through semantic indexing.
Maintains markdown as source of truth while enabling intelligent search.

Design Goals:
- Fast lookup: O(1) vs O(n) scanning through agent list
- Semantic search: Find agents by capability, not just keywords
- Performance tracking: Integrate with telemetry for quality metrics
- Extensible: Easy to add new index types and search strategies
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class AgentMetadata:
    """Parsed agent metadata from frontmatter"""
    name: str
    description: str
    color: Optional[str] = None
    model: Optional[str] = None
    computational_complexity: Optional[str] = None
    file_path: Optional[Path] = None
    content_preview: str = ""

    # Derived fields
    capabilities: Set[str] = field(default_factory=set)
    keywords: Set[str] = field(default_factory=set)
    domains: Set[str] = field(default_factory=set)


class AgentRegistry:
    """
    Fast agent discovery through multi-index lookup.

    Indices maintained:
    - capability_index: capability -> [agents]
    - keyword_index: keyword -> [agents]
    - domain_index: domain -> [agents]
    - name_index: agent_name -> AgentMetadata
    """

    # Domain classifications (can be extended)
    DOMAINS = {
        "web": ["react", "next.js", "vue", "svelte", "frontend", "backend", "api", "web"],
        "mobile": ["ios", "android", "swift", "kotlin", "react native", "flutter", "mobile", "app"],
        "ai_ml": ["ai", "ml", "llm", "rag", "vector", "embedding", "machine learning", "neural"],
        "data": ["database", "sql", "nosql", "etl", "pipeline", "analytics", "data"],
        "devops": ["ci/cd", "docker", "kubernetes", "deploy", "infrastructure", "cloud"],
        "security": ["security", "audit", "vulnerability", "compliance", "penetration"],
        "testing": ["test", "qa", "automation", "coverage", "pytest", "jest"],
        "seo": ["seo", "search", "ranking", "meta", "optimization", "keyword"],
        "business": ["product", "strategy", "roadmap", "requirements", "stakeholder"],
        "creative": ["design", "ui", "ux", "video", "audio", "3d", "art"],
    }

    # Common capability patterns
    CAPABILITY_PATTERNS = {
        "architecture": ["architect", "design", "structure", "pattern"],
        "implementation": ["implement", "code", "develop", "build"],
        "review": ["review", "audit", "analyze", "assess"],
        "optimization": ["optimize", "performance", "speed", "efficient"],
        "debugging": ["debug", "troubleshoot", "fix", "diagnose"],
        "documentation": ["document", "guide", "tutorial", "readme"],
        "deployment": ["deploy", "release", "publish", "ship"],
        "migration": ["migrate", "upgrade", "transition", "legacy"],
    }

    def __init__(self, agents_dir: Optional[Path] = None):
        """Initialize agent registry"""
        if agents_dir is None:
            # Default to repository agents directory
            script_dir = Path(__file__).parent.parent
            agents_dir = script_dir / "agents"

        self.agents_dir = Path(agents_dir)

        # Initialize indices
        self.name_index: Dict[str, AgentMetadata] = {}
        self.capability_index: Dict[str, List[str]] = defaultdict(list)
        self.keyword_index: Dict[str, List[str]] = defaultdict(list)
        self.domain_index: Dict[str, List[str]] = defaultdict(list)

        # Performance metrics (from telemetry if available)
        self.performance_metrics: Dict[str, Dict] = {}

        # Build indices
        self._build_indices()

    def _extract_capabilities(self, description: str, content: str) -> Set[str]:
        """Extract capabilities from description and content"""
        capabilities = set()
        combined_text = (description + " " + content).lower()

        for capability, patterns in self.CAPABILITY_PATTERNS.items():
            if any(pattern in combined_text for pattern in patterns):
                capabilities.add(capability)

        return capabilities

    def _extract_keywords(self, description: str, content: str) -> Set[str]:
        """Extract important keywords from description and content"""
        # Combine and normalize
        text = (description + " " + content).lower()

        # Remove common words
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
                     "of", "with", "by", "from", "as", "is", "was", "are", "be", "this",
                     "that", "it", "use", "using", "when", "will", "can", "could", "should"}

        # Extract words (alphanumeric + hyphens)
        words = re.findall(r'\b[a-z0-9][a-z0-9-]*\b', text)

        # Filter and collect important keywords
        keywords = set()
        for word in words:
            if len(word) > 2 and word not in stopwords:
                keywords.add(word)

        return keywords

    def _classify_domains(self, description: str, content: str) -> Set[str]:
        """Classify agent into domains based on content"""
        domains = set()
        combined_text = (description + " " + content).lower()

        for domain, patterns in self.DOMAINS.items():
            if any(pattern in combined_text for pattern in patterns):
                domains.add(domain)

        return domains

    def _parse_agent_file(self, filepath: Path) -> Optional[AgentMetadata]:
        """Parse agent markdown file and extract metadata"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split frontmatter and content
            parts = content.split('---', 2)
            if len(parts) < 3:
                return None

            # Parse YAML frontmatter
            try:
                metadata_dict = yaml.safe_load(parts[1])
            except yaml.YAMLError:
                return None

            # Extract required fields
            if not metadata_dict or 'name' not in metadata_dict:
                return None

            # Get content body (first 500 chars for analysis)
            content_body = parts[2].strip()
            content_preview = content_body[:500]

            # Create metadata object
            agent = AgentMetadata(
                name=metadata_dict['name'],
                description=metadata_dict.get('description', ''),
                color=metadata_dict.get('color'),
                model=metadata_dict.get('model'),
                computational_complexity=metadata_dict.get('computational_complexity'),
                file_path=filepath,
                content_preview=content_preview
            )

            # Extract derived fields
            agent.capabilities = self._extract_capabilities(
                agent.description, content_preview
            )
            agent.keywords = self._extract_keywords(
                agent.description, content_preview
            )
            agent.domains = self._classify_domains(
                agent.description, content_preview
            )

            return agent

        except Exception as e:
            print(f"Warning: Could not parse {filepath.name}: {e}")
            return None

    def _build_indices(self):
        """Build all indices from agent files"""
        # Find all agent markdown files
        agent_files = sorted(self.agents_dir.glob("*.md"))

        for filepath in agent_files:
            # Skip template files
            if "template" in filepath.name.lower():
                continue

            # Parse agent file
            agent = self._parse_agent_file(filepath)
            if not agent:
                continue

            # Add to name index
            self.name_index[agent.name] = agent

            # Add to capability index
            for capability in agent.capabilities:
                self.capability_index[capability].append(agent.name)

            # Add to keyword index
            for keyword in agent.keywords:
                self.keyword_index[keyword].append(agent.name)

            # Add to domain index
            for domain in agent.domains:
                self.domain_index[domain].append(agent.name)

    def find_by_capability(self, capability: str) -> List[str]:
        """Find agents by capability (O(1) lookup)"""
        return self.capability_index.get(capability.lower(), [])

    def find_by_keyword(self, keyword: str) -> List[str]:
        """Find agents by keyword (O(1) lookup)"""
        return self.keyword_index.get(keyword.lower(), [])

    def find_by_domain(self, domain: str) -> List[str]:
        """Find agents by domain (O(1) lookup)"""
        return self.domain_index.get(domain.lower(), [])

    def search(self, query: str, max_results: int = 10) -> List[Tuple[str, float]]:
        """
        Semantic search across all indices.

        Returns list of (agent_name, relevance_score) tuples.
        """
        query_lower = query.lower()
        query_words = set(re.findall(r'\b[a-z0-9][a-z0-9-]*\b', query_lower))

        # Scoring: agent_name -> score
        scores: Dict[str, float] = defaultdict(float)

        # 1. Exact name match (highest score)
        if query_lower in self.name_index:
            scores[query_lower] += 10.0

        # 2. Name substring match
        for agent_name in self.name_index:
            if query_lower in agent_name.lower():
                scores[agent_name] += 8.0

        # 3. Capability matches
        for capability in self.capability_index:
            if capability in query_lower or query_lower in capability:
                for agent_name in self.capability_index[capability]:
                    scores[agent_name] += 5.0

        # 4. Domain matches
        for domain in self.domain_index:
            if domain in query_lower or query_lower in domain:
                for agent_name in self.domain_index[domain]:
                    scores[agent_name] += 4.0

        # 5. Keyword matches
        for word in query_words:
            if word in self.keyword_index:
                for agent_name in self.keyword_index[word]:
                    scores[agent_name] += 2.0

        # 6. Description substring match
        for agent_name, agent in self.name_index.items():
            if query_lower in agent.description.lower():
                scores[agent_name] += 3.0

        # Sort by score and return top results
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:max_results]

    def get_agent(self, agent_name: str) -> Optional[AgentMetadata]:
        """Get agent metadata by name (O(1) lookup)"""
        return self.name_index.get(agent_name)

    def list_all_agents(self) -> List[str]:
        """Get list of all agent names"""
        return sorted(self.name_index.keys())

    def get_stats(self) -> Dict:
        """Get registry statistics"""
        return {
            "total_agents": len(self.name_index),
            "total_capabilities": len(self.capability_index),
            "total_keywords": len(self.keyword_index),
            "total_domains": len(self.domain_index),
            "domains": {
                domain: len(agents)
                for domain, agents in self.domain_index.items()
            },
            "capabilities": {
                cap: len(agents)
                for cap, agents in self.capability_index.items()
            }
        }

    def print_stats(self):
        """Print formatted statistics"""
        stats = self.get_stats()

        print("\n" + "="*60)
        print("AGENT REGISTRY STATISTICS")
        print("="*60)

        print(f"\n📊 Overview:")
        print(f"  • Total agents indexed: {stats['total_agents']}")
        print(f"  • Total capabilities: {stats['total_capabilities']}")
        print(f"  • Total keywords: {stats['total_keywords']}")
        print(f"  • Total domains: {stats['total_domains']}")

        print(f"\n🌐 Domain Distribution:")
        for domain, count in sorted(stats['domains'].items(),
                                    key=lambda x: x[1],
                                    reverse=True):
            print(f"  • {domain}: {count} agents")

        print(f"\n🔧 Capability Distribution:")
        for capability, count in sorted(stats['capabilities'].items(),
                                       key=lambda x: x[1],
                                       reverse=True):
            print(f"  • {capability}: {count} agents")

        print("\n" + "="*60 + "\n")


def main():
    """CLI interface for agent registry"""
    import sys

    registry = AgentRegistry()

    if len(sys.argv) < 2:
        print("Usage: python agent_registry.py [stats|search|find] <query>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "stats":
        registry.print_stats()

    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: python agent_registry.py search <query>")
            sys.exit(1)

        query = " ".join(sys.argv[2:])
        results = registry.search(query)

        print(f"\n🔍 Search results for: '{query}'")
        print("="*60)

        if not results:
            print("No agents found.")
        else:
            for i, (agent_name, score) in enumerate(results, 1):
                agent = registry.get_agent(agent_name)
                print(f"\n{i}. {agent_name} (relevance: {score:.1f})")
                if agent:
                    print(f"   {agent.description[:100]}...")
                    print(f"   Domains: {', '.join(sorted(agent.domains))}")

        print()

    elif command == "find":
        if len(sys.argv) < 3:
            print("Usage: python agent_registry.py find <capability|keyword|domain>")
            sys.exit(1)

        term = sys.argv[2].lower()

        # Try all indices
        cap_results = registry.find_by_capability(term)
        kw_results = registry.find_by_keyword(term)
        dom_results = registry.find_by_domain(term)

        print(f"\n🔍 Find results for: '{term}'")
        print("="*60)

        if cap_results:
            print(f"\nBy Capability ({len(cap_results)} agents):")
            for agent_name in cap_results[:10]:
                print(f"  • {agent_name}")

        if kw_results:
            print(f"\nBy Keyword ({len(kw_results)} agents):")
            for agent_name in kw_results[:10]:
                print(f"  • {agent_name}")

        if dom_results:
            print(f"\nBy Domain ({len(dom_results)} agents):")
            for agent_name in dom_results[:10]:
                print(f"  • {agent_name}")

        if not (cap_results or kw_results or dom_results):
            print("No agents found.")

        print()

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
