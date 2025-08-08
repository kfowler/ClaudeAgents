"""
Comprehensive Testing Framework for Semantic Agent Selection System

This module provides extensive testing capabilities including unit tests,
integration tests, performance tests, and example scenarios.
"""

import os
import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import numpy as np
import tempfile
import pytest

# Test database imports
import asyncpg
from contextlib import asynccontextmanager

# Local imports
from . import (
    SemanticAgentSelector,
    RequestAnalyzer,
    VectorSearchManager,
    MultiAgentOrchestrator,
    SuccessPredictor,
    AgentEmbeddingManager,
    SelectionStrategy,
    SearchBackend,
    IntentCategory,
    ComplexityLevel,
    RiskLevel,
    create_development_config,
    initialize_system
)


logger = logging.getLogger(__name__)


@dataclass
class TestScenario:
    """Test scenario definition."""
    name: str
    request: str
    expected_agents: List[str]
    expected_intent: IntentCategory
    expected_complexity: ComplexityLevel
    expected_risk: RiskLevel
    project_context: Optional[Dict[str, Any]] = None
    min_confidence: float = 0.5
    description: str = ""


@dataclass
class TestResult:
    """Test execution result."""
    scenario_name: str
    passed: bool
    actual_agents: List[str]
    expected_agents: List[str]
    confidence_score: float
    processing_time: float
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


