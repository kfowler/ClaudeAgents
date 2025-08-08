"""
Knowledge Graph Schema Definition

Defines the Neo4j graph schema for persistent knowledge representation,
including nodes, relationships, and constraints for the learning system.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid


class NodeType(Enum):
    """Node types in the knowledge graph"""
    PROJECT = "Project"
    AGENT = "Agent" 
    DECISION = "Decision"
    PATTERN = "Pattern"
    CONTEXT = "Context"
    OUTCOME = "Outcome"
    DEVELOPER = "Developer"
    TEAM = "Team"
    TECHNOLOGY = "Technology"
    REQUIREMENT = "Requirement"
    ISSUE = "Issue"
    SOLUTION = "Solution"


class RelationshipType(Enum):
    """Relationship types in the knowledge graph"""
    # Project relationships
    BELONGS_TO = "BELONGS_TO"
    CONTAINS = "CONTAINS"
    DEPENDS_ON = "DEPENDS_ON"
    
    # Agent relationships
    HANDLED_BY = "HANDLED_BY"
    COLLABORATED_WITH = "COLLABORATED_WITH"
    RECOMMENDED = "RECOMMENDED"
    
    # Decision relationships
    MADE_DECISION = "MADE_DECISION"
    INFLUENCED_BY = "INFLUENCED_BY"
    RESULTED_IN = "RESULTED_IN"
    
    # Pattern relationships
    IMPLEMENTS = "IMPLEMENTS"
    SIMILAR_TO = "SIMILAR_TO"
    EVOLVED_FROM = "EVOLVED_FROM"
    
    # Context relationships
    APPLIED_IN = "APPLIED_IN"
    RELEVANT_TO = "RELEVANT_TO"
    
    # Learning relationships
    LEARNED_FROM = "LEARNED_FROM"
    IMPROVED_BY = "IMPROVED_BY"
    VALIDATED_BY = "VALIDATED_BY"


@dataclass
class BaseNode:
    """Base class for all graph nodes"""
    id: str
    created_at: datetime
    updated_at: datetime
    version: int = 1
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.utcnow()
        if not self.updated_at:
            self.updated_at = datetime.utcnow()


@dataclass
class Project(BaseNode):
    """Project node representing a development project"""
    name: str
    description: str
    status: str  # active, completed, archived
    technology_stack: List[str]
    team_size: int
    complexity_score: float
    domain: str  # web, mobile, ai, etc.
    privacy_level: str  # public, private, confidential
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Agent(BaseNode):
    """Agent node representing an AI agent"""
    name: str
    type: str  # specialist type
    capabilities: List[str]
    success_rate: float
    usage_count: int
    last_used: datetime
    performance_metrics: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Decision(BaseNode):
    """Decision node representing architectural or technical decisions"""
    title: str
    description: str
    rationale: str
    alternatives_considered: List[str]
    decision_type: str  # architectural, technical, process
    impact_score: float
    confidence_level: float
    outcome_validated: bool
    validation_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Pattern(BaseNode):
    """Pattern node representing reusable solutions and approaches"""
    name: str
    description: str
    pattern_type: str  # architectural, design, implementation
    context: str
    problem: str
    solution: str
    consequences: List[str]
    usage_count: int
    success_rate: float
    code_examples: List[str]
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Context(BaseNode):
    """Context node representing situational information"""
    context_type: str  # project_context, technical_context, business_context
    data: Dict[str, Any]
    relevance_score: float
    expiry_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Outcome(BaseNode):
    """Outcome node representing results and metrics"""
    outcome_type: str  # success, failure, partial_success
    metrics: Dict[str, float]
    description: str
    lessons_learned: List[str]
    confidence_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Developer(BaseNode):
    """Developer node representing team members"""
    name: str
    role: str
    experience_level: str
    skills: List[str]
    preferences: Dict[str, Any]
    interaction_count: int
    satisfaction_score: float
    privacy_settings: Dict[str, bool]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Team(BaseNode):
    """Team node representing development teams"""
    name: str
    size: int
    domain_expertise: List[str]
    working_style: str
    communication_preferences: Dict[str, str]
    success_metrics: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Graph schema constraints and indexes
GRAPH_CONSTRAINTS = [
    # Unique constraints
    "CREATE CONSTRAINT project_id_unique IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT agent_id_unique IF NOT EXISTS FOR (a:Agent) REQUIRE a.id IS UNIQUE",
    "CREATE CONSTRAINT decision_id_unique IF NOT EXISTS FOR (d:Decision) REQUIRE d.id IS UNIQUE",
    "CREATE CONSTRAINT pattern_id_unique IF NOT EXISTS FOR (p:Pattern) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT context_id_unique IF NOT EXISTS FOR (c:Context) REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT outcome_id_unique IF NOT EXISTS FOR (o:Outcome) REQUIRE o.id IS UNIQUE",
    "CREATE CONSTRAINT developer_id_unique IF NOT EXISTS FOR (d:Developer) REQUIRE d.id IS UNIQUE",
    "CREATE CONSTRAINT team_id_unique IF NOT EXISTS FOR (t:Team) REQUIRE t.id IS UNIQUE",
]

GRAPH_INDEXES = [
    # Performance indexes
    "CREATE INDEX project_name_index IF NOT EXISTS FOR (p:Project) ON (p.name)",
    "CREATE INDEX agent_type_index IF NOT EXISTS FOR (a:Agent) ON (a.type)",
    "CREATE INDEX decision_type_index IF NOT EXISTS FOR (d:Decision) ON (d.decision_type)",
    "CREATE INDEX pattern_type_index IF NOT EXISTS FOR (p:Pattern) ON (p.pattern_type)",
    "CREATE INDEX context_type_index IF NOT EXISTS FOR (c:Context) ON (c.context_type)",
    "CREATE INDEX outcome_type_index IF NOT EXISTS FOR (o:Outcome) ON (o.outcome_type)",
    "CREATE INDEX created_at_index IF NOT EXISTS FOR (n) ON (n.created_at)",
    "CREATE INDEX updated_at_index IF NOT EXISTS FOR (n) ON (n.updated_at)",
    
    # Full-text search indexes
    "CREATE FULLTEXT INDEX project_search_index IF NOT EXISTS FOR (p:Project) ON EACH [p.name, p.description]",
    "CREATE FULLTEXT INDEX pattern_search_index IF NOT EXISTS FOR (p:Pattern) ON EACH [p.name, p.description, p.problem, p.solution]",
    "CREATE FULLTEXT INDEX decision_search_index IF NOT EXISTS FOR (d:Decision) ON EACH [d.title, d.description, d.rationale]",
]


def get_node_class(node_type: str) -> type:
    """Get the appropriate node class for a given node type"""
    node_classes = {
        NodeType.PROJECT.value: Project,
        NodeType.AGENT.value: Agent,
        NodeType.DECISION.value: Decision,
        NodeType.PATTERN.value: Pattern,
        NodeType.CONTEXT.value: Context,
        NodeType.OUTCOME.value: Outcome,
        NodeType.DEVELOPER.value: Developer,
        NodeType.TEAM.value: Team,
    }
    return node_classes.get(node_type)