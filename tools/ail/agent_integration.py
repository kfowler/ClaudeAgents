"""
Agent Integration Helpers - Sprint 1

This module provides helper functions for AI agents to easily request and
utilize archaeological context from the ArchaeologyContextProvider.

Features:
- Automatic file path detection from agent input
- Question formulation based on agent task type
- Context formatting for agent consumption
- Common query patterns for different agent types
"""

import re
from pathlib import Path
from typing import Optional, List, Dict, Any

from .context_provider import (
    ArchaeologyContextProvider,
    ArchaeologicalContext,
)


def extract_file_path(agent_input: str, repo_path: Optional[str] = None) -> Optional[str]:
    """
    Extract file path from agent input text.

    This function uses pattern matching to identify file paths in agent queries.

    Args:
        agent_input: Agent's input text (e.g., "Why does auth.py use JWT?")
        repo_path: Repository root path for validation (optional)

    Returns:
        Extracted file path or None if not found

    Examples:
        >>> extract_file_path("Why does src/auth.py use JWT?")
        'src/auth.py'
        >>> extract_file_path("Explain the logic in tools/ail/context_provider.py")
        'tools/ail/context_provider.py'
    """
    # Common file path patterns
    patterns = [
        # Quoted paths: "path/to/file.py"
        r'"([^"]+\.\w+)"',
        r"'([^']+\.\w+)'",
        # Backtick paths: `path/to/file.py`
        r'`([^`]+\.\w+)`',
        # Word-like paths: path/to/file.py
        r'\b((?:[\w.-]+/)*[\w.-]+\.\w+)\b',
        # Absolute paths: /absolute/path/to/file.py
        r'(/(?:[\w.-]+/)+[\w.-]+\.\w+)',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, agent_input)
        if matches:
            # Return first match
            candidate = matches[0]

            # Validate if repo_path provided
            if repo_path:
                full_path = Path(repo_path) / candidate
                if full_path.exists():
                    return candidate

            # Return candidate even if validation failed (might be relative)
            return candidate

    return None


def formulate_question(agent_input: str, task_type: str = "general") -> str:
    """
    Formulate an archaeological question from agent input and task type.

    Args:
        agent_input: Agent's input text
        task_type: Type of task (general, refactor, debug, review, implement)

    Returns:
        Formulated question optimized for archaeological search

    Examples:
        >>> formulate_question("Why does this use JWT?", "review")
        'Why was JWT chosen for authentication? What were the decision factors?'
        >>> formulate_question("How should I refactor this?", "refactor")
        'What was the original design intent? What patterns were established?'
    """
    # Task-specific question templates
    templates = {
        'general': [
            "What is the historical context and purpose of this code?",
            "Why was this approach chosen?",
        ],
        'refactor': [
            "What was the original design intent?",
            "What patterns were established in the codebase?",
            "What architectural decisions influenced this design?",
        ],
        'debug': [
            "What was the intended behavior of this code?",
            "What issues or bugs were previously fixed here?",
            "What edge cases were considered?",
        ],
        'review': [
            "Why was this implementation approach chosen?",
            "What were the decision factors?",
            "What alternatives were considered?",
        ],
        'implement': [
            "What patterns and conventions are used in similar code?",
            "What architectural principles guide this area?",
            "What dependencies and integrations exist?",
        ],
        'optimize': [
            "What performance considerations were discussed?",
            "Why was this algorithm/data structure chosen?",
            "What optimizations were previously attempted?",
        ],
    }

    # Get base question from input
    base_question = agent_input.strip()

    # Remove file path references for cleaner question
    cleaned_question = re.sub(r'\b(?:[\w.-]+/)*[\w.-]+\.\w+\b', '', base_question)
    cleaned_question = cleaned_question.strip()

    # If input is already a clear question, use it
    if '?' in cleaned_question and len(cleaned_question) > 20:
        return cleaned_question

    # Otherwise, use task-specific template
    template_questions = templates.get(task_type, templates['general'])

    # Combine with any extracted intent from input
    if cleaned_question:
        return f"{cleaned_question} {template_questions[0]}"
    else:
        return " ".join(template_questions)