class TestScenarios:
    """Collection of test scenarios for different use cases."""
    
    @staticmethod
    def get_web_development_scenarios() -> List[TestScenario]:
        """Web development test scenarios."""
        return [
            TestScenario(
                name="React App Development",
                request="I want to build a React application with user authentication and a modern UI",
                expected_agents=["full-stack-architect", "security-audit-specialist"],
                expected_intent=IntentCategory.NEW_PROJECT,
                expected_complexity=ComplexityLevel.MODERATE,
                expected_risk=RiskLevel.MEDIUM,
                description="Standard React web application"
            ),
            TestScenario(
                name="Next.js E-commerce Platform",
                request="Create a Next.js e-commerce platform with payment processing, user management, and admin dashboard",
                expected_agents=["full-stack-architect", "security-audit-specialist", "qa-test-engineer"],
                expected_intent=IntentCategory.NEW_PROJECT,
                expected_complexity=ComplexityLevel.COMPLEX,
                expected_risk=RiskLevel.HIGH,
                description="Complex e-commerce system"
            ),
            TestScenario(
                name="Website Performance Optimization",
                request="My website is loading slowly and I need to optimize Core Web Vitals",
                expected_agents=["full-stack-architect", "systems-engineer"],
                expected_intent=IntentCategory.OPTIMIZATION,
                expected_complexity=ComplexityLevel.MODERATE,
                expected_risk=RiskLevel.MEDIUM,
                description="Performance optimization task"
            )
        ]
    
    @staticmethod
    def get_mobile_development_scenarios() -> List[TestScenario]:
        """Mobile development test scenarios."""
        return [
            TestScenario(
                name="iOS App Development",
                request="I need to develop an iOS app using Swift with Core Data and push notifications",
                expected_agents=["mobile-developer", "security-audit-specialist"],
                expected_intent=IntentCategory.NEW_PROJECT,
                expected_complexity=ComplexityLevel.MODERATE,
                expected_risk=RiskLevel.MEDIUM,
                description="Native iOS application"
            ),
            TestScenario(
                name="React Native Cross-Platform App",
                request="Build a cross-platform mobile app with React Native that works on both iOS and Android",
                expected_agents=["mobile-developer", "full-stack-architect"],
                expected_intent=IntentCategory.NEW_PROJECT,
                expected_complexity=ComplexityLevel.COMPLEX,
                expected_risk=RiskLevel.MEDIUM,
                description="Cross-platform mobile solution"
            ),
            TestScenario(
                name="Mobile App Bug Fix",
                request="My Android app is crashing on certain devices when users try to upload photos",
                expected_agents=["mobile-developer", "qa-test-engineer"],
                expected_intent=IntentCategory.BUG_FIX,
                expected_complexity=ComplexityLevel.MODERATE,
                expected_risk=RiskLevel.MEDIUM,
                description="Mobile bug investigation"
            )
        ]
    
    @staticmethod
    def get_ai_ml_scenarios() -> List[TestScenario]:
        """AI/ML development test scenarios."""
        return [
            TestScenario(
                name="ChatGPT Integration",
                request="I want to add ChatGPT integration to my application for customer support chatbot",
                expected_agents=["ai-ml-engineer", "full-stack-architect"],
                expected_intent=IntentCategory.FEATURE_ENHANCEMENT,
                expected_complexity=ComplexityLevel.MODERATE,
                expected_risk=RiskLevel.MEDIUM,
                description="LLM integration for chatbot"
            ),
            TestScenario(
                name="RAG System Implementation",
                request="Build a RAG system with vector database for semantic search over our documentation",
                expected_agents=["ai-ml-engineer", "data-engineer"],
                expected_intent=IntentCategory.NEW_PROJECT,
                expected_complexity=ComplexityLevel.COMPLEX,
                expected_risk=RiskLevel.MEDIUM,
                description="Advanced RAG architecture"
            ),
            TestScenario(
                name="ML Model Training Pipeline",
                request="Set up MLOps pipeline for training and deploying recommendation models with A/B testing",
                expected_agents=["ai-ml-engineer", "devops-engineer", "data-engineer"],
                expected_intent=IntentCategory.NEW_PROJECT,
                expected_complexity=ComplexityLevel.VERY_COMPLEX,
                expected_risk=RiskLevel.HIGH,
                description="Complete MLOps infrastructure"
            )
        ]
    
    @staticmethod
    def get_security_scenarios() -> List[TestScenario]:
        """Security-focused test scenarios."""
        return [
            TestScenario(
                name="Security Audit Request",
                request="Perform a comprehensive security audit of our web application before production deployment",
                expected_agents=["security-audit-specialist", "qa-test-engineer"],
                expected_intent=IntentCategory.ANALYSIS,
                expected_complexity=ComplexityLevel.COMPLEX,
                expected_risk=RiskLevel.CRITICAL,
                description="Full security assessment"
            ),
            TestScenario(
                name="Financial App Security",
                request="We're building a fintech app with payment processing and need to ensure PCI compliance",
                expected_agents=["security-audit-specialist", "full-stack-architect", "qa-test-engineer"],
                expected_intent=IntentCategory.NEW_PROJECT,
                expected_complexity=ComplexityLevel.VERY_COMPLEX,
                expected_risk=RiskLevel.CRITICAL,
                description="High-security financial application"
            )
        ]
    
    @staticmethod
    def get_creative_scenarios() -> List[TestScenario]:
        """Creative work test scenarios."""
        return [
            TestScenario(
                name="Logo Design Request",
                request="I need a modern logo design for my startup with brand guidelines",
                expected_agents=["artist"],
                expected_intent=IntentCategory.CREATIVE,
                expected_complexity=ComplexityLevel.SIMPLE,
                expected_risk=RiskLevel.LOW,
                description="Visual design work"
            ),
            TestScenario(
                name="Video Production",
                request="Create a product demo video with animation and professional editing",
                expected_agents=["ava-the-director"],
                expected_intent=IntentCategory.CREATIVE,
                expected_complexity=ComplexityLevel.MODERATE,
                expected_risk=RiskLevel.LOW,
                description="Multimedia content creation"
            )
        ]
    
    @classmethod
    def get_all_scenarios(cls) -> List[TestScenario]:
        """Get all test scenarios."""
        all_scenarios = []
        all_scenarios.extend(cls.get_web_development_scenarios())
        all_scenarios.extend(cls.get_mobile_development_scenarios())
        all_scenarios.extend(cls.get_ai_ml_scenarios())
        all_scenarios.extend(cls.get_security_scenarios())
        all_scenarios.extend(cls.get_creative_scenarios())
        return all_scenarios


class MockDatabase:
    """Mock database for testing without real PostgreSQL."""
    
    def __init__(self):
        self.agent_embeddings = {}
        self.request_analysis = []
        self.semantic_matches = []
        self.agent_combinations = {}
        
    async def add_agent_embedding(self, agent_name: str, embedding: np.ndarray, metadata: dict):
        """Add agent embedding to mock database."""
        self.agent_embeddings[agent_name] = {
            'embedding': embedding,
            'metadata': metadata,
            'agent_name': agent_name
        }
    
    async def get_agent_embeddings(self) -> Dict[str, np.ndarray]:
        """Get all agent embeddings."""
        return {name: data['embedding'] for name, data in self.agent_embeddings.items()}
    
    async def add_request_analysis(self, request: str, analysis: dict):
        """Add request analysis."""
        self.request_analysis.append({
            'request_text': request,
            'analysis': analysis,
            'id': len(self.request_analysis) + 1
        })


