"""
AIL Integration Module for Production Agents

This module provides Archaeological Intelligence Layer integrations
for core production agents, enhancing their capabilities with
historical context from the Cognitive Code Archaeology system.

Integrated Agents (Sprint 2):
1. code-architect - Comprehensive code review with historical context
2. security-audit-specialist - Security reviews with vulnerability history
3. full-stack-architect - Architecture decisions with design evolution
4. backend-api-engineer - API design with endpoint history
5. qa-test-engineer - Test strategies with bug history
6. debugging-specialist - Bug investigation with fix history
7. frontend-performance-specialist - Performance optimization with regression history
"""

from .code_architect_ail import CodeArchitectAIL
from .security_audit_ail import SecurityAuditAIL
from .full_stack_architect_ail import FullStackArchitectAIL
from .backend_api_engineer_ail import BackendAPIEngineerAIL
from .qa_test_engineer_ail import QATestEngineerAIL
from .debugging_specialist_ail import DebuggingSpecialistAIL
from .frontend_performance_ail import FrontendPerformanceAIL

__all__ = [
    'CodeArchitectAIL',
    'SecurityAuditAIL',
    'FullStackArchitectAIL',
    'BackendAPIEngineerAIL',
    'QATestEngineerAIL',
    'DebuggingSpecialistAIL',
    'FrontendPerformanceAIL',
]

__version__ = '2.0.0'