def get_file_context(
    provider: ArchaeologyContextProvider,
    file_path: str,
    question: str,
    sync: bool = True,
) -> ArchaeologicalContext:
    """
    Get archaeological context for a specific file.

    High-level helper function for agents.

    Args:
        provider: Initialized ArchaeologyContextProvider
        file_path: Path to file (relative to repo root)
        question: Natural language question
        sync: Use synchronous API (default: True)

    Returns:
        ArchaeologicalContext with answer and sources

    Example:
        >>> provider = ArchaeologyContextProvider(repo_path="/path/to/repo")
        >>> context = get_file_context(
        ...     provider,
        ...     "tools/ail/context_provider.py",
        ...     "Why was LRU caching implemented?"
        ... )
        >>> print(context.answer)
    """
    if sync:
        return provider.get_context_sync(file_path, question)
    else:
        import asyncio
        return asyncio.run(provider.get_context(file_path, question))


def get_architectural_context(
    provider: ArchaeologyContextProvider,
    subsystem: str,
    question: Optional[str] = None,
) -> ArchaeologicalContext:
    """
    Get architectural context for a subsystem or module.

    Args:
        provider: Initialized ArchaeologyContextProvider
        subsystem: Subsystem or module name (e.g., "authentication", "tools/ail")
        question: Optional specific question (auto-generated if not provided)

    Returns:
        ArchaeologicalContext with architectural information

    Example:
        >>> context = get_architectural_context(
        ...     provider,
        ...     "tools/ail",
        ...     "What is the design philosophy of AIL?"
        ... )
    """
    # Auto-generate question if not provided
    if not question:
        question = (
            f"What is the architectural design and purpose of the {subsystem} subsystem? "
            f"What were the key design decisions and patterns?"
        )

    # Use subsystem as "file path" for context
    return provider.get_context_sync(subsystem, question)


def format_context_for_agent(context: ArchaeologicalContext, style: str = "markdown") -> str:
    """
    Format archaeological context for agent consumption.

    Args:
        context: ArchaeologicalContext to format
        style: Output style (markdown, text, json)

    Returns:
        Formatted context string

    Example:
        >>> formatted = format_context_for_agent(context, style="markdown")
        >>> print(formatted)
    """
    if style == "markdown":
        return context.to_markdown()

    elif style == "text":
        lines = [
            f"Context for: {context.file_path}",
            f"Question: {context.question}",
            "",
            f"Answer (Confidence: {context.confidence:.0%}):",
            context.answer,
            "",
        ]

        if context.sources:
            lines.append("Sources:")
            for i, source in enumerate(context.sources, 1):
                lines.append(
                    f"{i}. {source.commit_message} by {source.author} "
                    f"({source.date.date()}) - {source.source_type}"
                )

        return "\n".join(lines)

    elif style == "json":
        import json
        return json.dumps({
            'file_path': context.file_path,
            'question': context.question,
            'answer': context.answer,
            'confidence': context.confidence,
            'sources': [
                {
                    'commit_sha': s.commit_sha,
                    'author': s.author,
                    'date': s.date.isoformat(),
                    'source_type': s.source_type,
                    'relevance_score': s.relevance_score,
                }
                for s in context.sources
            ],
            'cached': context.cached,
            'query_time_ms': context.query_time_ms,
        }, indent=2)

    else:
        raise ValueError(f"Unknown style: {style}")


def detect_task_type(agent_input: str) -> str:
    """
    Detect task type from agent input for question formulation.

    Args:
        agent_input: Agent's input text

    Returns:
        Task type (general, refactor, debug, review, implement, optimize)

    Example:
        >>> detect_task_type("I need to refactor this module")
        'refactor'
        >>> detect_task_type("Why is this code failing?")
        'debug'
    """
    # Lowercase for matching
    text_lower = agent_input.lower()

    # Task keywords
    task_patterns = {
        'refactor': [
            'refactor', 'restructure', 'reorganize', 'clean up', 'improve structure'
        ],
        'debug': [
            'debug', 'fix', 'error', 'bug', 'issue', 'failing', 'broken', 'not working'
        ],
        'review': [
            'review', 'audit', 'analyze', 'assess', 'evaluate', 'check'
        ],
        'implement': [
            'implement', 'add', 'create', 'build', 'develop', 'write', 'new feature'
        ],
        'optimize': [
            'optimize', 'performance', 'speed up', 'improve efficiency', 'faster'
        ],
    }

    # Match patterns
    for task_type, keywords in task_patterns.items():
        for keyword in keywords:
            if keyword in text_lower:
                return task_type

    # Default to general
    return 'general'


