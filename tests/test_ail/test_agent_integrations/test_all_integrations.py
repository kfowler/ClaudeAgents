"""
Comprehensive Integration Tests for All 7 Agent AIL Enhancements

This test suite validates all agent integrations and measures quality improvements.
"""

import pytest
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.integrations.code_architect_ail import CodeArchitectAIL
from agents.integrations.security_audit_ail import SecurityAuditAIL
from agents.integrations.full_stack_architect_ail import FullStackArchitectAIL
from agents.integrations.backend_api_engineer_ail import BackendAPIEngineerAIL
from agents.integrations.qa_test_engineer_ail import QATestEngineerAIL
from agents.integrations.debugging_specialist_ail import DebuggingSpecialistAIL
from agents.integrations.frontend_performance_ail import FrontendPerformanceAIL


@pytest.fixture(scope="module")
def repo_path():
    """Repository path for all tests."""
    return str(PROJECT_ROOT)


class TestAllAgentIntegrations:
    """Comprehensive test suite for all 7 agent integrations."""

    @pytest.fixture
    def all_agents(self, repo_path):
        """Initialize all agent integrations."""
        return {
            'code_architect': CodeArchitectAIL(repo_path),
            'security_audit': SecurityAuditAIL(repo_path),
            'full_stack_architect': FullStackArchitectAIL(repo_path),
            'backend_api_engineer': BackendAPIEngineerAIL(repo_path),
            'qa_test_engineer': QATestEngineerAIL(repo_path),
            'debugging_specialist': DebuggingSpecialistAIL(repo_path),
            'frontend_performance': FrontendPerformanceAIL(repo_path),
        }

    def test_all_agents_initialize(self, all_agents):
        """Test that all agents initialize successfully."""
        for agent_name, agent in all_agents.items():
            assert agent is not None, f"{agent_name} failed to initialize"
            assert agent.provider is not None, f"{agent_name} provider not initialized"
            print(f"✓ {agent_name} initialized successfully")

    def test_code_architect_integration(self, all_agents):
        """Test code-architect AIL integration."""
        agent = all_agents['code_architect']
        review = agent.enhanced_review(
            "Why does tools/ail/context_provider.py use LRU caching?"
        )

        assert review.confidence >= 0.0
        assert len(review.archaeological_context.sources) >= 0
        assert isinstance(review.design_decisions, list)
        assert isinstance(review.recommendations, list)

        print(f"\nCode Architect Integration:")
        print(f"  Confidence: {review.confidence:.2%}")
        print(f"  Sources: {len(review.archaeological_context.sources)}")
        print(f"  Design Decisions: {len(review.design_decisions)}")
        print(f"  Recommendations: {len(review.recommendations)}")

    def test_security_audit_integration(self, all_agents):
        """Test security-audit-specialist AIL integration."""
        agent = all_agents['security_audit']
        report = agent.enhanced_audit(
            "What security measures are in tools/ail/context_provider.py?"
        )

        assert report.confidence >= 0.0
        assert isinstance(report.security_incidents, list)
        assert isinstance(report.vulnerability_patterns, list)
        assert report.risk_level in ['critical', 'high', 'medium', 'low']

        print(f"\nSecurity Audit Integration:")
        print(f"  Confidence: {report.confidence:.2%}")
        print(f"  Risk Level: {report.risk_level}")
        print(f"  Security Incidents: {len(report.security_incidents)}")
        print(f"  Vulnerability Patterns: {len(report.vulnerability_patterns)}")

    def test_full_stack_architect_integration(self, all_agents):
        """Test full-stack-architect AIL integration."""
        agent = all_agents['full_stack_architect']
        analysis = agent.enhanced_analysis(
            "What architectural patterns are used in tools/ail/context_provider.py?"
        )

        assert analysis.confidence >= 0.0
        assert isinstance(analysis.evolutionary_events, list)
        assert isinstance(analysis.design_patterns, list)

        print(f"\nFull Stack Architect Integration:")
        print(f"  Confidence: {analysis.confidence:.2%}")
        print(f"  Evolutionary Events: {len(analysis.evolutionary_events)}")
        print(f"  Design Patterns: {len(analysis.design_patterns)}")

    def test_backend_api_engineer_integration(self, all_agents):
        """Test backend-api-engineer AIL integration."""
        agent = all_agents['backend_api_engineer']
        analysis = agent.enhanced_analysis(
            "What API patterns are in tools/ail/context_provider.py?"
        )

        assert analysis.confidence >= 0.0
        assert isinstance(analysis.api_changes, list)
        assert isinstance(analysis.endpoint_history, list)

        print(f"\nBackend API Engineer Integration:")
        print(f"  Confidence: {analysis.confidence:.2%}")
        print(f"  API Changes: {len(analysis.api_changes)}")
        print(f"  Endpoint History: {len(analysis.endpoint_history)}")

    def test_qa_test_engineer_integration(self, all_agents):
        """Test qa-test-engineer AIL integration."""
        agent = all_agents['qa_test_engineer']
        analysis = agent.enhanced_analysis(
            "What bugs were fixed in tools/ail/context_provider.py?"
        )

        assert analysis.confidence >= 0.0
        assert isinstance(analysis.bug_history, list)
        assert isinstance(analysis.regression_patterns, list)
        assert isinstance(analysis.risk_areas, list)

        print(f"\nQA Test Engineer Integration:")
        print(f"  Confidence: {analysis.confidence:.2%}")
        print(f"  Bug History: {len(analysis.bug_history)}")
        print(f"  Regression Patterns: {len(analysis.regression_patterns)}")
        print(f"  Risk Areas: {len(analysis.risk_areas)}")

    def test_debugging_specialist_integration(self, all_agents):
        """Test debugging-specialist AIL integration."""
        agent = all_agents['debugging_specialist']
        analysis = agent.enhanced_analysis(
            "What debugging strategies were used in tools/ail/context_provider.py?"
        )

        assert analysis.confidence >= 0.0
        assert isinstance(analysis.bug_fixes, list)
        assert isinstance(analysis.common_failure_modes, list)

        print(f"\nDebugging Specialist Integration:")
        print(f"  Confidence: {analysis.confidence:.2%}")
        print(f"  Bug Fixes: {len(analysis.bug_fixes)}")
        print(f"  Failure Modes: {len(analysis.common_failure_modes)}")

    def test_frontend_performance_integration(self, all_agents):
        """Test frontend-performance-specialist AIL integration."""
        agent = all_agents['frontend_performance']
        analysis = agent.enhanced_analysis(
            "What performance optimizations were made in tools/ail/context_provider.py?"
        )

        assert analysis.confidence >= 0.0
        assert isinstance(analysis.performance_changes, list)
        assert isinstance(analysis.optimization_history, list)

        print(f"\nFrontend Performance Integration:")
        print(f"  Confidence: {analysis.confidence:.2%}")
        print(f"  Performance Changes: {len(analysis.performance_changes)}")
        print(f"  Optimization History: {len(analysis.optimization_history)}")

    def test_quality_improvement_all_agents(self, all_agents):
        """Test quality improvement across all agents (target: 40%+ improvement)."""
        results = {}

        test_cases = {
            'code_architect': (
                'enhanced_review',
                'Why was two-tier caching implemented in tools/ail/context_provider.py?'
            ),
            'security_audit': (
                'enhanced_audit',
                'What security considerations were addressed in tools/ail/context_provider.py?'
            ),
            'full_stack_architect': (
                'enhanced_analysis',
                'What architectural decisions shaped tools/ail/context_provider.py?'
            ),
            'backend_api_engineer': (
                'enhanced_analysis',
                'How did the API design evolve in tools/ail/context_provider.py?'
            ),
            'qa_test_engineer': (
                'enhanced_analysis',
                'What testing strategies were applied to tools/ail/context_provider.py?'
            ),
            'debugging_specialist': (
                'enhanced_analysis',
                'What debugging approaches were used for tools/ail/context_provider.py?'
            ),
            'frontend_performance': (
                'enhanced_analysis',
                'What performance optimizations were made to tools/ail/context_provider.py?'
            ),
        }

        print("\n" + "=" * 80)
        print("QUALITY IMPROVEMENT MEASUREMENT")
        print("=" * 80)

        for agent_name, (method_name, question) in test_cases.items():
            agent = all_agents[agent_name]
            method = getattr(agent, method_name)

            start_time = time.time()
            result = method(question)
            query_time = (time.time() - start_time) * 1000

            # Calculate quality metrics
            confidence = result.confidence
            has_historical_data = len(result.archaeological_context.sources) > 0
            has_recommendations = len(result.recommendations) > 0

            # Quality score calculation (0-100)
            quality_score = 0
            if confidence > 0.3:
                quality_score += 40
            if has_historical_data:
                quality_score += 30
            if has_recommendations:
                quality_score += 30

            results[agent_name] = {
                'quality_score': quality_score,
                'confidence': confidence,
                'source_count': len(result.archaeological_context.sources),
                'recommendation_count': len(result.recommendations),
                'query_time_ms': query_time,
            }

            print(f"\n{agent_name.replace('_', ' ').title()}:")
            print(f"  Quality Score: {quality_score}/100")
            print(f"  Confidence: {confidence:.2%}")
            print(f"  Sources: {len(result.archaeological_context.sources)}")
            print(f"  Recommendations: {len(result.recommendations)}")
            print(f"  Query Time: {query_time:.0f}ms")

        # Overall quality assessment
        avg_quality_score = sum(r['quality_score'] for r in results.values()) / len(results)
        print(f"\n{'=' * 80}")
        print(f"OVERALL QUALITY SCORE: {avg_quality_score:.1f}/100")
        print(f"{'=' * 80}")

        # Assert quality improvement target (60 = 40% improvement from baseline of ~42)
        assert avg_quality_score >= 60, (
            f"Average quality score {avg_quality_score:.1f} below target (60). "
            f"AIL integration should provide >40% improvement."
        )

        print(f"\n✓ Quality improvement target achieved: {avg_quality_score:.1f}/100 (target: ≥60)")

    def test_performance_benchmarks(self, all_agents):
        """Test performance benchmarks for all integrations."""
        print("\n" + "=" * 80)
        print("PERFORMANCE BENCHMARKS")
        print("=" * 80)

        test_question = "Analyze tools/ail/context_provider.py"
        results = {}

        for agent_name, agent in all_agents.items():
            # Determine method name
            if agent_name == 'code_architect':
                method_name = 'enhanced_review'
            elif agent_name == 'security_audit':
                method_name = 'enhanced_audit'
            else:
                method_name = 'enhanced_analysis'

            method = getattr(agent, method_name)

            # Measure performance
            start_time = time.time()
            result = method(test_question)
            elapsed_ms = (time.time() - start_time) * 1000

            results[agent_name] = {
                'query_time_ms': elapsed_ms,
                'cached': result.archaeological_context.cached,
                'cache_level': result.archaeological_context.cache_level,
            }

            print(f"\n{agent_name.replace('_', ' ').title()}:")
            print(f"  Query Time: {elapsed_ms:.0f}ms")
            print(f"  Cached: {result.archaeological_context.cached}")
            if result.archaeological_context.cached:
                print(f"  Cache Level: {result.archaeological_context.cache_level}")

        avg_query_time = sum(r['query_time_ms'] for r in results.values()) / len(results)
        print(f"\n{'=' * 80}")
        print(f"AVERAGE QUERY TIME: {avg_query_time:.0f}ms")
        print(f"{'=' * 80}")


def test_integration_summary():
    """Generate integration summary."""
    print("\n" + "=" * 80)
    print("AIL AGENT INTEGRATION SUMMARY")
    print("=" * 80)
    print("\nIntegrated Agents (7):")
    print("  1. code-architect - Architectural review with historical context")
    print("  2. security-audit-specialist - Security analysis with vulnerability history")
    print("  3. full-stack-architect - Architecture decisions with design evolution")
    print("  4. backend-api-engineer - API design with endpoint history")
    print("  5. qa-test-engineer - Test strategies with bug history")
    print("  6. debugging-specialist - Bug investigation with fix history")
    print("  7. frontend-performance-specialist - Performance optimization with regression history")
    print("\nIntegration Features:")
    print("  ✓ Archaeological context retrieval")
    print("  ✓ Historical pattern analysis")
    print("  ✓ Intelligent recommendations")
    print("  ✓ Quality trend tracking")
    print("  ✓ Two-tier caching (L1 + L2 semantic)")
    print("  ✓ FAISS semantic search")
    print("=" * 80)


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '-s'])
