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
from agent_registry import AgentRegistry, AgentMetadata


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
        "security": ["secure", "security", "auth", "authentication", "encryption"],
        "performance": ["fast", "performance", "optimize", "speed", "efficient"],
        "accessibility": ["accessible", "a11y", "wcag", "aria", "screen reader"],
        "testing": ["test", "coverage", "quality", "reliable"],
        "seo": ["seo", "search", "ranking", "visibility"],
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

    def print_workflow(self, workflow: OrchestratedWorkflow):
        """Print workflow in human-readable format"""
        print("\n" + "="*60)
        print("INTELLIGENT WORKFLOW ORCHESTRATION")
        print("="*60)

        print("\n📋 Selected Agents:")
        for i, agent in enumerate(workflow.agents, 1):
            print(f"  {i}. {agent}")

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


def main():
    """CLI interface for intelligent orchestrator"""
    import sys

    orchestrator = IntelligentOrchestrator()

    if len(sys.argv) < 2:
        print("Usage: python intelligent_orchestrator.py '<user request>'")
        print("\nExamples:")
        print("  python intelligent_orchestrator.py 'implement authentication system'")
        print("  python intelligent_orchestrator.py 'review code for security issues'")
        print("  python intelligent_orchestrator.py 'optimize frontend performance'")
        sys.exit(1)

    user_request = " ".join(sys.argv[1:])

    # Generate workflow
    workflow = orchestrator.orchestrate(user_request)

    # Print results
    orchestrator.print_workflow(workflow)


if __name__ == "__main__":
    main()
