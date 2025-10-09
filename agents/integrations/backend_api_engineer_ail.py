"""
AIL Integration for backend-api-engineer Agent

Enhances backend-api-engineer with archaeological intelligence for:
- API endpoint evolution and versioning history
- Database schema changes and migrations
- Authentication/authorization changes
- Performance optimization history
- Breaking changes and deprecation patterns
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.ail.context_provider import ArchaeologyContextProvider, ArchaeologicalContext
from tools.ail.agent_integration import get_context_from_input, extract_file_path, formulate_question

logger = logging.getLogger(__name__)


@dataclass
class APIChange:
    """API change event."""

    change_type: str  # "endpoint_added", "endpoint_modified", "endpoint_deprecated", "breaking_change"
    description: str
    impact: str  # "breaking", "backward_compatible", "internal"
    version: str
    date: datetime
    author: str
    commit_sha: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'change_type': self.change_type,
            'description': self.description,
            'impact': self.impact,
            'version': self.version,
            'date': self.date.isoformat(),
            'author': self.author,
            'commit_sha': self.commit_sha,
        }


@dataclass
class APIAnalysis:
    """Enhanced API analysis with AIL context."""

    file_path: str
    analysis_question: str
    archaeological_context: ArchaeologicalContext
    api_changes: List[APIChange]
    endpoint_history: List[str]
    schema_migrations: List[str]
    auth_changes: List[str]
    performance_history: List[str]
    breaking_changes: List[str]
    recommendations: List[str]
    confidence: float
    query_time_ms: float

    def to_markdown(self) -> str:
        lines = [
            f"# API Analysis: {self.file_path}",
            f"**Question**: {self.analysis_question}",
            f"**Confidence**: {self.confidence:.1%}",
            "",
            "## Archaeological Context",
            self.archaeological_context.answer,
            "",
        ]

        if self.api_changes:
            lines.append("## API Changes")
            for change in self.api_changes:
                lines.append(f"### {change.change_type.replace('_', ' ').title()} ({change.impact.upper()})")
                lines.append(f"**Description**: {change.description}")
                lines.append(f"**Date**: {change.date.date()} by {change.author}")
                lines.append("")

        if self.breaking_changes:
            lines.append("## Breaking Changes")
            for change in self.breaking_changes:
                lines.append(f"- {change}")
            lines.append("")

        if self.schema_migrations:
            lines.append("## Database Schema Migrations")
            for migration in self.schema_migrations:
                lines.append(f"- {migration}")
            lines.append("")

        if self.recommendations:
            lines.append("## Recommendations")
            for i, rec in enumerate(self.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        lines.append(f"*Query time: {self.query_time_ms:.0f}ms*")
        return "\n".join(lines)


class BackendAPIEngineerAIL:
    """Enhances backend-api-engineer with Archaeological Intelligence."""

    def __init__(self, repo_path: str):
        self.provider = ArchaeologyContextProvider(repo_path)
        self.repo_path = Path(repo_path).resolve()
        logger.info(f"BackendAPIEngineerAIL initialized for: {repo_path}")

    def enhanced_analysis(self, user_input: str) -> APIAnalysis:
        """Perform enhanced API analysis with archaeological context."""
        context = get_context_from_input(self.provider, user_input)

        if not context:
            file_path = extract_file_path(user_input, str(self.repo_path))
            if not file_path:
                raise ValueError("Could not extract file path from input")
            question = formulate_question(user_input, task_type="implement")
            context = self.provider.get_context_sync(file_path, question)

        api_changes = self._extract_api_changes(context)
        endpoint_history = self._extract_endpoint_history(context)
        schema_migrations = self._extract_schema_migrations(context)
        auth_changes = self._extract_auth_changes(context)
        performance_history = self._extract_performance_history(context)
        breaking_changes = self._extract_breaking_changes(context)
        recommendations = self._generate_recommendations(
            api_changes, breaking_changes, schema_migrations
        )

        return APIAnalysis(
            file_path=context.file_path,
            analysis_question=context.question,
            archaeological_context=context,
            api_changes=api_changes,
            endpoint_history=endpoint_history,
            schema_migrations=schema_migrations,
            auth_changes=auth_changes,
            performance_history=performance_history,
            breaking_changes=breaking_changes,
            recommendations=recommendations,
            confidence=context.confidence,
            query_time_ms=context.query_time_ms,
        )

    def _extract_api_changes(self, context: ArchaeologicalContext) -> List[APIChange]:
        """Extract API changes from context."""
        changes = []
        change_keywords = {
            'endpoint_added': ['add endpoint', 'new endpoint', 'create endpoint'],
            'endpoint_modified': ['update endpoint', 'modify endpoint', 'change endpoint'],
            'endpoint_deprecated': ['deprecate', 'remove endpoint', 'delete endpoint'],
            'breaking_change': ['breaking', 'breaking change', 'incompatible'],
        }

        for source in context.sources[:5]:
            msg_lower = source.commit_message.lower()

            change_type = 'endpoint_modified'
            for ctype, keywords in change_keywords.items():
                if any(kw in msg_lower for kw in keywords):
                    change_type = ctype
                    break

            impact = 'backward_compatible'
            if 'breaking' in msg_lower:
                impact = 'breaking'
            elif 'internal' in msg_lower:
                impact = 'internal'

            changes.append(APIChange(
                change_type=change_type,
                description=source.commit_message[:200],
                impact=impact,
                version="",  # Could extract from commit message
                date=source.date,
                author=source.author,
                commit_sha=source.commit_sha,
            ))

        return changes

    def _extract_endpoint_history(self, context: ArchaeologicalContext) -> List[str]:
        """Extract endpoint history."""
        history = []
        endpoint_keywords = ['endpoint', 'route', 'api', 'handler', 'controller']

        for source in context.sources:
            if any(kw in source.commit_message.lower() for kw in endpoint_keywords):
                history.append(f"{source.commit_message[:100]} ({source.date.date()})")

        return history[:5]

    def _extract_schema_migrations(self, context: ArchaeologicalContext) -> List[str]:
        """Extract database schema migrations."""
        migrations = []
        schema_keywords = ['migration', 'schema', 'database', 'table', 'column', 'index']

        for source in context.sources:
            if any(kw in source.commit_message.lower() for kw in schema_keywords):
                migrations.append(f"{source.commit_message[:100]} ({source.date.date()})")

        return migrations[:5]

    def _extract_auth_changes(self, context: ArchaeologicalContext) -> List[str]:
        """Extract authentication/authorization changes."""
        changes = []
        auth_keywords = ['auth', 'authentication', 'authorization', 'permission', 'role', 'jwt']

        for source in context.sources:
            if any(kw in source.commit_message.lower() for kw in auth_keywords):
                changes.append(f"{source.commit_message[:100]} ({source.date.date()})")

        return changes[:5]

    def _extract_performance_history(self, context: ArchaeologicalContext) -> List[str]:
        """Extract performance optimization history."""
        history = []
        perf_keywords = ['performance', 'optimize', 'cache', 'index', 'query', 'n+1']

        for source in context.sources:
            if any(kw in source.commit_message.lower() for kw in perf_keywords):
                history.append(f"{source.commit_message[:100]} ({source.date.date()})")

        return history[:5]

    def _extract_breaking_changes(self, context: ArchaeologicalContext) -> List[str]:
        """Extract breaking changes."""
        breaking = []
        breaking_keywords = ['breaking', 'incompatible', 'major version', 'removed', 'deprecated']

        for source in context.sources:
            if any(kw in source.commit_message.lower() for kw in breaking_keywords):
                breaking.append(f"{source.commit_message[:100]} ({source.date.date()})")

        return breaking[:3]

    def _generate_recommendations(
        self, changes: List[APIChange], breaking: List[str], migrations: List[str]
    ) -> List[str]:
        """Generate API recommendations."""
        recommendations = []

        if len(breaking) > 1:
            recommendations.append(
                "Multiple breaking changes detected. Implement API versioning strategy "
                "and maintain backward compatibility where possible."
            )

        if len(migrations) > 3:
            recommendations.append(
                "Frequent schema migrations detected. Consider using database migration "
                "tools (e.g., Alembic, Flyway) and implement rollback procedures."
            )

        if not recommendations:
            recommendations.append(
                "API shows healthy evolution. Continue documenting changes in changelogs "
                "and maintain comprehensive API documentation."
            )

        return recommendations


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python backend_api_engineer_ail.py <repo_path> <question>")
        sys.exit(1)

    repo_path = sys.argv[1]
    question = " ".join(sys.argv[2:])

    engineer = BackendAPIEngineerAIL(repo_path)
    analysis = engineer.enhanced_analysis(question)
    print(analysis.to_markdown())


if __name__ == '__main__':
    main()