class TestDatabase:
    """Test database manager for integration tests."""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.pool = None
        
    async def initialize(self):
        """Initialize test database."""
        self.pool = await asyncpg.create_pool(
            self.db_url,
            min_size=1,
            max_size=3,
            command_timeout=30
        )
        
        # Run schema setup
        await self._setup_schema()
    
    async def close(self):
        """Close database connections."""
        if self.pool:
            await self.pool.close()
    
    async def _setup_schema(self):
        """Set up test database schema."""
        schema_file = Path(__file__).parent / "schema.sql"
        
        if schema_file.exists():
            async with self.pool.acquire() as conn:
                with open(schema_file, 'r') as f:
                    schema_sql = f.read()
                try:
                    await conn.execute(schema_sql)
                except Exception as e:
                    logger.warning(f"Schema setup warning (may be expected): {e}")
    
    async def cleanup(self):
        """Clean up test data."""
        if not self.pool:
            return
            
        async with self.pool.acquire() as conn:
            # Clean up test data
            tables = [
                'semantic_matches', 'request_analysis', 'agent_embeddings',
                'agent_combinations', 'selection_feedback', 'agent_invocations'
            ]
            
            for table in tables:
                try:
                    await conn.execute(f"TRUNCATE TABLE {table} CASCADE")
                except Exception as e:
                    logger.debug(f"Cleanup warning for {table}: {e}")


