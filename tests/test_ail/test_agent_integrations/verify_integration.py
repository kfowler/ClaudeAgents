"""
Integration Verification Script

Quick verification that all 7 agent integrations are working correctly.
"""

import sys
from pathlib import Path

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


def verify_integration():
    """Verify all agent integrations."""
    print("=" * 80)
    print("AIL AGENT INTEGRATION VERIFICATION")
    print("=" * 80)
    print()

    repo_path = str(PROJECT_ROOT)
    test_file = "tools/ail/context_provider.py"

    agents = {
        'code-architect': (CodeArchitectAIL, 'enhanced_review'),
        'security-audit-specialist': (SecurityAuditAIL, 'enhanced_audit'),
        'full-stack-architect': (FullStackArchitectAIL, 'enhanced_analysis'),
        'backend-api-engineer': (BackendAPIEngineerAIL, 'enhanced_analysis'),
        'qa-test-engineer': (QATestEngineerAIL, 'enhanced_analysis'),
        'debugging-specialist': (DebuggingSpecialistAIL, 'enhanced_analysis'),
        'frontend-performance-specialist': (FrontendPerformanceAIL, 'enhanced_analysis'),
    }

    results = {}
    passed = 0
    failed = 0

    for agent_name, (AgentClass, method_name) in agents.items():
        print(f"Testing {agent_name}...")

        try:
            # Initialize agent
            agent = AgentClass(repo_path)

            # Run analysis
            method = getattr(agent, method_name)
            result = method(f"Analyze {test_file}")

            # Verify result structure
            assert result is not None, "Result is None"
            assert hasattr(result, 'confidence'), "Missing confidence attribute"
            assert hasattr(result, 'archaeological_context'), "Missing archaeological_context"
            assert hasattr(result, 'recommendations'), "Missing recommendations"
            assert result.confidence >= 0.0, "Invalid confidence value"

            # Collect metrics
            results[agent_name] = {
                'status': 'PASSED',
                'confidence': result.confidence,
                'sources': len(result.archaeological_context.sources),
                'recommendations': len(result.recommendations),
            }

            print(f"  ✓ PASSED (confidence: {result.confidence:.1%})")
            passed += 1

        except Exception as e:
            results[agent_name] = {
                'status': 'FAILED',
                'error': str(e),
            }
            print(f"  ✗ FAILED: {e}")
            failed += 1

        print()

    # Summary
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"\nTotal Agents: {len(agents)}")
    print(f"Passed: {passed} ✓")
    print(f"Failed: {failed} ✗")
    print()

    # Detailed results
    if passed > 0:
        print("Passed Agents:")
        for agent_name, metrics in results.items():
            if metrics['status'] == 'PASSED':
                print(f"  ✓ {agent_name}")
                print(f"    - Confidence: {metrics['confidence']:.1%}")
                print(f"    - Sources: {metrics['sources']}")
                print(f"    - Recommendations: {metrics['recommendations']}")

    if failed > 0:
        print("\nFailed Agents:")
        for agent_name, metrics in results.items():
            if metrics['status'] == 'FAILED':
                print(f"  ✗ {agent_name}: {metrics['error']}")

    print("\n" + "=" * 80)

    # Exit code
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(verify_integration())
