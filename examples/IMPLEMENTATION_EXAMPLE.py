"""
PROOF OF CONCEPT: AI-Enhanced Agent Selection System

⚠️  STATUS: Design Specification / Prototype - NOT PRODUCTION READY

This file demonstrates how machine learning could enhance agent selection
in future versions of the Claude Code Agent System. It explores using:
- Sentence embeddings for semantic similarity matching
- Performance metrics and user feedback for agent ranking
- Project context analysis for intelligent recommendations
- ML-based clustering and classification

IMPORTANT NOTES:
1. This is a DESIGN EXPLORATION, not a working implementation
2. Dependencies are NOT installed by default (numpy, scikit-learn, sentence-transformers)
3. Missing module: project_analyzer.py (referenced but not implemented)
4. This code is preserved as a reference for future development
5. See examples/README.md for full context

DO NOT USE IN PRODUCTION. For the current production agent selection
system, see docs/architecture.md for the keyword-based approach.

If you want to complete this implementation:
- Install ML dependencies: pip install numpy scikit-learn sentence-transformers
- Implement missing project_analyzer.py module
- Add comprehensive tests
- Submit PR when fully functional

Last Updated: 2025-10-06
Purpose: Design reference for future ML-based agent selection
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from collections import defaultdict
import sqlite3
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
import asyncio

@dataclass
class AgentCapability:
    """Represents an agent's capabilities and performance metrics."""
    agent_id: str
    description: str
    keywords: List[str]
    success_rate: float = 0.0
    avg_completion_time: float = 0.0
    user_satisfaction: float = 0.0
    embedding: Optional[np.ndarray] = None
    dynamic_capabilities: List[str] = field(default_factory=list)

@dataclass
class UserRequest:
    """Represents a user's request with context."""
    text: str
    project_context: Dict[str, Any]
    user_id: str
    timestamp: datetime
    urgency: str = "medium"  # low, medium, high, critical
    
@dataclass
class ProjectContext:
    """Rich project context for intelligent agent selection."""
    tech_stack: List[str]
    project_type: str  # web, mobile, ai, system, etc.
    complexity_score: float
    security_requirements: List[str]
    accessibility_needs: bool
    performance_critical: bool
    file_patterns: Dict[str, int]
    recent_changes: List[str]