class SemanticAgentSelectionTester:
    """Main test runner for the semantic agent selection system."""
    
    def __init__(self, 
                 test_db_url: Optional[str] = None,
                 use_mock_db: bool = True):
        """Initialize tester."""
        self.test_db_url = test_db_url
        self.use_mock_db = use_mock_db
        self.selector = None
        self.test_db = None
        self.mock_db = None
        
    async def setup(self):
        """Set up test environment."""
        if self.use_mock_db:
            self.mock_db = MockDatabase()
            await self._setup_mock_data()
        else:
            if not self.test_db_url:
                raise ValueError("Test database URL required for integration tests")
            
            self.test_db = TestDatabase(self.test_db_url)
            await self.test_db.initialize()
        
        # Create test configuration
        if self.test_db_url:
            config = create_development_config(self.test_db_url)
        else:
            # Use minimal config for mock tests
            config = {
                "db_url": "mock://test",
                "redis_url": None,
                "faiss_index_path": None,
                "model_path": None,
                "embedding_model": "all-MiniLM-L6-v2",
                "vector_search_backend": SearchBackend.PGVECTOR,
                "enable_caching": False,
                "enable_analytics": False,
                "max_agents": 5
            }
        
        # Initialize selector with mocking if needed
        if self.use_mock_db:
            self.selector = await self._create_mock_selector(config)
        else:
            self.selector = SemanticAgentSelector(
                db_url=config["db_url"],
                redis_url=config.get("redis_url"),
                faiss_index_path=config.get("faiss_index_path"),
                model_path=config.get("model_path")
            )
            await self.selector.initialize()
    
    async def teardown(self):
        """Clean up test environment."""
        if self.selector:
            await self.selector.close()
        
        if self.test_db:
            await self.test_db.cleanup()
            await self.test_db.close()
    
    async def _setup_mock_data(self):
        """Set up mock data for testing."""
        # Create mock embeddings for common agents
        agents = [
            "full-stack-architect", "mobile-developer", "ai-ml-engineer",
            "security-audit-specialist", "qa-test-engineer", "devops-engineer",
            "data-engineer", "systems-engineer", "artist", "writer"
        ]
        
        for agent_name in agents:
            # Generate random but consistent embedding
            np.random.seed(hash(agent_name) % 2**32)
            embedding = np.random.normal(0, 1, 384)
            embedding = embedding / np.linalg.norm(embedding)  # Normalize
            
            metadata = {
                'tier': 1 if agent_name in ['full-stack-architect', 'mobile-developer'] else 2,
                'technologies': self._get_mock_technologies(agent_name),
                'domains': self._get_mock_domains(agent_name)
            }
            
            await self.mock_db.add_agent_embedding(agent_name, embedding, metadata)
    
    def _get_mock_technologies(self, agent_name: str) -> List[str]:
        """Get mock technologies for agent."""
        tech_mapping = {
            'full-stack-architect': ['React', 'Node.js', 'TypeScript', 'PostgreSQL'],
            'mobile-developer': ['Swift', 'Kotlin', 'React Native', 'iOS', 'Android'],
            'ai-ml-engineer': ['Python', 'PyTorch', 'OpenAI', 'LangChain', 'Vector DB'],
            'security-audit-specialist': ['Security', 'OAuth', 'HTTPS', 'Penetration Testing'],
            'qa-test-engineer': ['Testing', 'Cypress', 'Jest', 'Quality Assurance'],
            'devops-engineer': ['Docker', 'Kubernetes', 'AWS', 'CI/CD'],
            'data-engineer': ['Python', 'SQL', 'Apache Spark', 'Data Pipeline'],
            'systems-engineer': ['Rust', 'Go', 'C++', 'Performance'],
            'artist': ['Design', 'Graphics', 'UI/UX'],
            'writer': ['Writing', 'Documentation', 'Content']
        }
        return tech_mapping.get(agent_name, [])
    
    def _get_mock_domains(self, agent_name: str) -> List[str]:
        """Get mock domains for agent."""
        domain_mapping = {
            'full-stack-architect': ['web_development'],
            'mobile-developer': ['mobile_development'],
            'ai-ml-engineer': ['ai_ml'],
            'security-audit-specialist': ['security'],
            'qa-test-engineer': ['testing'],
            'devops-engineer': ['devops'],
            'data-engineer': ['data_engineering'],
            'systems-engineer': ['systems'],
            'artist': ['creative'],
            'writer': ['creative']
        }
        return domain_mapping.get(agent_name, [])
    
    async def _create_mock_selector(self, config: dict):
        """Create selector with mocked components."""
        # This would involve extensive mocking - simplified for example
        # In practice, you'd mock the database connections and vector operations
        
        with patch('semantic_agent_selection.vector_search.asyncpg.create_pool'):
            with patch('semantic_agent_selection.request_analyzer.SentenceTransformer') as mock_transformer:
                # Mock the sentence transformer
                mock_model = MagicMock()
                mock_model.encode.return_value = np.random.normal(0, 1, 384)
                mock_transformer.return_value = mock_model
                
                selector = SemanticAgentSelector(
                    db_url=config["db_url"],
                    redis_url=config.get("redis_url"),
                    faiss_index_path=config.get("faiss_index_path"),
                    model_path=config.get("model_path")
                )
                
                # Mock initialization
                selector.request_analyzer.embedder = mock_model
                selector.vector_search.pg_search.db_pool = AsyncMock()
                
                return selector
    
    async def run_scenario_tests(self, scenarios: List[TestScenario]) -> List[TestResult]:
        """Run test scenarios and return results."""
        results = []
        
        for scenario in scenarios:
            try:
                start_time = time.time()
                
                # Run agent selection
                selection_result = await self.selector.select_agents(
                    request=scenario.request,
                    strategy=SelectionStrategy.ADAPTIVE,
                    max_agents=5
                )
                
                processing_time = time.time() - start_time
                
                # Extract actual agents
                actual_agents = selection_result.get_all_agent_names()
                
                # Check if expected agents are present
                expected_set = set(scenario.expected_agents)
                actual_set = set(actual_agents)
                
                # Calculate match score
                if expected_set:
                    match_score = len(expected_set & actual_set) / len(expected_set)
                    passed = match_score >= 0.5  # At least 50% of expected agents
                else:
                    passed = len(actual_agents) > 0
                    match_score = 1.0 if passed else 0.0
                
                # Check confidence threshold
                confidence_ok = selection_result.primary_recommendation.confidence_score >= scenario.min_confidence
                
                result = TestResult(
                    scenario_name=scenario.name,
                    passed=passed and confidence_ok,
                    actual_agents=list(actual_agents),
                    expected_agents=scenario.expected_agents,
                    confidence_score=selection_result.primary_recommendation.confidence_score,
                    processing_time=processing_time,
                    details={
                        'match_score': match_score,
                        'selection_strategy': selection_result.selection_strategy.value,
                        'confidence_level': selection_result.confidence_level,
                        'explanation': selection_result.explanation
                    }
                )
                
            except Exception as e:
                result = TestResult(
                    scenario_name=scenario.name,
                    passed=False,
                    actual_agents=[],
                    expected_agents=scenario.expected_agents,
                    confidence_score=0.0,
                    processing_time=0.0,
                    error=str(e)
                )
            
            results.append(result)
        
        return results
    
    async def run_performance_tests(self, num_requests: int = 100) -> Dict[str, Any]:
        """Run performance tests."""
        test_requests = [
            "Build a React application with authentication",
            "Create an iOS app with Core Data",
            "Implement AI chatbot with OpenAI",
            "Perform security audit of web application",
            "Set up CI/CD pipeline with Docker",
            "Design a logo for my startup",
            "Optimize database query performance",
            "Build REST API with Node.js",
            "Create mobile app for both iOS and Android",
            "Implement machine learning recommendation system"
        ]
        
        start_time = time.time()
        total_processing_time = 0.0
        successful_requests = 0
        
        for i in range(num_requests):
            request = test_requests[i % len(test_requests)]
            
            try:
                request_start = time.time()
                result = await self.selector.select_agents(request, max_agents=3)
                request_time = time.time() - request_start
                
                total_processing_time += request_time
                
                if result and result.primary_recommendation.all_agents:
                    successful_requests += 1
                    
            except Exception as e:
                logger.error(f"Performance test request {i} failed: {e}")
        
        total_time = time.time() - start_time
        
        return {
            'total_requests': num_requests,
            'successful_requests': successful_requests,
            'success_rate': successful_requests / num_requests,
            'total_wall_time': total_time,
            'total_processing_time': total_processing_time,
            'average_request_time': total_processing_time / num_requests,
            'requests_per_second': num_requests / total_time,
            'processing_requests_per_second': num_requests / total_processing_time
        }
    
    def generate_test_report(self, 
                           scenario_results: List[TestResult],
                           performance_results: Optional[Dict[str, Any]] = None) -> str:
        """Generate comprehensive test report."""
        report = []
        
        report.append("# Semantic Agent Selection System Test Report")
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Scenario test results
        report.append("## Scenario Test Results")
        report.append("")
        
        passed_tests = sum(1 for r in scenario_results if r.passed)
        total_tests = len(scenario_results)
        
        report.append(f"**Overall Results: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)**")
        report.append("")
        
        # Detailed results
        for result in scenario_results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            report.append(f"### {result.scenario_name} {status}")
            
            if result.error:
                report.append(f"**Error:** {result.error}")
            else:
                report.append(f"**Expected Agents:** {', '.join(result.expected_agents)}")
                report.append(f"**Actual Agents:** {', '.join(result.actual_agents)}")
                report.append(f"**Confidence:** {result.confidence_score:.3f}")
                report.append(f"**Processing Time:** {result.processing_time:.3f}s")
                
                if 'explanation' in result.details:
                    report.append(f"**Explanation:** {result.details['explanation']}")
            
            report.append("")
        
        # Performance results
        if performance_results:
            report.append("## Performance Test Results")
            report.append("")
            
            perf = performance_results
            report.append(f"**Total Requests:** {perf['total_requests']}")
            report.append(f"**Success Rate:** {perf['success_rate']:.1%}")
            report.append(f"**Average Request Time:** {perf['average_request_time']:.3f}s")
            report.append(f"**Requests per Second:** {perf['requests_per_second']:.1f}")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("")
        
        failed_tests = [r for r in scenario_results if not r.passed]
        if failed_tests:
            report.append("### Failed Tests Analysis")
            
            # Analyze failure patterns
            error_patterns = {}
            for test in failed_tests:
                if test.error:
                    error_type = type(test.error).__name__ if hasattr(test.error, '__name__') else "Unknown"
                    error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
            
            if error_patterns:
                report.append("**Error Pattern Analysis:**")
                for error_type, count in error_patterns.items():
                    report.append(f"- {error_type}: {count} occurrences")
        
        if performance_results and performance_results['average_request_time'] > 1.0:
            report.append("### Performance Optimization Needed")
            report.append("- Consider enabling caching")
            report.append("- Optimize vector search indexing")
            report.append("- Review model inference performance")
        
        return "\n".join(report)


