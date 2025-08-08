"""
Event Sourcing System

Implements complete history tracking through event sourcing pattern.
Captures all agent actions, decisions, and system changes as immutable events
with full audit trail and replay capabilities.
"""

import logging
from typing import Dict, List, Optional, Any, Type, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import json
import uuid
from abc import ABC, abstractmethod
import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import sqlite3
import threading

from ..knowledge_graph.graph_manager import GraphManager
from ..knowledge_graph.schema import NodeType, RelationshipType


logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events in the system"""
    # Agent events
    AGENT_SESSION_STARTED = "agent_session_started"
    AGENT_SESSION_ENDED = "agent_session_ended"
    AGENT_ACTION_PERFORMED = "agent_action_performed"
    AGENT_RECOMMENDATION_MADE = "agent_recommendation_made"
    AGENT_FEEDBACK_RECEIVED = "agent_feedback_received"
    
    # Decision events
    DECISION_PROPOSED = "decision_proposed"
    DECISION_MADE = "decision_made"
    DECISION_IMPLEMENTED = "decision_implemented"
    DECISION_VALIDATED = "decision_validated"
    DECISION_OUTCOME_RECORDED = "decision_outcome_recorded"
    
    # Pattern events
    PATTERN_DISCOVERED = "pattern_discovered"
    PATTERN_APPLIED = "pattern_applied"
    PATTERN_MODIFIED = "pattern_modified"
    PATTERN_VALIDATED = "pattern_validated"
    PATTERN_DEPRECATED = "pattern_deprecated"
    
    # Learning events
    MODEL_TRAINED = "model_trained"
    MODEL_PREDICTION_MADE = "model_prediction_made"
    MODEL_FEEDBACK_RECEIVED = "model_feedback_received"
    MODEL_UPDATED = "model_updated"
    
    # Knowledge events
    KNOWLEDGE_CREATED = "knowledge_created"
    KNOWLEDGE_UPDATED = "knowledge_updated"
    KNOWLEDGE_LINKED = "knowledge_linked"
    KNOWLEDGE_ACCESSED = "knowledge_accessed"
    
    # System events
    SYSTEM_ERROR = "system_error"
    SYSTEM_RECOVERY = "system_recovery"
    SYSTEM_MAINTENANCE = "system_maintenance"
    SYSTEM_UPGRADE = "system_upgrade"
    
    # User events
    USER_INTERACTION = "user_interaction"
    USER_PREFERENCE_CHANGED = "user_preference_changed"
    USER_FEEDBACK_PROVIDED = "user_feedback_provided"


@dataclass
class BaseEvent(ABC):
    """Base class for all events"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = field(init=False)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None  # For tracing related events
    causation_id: Optional[str] = None    # Event that caused this event
    
    # Context information
    session_id: Optional[str] = None
    project_id: Optional[str] = None
    user_id: Optional[str] = None
    agent_type: Optional[str] = None
    
    # Metadata
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEvent':
        """Create event from dictionary"""
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['event_type'] = EventType(data['event_type'])
        return cls(**data)


@dataclass
class AgentSessionStartedEvent(BaseEvent):
    """Agent session started event"""
    event_type: EventType = field(default=EventType.AGENT_SESSION_STARTED, init=False)
    goals: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentSessionEndedEvent(BaseEvent):
    """Agent session ended event"""
    event_type: EventType = field(default=EventType.AGENT_SESSION_ENDED, init=False)
    duration_seconds: float = 0.0
    actions_performed: int = 0
    decisions_made: int = 0
    patterns_applied: int = 0
    success_score: float = 0.0
    summary: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentActionPerformedEvent(BaseEvent):
    """Agent action performed event"""
    event_type: EventType = field(default=EventType.AGENT_ACTION_PERFORMED, init=False)
    action_type: str = ""
    action_description: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0


@dataclass
class DecisionMadeEvent(BaseEvent):
    """Decision made event"""
    event_type: EventType = field(default=EventType.DECISION_MADE, init=False)
    decision_id: str = ""
    title: str = ""
    description: str = ""
    rationale: str = ""
    alternatives_considered: List[str] = field(default_factory=list)
    decision_type: str = "technical"
    confidence_level: float = 0.8
    stakeholders: List[str] = field(default_factory=list)
    expected_impact: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PatternAppliedEvent(BaseEvent):
    """Pattern applied event"""
    event_type: EventType = field(default=EventType.PATTERN_APPLIED, init=False)
    pattern_id: str = ""
    pattern_name: str = ""
    pattern_type: str = ""
    application_context: Dict[str, Any] = field(default_factory=dict)
    adaptations_made: List[str] = field(default_factory=list)
    expected_outcome: str = ""