class IntelligentAgentSelector:
    """
    AI-powered agent selection system that learns from user behavior
    and adapts recommendations over time.
    """
    
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.agents: Dict[str, AgentCapability] = {}
        self.user_profiles: Dict[str, Dict] = {}
        self.performance_history: List[Dict] = []
        self.success_predictor = RandomForestClassifier(n_estimators=100)
        self.is_trained = False
        
        # Initialize with existing agents
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize the system with existing Claude Code agents."""
        
        # Load agent definitions from the existing system
        agent_definitions = {
            "full-stack-architect": {
                "description": "Specializes in React, Next.js, TypeScript, Node.js, full-stack web applications, API design, and modern web development practices",
                "keywords": ["react", "nextjs", "typescript", "web app", "frontend", "backend", "api", "full-stack"],
                "domain": "web_development"
            },
            "ai-ml-engineer": {
                "description": "Expert in LLM integration, RAG systems, vector databases, model deployment, ML infrastructure, and AI-powered features",
                "keywords": ["ai", "ml", "llm", "rag", "embeddings", "vector", "openai", "anthropic", "machine learning"],
                "domain": "artificial_intelligence"
            },
            "mobile-developer": {
                "description": "Specializes in iOS, Android, React Native, Flutter, mobile UI/UX, app store deployment, and cross-platform development",
                "keywords": ["ios", "android", "mobile", "swift", "kotlin", "react native", "flutter"],
                "domain": "mobile_development"
            },
            "security-audit-specialist": {
                "description": "Expert in security auditing, vulnerability assessment, authentication, authorization, compliance, and secure coding practices",
                "keywords": ["security", "audit", "vulnerability", "auth", "compliance", "encryption"],
                "domain": "security"
            },
            "systems-engineer": {
                "description": "Specializes in Rust, C++, Go, performance optimization, concurrent programming, memory management, and system-level development",
                "keywords": ["rust", "cpp", "go", "performance", "optimization", "concurrent", "memory", "systems"],
                "domain": "systems_programming"
            },
            "qa-test-engineer": {
                "description": "Expert in testing strategies, test automation, quality assurance, test-driven development, and comprehensive testing frameworks",
                "keywords": ["test", "testing", "qa", "quality", "automation", "tdd", "coverage"],
                "domain": "quality_assurance"
            },
            "accessibility-expert": {
                "description": "Specializes in WCAG compliance, inclusive design, screen reader compatibility, accessibility auditing, and universal design",
                "keywords": ["accessibility", "wcag", "a11y", "inclusive", "screen reader", "disability"],
                "domain": "accessibility"
            },
            "devops-engineer": {
                "description": "Expert in CI/CD, Docker, Kubernetes, cloud deployment, infrastructure as code, monitoring, and DevOps practices",
                "keywords": ["devops", "cicd", "docker", "kubernetes", "aws", "cloud", "infrastructure", "deploy"],
                "domain": "infrastructure"
            }
        }
        
        # Create AgentCapability objects and generate embeddings
        for agent_id, definition in agent_definitions.items():
            text_for_embedding = f"{definition['description']} {' '.join(definition['keywords'])}"
            embedding = self.embedding_model.encode(text_for_embedding)
            
            self.agents[agent_id] = AgentCapability(
                agent_id=agent_id,
                description=definition["description"],
                keywords=definition["keywords"],
                embedding=embedding,
                success_rate=0.85,  # Initialize with reasonable defaults
                avg_completion_time=300.0,  # 5 minutes default
                user_satisfaction=4.2  # Out of 5
            )
    
    async def select_optimal_agents(
        self, 
        request: UserRequest, 
        max_agents: int = 3
    ) -> List[Tuple[str, float, str]]:
        """
        Select optimal agents using AI/ML techniques.
        
        Returns:
            List of (agent_id, confidence_score, reasoning) tuples
        """
        
        # Generate request embedding
        request_embedding = self.embedding_model.encode(request.text)
        
        # Analyze project context
        context_insights = self._analyze_project_context(request.project_context)
        
        # Get user preferences
        user_preferences = self._get_user_preferences(request.user_id)
        
        # Compute agent scores
        agent_scores = {}
        for agent_id, agent in self.agents.items():
            
            # Semantic similarity score
            semantic_score = cosine_similarity(
                request_embedding.reshape(1, -1), 
                agent.embedding.reshape(1, -1)
            )[0][0]
            
            # Context relevance score
            context_score = self._compute_context_relevance(
                agent, context_insights
            )
            
            # User preference score
            preference_score = self._compute_preference_score(
                agent_id, user_preferences
            )
            
            # Historical success score
            success_score = self._compute_historical_success(
                agent_id, request, context_insights
            )
            
            # Performance score (speed, quality, reliability)
            performance_score = self._compute_performance_score(agent)
            
            # Combined score with weights
            combined_score = (
                0.25 * semantic_score +
                0.20 * context_score +
                0.20 * preference_score +
                0.20 * success_score +
                0.15 * performance_score
            )
            
            agent_scores[agent_id] = combined_score
        
        # Select top agents
        top_agents = sorted(
            agent_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:max_agents]
        
        # Generate reasoning for selections
        results = []
        for agent_id, score in top_agents:
            reasoning = self._generate_selection_reasoning(
                agent_id, request, context_insights, score
            )
            results.append((agent_id, score, reasoning))
        
        # Predict success and suggest fallbacks if needed
        results_with_fallbacks = await self._add_fallback_strategies(
            results, request, context_insights
        )
        
        return results_with_fallbacks
    
    def _analyze_project_context(self, project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project context to extract insights for agent selection."""
        
        insights = {
            "tech_stack_complexity": 0.0,
            "security_needs": False,
            "performance_critical": False,
            "accessibility_required": False,
            "ai_ml_involved": False,
            "mobile_platform": False,
            "dominant_language": None,
            "project_phase": "development",  # discovery, development, testing, deployment
            "risk_level": "medium"  # low, medium, high, critical
        }
        
        # Analyze tech stack
        tech_stack = project_context.get("tech_stack", [])
        if tech_stack:
            insights["tech_stack_complexity"] = len(set(tech_stack)) / 10.0  # Normalized
            
            # Detect AI/ML involvement
            ai_keywords = ["tensorflow", "pytorch", "openai", "anthropic", "langchain", "vector", "embedding"]
            insights["ai_ml_involved"] = any(tech.lower() in ai_keywords for tech in tech_stack)
            
            # Detect mobile platforms
            mobile_keywords = ["ios", "android", "swift", "kotlin", "react-native", "flutter"]
            insights["mobile_platform"] = any(tech.lower() in mobile_keywords for tech in tech_stack)
        
        # Analyze file patterns
        file_patterns = project_context.get("file_patterns", {})
        if file_patterns:
            # Security indicators
            security_files = file_patterns.get("auth", 0) + file_patterns.get("security", 0)
            insights["security_needs"] = security_files > 0
            
            # Performance indicators
            perf_files = file_patterns.get("performance", 0) + file_patterns.get("optimization", 0)
            insights["performance_critical"] = perf_files > 2
            
            # Accessibility indicators
            a11y_files = file_patterns.get("accessibility", 0) + file_patterns.get("a11y", 0)
            insights["accessibility_required"] = a11y_files > 0
        
        # Determine dominant programming language
        languages = project_context.get("languages", {})
        if languages:
            insights["dominant_language"] = max(languages.items(), key=lambda x: x[1])[0]
        
        # Assess risk level based on various factors
        risk_factors = 0
        if insights["security_needs"]: risk_factors += 2
        if insights["performance_critical"]: risk_factors += 1
        if project_context.get("user_data", False): risk_factors += 2
        if project_context.get("production_system", False): risk_factors += 3
        
        if risk_factors >= 5:
            insights["risk_level"] = "critical"
        elif risk_factors >= 3:
            insights["risk_level"] = "high"
        elif risk_factors >= 1:
            insights["risk_level"] = "medium"
        else:
            insights["risk_level"] = "low"
        
        return insights
    
    def _compute_context_relevance(self, agent: AgentCapability, context: Dict[str, Any]) -> float:
        """Compute how relevant an agent is given the project context."""
        
        relevance_score = 0.0
        
        # Domain-specific relevance
        if agent.agent_id == "ai-ml-engineer" and context["ai_ml_involved"]:
            relevance_score += 0.8
            
        if agent.agent_id == "mobile-developer" and context["mobile_platform"]:
            relevance_score += 0.8
            
        if agent.agent_id == "security-audit-specialist" and context["security_needs"]:
            relevance_score += 0.7
            
        if agent.agent_id == "systems-engineer" and context["performance_critical"]:
            relevance_score += 0.7
            
        if agent.agent_id == "accessibility-expert" and context["accessibility_required"]:
            relevance_score += 0.9
        
        # Risk-based relevance
        if context["risk_level"] in ["high", "critical"]:
            if agent.agent_id in ["security-audit-specialist", "qa-test-engineer"]:
                relevance_score += 0.5
        
        # Tech stack alignment
        dominant_lang = context.get("dominant_language", "").lower()
        if dominant_lang:
            if dominant_lang in ["rust", "cpp", "c++"] and agent.agent_id == "systems-engineer":
                relevance_score += 0.6
            elif dominant_lang in ["javascript", "typescript"] and agent.agent_id == "full-stack-architect":
                relevance_score += 0.6
            elif dominant_lang in ["swift", "kotlin"] and agent.agent_id == "mobile-developer":
                relevance_score += 0.6
        
        return min(relevance_score, 1.0)  # Cap at 1.0
    
    def _get_user_preferences(self, user_id: str) -> Dict[str, float]:
        """Get user preferences for different agents."""
        
        if user_id not in self.user_profiles:
            # Initialize with neutral preferences
            self.user_profiles[user_id] = {
                "agent_preferences": defaultdict(float),
                "quality_preference": 0.5,  # 0 = speed, 1 = quality
                "preferred_workflow": "single_agent",  # single_agent, multi_agent, orchestrated
                "risk_tolerance": 0.5  # 0 = conservative, 1 = aggressive
            }
        
        return self.user_profiles[user_id]
    
    def _compute_preference_score(self, agent_id: str, user_preferences: Dict[str, Any]) -> float:
        """Compute preference score based on user history."""
        
        agent_preferences = user_preferences.get("agent_preferences", {})
        base_preference = agent_preferences.get(agent_id, 0.0)
        
        # Adjust based on user's quality vs speed preference
        quality_preference = user_preferences.get("quality_preference", 0.5)
        agent = self.agents[agent_id]
        
        # Agents known for quality vs speed
        quality_agents = ["security-audit-specialist", "accessibility-expert", "qa-test-engineer"]
        speed_agents = ["full-stack-architect", "mobile-developer"]
        
        if agent_id in quality_agents:
            quality_bonus = quality_preference * 0.3
        elif agent_id in speed_agents:
            quality_bonus = (1 - quality_preference) * 0.3
        else:
            quality_bonus = 0.0
        
        return min(base_preference + quality_bonus, 1.0)
    
    def _compute_historical_success(
        self, 
        agent_id: str, 
        request: UserRequest, 
        context: Dict[str, Any]
    ) -> float:
        """Compute historical success rate for similar requests."""
        
        # This would normally query a database of historical performance
        # For this example, we'll simulate based on agent characteristics
        
        agent = self.agents[agent_id]
        base_success = agent.success_rate
        
        # Adjust based on request complexity and context
        complexity_penalty = context.get("tech_stack_complexity", 0.0) * 0.1
        risk_penalty = {"low": 0.0, "medium": 0.05, "high": 0.1, "critical": 0.15}[context["risk_level"]]
        
        adjusted_success = base_success - complexity_penalty - risk_penalty
        return max(adjusted_success, 0.0)
    
    def _compute_performance_score(self, agent: AgentCapability) -> float:
        """Compute performance score based on speed, satisfaction, and reliability."""
        
        # Normalize metrics
        speed_score = max(0, (600 - agent.avg_completion_time) / 600)  # 10 minutes max
        satisfaction_score = agent.user_satisfaction / 5.0  # Out of 5
        reliability_score = agent.success_rate
        
        # Weighted average
        performance_score = (
            0.3 * speed_score +
            0.4 * satisfaction_score +
            0.3 * reliability_score
        )
        
        return performance_score
    
    def _generate_selection_reasoning(
        self, 
        agent_id: str, 
        request: UserRequest, 
        context: Dict[str, Any], 
        score: float
    ) -> str:
        """Generate human-readable reasoning for agent selection."""
        
        agent = self.agents[agent_id]
        reasons = []
        
        # Semantic match
        if score > 0.7:
            reasons.append(f"Strong semantic match with your request")
        
        # Context-specific reasons
        if context["ai_ml_involved"] and agent_id == "ai-ml-engineer":
            reasons.append("Your project involves AI/ML technologies")
        
        if context["security_needs"] and agent_id == "security-audit-specialist":
            reasons.append("Security requirements detected in your project")
        
        if context["mobile_platform"] and agent_id == "mobile-developer":
            reasons.append("Mobile platform development identified")
        
        if context["performance_critical"] and agent_id == "systems-engineer":
            reasons.append("Performance optimization needs detected")
        
        # Performance reasons
        if agent.success_rate > 0.9:
            reasons.append(f"High success rate ({agent.success_rate:.1%}) for similar tasks")
        
        if agent.user_satisfaction > 4.0:
            reasons.append(f"Excellent user satisfaction ({agent.user_satisfaction:.1f}/5.0)")
        
        if not reasons:
            reasons.append("Good overall match for your requirements")
        
        return ". ".join(reasons) + "."
    
    async def _add_fallback_strategies(
        self,
        agent_selections: List[Tuple[str, float, str]],
        request: UserRequest,
        context: Dict[str, Any]
    ) -> List[Tuple[str, float, str]]:
        """Add fallback strategies for low-confidence selections."""
        
        enhanced_selections = []
        
        for agent_id, score, reasoning in agent_selections:
            
            # Predict success probability
            success_prob = await self._predict_success_probability(
                agent_id, request, context
            )
            
            if success_prob < 0.6:  # Low confidence
                fallback_agent = self._suggest_fallback_agent(agent_id, context)
                if fallback_agent:
                    reasoning += f" Fallback option: {fallback_agent} (success prediction: {success_prob:.1%})"
            
            enhanced_selections.append((agent_id, score, reasoning))
        
        return enhanced_selections
    
    async def _predict_success_probability(
        self,
        agent_id: str,
        request: UserRequest,
        context: Dict[str, Any]
    ) -> float:
        """Predict probability of successful task completion."""
        
        # This would normally use a trained ML model
        # For this example, we'll use a simple heuristic
        
        agent = self.agents[agent_id]
        
        # Base success rate
        base_prob = agent.success_rate
        
        # Adjust for complexity
        complexity_factor = 1 - (context.get("tech_stack_complexity", 0.0) * 0.3)
        
        # Adjust for risk
        risk_factor = {"low": 1.0, "medium": 0.9, "high": 0.8, "critical": 0.7}[context["risk_level"]]
        
        # Adjust for urgency
        urgency_factor = {"low": 1.0, "medium": 0.95, "high": 0.85, "critical": 0.75}[request.urgency]
        
        predicted_prob = base_prob * complexity_factor * risk_factor * urgency_factor
        
        return max(min(predicted_prob, 1.0), 0.0)
    
    def _suggest_fallback_agent(self, primary_agent_id: str, context: Dict[str, Any]) -> Optional[str]:
        """Suggest fallback agent if primary agent has low success probability."""
        
        fallback_mapping = {
            "full-stack-architect": "code-architect",  # More general architectural guidance
            "ai-ml-engineer": "systems-engineer",      # For performance-critical AI
            "mobile-developer": "full-stack-architect", # For web-based mobile solutions
            "systems-engineer": "code-architect",      # For code optimization
            "security-audit-specialist": "qa-test-engineer"  # For testing security
        }
        
        return fallback_mapping.get(primary_agent_id)
    
    def collect_feedback(
        self,
        session_id: str,
        agent_id: str,
        user_id: str,
        feedback_data: Dict[str, Any]
    ):
        """Collect feedback to improve future recommendations."""
        
        feedback_entry = {
            "session_id": session_id,
            "agent_id": agent_id,
            "user_id": user_id,
            "timestamp": datetime.now(),
            "satisfaction_rating": feedback_data.get("satisfaction", 3.0),
            "task_completed": feedback_data.get("completed", True),
            "completion_time": feedback_data.get("duration", 0),
            "would_recommend": feedback_data.get("recommend", True),
            "quality_rating": feedback_data.get("quality", 3.0),
            "agent_was_appropriate": feedback_data.get("appropriate", True)
        }
        
        self.performance_history.append(feedback_entry)
        
        # Update agent performance metrics
        self._update_agent_performance(agent_id, feedback_entry)
        
        # Update user preferences
        self._update_user_preferences(user_id, agent_id, feedback_entry)
    
    def _update_agent_performance(self, agent_id: str, feedback: Dict[str, Any]):
        """Update agent performance metrics based on feedback."""
        
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            
            # Update with exponential moving average
            alpha = 0.1  # Learning rate
            
            if feedback["task_completed"]:
                agent.success_rate = (1 - alpha) * agent.success_rate + alpha * 1.0
            else:
                agent.success_rate = (1 - alpha) * agent.success_rate + alpha * 0.0
            
            agent.user_satisfaction = (
                (1 - alpha) * agent.user_satisfaction + 
                alpha * feedback["satisfaction_rating"]
            )
            
            if feedback["completion_time"] > 0:
                agent.avg_completion_time = (
                    (1 - alpha) * agent.avg_completion_time + 
                    alpha * feedback["completion_time"]
                )
    
    def _update_user_preferences(self, user_id: str, agent_id: str, feedback: Dict[str, Any]):
        """Update user preferences based on feedback."""
        
        if user_id not in self.user_profiles:
            self._get_user_preferences(user_id)  # Initialize
        
        user_prefs = self.user_profiles[user_id]
        alpha = 0.2  # Learning rate
        
        # Update agent preference
        current_pref = user_prefs["agent_preferences"][agent_id]
        satisfaction_normalized = (feedback["satisfaction_rating"] - 3.0) / 2.0  # -1 to 1
        
        user_prefs["agent_preferences"][agent_id] = (
            (1 - alpha) * current_pref + alpha * satisfaction_normalized
        )
        
        # Update quality vs speed preference
        if feedback["completion_time"] > 0 and feedback["quality_rating"] > 0:
            # If they rated quality high despite longer time, they prefer quality
            time_vs_quality_signal = feedback["quality_rating"] / max(feedback["completion_time"] / 300, 1)
            if time_vs_quality_signal > 1.0:  # Quality was worth the time
                user_prefs["quality_preference"] = (
                    (1 - alpha) * user_prefs["quality_preference"] + alpha * 0.8
                )
    
    async def continuous_learning(self):
        """Continuously learn and adapt from collected data."""
        
        if len(self.performance_history) > 100:  # Minimum data for learning
            
            # Re-train success prediction model
            await self._retrain_success_predictor()
            
            # Update agent capability profiles
            self._update_capability_profiles()
            
            # Optimize agent selection weights
            self._optimize_selection_weights()
    
    async def _retrain_success_predictor(self):
        """Retrain the success prediction model with new data."""
        
        # This would implement actual ML model retraining
        # For this example, we'll just update some internal parameters
        
        recent_feedback = self.performance_history[-100:]  # Last 100 sessions
        
        # Calculate overall success rates by agent
        agent_success = defaultdict(list)
        for feedback in recent_feedback:
            agent_success[feedback["agent_id"]].append(
                1.0 if feedback["task_completed"] else 0.0
            )
        
        # Update agent success rates
        for agent_id, successes in agent_success.items():
            if agent_id in self.agents:
                self.agents[agent_id].success_rate = np.mean(successes)
    
    def get_agent_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics about agent performance and usage."""
        
        if not self.performance_history:
            return {"message": "No performance data available yet"}
        
        analytics = {
            "total_sessions": len(self.performance_history),
            "agent_performance": {},
            "user_satisfaction_trends": {},
            "recommendation_accuracy": 0.0,
            "top_performing_agents": [],
            "improvement_opportunities": []
        }
        
        # Agent performance analysis
        for agent_id, agent in self.agents.items():
            agent_sessions = [
                f for f in self.performance_history if f["agent_id"] == agent_id
            ]
            
            if agent_sessions:
                analytics["agent_performance"][agent_id] = {
                    "sessions": len(agent_sessions),
                    "success_rate": agent.success_rate,
                    "avg_satisfaction": agent.user_satisfaction,
                    "avg_completion_time": agent.avg_completion_time,
                    "recommendation_acceptance": np.mean([
                        f["agent_was_appropriate"] for f in agent_sessions
                    ])
                }
        
        # Overall recommendation accuracy
        if self.performance_history:
            analytics["recommendation_accuracy"] = np.mean([
                f["agent_was_appropriate"] for f in self.performance_history
            ])
        
        # Top performing agents
        agent_scores = []
        for agent_id, perf in analytics["agent_performance"].items():
            score = (perf["success_rate"] * 0.4 + 
                    perf["avg_satisfaction"] / 5.0 * 0.4 + 
                    perf["recommendation_acceptance"] * 0.2)
            agent_scores.append((agent_id, score))
        
        analytics["top_performing_agents"] = sorted(
            agent_scores, key=lambda x: x[1], reverse=True
        )[:5]
        
        return analytics


# Example usage demonstration
async def demonstrate_ai_enhanced_agent_selection():
    """Demonstrate the AI-enhanced agent selection system."""
    
    print("🤖 AI-Enhanced Agent Selection System Demo")
    print("=" * 50)
    
    # Initialize the system
    selector = IntelligentAgentSelector()
    
    # Example user request 1: Web development with AI features
    request1 = UserRequest(
        text="I want to build a web application that can analyze user documents using AI and provide intelligent recommendations",
        project_context={
            "tech_stack": ["react", "nextjs", "typescript", "openai", "vector-database"],
            "languages": {"typescript": 0.6, "python": 0.4},
            "file_patterns": {"auth": 2, "ai": 5, "frontend": 10},
            "production_system": True,
            "user_data": True
        },
        user_id="user123",
        timestamp=datetime.now(),
        urgency="high"
    )
    
    print(f"\n📝 Request: {request1.text}")
    print(f"🔧 Tech Stack: {request1.project_context['tech_stack']}")
    
    # Get agent recommendations
    recommendations = await selector.select_optimal_agents(request1, max_agents=3)
    
    print(f"\n🎯 Recommended Agents:")
    for i, (agent_id, score, reasoning) in enumerate(recommendations, 1):
        print(f"{i}. {agent_id} (confidence: {score:.1%})")
        print(f"   Reasoning: {reasoning}")
    
    # Simulate user feedback
    print(f"\n📊 Collecting Feedback...")
    selector.collect_feedback(
        session_id="session1",
        agent_id=recommendations[0][0],
        user_id="user123",
        feedback_data={
            "satisfaction": 4.5,
            "completed": True,
            "duration": 450,  # 7.5 minutes
            "recommend": True,
            "quality": 4.0,
            "appropriate": True
        }
    )
    
    # Example user request 2: Mobile development
    request2 = UserRequest(
        text="Create a cross-platform mobile app for iOS and Android with offline sync capabilities",
        project_context={
            "tech_stack": ["react-native", "redux", "sqlite", "firebase"],
            "languages": {"javascript": 0.8, "java": 0.1, "swift": 0.1},
            "file_patterns": {"mobile": 8, "database": 3, "sync": 4},
            "production_system": True,
            "user_data": False
        },
        user_id="user456",
        timestamp=datetime.now(),
        urgency="medium"
    )
    
    print(f"\n📝 Request 2: {request2.text}")
    print(f"🔧 Tech Stack: {request2.project_context['tech_stack']}")
    
    recommendations2 = await selector.select_optimal_agents(request2, max_agents=3)
    
    print(f"\n🎯 Recommended Agents:")
    for i, (agent_id, score, reasoning) in enumerate(recommendations2, 1):
        print(f"{i}. {agent_id} (confidence: {score:.1%})")
        print(f"   Reasoning: {reasoning}")
    
    # Show analytics
    print(f"\n📈 System Analytics:")
    analytics = selector.get_agent_analytics()
    print(f"Total sessions: {analytics['total_sessions']}")
    print(f"Recommendation accuracy: {analytics['recommendation_accuracy']:.1%}")
    
    if analytics['top_performing_agents']:
        print(f"\nTop performing agents:")
        for agent_id, score in analytics['top_performing_agents'][:3]:
            print(f"  • {agent_id}: {score:.1%}")


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(demonstrate_ai_enhanced_agent_selection())