# PyTest integration
class TestSemanticAgentSelection:
    """PyTest test class for semantic agent selection."""
    
    @pytest.fixture(scope="class")
    async def tester(self):
        """Create test environment."""
        tester = SemanticAgentSelectionTester(use_mock_db=True)
        await tester.setup()
        yield tester
        await tester.teardown()
    
    @pytest.mark.asyncio
    async def test_web_development_scenarios(self, tester):
        """Test web development scenarios."""
        scenarios = TestScenarios.get_web_development_scenarios()
        results = await tester.run_scenario_tests(scenarios)
        
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        
        assert passed > 0, "No web development scenarios passed"
        assert passed / total >= 0.7, f"Only {passed}/{total} web scenarios passed"
    
    @pytest.mark.asyncio
    async def test_mobile_development_scenarios(self, tester):
        """Test mobile development scenarios."""
        scenarios = TestScenarios.get_mobile_development_scenarios()
        results = await tester.run_scenario_tests(scenarios)
        
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        
        assert passed > 0, "No mobile development scenarios passed"
        assert passed / total >= 0.7, f"Only {passed}/{total} mobile scenarios passed"
    
    @pytest.mark.asyncio
    async def test_ai_ml_scenarios(self, tester):
        """Test AI/ML scenarios."""
        scenarios = TestScenarios.get_ai_ml_scenarios()
        results = await tester.run_scenario_tests(scenarios)
        
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        
        assert passed > 0, "No AI/ML scenarios passed"
        assert passed / total >= 0.7, f"Only {passed}/{total} AI/ML scenarios passed"
    
    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, tester):
        """Test performance benchmarks."""
        results = await tester.run_performance_tests(num_requests=50)
        
        assert results['success_rate'] >= 0.9, f"Success rate too low: {results['success_rate']:.1%}"
        assert results['average_request_time'] <= 2.0, f"Average request time too high: {results['average_request_time']:.2f}s"
        assert results['requests_per_second'] >= 1.0, f"Throughput too low: {results['requests_per_second']:.1f} req/s"


