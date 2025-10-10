#!/usr/bin/env python3
"""
ClaudeAgents Intelligent Workflow Orchestrator

Automatically selects optimal agents based on project context and user intent.
Reduces cognitive load by eliminating manual agent selection.

Design Goals:
- Context-aware: Analyze project structure and requirements
- Intent-driven: Understand user goals from natural language
- Quality-first: Prioritize high-performing agents (via telemetry)
- Transparent: Explain selection decisions to user
- Progressive: Start rule-based, add ML later (optional)
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from agent_registry import AgentRegistry, AgentMetadata


class AgentTier(Enum):
    """Agent quality tiers"""
    CORE = 1        # Top 10-15 agents, battle-tested
    EXTENDED = 2    # 25-30 agents, domain-specific
    EXPERIMENTAL = 3  # 10-15 agents, emerging
    UNKNOWN = 4     # Not yet assigned


class TierManager:
    """
    Manages agent tier assignments.

    Note: Tier assignments are provisional until telemetry data collected.
    Final assignments will be data-driven (usage, satisfaction, etc.)
    """

    # Provisional tier assignments (from docs/agent-tiers.md)
    CORE_AGENTS = {
        "project-orchestrator",
        "full-stack-architect",
        "backend-api-engineer",
        "mobile-developer",
        "ai-ml-engineer",
        "security-audit-specialist",
        "qa-test-engineer",
        "code-architect",
        "devops-engineer",
        "data-engineer",
        "the-critic",
        "the-skeptic",
        "product-strategist",
    }

    EXTENDED_AGENTS = {
        # Development specialists
        "systems-engineer",
        "functional-programmer",
        "game-development-engineer",
        "blockchain-web3-engineer",
        "embedded-iot-developer",
        # Quality specialists
        "frontend-performance-specialist",
        "accessibility-expert",
        "debugging-specialist",
        "test-automation-engineer",
        # Infrastructure specialists
        "cloud-architect",
        "infrastructure-as-code-specialist",
        "platform-engineering-specialist",
        "edge-computing-specialist",
        "observability-engineer",
        "incident-coordinator",
        "database-administrator",
        "linux-sysadmin",
        # SEO specialists
        "seo-meta-optimizer",
        "seo-technical-auditor",
        "seo-performance-specialist",
        "seo-keyword-strategist",
        "seo-content-optimizer",
        "seo-structure-architect",
        # Business & Operations
        "business-analyst",
        "product-manager",
        "technical-writer",
        # Specialized
        "platform-integrator",
        "legacy-specialist",
        "merge-conflict-resolver",
    }

    EXPERIMENTAL_AGENTS = {
        # Creative & Specialized
        "creative-catalyst",
        "the-inventor",
        "the-synthesist",
        "the-architect-of-experiments",
        "digital-artist",
        "video-director",
        "audio-engineer",
        "3d-modeler",
        "comedy-writer",
        "tv-writer",
        # Niche Development
        "elisp-specialist",
        "metaprogramming-specialist",
    }

    @classmethod
    def get_tier(cls, agent_name: str) -> AgentTier:
        """Get tier for agent"""
        if agent_name in cls.CORE_AGENTS:
            return AgentTier.CORE
        elif agent_name in cls.EXTENDED_AGENTS:
            return AgentTier.EXTENDED
        elif agent_name in cls.EXPERIMENTAL_AGENTS:
            return AgentTier.EXPERIMENTAL
        else:
            return AgentTier.UNKNOWN

    @classmethod
    def filter_by_tier(
        cls,
        agents: List[str],
        max_tier: AgentTier = AgentTier.EXTENDED
    ) -> List[str]:
        """
        Filter agents by tier, keeping only those at or above max_tier.

        Args:
            agents: List of agent names
            max_tier: Maximum tier to allow (CORE, EXTENDED, or EXPERIMENTAL)

        Returns:
            Filtered list of agents
        """
        return [
            agent for agent in agents
            if cls.get_tier(agent).value <= max_tier.value
        ]

    @classmethod
    def sort_by_tier(cls, agents: List[str]) -> List[str]:
        """
        Sort agents by tier (Core first, then Extended, then Experimental).
        Preserves order within each tier.
        """
        # Group by tier
        core = [a for a in agents if cls.get_tier(a) == AgentTier.CORE]
        extended = [a for a in agents if cls.get_tier(a) == AgentTier.EXTENDED]
        experimental = [a for a in agents if cls.get_tier(a) == AgentTier.EXPERIMENTAL]
        unknown = [a for a in agents if cls.get_tier(a) == AgentTier.UNKNOWN]

        # Combine in tier order
        return core + extended + experimental + unknown


@dataclass
class ProjectContext:
    """Detected project characteristics"""
    languages: Set[str] = field(default_factory=set)
    frameworks: Set[str] = field(default_factory=set)
    technologies: Set[str] = field(default_factory=set)
    project_type: Optional[str] = None  # web, mobile, data, ml, etc.
    has_tests: bool = False
    has_ci_cd: bool = False
    has_docs: bool = False
    file_count: int = 0
    complexity: str = "medium"  # low, medium, high


@dataclass
class UserIntent:
    """Parsed user request intent"""
    action: str  # implement, review, debug, optimize, deploy, etc.
    subject: str  # What to act on (e.g., "authentication system")
    constraints: List[str] = field(default_factory=list)
    quality_requirements: List[str] = field(default_factory=list)


@dataclass
class OrchestratedWorkflow:
    """Generated workflow with agent selections"""
    agents: List[str]
    reasoning: List[str]
    estimated_duration: Optional[int] = None  # minutes
    prerequisites: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)


class ProjectAnalyzer:
    """Analyzes project structure to build context"""

    # File extension to language mapping
    LANGUAGE_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".rs": "rust",
        ".go": "go",
        ".java": "java",
        ".kt": "kotlin",
        ".swift": "swift",
        ".rb": "ruby",
        ".php": "php",
        ".c": "c",
        ".cpp": "cpp",
        ".cs": "csharp",
        ".sql": "sql",
    }

    # Framework detection patterns (filename or content)
    FRAMEWORK_PATTERNS = {
        "react": ["package.json:react", "*.jsx", "*.tsx"],
        "next.js": ["next.config.js", "next.config.ts", "package.json:next"],
        "vue": ["*.vue", "package.json:vue"],
        "svelte": ["*.svelte", "package.json:svelte"],
        "angular": ["angular.json", "package.json:@angular"],
        "django": ["manage.py", "settings.py", "requirements.txt:django"],
        "flask": ["app.py", "requirements.txt:flask"],
        "fastapi": ["main.py", "requirements.txt:fastapi"],
        "express": ["package.json:express"],
        "spring": ["pom.xml", "build.gradle"],
        "rails": ["Gemfile:rails", "config/routes.rb"],
    }

    # Technology detection
    TECH_PATTERNS = {
        "docker": ["Dockerfile", "docker-compose.yml"],
        "kubernetes": ["*.yaml:kind:", "k8s/"],
        "terraform": ["*.tf", "terraform.tfstate"],
        "postgresql": ["*.sql", "package.json:pg", "requirements.txt:psycopg"],
        "mongodb": ["package.json:mongodb", "requirements.txt:pymongo"],
        "redis": ["package.json:redis", "requirements.txt:redis"],
        "graphql": ["*.graphql", "package.json:graphql"],
        "rest": ["routes.py", "api/", "controllers/"],
    }

    def __init__(self, project_dir: Optional[Path] = None):
        """Initialize project analyzer"""
        if project_dir is None:
            project_dir = Path.cwd()
        self.project_dir = Path(project_dir)

    def analyze(self) -> ProjectContext:
        """Analyze project and return context"""
        context = ProjectContext()

        # Detect languages
        context.languages = self._detect_languages()

        # Detect frameworks
        context.frameworks = self._detect_frameworks()

        # Detect technologies
        context.technologies = self._detect_technologies()

        # Classify project type
        context.project_type = self._classify_project_type(
            context.languages, context.frameworks
        )

        # Check for common artifacts
        context.has_tests = self._has_tests()
        context.has_ci_cd = self._has_ci_cd()
        context.has_docs = self._has_docs()

        # Count files
        context.file_count = self._count_code_files()

        # Estimate complexity
        context.complexity = self._estimate_complexity(context.file_count)

        return context

    def _detect_languages(self) -> Set[str]:
        """Detect programming languages in project"""
        languages = set()

        for ext, lang in self.LANGUAGE_MAP.items():
            if list(self.project_dir.rglob(f"*{ext}")):
                languages.add(lang)

        return languages

    def _detect_frameworks(self) -> Set[str]:
        """Detect frameworks in use"""
        frameworks = set()

        for framework, patterns in self.FRAMEWORK_PATTERNS.items():
            if self._check_patterns(patterns):
                frameworks.add(framework)

        return frameworks

    def _detect_technologies(self) -> Set[str]:
        """Detect technologies in use"""
        technologies = set()

        for tech, patterns in self.TECH_PATTERNS.items():
            if self._check_patterns(patterns):
                technologies.add(tech)

        return technologies

    def _check_patterns(self, patterns: List[str]) -> bool:
        """Check if any pattern matches in project"""
        for pattern in patterns:
            if ":" in pattern:
                # File content pattern (e.g., "package.json:react")
                filename, content_pattern = pattern.split(":", 1)
                files = list(self.project_dir.rglob(filename))
                for file in files:
                    try:
                        with open(file, 'r') as f:
                            if content_pattern in f.read():
                                return True
                    except:
                        pass
            else:
                # File existence pattern
                if list(self.project_dir.rglob(pattern)):
                    return True

        return False

    def _classify_project_type(
        self, languages: Set[str], frameworks: Set[str]
    ) -> str:
        """Classify project type based on languages and frameworks"""
        # Web frameworks
        web_frameworks = {"react", "next.js", "vue", "svelte", "angular",
                         "django", "flask", "fastapi", "express", "rails"}
        if frameworks & web_frameworks:
            return "web"

        # Mobile indicators
        if "swift" in languages or "kotlin" in languages:
            return "mobile"

        # Data/ML indicators
        if "sql" in languages or any(fw in frameworks for fw in ["django", "flask", "fastapi"]):
            if list(self.project_dir.rglob("*.ipynb")):
                return "ml"
            return "data"

        # Default fallback
        if "python" in languages:
            return "backend"
        elif "javascript" in languages or "typescript" in languages:
            return "web"

        return "general"

    def _has_tests(self) -> bool:
        """Check if project has tests"""
        test_patterns = ["test_*.py", "*_test.py", "*.test.js", "*.spec.ts",
                        "tests/", "__tests__/", "spec/"]
        return any(list(self.project_dir.rglob(p)) for p in test_patterns)

    def _has_ci_cd(self) -> bool:
        """Check if project has CI/CD setup"""
        ci_files = [".github/workflows/", ".gitlab-ci.yml", ".travis.yml",
                   "Jenkinsfile", ".circleci/"]
        return any((self.project_dir / f).exists() for f in ci_files)

    def _has_docs(self) -> bool:
        """Check if project has documentation"""
        doc_patterns = ["docs/", "README.md", "*.md"]
        return any(list(self.project_dir.rglob(p)) for p in doc_patterns)

    def _count_code_files(self) -> int:
        """Count code files (excluding node_modules, etc.)"""
        exclude_dirs = {".git", "node_modules", "venv", "__pycache__",
                       ".pytest_cache", "dist", "build"}

        count = 0
        for ext in self.LANGUAGE_MAP:
            for file in self.project_dir.rglob(f"*{ext}"):
                # Skip if in excluded directory
                if not any(excluded in file.parts for excluded in exclude_dirs):
                    count += 1

        return count

    def _estimate_complexity(self, file_count: int) -> str:
        """Estimate project complexity based on file count"""
        if file_count < 10:
            return "low"
        elif file_count < 50:
            return "medium"
        else:
            return "high"


class IntentParser:
    """Parses natural language requests to extract intent"""

    # Action keywords
    ACTIONS = {
        "implement": ["implement", "create", "build", "add", "develop", "write"],
        "review": ["review", "audit", "analyze", "check", "inspect", "assess"],
        "debug": ["debug", "fix", "troubleshoot", "diagnose", "solve"],
        "optimize": ["optimize", "improve", "speed up", "enhance", "refactor"],
        "deploy": ["deploy", "release", "publish", "ship", "launch"],
        "test": ["test", "verify", "validate", "qa"],
        "document": ["document", "explain", "describe", "write docs"],
        "migrate": ["migrate", "upgrade", "port", "convert"],
    }

    # Quality requirement keywords
    QUALITY_KEYWORDS = {
        "security": ["secure", "security", "auth", "authentication", "encryption", "compliance", "audit"],
        "performance": ["fast", "performance", "optimize", "speed", "efficient"],
        "accessibility": ["accessible", "accessibility", "a11y", "wcag", "aria", "screen reader", "inclusive"],
        "testing": ["test", "coverage", "quality", "reliable", "qa"],
        "seo": ["seo", "search", "ranking", "visibility", "google"],
    }

    def parse(self, user_request: str) -> UserIntent:
        """Parse user request and extract intent"""
        request_lower = user_request.lower()

        # Detect action
        action = self._detect_action(request_lower)

        # Extract subject (simplified - could be much more sophisticated)
        subject = self._extract_subject(user_request, action)

        # Detect quality requirements
        quality_reqs = self._detect_quality_requirements(request_lower)

        return UserIntent(
            action=action,
            subject=subject,
            quality_requirements=quality_reqs
        )

    def _detect_action(self, request: str) -> str:
        """Detect primary action from request"""
        for action, keywords in self.ACTIONS.items():
            if any(kw in request for kw in keywords):
                return action

        return "general"  # fallback

    def _extract_subject(self, request: str, action: str) -> str:
        """Extract what the action is being performed on"""
        # Remove action words
        subject = request
        for keywords in self.ACTIONS.values():
            for kw in keywords:
                subject = subject.replace(kw, "")

        # Clean up
        subject = subject.strip().strip(".,!?")

        return subject if subject else "project"

    def _detect_quality_requirements(self, request: str) -> List[str]:
        """Detect quality requirements mentioned"""
        requirements = []

        for req_type, keywords in self.QUALITY_KEYWORDS.items():
            if any(kw in request for kw in keywords):
                requirements.append(req_type)

        return requirements


@dataclass
class AgentRecommendation:
    """Single agent recommendation with explanation"""
    agent_name: str
    relevance_score: float  # 0.0-1.0
    tier: AgentTier
    explanation: str
    match_breakdown: Dict[str, float] = field(default_factory=dict)


class AgentDiscoveryEngine:
    """
    Solves the 78-agent navigation problem with intelligent search.

    Multi-modal discovery:
    - Keyword search (description, tags, capabilities)
    - Natural language queries (intent parsing)
    - Tier-based filtering (Core, Extended, Experimental)
    - Task-based recommendations (development, quality, security, etc.)

    Relevance scoring:
    - Keyword match: 40%
    - Intent alignment: 30%
    - Context fit: 20%
    - Tier priority: 10%
    """

    # Domain intent keywords
    DOMAIN_INTENTS = {
        "development": ["implement", "build", "create", "develop", "code", "write", "add", "feature"],
        "quality": ["review", "audit", "test", "qa", "quality", "verify", "validate", "check"],
        "security": ["security", "secure", "auth", "encrypt", "vulnerability", "compliance", "audit"],
        "optimization": ["optimize", "improve", "speed", "performance", "enhance", "refactor", "faster"],
        "deployment": ["deploy", "release", "publish", "ship", "ci/cd", "devops", "infrastructure"],
        "documentation": ["document", "docs", "readme", "guide", "tutorial", "explain", "describe"],
        "debugging": ["debug", "fix", "troubleshoot", "diagnose", "solve", "error", "bug"],
        "seo": ["seo", "search", "ranking", "visibility", "google", "meta", "keywords", "sitemap"],
    }

    # Agent capability keywords (manually curated from agent descriptions)
    AGENT_KEYWORDS = {
        "full-stack-architect": ["web", "react", "next.js", "frontend", "backend", "api", "full-stack", "web app", "webapp", "application"],
        "backend-api-engineer": ["backend", "api", "rest", "graphql", "microservices", "server"],
        "mobile-developer": ["mobile", "ios", "android", "react native", "flutter", "app"],
        "ai-ml-engineer": ["ai", "ml", "llm", "rag", "vector", "machine learning", "chatbot", "ai integration", "artificial intelligence"],
        "data-engineer": ["data", "pipeline", "etl", "analytics", "database", "sql"],
        "devops-engineer": ["devops", "ci/cd", "docker", "kubernetes", "deploy", "infrastructure"],
        "security-audit-specialist": ["security", "vulnerability", "auth", "compliance", "audit"],
        "qa-test-engineer": ["test", "qa", "quality", "testing", "coverage", "validation"],
        "accessibility-expert": ["accessibility", "a11y", "wcag", "inclusive", "screen reader"],
        "frontend-performance-specialist": ["performance", "core web vitals", "bundle", "optimize", "lcp", "react", "frontend", "web performance", "speed"],
        "seo-meta-optimizer": ["seo", "meta tags", "open graph", "structured data", "og"],
        "seo-technical-auditor": ["seo", "crawl", "sitemap", "robots.txt", "indexability"],
        "seo-performance-specialist": ["seo", "performance", "core web vitals", "mobile-first"],
        "seo-keyword-strategist": ["keywords", "search intent", "keyword research", "competitive"],
        "seo-content-optimizer": ["content", "on-page", "readability", "e-e-a-t", "snippets"],
        "seo-structure-architect": ["site architecture", "internal linking", "url structure", "silos"],
        "code-architect": ["architecture", "review", "refactor", "maintainability", "code quality"],
        "technical-writer": ["documentation", "api docs", "user guide", "tutorial", "readme"],
        "business-analyst": ["requirements", "stakeholder", "brd", "user stories", "analysis"],
        "product-manager": ["product", "roadmap", "okr", "prioritization", "product strategy"],
        "the-inventor": ["ideation", "brainstorming", "ideas", "divergent", "creativity", "inventor", "invention", "generate", "explore", "workflow"],
        "the-synthesist": ["synthesis", "framing", "convergent", "organize", "coherence", "synthesist", "combine", "integrate", "workflow", "ideation"],
        "the-architect-of-experiments": ["experiment", "hypothesis", "validation", "mvp", "testing", "architect", "design", "falsifiable", "workflow", "ideation"],
        "creative-catalyst": ["creative", "oblique strategies", "lateral thinking", "innovation", "catalyst", "disruption"],
        "the-critic": ["decision", "analysis", "tradeoffs", "evaluation", "critique"],
        "product-strategist": ["strategy", "market", "validation", "product-market fit", "startup"],
        "linux-sysadmin": ["linux", "systemd", "kernel", "firewall", "os", "sysadmin"],
        "database-administrator": ["database", "dba", "tuning", "backup", "oltp", "admin"],
    }

    def __init__(self, registry: AgentRegistry):
        """Initialize discovery engine"""
        self.registry = registry

    def discover(
        self,
        query: str,
        max_results: int = 5,
        tier_filter: Optional[AgentTier] = None
    ) -> List[AgentRecommendation]:
        """
        Discover agents matching query.

        Args:
            query: Natural language or keyword search
            max_results: Maximum recommendations to return
            tier_filter: Filter to specific tier (e.g., CORE only)

        Returns:
            List of agent recommendations sorted by relevance
        """
        query_lower = query.lower()

        # Score all agents
        scored_agents = []
        for agent_name in self.registry.list_all_agents():
            # Apply tier filter if specified
            if tier_filter and TierManager.get_tier(agent_name) != tier_filter:
                continue

            score, breakdown = self._calculate_relevance(agent_name, query_lower)

            if score > 0.1:  # Minimum threshold
                agent_meta = self.registry.get_agent(agent_name)
                explanation = self._generate_explanation(agent_name, query, breakdown)

                recommendation = AgentRecommendation(
                    agent_name=agent_name,
                    relevance_score=score,
                    tier=TierManager.get_tier(agent_name),
                    explanation=explanation,
                    match_breakdown=breakdown
                )
                scored_agents.append(recommendation)

        # Sort by relevance score (descending)
        scored_agents.sort(key=lambda x: x.relevance_score, reverse=True)

        return scored_agents[:max_results]

    def _calculate_relevance(self, agent_name: str, query: str) -> Tuple[float, Dict[str, float]]:
        """
        Calculate relevance score for agent.

        Scoring breakdown:
        - Keyword match: 40% (query matches agent keywords)
        - Intent alignment: 30% (query intent matches agent domain)
        - Context fit: 20% (agent description relevance)
        - Tier priority: 10% (Core > Extended > Experimental)
        """
        scores = {}

        # 1. Keyword match (40%)
        scores['keyword'] = self._keyword_match_score(agent_name, query) * 0.4

        # 2. Intent alignment (30%)
        scores['intent'] = self._intent_alignment_score(agent_name, query) * 0.3

        # 3. Context fit (20%)
        scores['context'] = self._context_fit_score(agent_name, query) * 0.2

        # 4. Tier priority (10%)
        scores['tier'] = self._tier_priority_score(agent_name) * 0.1

        total_score = sum(scores.values())

        return total_score, scores

    def _keyword_match_score(self, agent_name: str, query: str) -> float:
        """Score based on keyword matching"""
        # Check if query matches agent name directly (highest priority)
        if agent_name == query or agent_name.replace("-", " ") == query:
            return 1.0  # Perfect match

        if agent_name not in self.AGENT_KEYWORDS:
            return 0.0

        keywords = self.AGENT_KEYWORDS[agent_name]
        query_words = set(query.split())

        # Check for exact keyword matches (worth more)
        exact_matches = sum(1 for kw in keywords if kw == query or kw in query_words)
        # Check for partial matches (keyword appears as substring in query)
        partial_matches = sum(1 for kw in keywords if kw != query and kw in query and kw not in query_words)

        total_matches = exact_matches * 2 + partial_matches  # Exact matches worth double

        if total_matches == 0:
            return 0.0

        # Normalize by keyword count (more matches = higher score)
        # Cap at 1.0 but allow exact matches to boost score significantly
        return min(total_matches / len(keywords), 1.0)

    def _intent_alignment_score(self, agent_name: str, query: str) -> float:
        """Score based on domain intent alignment"""
        agent_meta = self.registry.get_agent(agent_name)
        if not agent_meta:
            return 0.0

        # Detect query intent
        detected_intents = []
        for intent, keywords in self.DOMAIN_INTENTS.items():
            if any(kw in query for kw in keywords):
                detected_intents.append(intent)

        if not detected_intents:
            return 0.5  # Neutral if no intent detected

        # Check if agent aligns with detected intents
        agent_desc = agent_meta.description.lower()
        intent_matches = sum(1 for intent in detected_intents if any(
            kw in agent_desc for kw in self.DOMAIN_INTENTS[intent]
        ))

        return min(intent_matches / len(detected_intents), 1.0)

    def _context_fit_score(self, agent_name: str, query: str) -> float:
        """Score based on description relevance"""
        agent_meta = self.registry.get_agent(agent_name)
        if not agent_meta:
            return 0.0

        description = agent_meta.description.lower()

        # Split query into words, filter common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "my", "i", "need", "want", "help"}
        query_words = [w for w in query.split() if w not in stop_words and len(w) > 2]

        if not query_words:
            return 0.0

        # Count how many query words appear in description
        matches = sum(1 for word in query_words if word in description)

        return min(matches / len(query_words), 1.0)

    def _tier_priority_score(self, agent_name: str) -> float:
        """Score based on agent tier (Core > Extended > Experimental)"""
        tier = TierManager.get_tier(agent_name)
        return {
            AgentTier.CORE: 1.0,
            AgentTier.EXTENDED: 0.7,
            AgentTier.EXPERIMENTAL: 0.4,
            AgentTier.UNKNOWN: 0.0,
        }[tier]

    def _generate_explanation(
        self, agent_name: str, query: str, breakdown: Dict[str, float]
    ) -> str:
        """Generate human-readable explanation for recommendation"""
        agent_meta = self.registry.get_agent(agent_name)
        if not agent_meta:
            return "Agent not found in registry"

        # Find strongest match component
        max_component = max(breakdown.items(), key=lambda x: x[1])
        component_name, component_score = max_component

        explanations = {
            'keyword': f"Strong keyword match with '{query}'",
            'intent': f"Aligns well with task intent",
            'context': f"Description matches query context",
            'tier': f"{TierManager.get_tier(agent_name).name} tier agent",
        }

        explanation = explanations.get(component_name, "Good match")

        # Add tier badge
        tier = TierManager.get_tier(agent_name)
        tier_badge = {
            AgentTier.CORE: "⭐ CORE",
            AgentTier.EXTENDED: "✓ EXTENDED",
            AgentTier.EXPERIMENTAL: "🧪 EXPERIMENTAL",
            AgentTier.UNKNOWN: "? UNKNOWN"
        }[tier]

        return f"{tier_badge} | {explanation}"


class IntelligentOrchestrator:
    """
    Orchestrates agent selection based on context and intent.

    Selection Strategy:
    1. Analyze project context
    2. Parse user intent
    3. Match to agent capabilities
    4. Consider quality requirements
    5. Check performance metrics (if telemetry available)
    6. Generate workflow with reasoning
    """

    def __init__(self, project_dir: Optional[Path] = None):
        """Initialize orchestrator"""
        self.registry = AgentRegistry()
        self.analyzer = ProjectAnalyzer(project_dir)
        self.parser = IntentParser()
        self.discovery = AgentDiscoveryEngine(self.registry)

        # Load telemetry if available
        try:
            from telemetry import TelemetryCollector
            self.telemetry = TelemetryCollector()
            self.has_telemetry = self.telemetry.is_enabled()
        except:
            self.telemetry = None
            self.has_telemetry = False

    def orchestrate(self, user_request: str) -> OrchestratedWorkflow:
        """
        Generate optimal workflow for user request.

        Returns workflow with selected agents and reasoning.
        """
        # 1. Analyze project
        context = self.analyzer.analyze()

        # 2. Parse intent
        intent = self.parser.parse(user_request)

        # 3. Select agents
        agents = self._select_agents(context, intent)

        # 4. Generate reasoning
        reasoning = self._generate_reasoning(context, intent, agents)

        # 5. Build workflow
        workflow = OrchestratedWorkflow(
            agents=agents,
            reasoning=reasoning,
            estimated_duration=self._estimate_duration(agents),
            prerequisites=self._determine_prerequisites(context, agents),
            success_criteria=self._define_success_criteria(intent, agents)
        )

        return workflow

    def _select_agents(
        self, context: ProjectContext, intent: UserIntent
    ) -> List[str]:
        """Select optimal agents for the task"""
        selected = []

        # Core agent based on intent action
        core_agent = self._select_core_agent(context, intent)
        if core_agent:
            selected.append(core_agent)

        # Quality agents based on requirements
        quality_agents = self._select_quality_agents(intent.quality_requirements)
        selected.extend(quality_agents)

        # Project-specific support agents
        support_agents = self._select_support_agents(context, intent)
        selected.extend(support_agents)

        # Remove duplicates while preserving order
        seen = set()
        result = []
        for agent in selected:
            if agent not in seen:
                seen.add(agent)
                result.append(agent)

        # Sort by tier (Core > Extended > Experimental)
        # This ensures higher-quality agents are prioritized
        result = TierManager.sort_by_tier(result)

        return result

    def _select_core_agent(
        self, context: ProjectContext, intent: UserIntent
    ) -> Optional[str]:
        """Select primary agent based on project type and action"""

        # Web projects
        if context.project_type == "web":
            if intent.action == "implement":
                return "full-stack-architect"
            elif intent.action == "review":
                return "code-architect"
            elif intent.action == "optimize":
                return "frontend-performance-specialist"

        # Mobile projects
        elif context.project_type == "mobile":
            if intent.action in ["implement", "build"]:
                return "mobile-developer"

        # Data/ML projects
        elif context.project_type in ["data", "ml"]:
            if intent.action == "implement":
                return "data-engineer" if context.project_type == "data" else "ai-ml-engineer"

        # Backend API
        elif "api" in intent.subject.lower() or "rest" in intent.subject.lower():
            return "backend-api-engineer"

        # Deployment tasks
        if intent.action == "deploy":
            return "devops-engineer"

        # Documentation tasks
        if intent.action == "document":
            return "technical-writer"

        # Debugging tasks
        if intent.action == "debug":
            return "debugging-specialist"

        # Default fallback
        return "project-orchestrator"

    def _select_quality_agents(self, requirements: List[str]) -> List[str]:
        """Select quality-focused agents"""
        agents = []

        quality_map = {
            "security": "security-audit-specialist",
            "performance": "frontend-performance-specialist",
            "accessibility": "accessibility-expert",
            "testing": "qa-test-engineer",
            "seo": "seo-meta-optimizer",
        }

        for req in requirements:
            if req in quality_map:
                agents.append(quality_map[req])

        return agents

    def _select_support_agents(
        self, context: ProjectContext, intent: UserIntent
    ) -> List[str]:
        """Select supporting agents based on project context"""
        agents = []

        # Add testing if project has tests
        if context.has_tests and intent.action == "implement":
            agents.append("qa-test-engineer")

        # Add devops if has CI/CD
        if context.has_ci_cd and intent.action in ["implement", "deploy"]:
            agents.append("devops-engineer")

        return agents

    def _generate_reasoning(
        self, context: ProjectContext, intent: UserIntent, agents: List[str]
    ) -> List[str]:
        """Generate human-readable reasoning for agent selections"""
        reasoning = []

        # Context summary
        reasoning.append(
            f"Detected {context.project_type} project with "
            f"{', '.join(context.frameworks or ['no framework'])}"
        )

        # Intent summary
        reasoning.append(
            f"Goal: {intent.action} {intent.subject}"
        )

        # Agent selection reasoning
        for agent in agents:
            agent_meta = self.registry.get_agent(agent)
            if agent_meta:
                reason = f"{agent}: {agent_meta.description[:80]}..."
                reasoning.append(reason)

        return reasoning

    def _estimate_duration(self, agents: List[str]) -> int:
        """Estimate workflow duration in minutes"""
        # Rough heuristic: 30 minutes per agent
        return len(agents) * 30

    def _determine_prerequisites(
        self, context: ProjectContext, agents: List[str]
    ) -> List[str]:
        """Determine prerequisites for workflow"""
        prereqs = []

        if "devops-engineer" in agents and not context.has_ci_cd:
            prereqs.append("Set up CI/CD configuration")

        if "qa-test-engineer" in agents and not context.has_tests:
            prereqs.append("Initialize testing framework")

        return prereqs

    def _define_success_criteria(
        self, intent: UserIntent, agents: List[str]
    ) -> List[str]:
        """Define success criteria for workflow"""
        criteria = []

        # Intent-based criteria
        if intent.action == "implement":
            criteria.append("Feature implemented and tested")
        elif intent.action == "review":
            criteria.append("Code review completed with recommendations")
        elif intent.action == "deploy":
            criteria.append("Successfully deployed to target environment")

        # Quality-based criteria
        if "security-audit-specialist" in agents:
            criteria.append("Security audit passed with no critical issues")

        if "qa-test-engineer" in agents:
            criteria.append("Test coverage >80%")

        return criteria

    def discover_agents(
        self,
        query: str,
        max_results: int = 5,
        tier_filter: Optional[AgentTier] = None
    ) -> List[AgentRecommendation]:
        """
        Discover agents matching query.

        Args:
            query: Natural language or keyword search
            max_results: Maximum recommendations to return
            tier_filter: Filter to specific tier

        Returns:
            List of agent recommendations
        """
        return self.discovery.discover(query, max_results, tier_filter)

    def print_workflow(self, workflow: OrchestratedWorkflow):
        """Print workflow in human-readable format"""
        print("\n" + "="*60)
        print("INTELLIGENT WORKFLOW ORCHESTRATION")
        print("="*60)

        print("\n📋 Selected Agents (sorted by tier):")
        for i, agent in enumerate(workflow.agents, 1):
            tier = TierManager.get_tier(agent)
            tier_badge = {
                AgentTier.CORE: "⭐ CORE",
                AgentTier.EXTENDED: "✓ EXTENDED",
                AgentTier.EXPERIMENTAL: "🧪 EXPERIMENTAL",
                AgentTier.UNKNOWN: "? UNKNOWN"
            }[tier]
            print(f"  {i}. {agent} [{tier_badge}]")

        print("\n🧠 Reasoning:")
        for reason in workflow.reasoning:
            print(f"  • {reason}")

        if workflow.prerequisites:
            print("\n⚠️  Prerequisites:")
            for prereq in workflow.prerequisites:
                print(f"  • {prereq}")

        print(f"\n⏱️  Estimated Duration: {workflow.estimated_duration} minutes")

        print("\n✅ Success Criteria:")
        for criterion in workflow.success_criteria:
            print(f"  • {criterion}")

        print("\n" + "="*60 + "\n")

    def print_recommendations(self, recommendations: List[AgentRecommendation]):
        """Print agent recommendations in human-readable format"""
        print("\n" + "="*60)
        print("AGENT DISCOVERY RESULTS")
        print("="*60)

        if not recommendations:
            print("\nNo agents found matching your query.")
            print("Try different keywords or broaden your search.")
            return

        print(f"\nTop {len(recommendations)} recommendations:\n")

        for i, rec in enumerate(recommendations, 1):
            agent_meta = self.registry.get_agent(rec.agent_name)

            print(f"{i}. {rec.agent_name}")
            print(f"   Relevance: {rec.relevance_score:.2f} | {rec.explanation}")

            if agent_meta:
                # Truncate description to 100 chars
                desc = agent_meta.description
                if len(desc) > 100:
                    desc = desc[:97] + "..."
                print(f"   {desc}")

            # Show score breakdown
            breakdown_str = " | ".join([
                f"{k}: {v:.2f}" for k, v in rec.match_breakdown.items()
            ])
            print(f"   Score: {breakdown_str}")
            print()

        print("="*60 + "\n")


def main():
    """CLI interface for intelligent orchestrator"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python intelligent_orchestrator.py <command> '<query>'")
        print("\nCommands:")
        print("  orchestrate '<request>'  - Generate workflow for user request")
        print("  discover '<query>'       - Discover agents matching query")
        print("\nExamples:")
        print("  python intelligent_orchestrator.py orchestrate 'implement authentication'")
        print("  python intelligent_orchestrator.py discover 'optimize my React app'")
        print("  python intelligent_orchestrator.py discover 'seo performance'")
        sys.exit(1)

    command = sys.argv[1]
    orchestrator = IntelligentOrchestrator()

    if command == "orchestrate":
        if len(sys.argv) < 3:
            print("Error: orchestrate requires a request")
            sys.exit(1)

        user_request = " ".join(sys.argv[2:])
        workflow = orchestrator.orchestrate(user_request)
        orchestrator.print_workflow(workflow)

    elif command == "discover":
        if len(sys.argv) < 3:
            print("Error: discover requires a query")
            sys.exit(1)

        query = " ".join(sys.argv[2:])
        recommendations = orchestrator.discover_agents(query, max_results=5)
        orchestrator.print_recommendations(recommendations)

    else:
        # Backward compatibility: treat as orchestrate command
        user_request = " ".join(sys.argv[1:])
        workflow = orchestrator.orchestrate(user_request)
        orchestrator.print_workflow(workflow)


if __name__ == "__main__":
    main()
