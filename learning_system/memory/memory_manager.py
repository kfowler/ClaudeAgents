"""
Cross-Session Memory Manager

Manages persistent memory, context, and decision tracking across agent sessions.
Provides sophisticated memory retrieval, context management, and learning from
historical interactions.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import json
import uuid
from enum import Enum

from ..knowledge_graph.graph_manager import GraphManager
from ..knowledge_graph.schema import (
    Project, Agent, Decision, Pattern, Context, Outcome,
    NodeType, RelationshipType
)


logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Types of memory stored in the system"""
    CONVERSATION = "conversation"
    DECISION = "decision"
    PATTERN_USAGE = "pattern_usage"
    CONTEXT = "context"
    OUTCOME = "outcome"
    PREFERENCE = "preference"
    INTERACTION = "interaction"


class ContextScope(Enum):
    """Scope of context information"""
    SESSION = "session"
    PROJECT = "project"
    TEAM = "team"
    GLOBAL = "global"


@dataclass
class MemoryEntry:
    """Individual memory entry"""
    id: str
    memory_type: MemoryType
    scope: ContextScope
    content: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime]
    relevance_score: float
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class SessionContext:
    """Context for a specific agent session"""
    session_id: str
    project_id: Optional[str]
    agent_type: str
    user_id: Optional[str]
    team_id: Optional[str]
    started_at: datetime
    goals: List[str]
    constraints: List[str]
    preferences: Dict[str, Any]
    current_context: Dict[str, Any]
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())


