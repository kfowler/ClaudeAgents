"""
Knowledge Graph Manager

Manages Neo4j connections, CRUD operations, and graph queries
for the persistent knowledge system.
"""

import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
import json
from contextlib import contextmanager
from dataclasses import asdict

from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import Neo4jError

from .schema import (
    BaseNode, NodeType, RelationshipType,
    Project, Agent, Decision, Pattern, Context, Outcome, Developer, Team,
    GRAPH_CONSTRAINTS, GRAPH_INDEXES,
    get_node_class
)


logger = logging.getLogger(__name__)


class GraphManager:
    """
    Manages Neo4j graph database operations for the knowledge system
    """
    
    def __init__(self, uri: str, username: str, password: str):
        """
        Initialize graph manager with Neo4j connection
        
        Args:
            uri: Neo4j database URI
            username: Database username
            password: Database password
        """
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.initialize_schema()
    
    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()
    
    @contextmanager
    def get_session(self) -> Session:
        """Context manager for database sessions"""
        session = self.driver.session()
        try:
            yield session
        finally:
            session.close()
    
    def initialize_schema(self):
        """Initialize graph schema with constraints and indexes"""
        with self.get_session() as session:
            # Create constraints
            for constraint in GRAPH_CONSTRAINTS:
                try:
                    session.run(constraint)
                except Neo4jError as e:
                    logger.warning(f"Constraint creation failed: {e}")
            
            # Create indexes
            for index in GRAPH_INDEXES:
                try:
                    session.run(index)
                except Neo4jError as e:
                    logger.warning(f"Index creation failed: {e}")
    
    # Node CRUD Operations
    
    def create_node(self, node: BaseNode, node_type: NodeType) -> str:
        """
        Create a new node in the graph
        
        Args:
            node: Node data object
            node_type: Type of node to create
            
        Returns:
            Node ID
        """
        with self.get_session() as session:
            query = f"""
            CREATE (n:{node_type.value} $props)
            RETURN n.id as id
            """
            
            props = node.to_dict()
            # Convert datetime objects to ISO format strings
            for key, value in props.items():
                if isinstance(value, datetime):
                    props[key] = value.isoformat()
            
            result = session.run(query, props=props)
            return result.single()["id"]
    
    def get_node(self, node_id: str, node_type: NodeType) -> Optional[BaseNode]:
        """
        Retrieve a node by ID and type
        
        Args:
            node_id: Node identifier
            node_type: Type of node
            
        Returns:
            Node object or None if not found
        """
        with self.get_session() as session:
            query = f"""
            MATCH (n:{node_type.value} {{id: $node_id}})
            RETURN n
            """
            
            result = session.run(query, node_id=node_id)
            record = result.single()
            
            if record:
                node_data = dict(record["n"])
                # Convert ISO strings back to datetime objects
                for key, value in node_data.items():
                    if isinstance(value, str) and key.endswith('_at'):
                        try:
                            node_data[key] = datetime.fromisoformat(value)
                        except ValueError:
                            pass
                
                node_class = get_node_class(node_type.value)
                return node_class(**node_data)
            
            return None
    
    def update_node(self, node_id: str, node_type: NodeType, updates: Dict[str, Any]) -> bool:
        """
        Update node properties
        
        Args:
            node_id: Node identifier
            node_type: Type of node
            updates: Dictionary of properties to update
            
        Returns:
            True if update successful, False otherwise
        """
        with self.get_session() as session:
            # Convert datetime objects to ISO format strings
            processed_updates = {}
            for key, value in updates.items():
                if isinstance(value, datetime):
                    processed_updates[key] = value.isoformat()
                else:
                    processed_updates[key] = value
            
            # Always update the updated_at timestamp and increment version
            processed_updates['updated_at'] = datetime.utcnow().isoformat()
            
            query = f"""
            MATCH (n:{node_type.value} {{id: $node_id}})
            SET n += $updates, n.version = COALESCE(n.version, 0) + 1
            RETURN n.id as id
            """
            
            result = session.run(query, node_id=node_id, updates=processed_updates)
            return result.single() is not None
    
    def delete_node(self, node_id: str, node_type: NodeType) -> bool:
        """
        Delete a node and all its relationships
        
        Args:
            node_id: Node identifier
            node_type: Type of node
            
        Returns:
            True if deletion successful, False otherwise
        """
        with self.get_session() as session:
            query = f"""
            MATCH (n:{node_type.value} {{id: $node_id}})
            DETACH DELETE n
            RETURN count(n) as deleted_count
            """
            
            result = session.run(query, node_id=node_id)
            return result.single()["deleted_count"] > 0
    
    # Relationship Operations
    
    def create_relationship(
        self, 
        from_id: str, 
        to_id: str, 
        relationship_type: RelationshipType,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create a relationship between two nodes
        
        Args:
            from_id: Source node ID
            to_id: Target node ID
            relationship_type: Type of relationship
            properties: Optional relationship properties
            
        Returns:
            True if creation successful, False otherwise
        """
        with self.get_session() as session:
            props = properties or {}
            props['created_at'] = datetime.utcnow().isoformat()
            
            query = f"""
            MATCH (a {{id: $from_id}}), (b {{id: $to_id}})
            CREATE (a)-[r:{relationship_type.value} $props]->(b)
            RETURN r
            """
            
            result = session.run(query, from_id=from_id, to_id=to_id, props=props)
            return result.single() is not None
    
    def get_relationships(
        self, 
        node_id: str, 
        relationship_type: Optional[RelationshipType] = None,
        direction: str = "both"  # "in", "out", "both"
    ) -> List[Dict[str, Any]]:
        """
        Get relationships for a node
        
        Args:
            node_id: Node identifier
            relationship_type: Optional relationship type filter
            direction: Relationship direction ("in", "out", "both")
            
        Returns:
            List of relationship data
        """
        with self.get_session() as session:
            if relationship_type:
                rel_pattern = f":{relationship_type.value}"
            else:
                rel_pattern = ""
            
            if direction == "in":
                pattern = f"(other)-[r{rel_pattern}]->(n)"
            elif direction == "out":
                pattern = f"(n)-[r{rel_pattern}]->(other)"
            else:  # both
                pattern = f"(n)-[r{rel_pattern}]-(other)"
            
            query = f"""
            MATCH (n {{id: $node_id}})
            MATCH {pattern}
            RETURN r, other.id as other_id, labels(other) as other_labels
            """
            
            result = session.run(query, node_id=node_id)
            relationships = []
            
            for record in result:
                rel_data = dict(record["r"])
                rel_data["target_id"] = record["other_id"]
                rel_data["target_labels"] = record["other_labels"]
                relationships.append(rel_data)
            
            return relationships
    
    # Advanced Query Operations
    
    def find_similar_patterns(
        self, 
        pattern_id: str, 
        similarity_threshold: float = 0.7,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find patterns similar to the given pattern
        
        Args:
            pattern_id: Pattern identifier
            similarity_threshold: Minimum similarity score
            limit: Maximum number of results
            
        Returns:
            List of similar patterns with similarity scores
        """
        with self.get_session() as session:
            query = """
            MATCH (p:Pattern {id: $pattern_id})
            MATCH (similar:Pattern)
            WHERE p.id <> similar.id
            AND similar.pattern_type = p.pattern_type
            WITH p, similar,
                 size(apoc.coll.intersection(p.tags, similar.tags)) as common_tags,
                 size(p.tags) as p_tags_count,
                 size(similar.tags) as similar_tags_count
            WITH p, similar,
                 toFloat(common_tags) / (p_tags_count + similar_tags_count - common_tags) as jaccard_similarity
            WHERE jaccard_similarity >= $threshold
            RETURN similar, jaccard_similarity
            ORDER BY jaccard_similarity DESC
            LIMIT $limit
            """
            
            result = session.run(
                query, 
                pattern_id=pattern_id, 
                threshold=similarity_threshold, 
                limit=limit
            )
            
            similar_patterns = []
            for record in result:
                pattern_data = dict(record["similar"])
                pattern_data["similarity_score"] = record["jaccard_similarity"]
                similar_patterns.append(pattern_data)
            
            return similar_patterns
    
    def get_project_decision_history(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get chronological decision history for a project
        
        Args:
            project_id: Project identifier
            
        Returns:
            List of decisions with outcomes and impacts
        """
        with self.get_session() as session:
            query = """
            MATCH (p:Project {id: $project_id})
            MATCH (p)-[:CONTAINS]->(d:Decision)
            OPTIONAL MATCH (d)-[:RESULTED_IN]->(o:Outcome)
            OPTIONAL MATCH (d)-[:HANDLED_BY]->(a:Agent)
            RETURN d, o, a
            ORDER BY d.created_at ASC
            """
            
            result = session.run(query, project_id=project_id)
            decisions = []
            
            for record in result:
                decision_data = dict(record["d"])
                if record["o"]:
                    decision_data["outcome"] = dict(record["o"])
                if record["a"]:
                    decision_data["handled_by"] = dict(record["a"])
                decisions.append(decision_data)
            
            return decisions
    
    def get_agent_success_patterns(
        self, 
        agent_type: str,
        min_confidence: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Get successful patterns associated with an agent type
        
        Args:
            agent_type: Type of agent
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of successful patterns with context
        """
        with self.get_session() as session:
            query = """
            MATCH (a:Agent {type: $agent_type})
            MATCH (a)-[:RECOMMENDED]->(p:Pattern)
            MATCH (p)-[:APPLIED_IN]->(proj:Project)
            MATCH (proj)-[:CONTAINS]->(o:Outcome {outcome_type: 'success'})
            WHERE o.confidence_score >= $min_confidence
            WITH p, count(o) as success_count
            MATCH (p)-[:APPLIED_IN]->(all_proj:Project)
            WITH p, success_count, count(all_proj) as total_usage
            RETURN p, success_count, total_usage,
                   toFloat(success_count) / total_usage as success_rate
            ORDER BY success_rate DESC, success_count DESC
            """
            
            result = session.run(query, agent_type=agent_type, min_confidence=min_confidence)
            patterns = []
            
            for record in result:
                pattern_data = dict(record["p"])
                pattern_data["success_count"] = record["success_count"]
                pattern_data["total_usage"] = record["total_usage"]
                pattern_data["success_rate"] = record["success_rate"]
                patterns.append(pattern_data)
            
            return patterns
    
    def find_knowledge_gaps(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Identify knowledge gaps in a project based on missing patterns or decisions
        
        Args:
            project_id: Project identifier
            
        Returns:
            List of potential knowledge gaps
        """
        with self.get_session() as session:
            query = """
            MATCH (p:Project {id: $project_id})
            MATCH (similar:Project)
            WHERE similar.domain = p.domain 
            AND similar.id <> p.id
            AND similar.complexity_score <= p.complexity_score * 1.2
            MATCH (similar)-[:CONTAINS]->(pattern:Pattern)
            WHERE NOT EXISTS {
                MATCH (p)-[:CONTAINS]->(existing:Pattern)
                WHERE existing.pattern_type = pattern.pattern_type
                AND existing.name = pattern.name
            }
            WITH pattern, count(*) as usage_frequency
            WHERE usage_frequency >= 2
            RETURN pattern, usage_frequency
            ORDER BY usage_frequency DESC
            """
            
            result = session.run(query, project_id=project_id)
            gaps = []
            
            for record in result:
                gap_data = dict(record["pattern"])
                gap_data["usage_frequency"] = record["usage_frequency"]
                gap_data["gap_type"] = "missing_pattern"
                gaps.append(gap_data)
            
            return gaps
    
    def get_context_timeline(self, project_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get contextual timeline for a project
        
        Args:
            project_id: Project identifier
            days: Number of days to look back
            
        Returns:
            Chronological list of contexts and events
        """
        with self.get_session() as session:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            query = """
            MATCH (p:Project {id: $project_id})
            MATCH (p)-[:CONTAINS|APPLIED_IN]-(item)
            WHERE item.created_at >= $cutoff_date
            RETURN item, labels(item) as item_type
            ORDER BY item.created_at DESC
            """
            
            result = session.run(query, project_id=project_id, cutoff_date=cutoff_date)
            timeline = []
            
            for record in result:
                item_data = dict(record["item"])
                item_data["item_type"] = record["item_type"][0]
                timeline.append(item_data)
            
            return timeline
    
    # Analytics and Metrics
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get overall system metrics and statistics"""
        with self.get_session() as session:
            queries = {
                "total_projects": "MATCH (p:Project) RETURN count(p) as count",
                "active_projects": "MATCH (p:Project {status: 'active'}) RETURN count(p) as count",
                "total_patterns": "MATCH (p:Pattern) RETURN count(p) as count",
                "total_decisions": "MATCH (d:Decision) RETURN count(d) as count",
                "successful_outcomes": "MATCH (o:Outcome {outcome_type: 'success'}) RETURN count(o) as count",
                "agent_types": "MATCH (a:Agent) RETURN a.type as type, count(*) as count ORDER BY count DESC",
                "popular_patterns": """
                    MATCH (p:Pattern)-[:APPLIED_IN]->()
                    RETURN p.name as pattern, count(*) as usage_count
                    ORDER BY usage_count DESC LIMIT 10
                """,
            }
            
            metrics = {}
            for metric_name, query in queries.items():
                try:
                    result = session.run(query)
                    if metric_name in ["agent_types", "popular_patterns"]:
                        metrics[metric_name] = [dict(record) for record in result]
                    else:
                        metrics[metric_name] = result.single()["count"]
                except Neo4jError as e:
                    logger.error(f"Failed to get metric {metric_name}: {e}")
                    metrics[metric_name] = None
            
            return metrics
    
    # Full-text Search
    
    def search_patterns(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Full-text search across patterns
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of matching patterns with relevance scores
        """
        with self.get_session() as session:
            search_query = """
            CALL db.index.fulltext.queryNodes('pattern_search_index', $query)
            YIELD node, score
            RETURN node, score
            ORDER BY score DESC
            LIMIT $limit
            """
            
            result = session.run(search_query, query=query, limit=limit)
            patterns = []
            
            for record in result:
                pattern_data = dict(record["node"])
                pattern_data["relevance_score"] = record["score"]
                patterns.append(pattern_data)
            
            return patterns
    
    def search_decisions(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Full-text search across decisions
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of matching decisions with relevance scores
        """
        with self.get_session() as session:
            search_query = """
            CALL db.index.fulltext.queryNodes('decision_search_index', $query)
            YIELD node, score
            RETURN node, score
            ORDER BY score DESC
            LIMIT $limit
            """
            
            result = session.run(search_query, query=query, limit=limit)
            decisions = []
            
            for record in result:
                decision_data = dict(record["node"])
                decision_data["relevance_score"] = record["score"]
                decisions.append(decision_data)
            
            return decisions