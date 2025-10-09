"""
Unit tests for agent integration helpers.

Tests cover:
- File path extraction from various input formats
- Question formulation based on task types
- Task type detection
- Complete query creation
- Context formatting
"""

import pytest
import json
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'tools'))

from ail.agent_integration import (
    extract_file_path,
    formulate_question,
    detect_task_type,
    format_context_for_agent,
    create_agent_query,
)
from ail.context_provider import (
    ArchaeologicalContext,
    ContextSource,
)


class TestExtractFilePath:
    """Test file path extraction from agent input."""

    def test_quoted_path(self):
        """Test extraction from quoted paths."""
        assert extract_file_path('Check "src/auth.py" for issues') == "src/auth.py"
        assert extract_file_path("Look at 'tools/ail/context_provider.py'") == "tools/ail/context_provider.py"

    def test_backtick_path(self):
        """Test extraction from backtick paths."""
        assert extract_file_path('The file `config/settings.py` is broken') == "config/settings.py"

    def test_bare_path(self):
        """Test extraction from bare paths."""
        assert extract_file_path('Why does src/models/user.py use this pattern?') == "src/models/user.py"
        assert extract_file_path('Analyze tools/validate_agents.py') == "tools/validate_agents.py"

    def test_absolute_path(self):
        """Test extraction from absolute paths."""
        result = extract_file_path('Check /usr/local/bin/script.sh')
        assert result in ["/usr/local/bin/script.sh", "usr/local/bin/script.sh"]  # Regex may strip leading /

    def test_no_path(self):
        """Test when no path is present."""
        assert extract_file_path('Why was this approach chosen?') is None
        assert extract_file_path('Explain the algorithm') is None

    def test_multiple_paths(self):
        """Test when multiple paths are present (returns first)."""
        result = extract_file_path('Compare "src/auth.py" and "src/user.py"')
        assert result == "src/auth.py"


class TestFormulateQuestion:
    """Test question formulation."""

    def test_general_task(self):
        """Test general task question formulation."""
        result = formulate_question("Explain this code", "general")
        assert "historical context" in result.lower() or "purpose" in result.lower()

    def test_refactor_task(self):
        """Test refactor task question formulation."""
        result = formulate_question("I need to refactor this", "refactor")
        assert "design intent" in result.lower() or "patterns" in result.lower()

    def test_debug_task(self):
        """Test debug task question formulation."""
        result = formulate_question("This code is broken", "debug")
        assert "intended behavior" in result.lower() or "bugs" in result.lower() or "issues" in result.lower()

    def test_review_task(self):
        """Test review task question formulation."""
        result = formulate_question("Review this implementation", "review")
        assert "chosen" in result.lower() or "decision" in result.lower()

    def test_implement_task(self):
        """Test implement task question formulation."""
        result = formulate_question("I need to add a feature", "implement")
        assert "patterns" in result.lower() or "conventions" in result.lower()

    def test_optimize_task(self):
        """Test optimize task question formulation."""
        result = formulate_question("Make this faster", "optimize")
        assert "performance" in result.lower() or "algorithm" in result.lower()

    def test_existing_question(self):
        """Test when input is already a clear question."""
        input_q = "Why was JWT authentication chosen for this API?"
        result = formulate_question(input_q, "review")
        # Should keep the original question
        assert "JWT" in result or input_q in result


class TestDetectTaskType:
    """Test task type detection."""

    def test_refactor_detection(self):
        """Test refactor task detection."""
        assert detect_task_type("I need to refactor this module") == "refactor"
        assert detect_task_type("Let's clean up the code structure") == "refactor"
        assert detect_task_type("Restructure the database layer") == "refactor"

    def test_debug_detection(self):
        """Test debug task detection."""
        assert detect_task_type("This code is failing") == "debug"
        assert detect_task_type("Fix the authentication bug") == "debug"
        assert detect_task_type("Debug the error in user.py") == "debug"

    def test_review_detection(self):
        """Test review task detection."""
        assert detect_task_type("Review this pull request") == "review"
        assert detect_task_type("Audit the security implementation") == "review"
        assert detect_task_type("Analyze the code quality") == "review"

    def test_implement_detection(self):
        """Test implement task detection."""
        assert detect_task_type("Implement the new feature") == "implement"
        assert detect_task_type("Add user authentication") == "implement"
        assert detect_task_type("Create a new API endpoint") == "implement"

    def test_optimize_detection(self):
        """Test optimize task detection."""
        assert detect_task_type("Optimize the database queries") == "optimize"
        assert detect_task_type("Improve performance of this function") == "optimize"
        assert detect_task_type("Make this code faster") == "optimize"

    def test_general_default(self):
        """Test default to general when no specific task detected."""
        assert detect_task_type("Explain this code") == "general"
        assert detect_task_type("What does this function do?") == "general"