def create_agent_query(
    agent_input: str,
    repo_path: str,
    auto_detect: bool = True,
) -> Dict[str, Any]:
    """
    Create a complete query configuration from agent input.

    This is the highest-level helper that automatically extracts file paths,
    formulates questions, and detects task types.

    Args:
        agent_input: Agent's input text
        repo_path: Repository root path
        auto_detect: Automatically detect file paths and task types

    Returns:
        Dictionary with query configuration

    Example:
        >>> query = create_agent_query(
        ...     "Why does src/auth.py use JWT tokens?",
        ...     "/path/to/repo"
        ... )
        >>> print(query['file_path'])
        'src/auth.py'
        >>> print(query['question'])
        'Why was JWT chosen for authentication? What were the decision factors?'
    """
    result = {
        'agent_input': agent_input,
        'file_path': None,
        'question': None,
        'task_type': 'general',
    }

    if not auto_detect:
        return result

    # Extract file path
    file_path = extract_file_path(agent_input, repo_path)
    if file_path:
        result['file_path'] = file_path

    # Detect task type
    task_type = detect_task_type(agent_input)
    result['task_type'] = task_type

    # Formulate question
    question = formulate_question(agent_input, task_type)
    result['question'] = question

    return result


def get_context_from_input(
    provider: ArchaeologyContextProvider,
    agent_input: str,
    repo_path: Optional[str] = None,
) -> Optional[ArchaeologicalContext]:
    """
    One-line helper: Get context directly from agent input.

    This function handles all the complexity of extracting file paths,
    formulating questions, and querying the provider.

    Args:
        provider: Initialized ArchaeologyContextProvider
        agent_input: Agent's natural language input
        repo_path: Repository path for file validation (optional)

    Returns:
        ArchaeologicalContext or None if file path couldn't be extracted

    Example:
        >>> provider = ArchaeologyContextProvider(repo_path=".")
        >>> context = get_context_from_input(
        ...     provider,
        ...     "Why does tools/ail/context_provider.py implement LRU caching?"
        ... )
        >>> if context:
        ...     print(context.answer)
    """
    # Use provider's repo path if not specified
    if repo_path is None:
        repo_path = str(provider.repo_path)

    # Create query
    query = create_agent_query(agent_input, repo_path, auto_detect=True)

    # Check if we extracted a file path
    if not query['file_path']:
        return None

    # Get context
    return get_file_context(
        provider,
        query['file_path'],
        query['question'],
        sync=True,
    )


def main():
    """CLI entry point for testing integration helpers."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python agent_integration.py <repo_path> <agent_input>")
        print("\nExample:")
        print("  python agent_integration.py . 'Why does tools/ail/context_provider.py use LRU caching?'")
        sys.exit(1)

    repo_path = sys.argv[1]
    agent_input = " ".join(sys.argv[2:])

    print(f"Agent Input: {agent_input}")
    print("=" * 80)

    # Test extraction and formulation
    file_path = extract_file_path(agent_input, repo_path)
    print(f"\nExtracted File Path: {file_path}")

    task_type = detect_task_type(agent_input)
    print(f"Detected Task Type: {task_type}")

    question = formulate_question(agent_input, task_type)
    print(f"Formulated Question: {question}")

    # Test complete query creation
    print("\n" + "=" * 80)
    query = create_agent_query(agent_input, repo_path)
    print("Complete Query Configuration:")
    for key, value in query.items():
        print(f"  {key}: {value}")

    # Test full integration
    if file_path:
        print("\n" + "=" * 80)
        print("Testing full integration...")

        from .context_provider import ArchaeologyContextProvider

        provider = ArchaeologyContextProvider(repo_path=repo_path)
        context = get_context_from_input(provider, agent_input, repo_path)

        if context:
            print("\n" + context.to_markdown())
        else:
            print("No context retrieved")


if __name__ == '__main__':
    main()
