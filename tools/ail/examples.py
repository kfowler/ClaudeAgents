#!/usr/bin/env python3
"""
AIL Usage Examples

This script demonstrates various usage patterns for the
Archaeology Intelligence Layer (AIL).
"""

import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ail import ArchaeologyContextProvider, get_context_from_input
from ail.agent_integration import (
    extract_file_path,
    detect_task_type,
    formulate_question,
    create_agent_query,
    format_context_for_agent,
)


def example_1_basic_usage():
    """Example 1: Basic context retrieval."""
    print("=" * 80)
    print("Example 1: Basic Context Retrieval")
    print("=" * 80)

    # Initialize provider for current repository
    provider = ArchaeologyContextProvider(
        repo_path="../../",  # ClaudeAgents root
        cache_size=100,
    )

    # Get context about this very file
    context = provider.get_context_sync(
        file_path="tools/ail/context_provider.py",
        question="Why was LRU caching implemented?"
    )

    print(f"\nFile: {context.file_path}")
    print(f"Question: {context.question}")
    print(f"Confidence: {context.confidence:.1%}")
    print(f"Query Time: {context.query_time_ms:.0f}ms")
    print(f"Cached: {context.cached}")
    print(f"\nAnswer:\n{context.answer}\n")

    if context.sources:
        print(f"Sources: {len(context.sources)}")
        for i, source in enumerate(context.sources[:3], 1):
            print(f"  {i}. {source.commit_message[:60]}... by {source.author}")


def example_2_natural_language_input():
    """Example 2: Natural language input processing."""
    print("\n" + "=" * 80)
    print("Example 2: Natural Language Input Processing")
    print("=" * 80)

    provider = ArchaeologyContextProvider(repo_path="../../")

    # Agent's natural language input
    agent_input = 'Why does "tools/ail/context_provider.py" implement LRU caching?'

    print(f"\nAgent Input: {agent_input}")

    # Automatically extract file path and get context
    context = get_context_from_input(provider, agent_input, repo_path="../../")

    if context:
        print(f"\nExtracted File: {context.file_path}")
        print(f"Confidence: {context.confidence:.1%}")
        print(f"Answer: {context.answer[:200]}...")
    else:
        print("Could not extract file path from input")


def example_3_task_type_detection():
    """Example 3: Task type detection and question formulation."""
    print("\n" + "=" * 80)
    print("Example 3: Task Type Detection")
    print("=" * 80)

    test_inputs = [
        "I need to refactor the authentication module",
        "Fix the bug in database.py",
        "Review this pull request for security issues",
        "Implement a new caching layer",
        "Optimize the query performance",
        "Why does this code work this way?",
    ]

    for agent_input in test_inputs:
        task_type = detect_task_type(agent_input)
        question = formulate_question(agent_input, task_type)

        print(f"\nInput: {agent_input}")
        print(f"  Task Type: {task_type}")
        print(f"  Question: {question[:100]}...")


def example_4_query_creation():
    """Example 4: Complete query creation."""
    print("\n" + "=" * 80)
    print("Example 4: Complete Query Creation")
    print("=" * 80)

    agent_input = 'I need to refactor "tools/ail/context_provider.py"'

    query = create_agent_query(agent_input, repo_path="../../", auto_detect=True)

    print(f"\nAgent Input: {agent_input}")
    print(f"\nExtracted Query Configuration:")
    print(f"  File Path: {query['file_path']}")
    print(f"  Task Type: {query['task_type']}")
    print(f"  Question: {query['question'][:100]}...")


def example_5_caching_performance():
    """Example 5: Cache performance demonstration."""
    print("\n" + "=" * 80)
    print("Example 5: Cache Performance")
    print("=" * 80)

    provider = ArchaeologyContextProvider(repo_path="../../", cache_size=10)

    # First query - cache miss
    print("\nFirst query (cache miss):")
    context1 = provider.get_context_sync(
        "tools/ail/context_provider.py",
        "Why was this implemented?"
    )
    print(f"  Query Time: {context1.query_time_ms:.0f}ms")
    print(f"  Cached: {context1.cached}")

    # Second query - cache hit
    print("\nSecond query (cache hit):")
    context2 = provider.get_context_sync(
        "tools/ail/context_provider.py",
        "Why was this implemented?"
    )
    print(f"  Query Time: {context2.query_time_ms:.0f}ms")
    print(f"  Cached: {context2.cached}")
    print(f"  Speedup: {context1.query_time_ms / max(context2.query_time_ms, 0.1):.1f}x")

    # Cache statistics
    stats = provider.get_cache_stats()
    print(f"\nCache Statistics:")
    print(f"  Total Queries: {stats.total_queries}")
    print(f"  Cache Hits: {stats.hits}")
    print(f"  Cache Misses: {stats.misses}")
    print(f"  Hit Rate: {stats.hit_rate:.1%}")
    print(f"  Cache Size: {stats.cache_size}/{stats.max_cache_size}")


def example_6_formatting():
    """Example 6: Context formatting for agents."""
    print("\n" + "=" * 80)
    print("Example 6: Context Formatting")
    print("=" * 80)

    provider = ArchaeologyContextProvider(repo_path="../../")

    context = provider.get_context_sync(
        "tools/ail/context_provider.py",
        "What is the purpose of this module?"
    )

    print("\n--- Markdown Format ---")
    print(format_context_for_agent(context, style="markdown")[:400] + "...")

    print("\n--- Text Format ---")
    print(format_context_for_agent(context, style="text")[:400] + "...")

    print("\n--- JSON Format ---")
    json_output = format_context_for_agent(context, style="json")
    print(json_output[:400] + "...")


def example_7_error_handling():
    """Example 7: Error handling and graceful degradation."""
    print("\n" + "=" * 80)
    print("Example 7: Error Handling")
    print("=" * 80)

    provider = ArchaeologyContextProvider(repo_path="../../")

    # Simulate error by forcing init error
    provider._init_error = "Simulated CCA failure"

    context = provider.get_context_sync(
        "nonexistent.py",
        "Why does this exist?"
    )

    print(f"\nError Handling:")
    print(f"  Confidence: {context.confidence}")
    print(f"  Answer: {context.answer}")
    print(f"\nProvider gracefully degraded and returned error context.")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "AIL Usage Examples" + " " * 40 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    examples = [
        ("Basic Usage", example_1_basic_usage),
        ("Natural Language Input", example_2_natural_language_input),
        ("Task Type Detection", example_3_task_type_detection),
        ("Query Creation", example_4_query_creation),
        ("Cache Performance", example_5_caching_performance),
        ("Context Formatting", example_6_formatting),
        ("Error Handling", example_7_error_handling),
    ]

    for i, (name, func) in enumerate(examples, 1):
        try:
            func()
        except Exception as e:
            print(f"\n❌ Example {i} ({name}) failed: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("Examples complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
