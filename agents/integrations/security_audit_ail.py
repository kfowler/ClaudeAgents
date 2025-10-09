"""
AIL Integration for security-audit-specialist Agent

Enhances security-audit-specialist with archaeological intelligence for:
- Historical vulnerability patterns and fixes
- Security incident history and remediation
- Authentication/authorization evolution
- Dependency vulnerability history
- Security policy changes over time
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.ail.context_provider import ArchaeologyContextProvider, ArchaeologicalContext
from tools.ail.agent_integration import (
    get_context_from_input,
    extract_file_path,
    formulate_question,
)

logger = logging.getLogger(__name__)


@dataclass
class SecurityIncident:
    """Security incident extracted from history."""

    incident_type: str  # "vulnerability", "breach", "misconfig", "dependency"
    description: str
    severity: str  # "critical", "high", "medium", "low"
    remediation: str
    date: datetime
    author: str
    commit_sha: str
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            'incident_type': self.incident_type,
            'description': self.description,
            'severity': self.severity,
            'remediation': self.remediation,
            'date': self.date.isoformat(),
            'author': self.author,
            'commit_sha': self.commit_sha,
            'confidence': self.confidence,
        }


@dataclass
class SecurityAuditReport:
    """Enhanced security audit with AIL context."""

    file_path: str
    audit_question: str
    archaeological_context: ArchaeologicalContext
    security_incidents: List[SecurityIncident]
    vulnerability_patterns: List[str]
    authentication_evolution: List[str]
    security_policy_changes: List[str]
    dependency_vulnerabilities: List[str]
    recommendations: List[str]
    risk_level: str  # "critical", "high", "medium", "low"
    confidence: float
    query_time_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            'file_path': self.file_path,
            'audit_question': self.audit_question,
            'archaeological_answer': self.archaeological_context.answer,
            'security_incidents': [i.to_dict() for i in self.security_incidents],
            'vulnerability_patterns': self.vulnerability_patterns,
            'authentication_evolution': self.authentication_evolution,
            'security_policy_changes': self.security_policy_changes,
            'dependency_vulnerabilities': self.dependency_vulnerabilities,
            'recommendations': self.recommendations,
            'risk_level': self.risk_level,
            'confidence': self.confidence,
            'query_time_ms': self.query_time_ms,
        }

    def to_markdown(self) -> str:
        lines = [
            f"# Security Audit Report: {self.file_path}",
            f"**Question**: {self.audit_question}",
            f"**Risk Level**: {self.risk_level.upper()}",
            f"**Confidence**: {self.confidence:.1%}",
            "",
            "## Archaeological Context",
            self.archaeological_context.answer,
            "",
        ]

        if self.security_incidents:
            lines.append("## Security Incidents")
            for incident in self.security_incidents:
                lines.append(f"### {incident.incident_type.replace('_', ' ').title()} ({incident.severity.upper()})")
                lines.append(f"**Description**: {incident.description}")
                lines.append(f"**Remediation**: {incident.remediation}")
                lines.append(f"**Date**: {incident.date.date()} by {incident.author}")
                lines.append("")

        if self.vulnerability_patterns:
            lines.append("## Vulnerability Patterns")
            for pattern in self.vulnerability_patterns:
                lines.append(f"- {pattern}")
            lines.append("")

        if self.authentication_evolution:
            lines.append("## Authentication Evolution")
            for evolution in self.authentication_evolution:
                lines.append(f"- {evolution}")
            lines.append("")

        if self.dependency_vulnerabilities:
            lines.append("## Dependency Vulnerabilities")
            for vuln in self.dependency_vulnerabilities:
                lines.append(f"- {vuln}")
            lines.append("")

        if self.recommendations:
            lines.append("## Security Recommendations")
            for i, rec in enumerate(self.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        lines.append(f"*Query time: {self.query_time_ms:.0f}ms | Sources: {len(self.archaeological_context.sources)}*")
        return "\n".join(lines)


class SecurityAuditAIL:
    """
    Enhances security-audit-specialist with Archaeological Intelligence.

    Provides historical security context including:
    - Vulnerability patterns and past incidents
    - Authentication/authorization evolution
    - Security policy changes
    - Dependency vulnerability tracking
    """

    def __init__(self, repo_path: str):
        self.provider = ArchaeologyContextProvider(repo_path)
        self.repo_path = Path(repo_path).resolve()
        logger.info(f"SecurityAuditAIL initialized for: {repo_path}")

    def enhanced_audit(self, user_input: str) -> SecurityAuditReport:
        """Perform enhanced security audit with archaeological context."""
        context = get_context_from_input(self.provider, user_input)

        if not context:
            file_path = extract_file_path(user_input, str(self.repo_path))
            if not file_path:
                raise ValueError("Could not extract file path from input")
            question = formulate_question(user_input, task_type="review")
            context = self.provider.get_context_sync(file_path, question)

        incidents = self._extract_security_incidents(context)
        vulnerability_patterns = self._extract_vulnerability_patterns(context)
        auth_evolution = self._extract_authentication_evolution(context)
        policy_changes = self._extract_security_policy_changes(context)
        dependency_vulns = self._extract_dependency_vulnerabilities(context)
        risk_level = self._assess_risk_level(incidents, vulnerability_patterns)
        recommendations = self._generate_security_recommendations(
            incidents, vulnerability_patterns, risk_level
        )

        return SecurityAuditReport(
            file_path=context.file_path,
            audit_question=context.question,
            archaeological_context=context,
            security_incidents=incidents,
            vulnerability_patterns=vulnerability_patterns,
            authentication_evolution=auth_evolution,
            security_policy_changes=policy_changes,
            dependency_vulnerabilities=dependency_vulns,
            recommendations=recommendations,
            risk_level=risk_level,
            confidence=context.confidence,
            query_time_ms=context.query_time_ms,
        )

    def _extract_security_incidents(
        self, context: ArchaeologicalContext
    ) -> List[SecurityIncident]:
        """Extract security incidents from archaeological context."""
        incidents = []
        security_keywords = {
            'vulnerability': ['vulnerability', 'vuln', 'cve', 'exploit', 'security hole'],
            'breach': ['breach', 'unauthorized', 'intrusion', 'attack'],
            'misconfig': ['misconfiguration', 'misconfig', 'exposed', 'leaked'],
            'dependency': ['dependency', 'package', 'library', 'upgrade security'],
        }

        severity_keywords = {
            'critical': ['critical', 'severe', 'emergency'],
            'high': ['high', 'important', 'serious'],
            'medium': ['medium', 'moderate'],
            'low': ['low', 'minor', 'trivial'],
        }

        for source in context.sources[:5]:
            msg_lower = source.commit_message.lower()

            # Determine incident type
            incident_type = 'vulnerability'
            for itype, keywords in security_keywords.items():
                if any(kw in msg_lower for kw in keywords):
                    incident_type = itype
                    break

            # Determine severity
            severity = 'medium'
            for sev, keywords in severity_keywords.items():
                if any(kw in msg_lower for kw in keywords):
                    severity = sev
                    break

            # Check if it's actually a security-related commit
            if any(kw in msg_lower for incident_keywords in security_keywords.values()
                   for kw in incident_keywords):
                incidents.append(SecurityIncident(
                    incident_type=incident_type,
                    description=source.commit_message[:200],
                    severity=severity,
                    remediation=source.excerpt[:200],
                    date=source.date,
                    author=source.author,
                    commit_sha=source.commit_sha,
                    confidence=source.relevance_score,
                ))

        return incidents

    def _extract_vulnerability_patterns(self, context: ArchaeologicalContext) -> List[str]:
        """Extract vulnerability patterns from context."""
        patterns = []
        vuln_keywords = [
            'sql injection', 'xss', 'csrf', 'rce', 'authentication bypass',
            'authorization', 'privilege escalation', 'buffer overflow',
            'path traversal', 'xxe', 'deserialization', 'injection'
        ]

        for source in context.sources:
            msg_lower = source.commit_message.lower()
            for keyword in vuln_keywords:
                if keyword in msg_lower:
                    patterns.append(
                        f"{keyword.title()} addressed in {source.commit_sha[:8]} by {source.author}"
                    )
                    break

        return patterns[:5]

    def _extract_authentication_evolution(self, context: ArchaeologicalContext) -> List[str]:
        """Extract authentication/authorization evolution."""
        evolution = []
        auth_keywords = [
            'authentication', 'authorization', 'auth', 'login', 'oauth',
            'jwt', 'session', 'token', 'password', 'credential'
        ]

        for source in context.sources:
            if any(kw in source.commit_message.lower() for kw in auth_keywords):
                evolution.append(
                    f"{source.commit_message[:100]} ({source.date.date()})"
                )

        return evolution[:5]

    def _extract_security_policy_changes(self, context: ArchaeologicalContext) -> List[str]:
        """Extract security policy changes."""
        changes = []
        policy_keywords = [
            'policy', 'compliance', 'gdpr', 'hipaa', 'pci', 'security standard',
            'audit', 'encryption', 'tls', 'ssl', 'certificate'
        ]

        for source in context.sources:
            if any(kw in source.commit_message.lower() for kw in policy_keywords):
                changes.append(
                    f"{source.commit_message[:100]} ({source.date.date()})"
                )

        return changes[:5]

    def _extract_dependency_vulnerabilities(self, context: ArchaeologicalContext) -> List[str]:
        """Extract dependency vulnerability information."""
        vulns = []
        dep_keywords = [
            'upgrade', 'update dependency', 'security patch', 'npm audit',
            'pip audit', 'vulnerability scan', 'dependabot'
        ]

        for source in context.sources:
            if any(kw in source.commit_message.lower() for kw in dep_keywords):
                vulns.append(
                    f"{source.commit_message[:100]} ({source.date.date()})"
                )

        return vulns[:5]

    def _assess_risk_level(
        self, incidents: List[SecurityIncident], patterns: List[str]
    ) -> str:
        """Assess overall risk level."""
        if any(i.severity == 'critical' for i in incidents):
            return 'critical'
        elif any(i.severity == 'high' for i in incidents) or len(incidents) > 3:
            return 'high'
        elif len(patterns) > 2:
            return 'medium'
        else:
            return 'low'

    def _generate_security_recommendations(
        self, incidents: List[SecurityIncident], patterns: List[str], risk_level: str
    ) -> List[str]:
        """Generate security recommendations."""
        recommendations = []

        if risk_level in ['critical', 'high']:
            recommendations.append(
                "URGENT: High-risk security issues detected. Conduct immediate security review."
            )

        if len(incidents) > 2:
            recommendations.append(
                "Multiple security incidents found in history. Consider security training "
                "for development team and implementing automated security scanning."
            )

        if len(patterns) > 1:
            recommendations.append(
                "Recurring vulnerability patterns detected. Implement security code review "
                "checklist and static analysis tools (e.g., Semgrep, Bandit, ESLint security plugins)."
            )

        if not incidents:
            recommendations.append(
                "No major security incidents found in history. Continue security best practices "
                "and regular dependency updates."
            )

        return recommendations


def main():
    """CLI entry point for testing."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python security_audit_ail.py <repo_path> <audit_question>")
        print("\nExample:")
        print("  python security_audit_ail.py . 'What security vulnerabilities were found in auth.py?'")
        sys.exit(1)

    repo_path = sys.argv[1]
    audit_question = " ".join(sys.argv[2:])

    auditor = SecurityAuditAIL(repo_path)
    report = auditor.enhanced_audit(audit_question)
    print(report.to_markdown())


if __name__ == '__main__':
    main()