class MemoryManager:
    """
    Manages cross-session memory and context for AI agents
    """
    
    def __init__(self, graph_manager: GraphManager):
        """
        Initialize memory manager
        
        Args:
            graph_manager: Knowledge graph manager instance
        """
        self.graph = graph_manager
        self.active_sessions: Dict[str, SessionContext] = {}
        self.memory_cache: Dict[str, MemoryEntry] = {}
        self.context_embeddings: Dict[str, List[float]] = {}
    
    # Session Management
    
    def start_session(
        self, 
        agent_type: str,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
        team_id: Optional[str] = None,
        goals: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None
    ) -> str:
        """
        Start a new agent session with context
        
        Args:
            agent_type: Type of agent
            project_id: Optional project identifier
            user_id: Optional user identifier
            team_id: Optional team identifier
            goals: Session goals
            constraints: Session constraints
            
        Returns:
            Session ID
        """
        session_context = SessionContext(
            session_id=str(uuid.uuid4()),
            project_id=project_id,
            agent_type=agent_type,
            user_id=user_id,
            team_id=team_id,
            started_at=datetime.utcnow(),
            goals=goals or [],
            constraints=constraints or [],
            preferences=self._load_preferences(user_id, team_id, project_id),
            current_context={}
        )
        
        self.active_sessions[session_context.session_id] = session_context
        
        # Load relevant memory into session context
        self._load_session_memory(session_context)
        
        logger.info(f"Started session {session_context.session_id} for agent {agent_type}")
        return session_context.session_id
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """
        End a session and persist learned context
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session summary
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        # Create session summary
        summary = self._create_session_summary(session)
        
        # Persist session memory
        self._persist_session_memory(session, summary)
        
        # Clean up
        del self.active_sessions[session_id]
        
        logger.info(f"Ended session {session_id}")
        return summary
    
    def get_session_context(self, session_id: str) -> Optional[SessionContext]:
        """Get current session context"""
        return self.active_sessions.get(session_id)
    
    def update_session_context(
        self, 
        session_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update session context
        
        Args:
            session_id: Session identifier
            updates: Context updates
            
        Returns:
            True if successful
        """
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        session.current_context.update(updates)
        return True
    
    # Memory Storage and Retrieval
    
    def store_memory(
        self,
        memory_type: MemoryType,
        scope: ContextScope,
        content: Dict[str, Any],
        session_id: Optional[str] = None,
        expires_in_hours: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Store a memory entry
        
        Args:
            memory_type: Type of memory
            scope: Scope of memory
            content: Memory content
            session_id: Optional session ID
            expires_in_hours: Optional expiration time
            tags: Optional tags for categorization
            
        Returns:
            Memory ID
        """
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        memory_entry = MemoryEntry(
            id=str(uuid.uuid4()),
            memory_type=memory_type,
            scope=scope,
            content=content,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            relevance_score=1.0,
            tags=tags or []
        )
        
        # Add session context if available
        if session_id and session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            memory_entry.content['session_context'] = {
                'project_id': session.project_id,
                'agent_type': session.agent_type,
                'user_id': session.user_id,
                'team_id': session.team_id
            }
        
        self.memory_cache[memory_entry.id] = memory_entry
        
        # Persist to knowledge graph based on memory type
        self._persist_memory_to_graph(memory_entry)
        
        logger.debug(f"Stored memory {memory_entry.id} of type {memory_type}")
        return memory_entry.id
    
    def retrieve_memory(
        self,
        memory_types: Optional[List[MemoryType]] = None,
        scopes: Optional[List[ContextScope]] = None,
        tags: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        agent_type: Optional[str] = None,
        limit: int = 50,
        min_relevance: float = 0.1
    ) -> List[MemoryEntry]:
        """
        Retrieve memory entries based on filters
        
        Args:
            memory_types: Filter by memory types
            scopes: Filter by scopes
            tags: Filter by tags
            project_id: Filter by project
            agent_type: Filter by agent type
            limit: Maximum results
            min_relevance: Minimum relevance score
            
        Returns:
            List of memory entries
        """
        # Search in cache first
        results = []
        
        for memory_id, memory in self.memory_cache.items():
            # Check expiration
            if memory.expires_at and memory.expires_at < datetime.utcnow():
                continue
            
            # Apply filters
            if memory_types and memory.memory_type not in memory_types:
                continue
            
            if scopes and memory.scope not in scopes:
                continue
            
            if tags and not any(tag in memory.tags for tag in tags):
                continue
            
            if memory.relevance_score < min_relevance:
                continue
            
            # Check context filters
            session_context = memory.content.get('session_context', {})
            if project_id and session_context.get('project_id') != project_id:
                continue
            
            if agent_type and session_context.get('agent_type') != agent_type:
                continue
            
            # Update access tracking
            memory.access_count += 1
            memory.last_accessed = datetime.utcnow()
            
            results.append(memory)
        
        # Sort by relevance and recency
        results.sort(key=lambda m: (m.relevance_score, m.created_at), reverse=True)
        
        return results[:limit]
    
    def get_contextual_memory(
        self, 
        session_id: str,
        query_context: Optional[Dict[str, Any]] = None,
        limit: int = 20
    ) -> List[MemoryEntry]:
        """
        Get contextually relevant memory for a session
        
        Args:
            session_id: Session identifier
            query_context: Additional context for relevance
            limit: Maximum results
            
        Returns:
            List of contextually relevant memories
        """
        if session_id not in self.active_sessions:
            return []
        
        session = self.active_sessions[session_id]
        
        # Retrieve memories relevant to current session
        memories = self.retrieve_memory(
            project_id=session.project_id,
            agent_type=session.agent_type,
            limit=limit * 2  # Get more to filter
        )
        
        # Score memories based on context relevance
        scored_memories = []
        for memory in memories:
            relevance_score = self._calculate_context_relevance(
                memory, session, query_context
            )
            if relevance_score > 0.1:
                memory.relevance_score = relevance_score
                scored_memories.append(memory)
        
        # Sort by relevance and return top results
        scored_memories.sort(key=lambda m: m.relevance_score, reverse=True)
        return scored_memories[:limit]
    
    # Decision Tracking
    
    def record_decision(
        self,
        session_id: str,
        title: str,
        description: str,
        rationale: str,
        alternatives: List[str],
        decision_type: str = "technical",
        confidence: float = 0.8,
        stakeholders: Optional[List[str]] = None
    ) -> str:
        """
        Record a decision made during the session
        
        Args:
            session_id: Session identifier
            title: Decision title
            description: Decision description
            rationale: Decision rationale
            alternatives: Alternatives considered
            decision_type: Type of decision
            confidence: Confidence level
            stakeholders: People involved in decision
            
        Returns:
            Decision ID
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        # Create decision node
        decision = Decision(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            rationale=rationale,
            alternatives_considered=alternatives,
            decision_type=decision_type,
            impact_score=0.0,  # Will be updated based on outcomes
            confidence_level=confidence,
            outcome_validated=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Store in graph
        decision_id = self.graph.create_node(decision, NodeType.DECISION)
        
        # Create relationships
        if session.project_id:
            self.graph.create_relationship(
                session.project_id,
                decision_id,
                RelationshipType.CONTAINS
            )
        
        # Store as memory
        memory_content = {
            'decision_id': decision_id,
            'title': title,
            'rationale': rationale,
            'confidence': confidence,
            'stakeholders': stakeholders or []
        }
        
        self.store_memory(
            MemoryType.DECISION,
            ContextScope.PROJECT,
            memory_content,
            session_id,
            tags=['decision', decision_type]
        )
        
        logger.info(f"Recorded decision {decision_id} in session {session_id}")
        return decision_id
    
    def update_decision_outcome(
        self,
        decision_id: str,
        outcome_type: str,
        metrics: Dict[str, float],
        lessons_learned: List[str],
        confidence_score: float = 0.8
    ) -> bool:
        """
        Update decision with outcome information
        
        Args:
            decision_id: Decision identifier
            outcome_type: Type of outcome
            metrics: Outcome metrics
            lessons_learned: Lessons from the decision
            confidence_score: Confidence in outcome assessment
            
        Returns:
            True if successful
        """
        # Create outcome node
        outcome = Outcome(
            id=str(uuid.uuid4()),
            outcome_type=outcome_type,
            metrics=metrics,
            description=f"Outcome for decision {decision_id}",
            lessons_learned=lessons_learned,
            confidence_score=confidence_score,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Store outcome
        outcome_id = self.graph.create_node(outcome, NodeType.OUTCOME)
        
        # Create relationship
        self.graph.create_relationship(
            decision_id,
            outcome_id,
            RelationshipType.RESULTED_IN
        )
        
        # Update decision validation
        self.graph.update_node(
            decision_id,
            NodeType.DECISION,
            {
                'outcome_validated': True,
                'validation_date': datetime.utcnow(),
                'impact_score': metrics.get('impact_score', 0.0)
            }
        )
        
        logger.info(f"Updated decision {decision_id} with outcome {outcome_id}")
        return True
    
    # Pattern Usage Tracking
    
    def record_pattern_usage(
        self,
        session_id: str,
        pattern_id: str,
        context: Dict[str, Any],
        success: bool,
        metrics: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Record usage of a pattern
        
        Args:
            session_id: Session identifier
            pattern_id: Pattern identifier
            context: Usage context
            success: Whether usage was successful
            metrics: Optional metrics
            
        Returns:
            Usage record ID
        """
        usage_content = {
            'pattern_id': pattern_id,
            'context': context,
            'success': success,
            'metrics': metrics or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        memory_id = self.store_memory(
            MemoryType.PATTERN_USAGE,
            ContextScope.PROJECT,
            usage_content,
            session_id,
            tags=['pattern_usage', 'success' if success else 'failure']
        )
        
        # Update pattern success rate
        self._update_pattern_metrics(pattern_id, success)
        
        return memory_id
    
    # Private Helper Methods
    
    def _load_preferences(
        self, 
        user_id: Optional[str],
        team_id: Optional[str],
        project_id: Optional[str]
    ) -> Dict[str, Any]:
        """Load user, team, and project preferences"""
        preferences = {}
        
        # Load from graph if available
        if user_id:
            user_node = self.graph.get_node(user_id, NodeType.DEVELOPER)
            if user_node:
                preferences.update(user_node.preferences)
        
        if team_id:
            team_node = self.graph.get_node(team_id, NodeType.TEAM)
            if team_node:
                preferences.update(team_node.communication_preferences)
        
        return preferences
    
    def _load_session_memory(self, session: SessionContext):
        """Load relevant memory into session context"""
        # Load recent project decisions
        if session.project_id:
            recent_decisions = self.graph.get_project_decision_history(session.project_id)
            session.current_context['recent_decisions'] = recent_decisions[-5:]  # Last 5
        
        # Load agent-specific patterns
        successful_patterns = self.graph.get_agent_success_patterns(session.agent_type)
        session.current_context['successful_patterns'] = successful_patterns[:10]
        
        # Load contextual memory
        contextual_memories = self.retrieve_memory(
            project_id=session.project_id,
            agent_type=session.agent_type,
            limit=20
        )
        session.current_context['relevant_memories'] = [
            m.content for m in contextual_memories
        ]
    
    def _create_session_summary(self, session: SessionContext) -> Dict[str, Any]:
        """Create summary of session activities"""
        return {
            'session_id': session.session_id,
            'duration': (datetime.utcnow() - session.started_at).total_seconds(),
            'agent_type': session.agent_type,
            'project_id': session.project_id,
            'goals_achieved': len([g for g in session.goals if g]),  # Simplified
            'decisions_made': len([
                m for m in self.memory_cache.values() 
                if m.content.get('session_context', {}).get('session_id') == session.session_id
                and m.memory_type == MemoryType.DECISION
            ]),
            'patterns_used': len([
                m for m in self.memory_cache.values()
                if m.content.get('session_context', {}).get('session_id') == session.session_id
                and m.memory_type == MemoryType.PATTERN_USAGE
            ]),
            'context_snapshot': session.current_context
        }
    
    def _persist_session_memory(self, session: SessionContext, summary: Dict[str, Any]):
        """Persist session memory to knowledge graph"""
        # Store session summary as context
        session_context = Context(
            id=str(uuid.uuid4()),
            context_type="session_summary",
            data=summary,
            relevance_score=1.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.graph.create_node(session_context, NodeType.CONTEXT)
        
        # Link to project if available
        if session.project_id:
            self.graph.create_relationship(
                session.project_id,
                session_context.id,
                RelationshipType.CONTAINS
            )
    
    def _persist_memory_to_graph(self, memory: MemoryEntry):
        """Persist memory to knowledge graph based on type"""
        if memory.memory_type == MemoryType.CONTEXT:
            context = Context(
                id=memory.id,
                context_type=memory.content.get('type', 'general'),
                data=memory.content,
                relevance_score=memory.relevance_score,
                expiry_date=memory.expires_at,
                created_at=memory.created_at,
                updated_at=memory.created_at
            )
            self.graph.create_node(context, NodeType.CONTEXT)
    
    def _calculate_context_relevance(
        self,
        memory: MemoryEntry,
        session: SessionContext,
        query_context: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate relevance score based on context"""
        relevance = 0.0
        
        # Base relevance from memory
        relevance += memory.relevance_score * 0.3
        
        # Recency bonus
        age_hours = (datetime.utcnow() - memory.created_at).total_seconds() / 3600
        recency_score = max(0, 1 - age_hours / (24 * 7))  # Decay over a week
        relevance += recency_score * 0.2
        
        # Context matching
        memory_context = memory.content.get('session_context', {})
        
        if memory_context.get('project_id') == session.project_id:
            relevance += 0.3
        
        if memory_context.get('agent_type') == session.agent_type:
            relevance += 0.2
        
        # Query context matching
        if query_context:
            # Simple keyword matching
            memory_text = json.dumps(memory.content).lower()
            query_text = json.dumps(query_context).lower()
            
            common_words = set(memory_text.split()) & set(query_text.split())
            if common_words:
                relevance += len(common_words) * 0.05
        
        return min(1.0, relevance)
    
    def _update_pattern_metrics(self, pattern_id: str, success: bool):
        """Update pattern success metrics"""
        pattern = self.graph.get_node(pattern_id, NodeType.PATTERN)
        if pattern:
            current_usage = pattern.usage_count
            current_success_rate = pattern.success_rate
            
            new_usage = current_usage + 1
            if success:
                new_success_rate = ((current_success_rate * current_usage) + 1) / new_usage
            else:
                new_success_rate = (current_success_rate * current_usage) / new_usage
            
            self.graph.update_node(
                pattern_id,
                NodeType.PATTERN,
                {
                    'usage_count': new_usage,
                    'success_rate': new_success_rate
                }
            )