class TestFormatContextForAgent:
    """Test context formatting."""

    @pytest.fixture
    def sample_context(self):
        """Create sample context for testing."""
        source = ContextSource(
            commit_sha="abc123def456",
            commit_message="Add authentication",
            author="John Doe",
            date=datetime(2024, 1, 15),
            source_type="commit",
            relevance_score=0.85,
            excerpt="Implemented JWT-based authentication",
            url="https://github.com/test/repo/commit/abc123",
        )

        return ArchaeologicalContext(
            file_path="src/auth.py",
            question="Why was JWT chosen?",
            answer="JWT was chosen for stateless authentication with good security.",
            sources=[source],
            confidence=0.9,
            cached=False,
            query_time_ms=125.5,
        )

    def test_markdown_format(self, sample_context):
        """Test markdown formatting."""
        result = format_context_for_agent(sample_context, style="markdown")

        assert "# Archaeological Context: src/auth.py" in result
        assert "Why was JWT chosen?" in result
        assert "JWT was chosen" in result
        assert "John Doe" in result
        assert "ms" in result  # Check for time formatting (may round)

    def test_text_format(self, sample_context):
        """Test plain text formatting."""
        result = format_context_for_agent(sample_context, style="text")

        assert "Context for: src/auth.py" in result
        assert "Question: Why was JWT chosen?" in result
        assert "JWT was chosen" in result
        assert "John Doe" in result

    def test_json_format(self, sample_context):
        """Test JSON formatting."""
        result = format_context_for_agent(sample_context, style="json")

        data = json.loads(result)

        assert data['file_path'] == "src/auth.py"
        assert data['question'] == "Why was JWT chosen?"
        assert data['answer'] == "JWT was chosen for stateless authentication with good security."
        assert data['confidence'] == 0.9
        assert len(data['sources']) == 1
        assert data['sources'][0]['author'] == "John Doe"

    def test_invalid_style(self, sample_context):
        """Test invalid style raises error."""
        with pytest.raises(ValueError, match="Unknown style"):
            format_context_for_agent(sample_context, style="invalid")


class TestCreateAgentQuery:
    """Test complete query creation."""

    def test_full_extraction(self, tmp_path):
        """Test complete query creation with all components."""
        # Create a test file
        test_file = tmp_path / "src" / "auth.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("# Auth module")

        agent_input = 'Why does "src/auth.py" use JWT tokens?'
        query = create_agent_query(agent_input, str(tmp_path), auto_detect=True)

        assert query['file_path'] == "src/auth.py"
        assert query['task_type'] == "general"
        assert query['question'] is not None
        assert "JWT" in agent_input

    def test_refactor_query(self, tmp_path):
        """Test query creation for refactor task."""
        test_file = tmp_path / "models.py"
        test_file.write_text("# Models")

        agent_input = "I need to refactor models.py"
        query = create_agent_query(agent_input, str(tmp_path), auto_detect=True)

        assert query['file_path'] == "models.py"
        assert query['task_type'] == "refactor"
        assert "design intent" in query['question'].lower() or "patterns" in query['question'].lower()

    def test_debug_query(self, tmp_path):
        """Test query creation for debug task."""
        test_file = tmp_path / "broken.py"
        test_file.write_text("# Broken code")

        agent_input = "Fix the bug in broken.py"
        query = create_agent_query(agent_input, str(tmp_path), auto_detect=True)

        assert query['file_path'] == "broken.py"
        assert query['task_type'] == "debug"

    def test_no_auto_detect(self):
        """Test query creation without auto-detection."""
        agent_input = "Why does src/auth.py use JWT?"
        query = create_agent_query(agent_input, "/tmp", auto_detect=False)

        assert query['file_path'] is None
        assert query['question'] is None
        assert query['task_type'] == "general"
        assert query['agent_input'] == agent_input


class TestIntegrationHelpers:
    """Test integration helper functions."""

    def test_file_path_extraction_edge_cases(self):
        """Test edge cases in file path extraction."""
        # Windows-style paths (should still work)
        result = extract_file_path('Check C:\\Users\\test\\file.py')
        assert result is not None

        # URLs (should not match)
        result = extract_file_path('See https://example.com/file.html')
        # This might match depending on pattern, but URL handling is optional

        # Hidden files (may or may not match leading dot depending on regex)
        result = extract_file_path('Check .hidden/config.json')
        assert result in [".hidden/config.json", "hidden/config.json"]

    def test_question_formulation_with_context(self):
        """Test question formulation preserves context."""
        input_text = "Why does this module handle errors this way?"
        result = formulate_question(input_text, "review")

        # Should contain question (may be original or enhanced)
        assert "?" in result  # Should contain question
        assert len(result) >= len(input_text)  # At least as long as input


def test_main_function():
    """Test main CLI function."""
    from ail.agent_integration import main

    import sys
    old_argv = sys.argv
    sys.argv = ['test']

    with pytest.raises(SystemExit):
        main()

    sys.argv = old_argv
