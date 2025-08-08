#!/usr/bin/env python3
"""
Demonstration script for the Project Context Analysis System

Shows how the system analyzes projects and provides intelligent agent recommendations
that integrate with the Claude Code agent selection framework.
"""

import sys
import os
sys.path.insert(0, '.')

from analysis import (
    ProjectAnalyzer, 
    AgentRecommender, 
    get_recommended_agents,
    analyze_project_quick,
    detect_project_type
)
from analysis.integration import get_smart_agent_recommendations


def demo_basic_analysis():
    """Demonstrate basic project analysis"""
    print("🔍 BASIC PROJECT ANALYSIS")
    print("=" * 50)
    
    analyzer = ProjectAnalyzer()
    context = analyzer.analyze_project('.')
    
    print(f"Project Path: {context.project_path}")
    print(f"Domain Type: {context.architecture.domain_type.replace('_', ' ').title()}")
    
    if context.tech_stack.languages:
        print(f"Languages: {', '.join(context.tech_stack.languages.keys())}")
    
    print(f"Files: {context.complexity.file_count:,}")
    print(f"Lines of Code: {context.complexity.line_count:,}")
    print(f"Technical Debt Score: {context.complexity.technical_debt_score:.1f}/100")
    
    quality_indicators = [
        ("Tests", "✅" if context.quality.has_tests else "❌"),
        ("CI/CD", "✅" if context.quality.has_ci_cd else "❌"),
        ("Documentation", "✅" if context.quality.has_documentation else "❌"),
        ("Linting", "✅" if context.quality.has_linting else "❌")
    ]
    
    print("Quality Indicators:")
    for indicator, status in quality_indicators:
        print(f"  {status} {indicator}")
    
    print()


def demo_agent_recommendations():
    """Demonstrate agent recommendation system"""
    print("🤖 AGENT RECOMMENDATIONS")
    print("=" * 50)
    
    test_scenarios = [
        ("Build a web application", "web development"),
        ("Add AI features", "AI integration"),
        ("Deploy to production", "deployment"),
        ("Security audit needed", "security review"),
        ("Performance optimization", "systems optimization")
    ]
    
    for request, scenario in test_scenarios:
        print(f"Scenario: {scenario}")
        print(f"Request: '{request}'")
        
        agents = get_recommended_agents('.', request)
        print(f"Recommended agents: {', '.join(agents[:3])}")
        print()


def demo_smart_recommendations():
    """Demonstrate smart integration with decision tree"""
    print("🧠 SMART INTEGRATION DEMO")
    print("=" * 50)
    
    result = get_smart_agent_recommendations('.', 'create a new mobile app with real-time features')
    
    recommendation = result['agent_recommendation']
    guidance = result['integration_guidance']
    
    print(f"Risk Level: {recommendation.risk_level.upper()}")
    print(f"Complexity: {recommendation.estimated_complexity.upper()}")
    print(f"Orchestration Pattern: {recommendation.orchestration_pattern.replace('_', ' ').title()}")
    
    print("\n🎯 Tier 1: Primary Agents")
    for agent in recommendation.primary_agents[:4]:
        required = " (REQUIRED)" if agent.required else ""
        print(f"  • {agent.agent_name}: {agent.score:.0f}/100{required}")
        if agent.reasoning:
            print(f"    - {agent.reasoning[0]}")
    
    if recommendation.context_agents:
        print("\n🔧 Tier 2: Context-Triggered Agents")
        for agent in recommendation.context_agents[:3]:
            print(f"  • {agent.agent_name}: {agent.score:.0f}/100")
            if agent.reasoning:
                print(f"    - {agent.reasoning[0]}")
    
    print(f"\n🔄 Suggested Workflow:")
    for step in guidance['suggested_workflow']:
        print(f"  1. {step}")
    
    print()


def demo_convenience_functions():
    """Demonstrate convenience functions"""
    print("⚡ CONVENIENCE FUNCTIONS")
    print("=" * 50)
    
    # Quick project type detection
    project_type = detect_project_type('.')
    print(f"Quick project type detection: {project_type}")
    
    # Quick analysis with summary
    result = analyze_project_quick('.')
    if 'error' not in result:
        summary = result['summary']
        print(f"Primary language: {summary['primary_language']}")
        print(f"Complexity: {summary['complexity']}")
        print(f"Top recommended agent: {summary['top_agent']}")
    
    print()


def demo_performance():
    """Demonstrate performance characteristics"""
    print("⚡ PERFORMANCE CHARACTERISTICS")
    print("=" * 50)
    
    import time
    
    # Time analysis with cache miss
    start_time = time.time()
    analyzer = ProjectAnalyzer()
    context = analyzer.analyze_project('.', force_refresh=True)
    cache_miss_time = (time.time() - start_time) * 1000
    
    # Time analysis with cache hit
    start_time = time.time()
    context = analyzer.analyze_project('.')  # Should hit cache
    cache_hit_time = (time.time() - start_time) * 1000
    
    print(f"Cache miss analysis time: {cache_miss_time:.1f}ms")
    print(f"Cache hit analysis time: {cache_hit_time:.1f}ms")
    print(f"Performance improvement: {cache_miss_time/cache_hit_time:.1f}x faster with cache")
    
    print()


def main():
    """Run all demonstrations"""
    print("🚀 PROJECT CONTEXT ANALYSIS SYSTEM DEMO")
    print("=" * 60)
    print()
    
    demos = [
        demo_basic_analysis,
        demo_agent_recommendations,
        demo_smart_recommendations,
        demo_convenience_functions,
        demo_performance
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"Demo failed: {e}")
        
        # Add separator between demos
        print("-" * 60)
        print()
    
    print("✅ Demo completed successfully!")
    print("\nKey Integration Points for Claude Code:")
    print("1. Use get_recommended_agents() for simple agent lists")
    print("2. Use get_smart_agent_recommendations() for full analysis")
    print("3. Use detect_project_type() for quick project classification")
    print("4. All functions work with project paths and optional user requests")
    print("5. Results follow the 3-tier progressive disclosure system")


if __name__ == '__main__':
    main()