@dataclass
class ModelPredictionMadeEvent(BaseEvent):
    """ML model prediction made event"""
    event_type: EventType = field(default=EventType.MODEL_PREDICTION_MADE, init=False)
    model_type: str = ""
    model_version: str = ""
    input_features: Dict[str, Any] = field(default_factory=dict)
    prediction: Any = None
    confidence: float = 0.0
    explanation: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeCreatedEvent(BaseEvent):
    """Knowledge created event"""
    event_type: EventType = field(default=EventType.KNOWLEDGE_CREATED, init=False)
    knowledge_type: str = ""
    knowledge_id: str = ""
    content_summary: str = ""
    tags: List[str] = field(default_factory=list)
    source: str = ""
    quality_score: float = 0.0


@dataclass
class UserInteractionEvent(BaseEvent):
    """User interaction event"""
    event_type: EventType = field(default=EventType.USER_INTERACTION, init=False)
    interaction_type: str = ""
    request_summary: str = ""
    response_summary: str = ""
    satisfaction_score: Optional[float] = None
    duration_seconds: float = 0.0
    follow_up_questions: int = 0


class EventStore:
    """
    Event store for capturing and retrieving all system events
    """
    
    def __init__(self, storage_path: str = "/tmp/learning_events.db"):
        """
        Initialize event store
        
        Args:
            storage_path: Path to SQLite database file
        """
        self.storage_path = storage_path
        self.connection_pool = {}
        self.lock = threading.Lock()
        
        # Event type registry
        self.event_types: Dict[EventType, Type[BaseEvent]] = {
            EventType.AGENT_SESSION_STARTED: AgentSessionStartedEvent,
            EventType.AGENT_SESSION_ENDED: AgentSessionEndedEvent,
            EventType.AGENT_ACTION_PERFORMED: AgentActionPerformedEvent,
            EventType.DECISION_MADE: DecisionMadeEvent,
            EventType.PATTERN_APPLIED: PatternAppliedEvent,
            EventType.MODEL_PREDICTION_MADE: ModelPredictionMadeEvent,
            EventType.KNOWLEDGE_CREATED: KnowledgeCreatedEvent,
            EventType.USER_INTERACTION: UserInteractionEvent,
        }
        
        # Event handlers
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        
        # Async event processing
        self.event_queue = asyncio.Queue()
        self.processing_events = False
        
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize SQLite storage"""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    correlation_id TEXT,
                    causation_id TEXT,
                    session_id TEXT,
                    project_id TEXT,
                    user_id TEXT,
                    agent_type TEXT,
                    version INTEGER DEFAULT 1,
                    event_data TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for common queries
            conn.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON events(session_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_project_id ON events(project_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_correlation_id ON events(correlation_id)')
            
            # Create event snapshots table for aggregations
            conn.execute('''
                CREATE TABLE IF NOT EXISTS event_snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    snapshot_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('CREATE INDEX IF NOT EXISTS idx_snapshot_entity ON event_snapshots(entity_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_snapshot_type ON event_snapshots(snapshot_type)')
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper cleanup"""
        thread_id = threading.get_ident()
        
        with self.lock:
            if thread_id not in self.connection_pool:
                self.connection_pool[thread_id] = sqlite3.connect(
                    self.storage_path,
                    check_same_thread=False
                )
                self.connection_pool[thread_id].row_factory = sqlite3.Row
        
        conn = self.connection_pool[thread_id]
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            raise e
    
    # Event Publishing
    
    def publish_event(self, event: BaseEvent) -> bool:
        """
        Publish an event to the store
        
        Args:
            event: Event to publish
            
        Returns:
            True if successful
        """
        try:
            # Store event
            event_data = event.to_dict()
            
            with self._get_connection() as conn:
                conn.execute('''
                    INSERT INTO events (
                        event_id, event_type, timestamp, correlation_id, causation_id,
                        session_id, project_id, user_id, agent_type, version, event_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.event_id,
                    event.event_type.value,
                    event.timestamp.isoformat(),
                    event.correlation_id,
                    event.causation_id,
                    event.session_id,
                    event.project_id,
                    event.user_id,
                    event.agent_type,
                    event.version,
                    json.dumps(event_data)
                ))
                conn.commit()
            
            # Trigger event handlers
            self._trigger_handlers(event)
            
            logger.debug(f"Published event {event.event_id} of type {event.event_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False
    
    def publish_events_batch(self, events: List[BaseEvent]) -> int:
        """
        Publish multiple events in batch
        
        Args:
            events: List of events to publish
            
        Returns:
            Number of events successfully published
        """
        if not events:
            return 0
        
        successful = 0
        
        try:
            with self._get_connection() as conn:
                for event in events:
                    try:
                        event_data = event.to_dict()
                        
                        conn.execute('''
                            INSERT INTO events (
                                event_id, event_type, timestamp, correlation_id, causation_id,
                                session_id, project_id, user_id, agent_type, version, event_data
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            event.event_id,
                            event.event_type.value,
                            event.timestamp.isoformat(),
                            event.correlation_id,
                            event.causation_id,
                            event.session_id,
                            event.project_id,
                            event.user_id,
                            event.agent_type,
                            event.version,
                            json.dumps(event_data)
                        ))
                        
                        successful += 1
                        
                        # Trigger handlers
                        self._trigger_handlers(event)
                        
                    except Exception as e:
                        logger.error(f"Failed to publish event {event.event_id}: {e}")
                
                conn.commit()
            
            logger.info(f"Published {successful}/{len(events)} events in batch")
            return successful
            
        except Exception as e:
            logger.error(f"Failed to publish event batch: {e}")
            return successful
    
    # Event Retrieval
    
    def get_events(
        self,
        event_types: Optional[List[EventType]] = None,
        session_id: Optional[str] = None,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
        agent_type: Optional[str] = None,
        correlation_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[BaseEvent]:
        """
        Retrieve events based on filters
        
        Args:
            event_types: Filter by event types
            session_id: Filter by session ID
            project_id: Filter by project ID
            user_id: Filter by user ID
            agent_type: Filter by agent type
            correlation_id: Filter by correlation ID
            start_time: Start time filter
            end_time: End time filter
            limit: Maximum number of events
            offset: Offset for pagination
            
        Returns:
            List of events
        """
        try:
            # Build query
            where_clauses = []
            params = []
            
            if event_types:
                placeholders = ','.join('?' * len(event_types))
                where_clauses.append(f"event_type IN ({placeholders})")
                params.extend([et.value for et in event_types])
            
            if session_id:
                where_clauses.append("session_id = ?")
                params.append(session_id)
            
            if project_id:
                where_clauses.append("project_id = ?")
                params.append(project_id)
            
            if user_id:
                where_clauses.append("user_id = ?")
                params.append(user_id)
            
            if agent_type:
                where_clauses.append("agent_type = ?")
                params.append(agent_type)
            
            if correlation_id:
                where_clauses.append("correlation_id = ?")
                params.append(correlation_id)
            
            if start_time:
                where_clauses.append("timestamp >= ?")
                params.append(start_time.isoformat())
            
            if end_time:
                where_clauses.append("timestamp <= ?")
                params.append(end_time.isoformat())
            
            where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            
            query = f'''
                SELECT event_data FROM events
                {where_clause}
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            '''
            
            params.extend([limit, offset])
            
            # Execute query
            with self._get_connection() as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
            
            # Deserialize events
            events = []
            for row in rows:
                try:
                    event_data = json.loads(row['event_data'])
                    event_type = EventType(event_data['event_type'])
                    
                    if event_type in self.event_types:
                        event_class = self.event_types[event_type]
                        event = event_class.from_dict(event_data)
                        events.append(event)
                    else:
                        # Generic event
                        event = BaseEvent.from_dict(event_data)
                        events.append(event)
                        
                except Exception as e:
                    logger.error(f"Failed to deserialize event: {e}")
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to retrieve events: {e}")
            return []
    
    def get_event_stream(
        self,
        session_id: Optional[str] = None,
        project_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[BaseEvent]:
        """
        Get chronological stream of events for analysis
        
        Args:
            session_id: Filter by session
            project_id: Filter by project
            start_time: Start time
            end_time: End time
            
        Returns:
            Chronologically ordered events
        """
        return self.get_events(
            session_id=session_id,
            project_id=project_id,
            start_time=start_time,
            end_time=end_time,
            limit=10000  # Large limit for full stream
        )
    
    def get_event_by_id(self, event_id: str) -> Optional[BaseEvent]:
        """Get specific event by ID"""
        events = self.get_events(limit=1)  # This needs to be fixed to query by ID
        # Simplified implementation - would need proper query
        return events[0] if events else None
    
    # Event Aggregation
    
    def get_event_counts(
        self,
        group_by: str = "event_type",
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Get event counts grouped by specified field
        
        Args:
            group_by: Field to group by (event_type, session_id, etc.)
            start_time: Start time filter
            end_time: End time filter
            project_id: Project filter
            
        Returns:
            Dictionary of counts
        """
        try:
            where_clauses = []
            params = []
            
            if start_time:
                where_clauses.append("timestamp >= ?")
                params.append(start_time.isoformat())
            
            if end_time:
                where_clauses.append("timestamp <= ?")
                params.append(end_time.isoformat())
            
            if project_id:
                where_clauses.append("project_id = ?")
                params.append(project_id)
            
            where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            
            query = f'''
                SELECT {group_by}, COUNT(*) as count
                FROM events
                {where_clause}
                GROUP BY {group_by}
                ORDER BY count DESC
            '''
            
            with self._get_connection() as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
            
            return {row[group_by]: row['count'] for row in rows}
            
        except Exception as e:
            logger.error(f"Failed to get event counts: {e}")
            return {}
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get summary of events for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session summary
        """
        events = self.get_events(session_id=session_id, limit=1000)
        
        if not events:
            return {}
        
        # Calculate summary metrics
        start_time = min(event.timestamp for event in events)
        end_time = max(event.timestamp for event in events)
        duration = (end_time - start_time).total_seconds()
        
        event_counts = {}
        for event in events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Extract specific metrics
        actions_performed = event_counts.get(EventType.AGENT_ACTION_PERFORMED.value, 0)
        decisions_made = event_counts.get(EventType.DECISION_MADE.value, 0)
        patterns_applied = event_counts.get(EventType.PATTERN_APPLIED.value, 0)
        
        return {
            'session_id': session_id,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'total_events': len(events),
            'event_counts': event_counts,
            'actions_performed': actions_performed,
            'decisions_made': decisions_made,
            'patterns_applied': patterns_applied
        }
    
    # Event Handlers
    
    def add_event_handler(self, event_type: EventType, handler: Callable[[BaseEvent], None]):
        """
        Add event handler for specific event type
        
        Args:
            event_type: Type of event to handle
            handler: Handler function
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def remove_event_handler(self, event_type: EventType, handler: Callable):
        """Remove event handler"""
        if event_type in self.event_handlers:
            self.event_handlers[event_type] = [
                h for h in self.event_handlers[event_type] if h != handler
            ]
    
    def _trigger_handlers(self, event: BaseEvent):
        """Trigger all handlers for an event"""
        handlers = self.event_handlers.get(event.event_type, [])
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Event handler failed for {event.event_type}: {e}")
    
    # Event Replay and Analysis
    
    def replay_events(
        self,
        target_time: datetime,
        entity_id: Optional[str] = None,
        event_types: Optional[List[EventType]] = None
    ) -> List[BaseEvent]:
        """
        Replay events up to a specific point in time
        
        Args:
            target_time: Time to replay to
            entity_id: Specific entity to replay for
            event_types: Types of events to include
            
        Returns:
            Events in replay order
        """
        return self.get_events(
            event_types=event_types,
            session_id=entity_id,  # Simplified - could be project_id etc.
            end_time=target_time,
            limit=10000
        )
    
    def analyze_event_patterns(
        self,
        pattern_type: str = "sequence",
        time_window_hours: int = 24,
        min_occurrences: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Analyze patterns in event sequences
        
        Args:
            pattern_type: Type of pattern analysis
            time_window_hours: Time window for pattern detection
            min_occurrences: Minimum occurrences to consider a pattern
            
        Returns:
            List of detected patterns
        """
        # Simplified implementation - in practice would use more sophisticated analysis
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            events = self.get_events(start_time=cutoff_time, limit=10000)
            
            if pattern_type == "sequence":
                # Analyze event type sequences
                sequences = {}
                
                # Group events by session
                session_events = {}
                for event in events:
                    if event.session_id:
                        if event.session_id not in session_events:
                            session_events[event.session_id] = []
                        session_events[event.session_id].append(event)
                
                # Find common sequences
                for session_id, session_event_list in session_events.items():
                    # Sort by timestamp
                    session_event_list.sort(key=lambda e: e.timestamp)
                    
                    # Extract sequences of event types
                    event_types = [e.event_type.value for e in session_event_list]
                    
                    # Find subsequences of length 3
                    for i in range(len(event_types) - 2):
                        seq = tuple(event_types[i:i+3])
                        sequences[seq] = sequences.get(seq, 0) + 1
                
                # Filter by minimum occurrences
                patterns = []
                for sequence, count in sequences.items():
                    if count >= min_occurrences:
                        patterns.append({
                            'pattern_type': 'sequence',
                            'sequence': list(sequence),
                            'occurrences': count,
                            'confidence': count / len(session_events) if session_events else 0
                        })
                
                # Sort by occurrences
                patterns.sort(key=lambda p: p['occurrences'], reverse=True)
                return patterns[:10]  # Top 10 patterns
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to analyze event patterns: {e}")
            return []
    
    # Maintenance
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get event store statistics"""
        try:
            with self._get_connection() as conn:
                # Total events
                cursor = conn.execute("SELECT COUNT(*) as count FROM events")
                total_events = cursor.fetchone()['count']
                
                # Events by type
                cursor = conn.execute('''
                    SELECT event_type, COUNT(*) as count 
                    FROM events 
                    GROUP BY event_type 
                    ORDER BY count DESC
                ''')
                events_by_type = {row['event_type']: row['count'] for row in cursor.fetchall()}
                
                # Recent activity (last 24 hours)
                cutoff = datetime.utcnow() - timedelta(hours=24)
                cursor = conn.execute(
                    "SELECT COUNT(*) as count FROM events WHERE timestamp >= ?",
                    (cutoff.isoformat(),)
                )
                recent_events = cursor.fetchone()['count']
                
                # Database size
                cursor = conn.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                cursor = conn.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                db_size_bytes = page_count * page_size
            
            return {
                'total_events': total_events,
                'events_by_type': events_by_type,
                'recent_events_24h': recent_events,
                'database_size_bytes': db_size_bytes,
                'database_size_mb': db_size_bytes / (1024 * 1024),
                'storage_path': self.storage_path
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {}
    
    def cleanup_old_events(self, days_to_keep: int = 90) -> int:
        """
        Clean up old events
        
        Args:
            days_to_keep: Number of days of events to keep
            
        Returns:
            Number of events deleted
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days_to_keep)
            
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "DELETE FROM events WHERE timestamp < ?",
                    (cutoff_time.isoformat(),)
                )
                deleted_count = cursor.rowcount
                conn.commit()
            
            logger.info(f"Cleaned up {deleted_count} old events")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old events: {e}")
            return 0


# Event builder helpers
def create_session_started_event(
    session_id: str,
    agent_type: str,
    project_id: Optional[str] = None,
    user_id: Optional[str] = None,
    goals: Optional[List[str]] = None,
    **kwargs
) -> AgentSessionStartedEvent:
    """Create agent session started event"""
    return AgentSessionStartedEvent(
        session_id=session_id,
        agent_type=agent_type,
        project_id=project_id,
        user_id=user_id,
        goals=goals or [],
        **kwargs
    )


def create_action_event(
    session_id: str,
    action_type: str,
    action_description: str,
    success: bool = True,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    **kwargs
) -> AgentActionPerformedEvent:
    """Create agent action performed event"""
    return AgentActionPerformedEvent(
        session_id=session_id,
        action_type=action_type,
        action_description=action_description,
        success=success,
        inputs=inputs or {},
        outputs=outputs or {},
        **kwargs
    )


def create_decision_event(
    session_id: str,
    decision_id: str,
    title: str,
    description: str,
    rationale: str,
    **kwargs
) -> DecisionMadeEvent:
    """Create decision made event"""
    return DecisionMadeEvent(
        session_id=session_id,
        decision_id=decision_id,
        title=title,
        description=description,
        rationale=rationale,
        **kwargs
    )