# CLI interface for running tests
async def main():
    """Main CLI interface for test framework."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Semantic Agent Selection Test Framework")
    parser.add_argument("--db-url", help="Test database URL")
    parser.add_argument("--scenario", choices=['web', 'mobile', 'ai', 'security', 'creative', 'all'], 
                       default='all', help="Test scenario category")
    parser.add_argument("--performance", action='store_true', help="Run performance tests")
    parser.add_argument("--num-requests", type=int, default=100, help="Number of performance test requests")
    parser.add_argument("--output", help="Output file for test report")
    parser.add_argument("--mock", action='store_true', help="Use mock database")
    parser.add_argument("--verbose", action='store_true', help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Initialize tester
    use_mock = args.mock or not args.db_url
    tester = SemanticAgentSelectionTester(args.db_url, use_mock_db=use_mock)
    
    try:
        await tester.setup()
        print("✓ Test environment initialized")
        
        # Run scenario tests
        if args.scenario == 'all':
            scenarios = TestScenarios.get_all_scenarios()
        elif args.scenario == 'web':
            scenarios = TestScenarios.get_web_development_scenarios()
        elif args.scenario == 'mobile':
            scenarios = TestScenarios.get_mobile_development_scenarios()
        elif args.scenario == 'ai':
            scenarios = TestScenarios.get_ai_ml_scenarios()
        elif args.scenario == 'security':
            scenarios = TestScenarios.get_security_scenarios()
        else:
            scenarios = TestScenarios.get_creative_scenarios()
        
        print(f"Running {len(scenarios)} scenario tests...")
        scenario_results = await tester.run_scenario_tests(scenarios)
        
        passed = sum(1 for r in scenario_results if r.passed)
        print(f"✓ Scenario tests completed: {passed}/{len(scenarios)} passed")
        
        # Run performance tests
        performance_results = None
        if args.performance:
            print(f"Running performance tests with {args.num_requests} requests...")
            performance_results = await tester.run_performance_tests(args.num_requests)
            print(f"✓ Performance tests completed: {performance_results['success_rate']:.1%} success rate, "
                  f"{performance_results['average_request_time']:.3f}s avg time")
        
        # Generate report
        report = tester.generate_test_report(scenario_results, performance_results)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"✓ Test report saved to {args.output}")
        else:
            print("\n" + report)
        
        # Exit with error code if tests failed
        if passed < len(scenarios):
            exit(1)
    
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        exit(1)
    
    finally:
        await tester.teardown()


if __name__ == "__main__":
    asyncio.run(main())