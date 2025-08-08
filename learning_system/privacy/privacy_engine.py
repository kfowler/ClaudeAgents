"""
Privacy-Preserving Learning Engine

Implements differential privacy, data isolation, and privacy-preserving
machine learning techniques for secure cross-project learning while
maintaining user privacy and data protection standards.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import hashlib
import json
import random
from abc import ABC, abstractmethod
import math
from collections import defaultdict

from ..knowledge_graph.graph_manager import GraphManager
from ..memory.memory_manager import MemoryManager
from ..learning.ml_pipeline import MLPipeline


logger = logging.getLogger(__name__)


class PrivacyLevel(Enum):
    """Privacy levels for data and projects"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class DataSensitivity(Enum):
    """Sensitivity levels for different data types"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PrivacyPolicy:
    """Privacy policy configuration"""
    policy_id: str
    name: str
    description: str
    privacy_level: PrivacyLevel
    data_sensitivity: DataSensitivity
    
    # Differential privacy parameters
    epsilon: float = 1.0  # Privacy budget
    delta: float = 1e-5   # Privacy parameter
    
    # Data retention
    retention_days: int = 365
    
    # Sharing permissions
    allow_cross_project_learning: bool = False
    allow_cross_team_learning: bool = False
    allow_external_sharing: bool = False
    
    # Anonymization requirements
    require_anonymization: bool = True
    require_pseudonymization: bool = False
    
    # Audit requirements
    require_audit_trail: bool = True
    require_consent_tracking: bool = True
    
    # Encryption requirements
    require_encryption_at_rest: bool = True
    require_encryption_in_transit: bool = True
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PrivacyBudget:
    """Privacy budget tracking for differential privacy"""
    entity_id: str  # Project, user, or team ID
    entity_type: str
    total_epsilon: float
    used_epsilon: float
    remaining_epsilon: float
    queries_count: int
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def consume_budget(self, epsilon: float) -> bool:
        """Consume privacy budget"""
        if self.remaining_epsilon >= epsilon:
            self.used_epsilon += epsilon
            self.remaining_epsilon -= epsilon
            self.queries_count += 1
            self.last_updated = datetime.utcnow()
            return True
        return False
    
    def reset_budget(self, new_total: Optional[float] = None):
        """Reset privacy budget"""
        if new_total:
            self.total_epsilon = new_total
        self.used_epsilon = 0.0
        self.remaining_epsilon = self.total_epsilon
        self.queries_count = 0
        self.last_updated = datetime.utcnow()


class DifferentialPrivacyMechanism(ABC):
    """Abstract base class for differential privacy mechanisms"""
    
    @abstractmethod
    def add_noise(self, data: Union[float, np.ndarray], sensitivity: float, epsilon: float) -> Union[float, np.ndarray]:
        """Add noise to data for differential privacy"""
        pass
    
    @abstractmethod
    def get_sensitivity(self, query_type: str, data_shape: Tuple[int, ...]) -> float:
        """Get sensitivity for query type"""
        pass


class LaplaceMechanism(DifferentialPrivacyMechanism):
    """Laplace mechanism for differential privacy"""
    
    def add_noise(self, data: Union[float, np.ndarray], sensitivity: float, epsilon: float) -> Union[float, np.ndarray]:
        """Add Laplace noise to data"""
        if epsilon <= 0:
            raise ValueError("Epsilon must be positive")
        
        scale = sensitivity / epsilon
        
        if isinstance(data, (int, float)):
            noise = np.random.laplace(0, scale)
            return float(data + noise)
        else:
            noise = np.random.laplace(0, scale, size=data.shape)
            return data + noise
    
    def get_sensitivity(self, query_type: str, data_shape: Tuple[int, ...]) -> float:
        """Get sensitivity based on query type"""
        if query_type == "count":
            return 1.0
        elif query_type == "sum":
            return 1.0  # Assuming bounded data
        elif query_type == "mean":
            n = data_shape[0] if data_shape else 1
            return 1.0 / n
        elif query_type == "histogram":
            return 1.0
        else:
            return 1.0  # Default conservative sensitivity


class GaussianMechanism(DifferentialPrivacyMechanism):
    """Gaussian mechanism for differential privacy"""
    
    def add_noise(self, data: Union[float, np.ndarray], sensitivity: float, epsilon: float, delta: float = 1e-5) -> Union[float, np.ndarray]:
        """Add Gaussian noise to data"""
        if epsilon <= 0 or delta <= 0:
            raise ValueError("Epsilon and delta must be positive")
        
        # Calculate sigma for Gaussian mechanism
        sigma = sensitivity * math.sqrt(2 * math.log(1.25 / delta)) / epsilon
        
        if isinstance(data, (int, float)):
            noise = np.random.normal(0, sigma)
            return float(data + noise)
        else:
            noise = np.random.normal(0, sigma, size=data.shape)
            return data + noise
    
    def get_sensitivity(self, query_type: str, data_shape: Tuple[int, ...]) -> float:
        """Get sensitivity based on query type"""
        # Same as Laplace for basic queries
        return LaplaceMechanism().get_sensitivity(query_type, data_shape)


class DataAnonymizer:
    """Data anonymization and pseudonymization utilities"""
    
    def __init__(self):
        self.salt = self._generate_salt()
        self.anonymization_cache: Dict[str, str] = {}
    
    def _generate_salt(self) -> str:
        """Generate random salt for hashing"""
        return hashlib.sha256(str(random.random()).encode()).hexdigest()[:16]
    
    def anonymize_identifier(self, identifier: str) -> str:
        """Anonymize an identifier using consistent hashing"""
        if identifier in self.anonymization_cache:
            return self.anonymization_cache[identifier]
        
        # Use HMAC-style hashing with salt
        combined = f"{identifier}:{self.salt}"
        hash_value = hashlib.sha256(combined.encode()).hexdigest()[:16]
        
        self.anonymization_cache[identifier] = hash_value
        return hash_value
    
    def pseudonymize_data(self, data: Dict[str, Any], sensitive_fields: Set[str]) -> Dict[str, Any]:
        """Pseudonymize sensitive fields in data"""
        pseudonymized = data.copy()
        
        for field in sensitive_fields:
            if field in pseudonymized and pseudonymized[field]:
                if isinstance(pseudonymized[field], str):
                    pseudonymized[field] = self.anonymize_identifier(pseudonymized[field])
                elif isinstance(pseudonymized[field], list):
                    pseudonymized[field] = [
                        self.anonymize_identifier(str(item)) if item else item
                        for item in pseudonymized[field]
                    ]
        
        return pseudonymized
    
    def k_anonymize(self, data: List[Dict[str, Any]], k: int = 3, quasi_identifiers: Optional[Set[str]] = None) -> List[Dict[str, Any]]:
        """Apply k-anonymity to dataset"""
        if not data or k <= 1:
            return data
        
        quasi_identifiers = quasi_identifiers or set()
        
        # Group records by quasi-identifier values
        groups = defaultdict(list)
        for record in data:
            key = tuple(record.get(qi, '') for qi in quasi_identifiers)
            groups[key].append(record)
        
        # Suppress records in groups smaller than k
        anonymized = []
        for group_records in groups.values():
            if len(group_records) >= k:
                anonymized.extend(group_records)
            else:
                # Suppress or generalize these records
                for record in group_records:
                    suppressed = record.copy()
                    for qi in quasi_identifiers:
                        suppressed[qi] = "*"  # Suppress value
                    anonymized.append(suppressed)
        
        return anonymized
    
    def l_diversify(self, data: List[Dict[str, Any]], l: int = 2, sensitive_attribute: str = 'outcome') -> List[Dict[str, Any]]:
        """Apply l-diversity to dataset"""
        if not data or l <= 1:
            return data
        
        # Group by quasi-identifiers (simplified)
        groups = defaultdict(list)
        for record in data:
            # Use a simple grouping key - in practice would use proper quasi-identifiers
            key = str(record.get('project_type', '')) + str(record.get('team_size', ''))
            groups[key].append(record)
        
        # Ensure l-diversity within each group
        diversified = []
        for group_records in groups.values():
            sensitive_values = [record.get(sensitive_attribute) for record in group_records]
            unique_values = len(set(sensitive_values))
            
            if unique_values >= l:
                diversified.extend(group_records)
            else:
                # Skip or modify records that don't meet l-diversity
                # In practice, would apply more sophisticated techniques
                continue
        
        return diversified


class PrivacyEngine:
    """
    Privacy-preserving learning engine with differential privacy,
    data isolation, and privacy-aware machine learning.
    """
    
    def __init__(
        self,
        graph_manager: GraphManager,
        memory_manager: MemoryManager,
        ml_pipeline: MLPipeline
    ):
        """
        Initialize privacy engine
        
        Args:
            graph_manager: Knowledge graph manager
            memory_manager: Memory manager
            ml_pipeline: ML pipeline
        """
        self.graph = graph_manager
        self.memory = memory_manager
        self.ml_pipeline = ml_pipeline
        
        # Privacy mechanisms
        self.dp_mechanisms = {
            'laplace': LaplaceMechanism(),
            'gaussian': GaussianMechanism()
        }
        
        # Data anonymizer
        self.anonymizer = DataAnonymizer()
        
        # Privacy policies and budgets
        self.policies: Dict[str, PrivacyPolicy] = {}
        self.privacy_budgets: Dict[str, PrivacyBudget] = {}
        
        # Access control
        self.access_permissions: Dict[str, Set[str]] = defaultdict(set)
        self.audit_log: List[Dict[str, Any]] = []
        
        self._load_default_policies()
    
    def _load_default_policies(self):
        """Load default privacy policies"""
        # Public policy - minimal restrictions
        public_policy = PrivacyPolicy(
            policy_id="public",
            name="Public Data Policy",
            description="For publicly shareable data",
            privacy_level=PrivacyLevel.PUBLIC,
            data_sensitivity=DataSensitivity.LOW,
            epsilon=10.0,  # High privacy budget
            allow_cross_project_learning=True,
            allow_cross_team_learning=True,
            require_anonymization=False
        )
        self.policies["public"] = public_policy
        
        # Internal policy - moderate restrictions
        internal_policy = PrivacyPolicy(
            policy_id="internal",
            name="Internal Data Policy",
            description="For internal team/company data",
            privacy_level=PrivacyLevel.INTERNAL,
            data_sensitivity=DataSensitivity.MEDIUM,
            epsilon=5.0,
            allow_cross_project_learning=True,
            allow_cross_team_learning=True,
            require_anonymization=True
        )
        self.policies["internal"] = internal_policy
        
        # Confidential policy - strict restrictions
        confidential_policy = PrivacyPolicy(
            policy_id="confidential",
            name="Confidential Data Policy",
            description="For confidential project data",
            privacy_level=PrivacyLevel.CONFIDENTIAL,
            data_sensitivity=DataSensitivity.HIGH,
            epsilon=1.0,  # Low privacy budget
            allow_cross_project_learning=False,
            allow_cross_team_learning=False,
            require_anonymization=True,
            require_pseudonymization=True
        )
        self.policies["confidential"] = confidential_policy
    
    # Privacy Policy Management
    
    def create_privacy_policy(
        self,
        policy_id: str,
        name: str,
        description: str,
        privacy_level: PrivacyLevel,
        data_sensitivity: DataSensitivity,
        **kwargs
    ) -> PrivacyPolicy:
        """Create a new privacy policy"""
        policy = PrivacyPolicy(
            policy_id=policy_id,
            name=name,
            description=description,
            privacy_level=privacy_level,
            data_sensitivity=data_sensitivity,
            **kwargs
        )
        
        self.policies[policy_id] = policy
        self._audit_log_event("privacy_policy_created", policy_id, {"policy": policy})
        
        return policy
    
    def get_privacy_policy(self, policy_id: str) -> Optional[PrivacyPolicy]:
        """Get privacy policy by ID"""
        return self.policies.get(policy_id)
    
    def assign_policy_to_entity(self, entity_id: str, entity_type: str, policy_id: str) -> bool:
        """Assign privacy policy to an entity (project, team, etc.)"""
        if policy_id not in self.policies:
            logger.error(f"Privacy policy {policy_id} not found")
            return False
        
        policy = self.policies[policy_id]
        
        # Initialize privacy budget for entity
        self.privacy_budgets[entity_id] = PrivacyBudget(
            entity_id=entity_id,
            entity_type=entity_type,
            total_epsilon=policy.epsilon,
            used_epsilon=0.0,
            remaining_epsilon=policy.epsilon,
            queries_count=0
        )
        
        self._audit_log_event(
            "privacy_policy_assigned", 
            entity_id, 
            {"entity_type": entity_type, "policy_id": policy_id}
        )
        
        return True
    
    # Differential Privacy
    
    def add_differential_privacy_noise(
        self,
        data: Union[float, np.ndarray, List[float]],
        entity_id: str,
        query_type: str = "general",
        mechanism: str = "laplace",
        epsilon: Optional[float] = None
    ) -> Optional[Union[float, np.ndarray]]:
        """
        Add differential privacy noise to data
        
        Args:
            data: Data to add noise to
            entity_id: Entity the data belongs to
            query_type: Type of query (count, sum, mean, etc.)
            mechanism: DP mechanism to use (laplace, gaussian)
            epsilon: Privacy budget to consume
            
        Returns:
            Noisy data or None if privacy budget exceeded
        """
        # Get privacy budget
        if entity_id not in self.privacy_budgets:
            logger.error(f"No privacy budget found for entity {entity_id}")
            return None
        
        budget = self.privacy_budgets[entity_id]
        
        # Use default epsilon if not provided
        if epsilon is None:
            epsilon = min(0.1, budget.remaining_epsilon)
        
        # Check if we can consume the budget
        if not budget.consume_budget(epsilon):
            logger.warning(f"Privacy budget exceeded for entity {entity_id}")
            self._audit_log_event(
                "privacy_budget_exceeded", 
                entity_id, 
                {"requested_epsilon": epsilon, "remaining": budget.remaining_epsilon}
            )
            return None
        
        # Convert data to numpy array if needed
        if isinstance(data, list):
            data = np.array(data)
        
        # Get appropriate mechanism
        dp_mechanism = self.dp_mechanisms.get(mechanism, self.dp_mechanisms['laplace'])
        
        # Calculate sensitivity
        data_shape = data.shape if hasattr(data, 'shape') else ()
        sensitivity = dp_mechanism.get_sensitivity(query_type, data_shape)
        
        # Add noise
        noisy_data = dp_mechanism.add_noise(data, sensitivity, epsilon)
        
        self._audit_log_event(
            "differential_privacy_applied",
            entity_id,
            {
                "query_type": query_type,
                "mechanism": mechanism,
                "epsilon": epsilon,
                "sensitivity": sensitivity,
                "budget_remaining": budget.remaining_epsilon
            }
        )
        
        return noisy_data
    
    def get_privacy_budget_status(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get privacy budget status for entity"""
        if entity_id not in self.privacy_budgets:
            return None
        
        budget = self.privacy_budgets[entity_id]
        return {
            'entity_id': entity_id,
            'entity_type': budget.entity_type,
            'total_epsilon': budget.total_epsilon,
            'used_epsilon': budget.used_epsilon,
            'remaining_epsilon': budget.remaining_epsilon,
            'utilization_rate': budget.used_epsilon / budget.total_epsilon if budget.total_epsilon > 0 else 0,
            'queries_count': budget.queries_count,
            'last_updated': budget.last_updated.isoformat()
        }
    
    # Data Anonymization
    
    def anonymize_dataset(
        self,
        data: List[Dict[str, Any]],
        entity_id: str,
        sensitive_fields: Optional[Set[str]] = None,
        apply_k_anonymity: bool = True,
        k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Anonymize a dataset according to privacy policy
        
        Args:
            data: Dataset to anonymize
            entity_id: Entity the data belongs to
            sensitive_fields: Fields to anonymize
            apply_k_anonymity: Whether to apply k-anonymity
            k: k value for k-anonymity
            
        Returns:
            Anonymized dataset
        """
        if not data:
            return data
        
        # Get privacy policy for entity
        policy = self._get_entity_policy(entity_id)
        if not policy:
            logger.warning(f"No privacy policy found for entity {entity_id}, using default")
            policy = self.policies["internal"]
        
        anonymized_data = data.copy()
        
        # Default sensitive fields
        if sensitive_fields is None:
            sensitive_fields = {
                'user_id', 'developer_id', 'team_id', 'email', 'name',
                'session_id', 'ip_address', 'location'
            }
        
        # Apply pseudonymization if required
        if policy.require_pseudonymization or policy.require_anonymization:
            anonymized_data = [
                self.anonymizer.pseudonymize_data(record, sensitive_fields)
                for record in anonymized_data
            ]
        
        # Apply k-anonymity if requested
        if apply_k_anonymity and k > 1:
            quasi_identifiers = {'project_type', 'team_size', 'domain'}
            anonymized_data = self.anonymizer.k_anonymize(
                anonymized_data, k, quasi_identifiers
            )
        
        self._audit_log_event(
            "data_anonymized",
            entity_id,
            {
                "records_count": len(data),
                "sensitive_fields": list(sensitive_fields),
                "k_anonymity": k if apply_k_anonymity else None,
                "policy_id": policy.policy_id
            }
        )
        
        return anonymized_data
    
    # Privacy-Preserving Learning
    
    def privacy_preserving_model_training(
        self,
        entity_id: str,
        training_data: List[Dict[str, Any]],
        model_type: str,
        allow_cross_entity_learning: bool = False
    ) -> Optional[Any]:
        """
        Train model with privacy preservation
        
        Args:
            entity_id: Entity training the model
            training_data: Training data
            model_type: Type of model to train
            allow_cross_entity_learning: Whether to allow cross-entity learning
            
        Returns:
            Trained model or None if privacy constraints violated
        """
        # Check privacy policy
        policy = self._get_entity_policy(entity_id)
        if not policy:
            logger.error(f"No privacy policy found for entity {entity_id}")
            return None
        
        # Check if cross-entity learning is allowed
        if allow_cross_entity_learning and not policy.allow_cross_project_learning:
            logger.warning(f"Cross-entity learning not allowed for entity {entity_id}")
            return None
        
        # Anonymize training data
        anonymized_data = self.anonymize_dataset(
            training_data,
            entity_id,
            apply_k_anonymity=True,
            k=3
        )
        
        if not anonymized_data:
            logger.error("No data available after anonymization")
            return None
        
        # Add differential privacy to training process
        # This is simplified - in practice would integrate with model training
        if policy.data_sensitivity in [DataSensitivity.HIGH, DataSensitivity.CRITICAL]:
            # Apply stronger privacy measures for sensitive data
            epsilon_budget = min(0.5, self.privacy_budgets.get(entity_id, PrivacyBudget("", "", 1.0, 0, 1.0, 0)).remaining_epsilon)
            
            # Add noise to aggregated statistics used in training
            # This is a simplified approach - real implementation would use
            # differentially private SGD or other DP-ML techniques
            pass
        
        self._audit_log_event(
            "privacy_preserving_training",
            entity_id,
            {
                "model_type": model_type,
                "training_records": len(anonymized_data),
                "cross_entity_learning": allow_cross_entity_learning,
                "policy_id": policy.policy_id
            }
        )
        
        # Note: Actual model training would be implemented here
        # using the anonymized data and privacy-preserving techniques
        return None  # Placeholder
    
    def federated_learning_aggregation(
        self,
        model_updates: Dict[str, Any],
        entity_ids: List[str],
        epsilon_per_entity: float = 0.1
    ) -> Optional[Dict[str, Any]]:
        """
        Aggregate model updates using differential privacy for federated learning
        
        Args:
            model_updates: Model updates from different entities
            entity_ids: Entity IDs providing updates
            epsilon_per_entity: Privacy budget per entity
            
        Returns:
            Aggregated model update with differential privacy
        """
        # Check privacy budgets for all entities
        for entity_id in entity_ids:
            if entity_id in self.privacy_budgets:
                budget = self.privacy_budgets[entity_id]
                if budget.remaining_epsilon < epsilon_per_entity:
                    logger.warning(f"Insufficient privacy budget for entity {entity_id}")
                    return None
        
        # Consume privacy budget from all entities
        for entity_id in entity_ids:
            if entity_id in self.privacy_budgets:
                self.privacy_budgets[entity_id].consume_budget(epsilon_per_entity)
        
        # Apply differential privacy to aggregation
        # This is a simplified implementation - real federated learning would be more complex
        aggregated_update = {}
        
        # For each parameter in the model update
        for param_name in model_updates:
            param_values = [update.get(param_name, 0) for update in model_updates.values()]
            
            # Calculate mean (could be sum or other aggregation)
            mean_value = np.mean(param_values)
            
            # Add differential privacy noise
            total_epsilon = epsilon_per_entity * len(entity_ids)
            sensitivity = 1.0 / len(entity_ids)  # Simplified sensitivity
            
            noisy_mean = self.dp_mechanisms['laplace'].add_noise(
                mean_value, sensitivity, total_epsilon
            )
            
            aggregated_update[param_name] = noisy_mean
        
        self._audit_log_event(
            "federated_learning_aggregation",
            "system",
            {
                "entities_count": len(entity_ids),
                "epsilon_per_entity": epsilon_per_entity,
                "total_epsilon": epsilon_per_entity * len(entity_ids)
            }
        )
        
        return aggregated_update
    
    # Access Control and Audit
    
    def check_data_access_permission(
        self,
        requesting_entity: str,
        data_owner_entity: str,
        data_type: str
    ) -> bool:
        """
        Check if entity has permission to access data
        
        Args:
            requesting_entity: Entity requesting access
            data_owner_entity: Entity that owns the data
            data_type: Type of data being accessed
            
        Returns:
            True if access is allowed
        """
        # Same entity can always access its own data
        if requesting_entity == data_owner_entity:
            return True
        
        # Check privacy policy of data owner
        owner_policy = self._get_entity_policy(data_owner_entity)
        if not owner_policy:
            return False
        
        # Check specific permissions
        permission_key = f"{data_owner_entity}:{data_type}"
        if requesting_entity in self.access_permissions.get(permission_key, set()):
            return True
        
        # Check policy-level permissions
        if data_type == "aggregated_stats" and owner_policy.allow_cross_project_learning:
            return True
        
        # Deny by default
        self._audit_log_event(
            "data_access_denied",
            requesting_entity,
            {
                "data_owner": data_owner_entity,
                "data_type": data_type,
                "reason": "insufficient_permissions"
            }
        )
        
        return False
    
    def grant_data_access_permission(
        self,
        data_owner_entity: str,
        requesting_entity: str,
        data_type: str
    ) -> bool:
        """Grant data access permission"""
        permission_key = f"{data_owner_entity}:{data_type}"
        self.access_permissions[permission_key].add(requesting_entity)
        
        self._audit_log_event(
            "data_access_granted",
            data_owner_entity,
            {
                "granted_to": requesting_entity,
                "data_type": data_type
            }
        )
        
        return True
    
    def revoke_data_access_permission(
        self,
        data_owner_entity: str,
        requesting_entity: str,
        data_type: str
    ) -> bool:
        """Revoke data access permission"""
        permission_key = f"{data_owner_entity}:{data_type}"
        if permission_key in self.access_permissions:
            self.access_permissions[permission_key].discard(requesting_entity)
        
        self._audit_log_event(
            "data_access_revoked",
            data_owner_entity,
            {
                "revoked_from": requesting_entity,
                "data_type": data_type
            }
        )
        
        return True
    
    def _get_entity_policy(self, entity_id: str) -> Optional[PrivacyPolicy]:
        """Get privacy policy for entity"""
        # In practice, this would query the graph to get the entity's policy
        # For now, return internal policy as default
        return self.policies.get("internal")
    
    def _audit_log_event(self, event_type: str, entity_id: str, details: Dict[str, Any]):
        """Log audit event"""
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'entity_id': entity_id,
            'details': details
        }
        
        self.audit_log.append(audit_entry)
        
        # Keep only recent audit logs in memory
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-5000:]  # Keep last 5000
    
    def get_audit_log(
        self,
        entity_id: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        filtered_log = []
        
        for entry in self.audit_log:
            # Apply filters
            if entity_id and entry.get('entity_id') != entity_id:
                continue
            
            if event_types and entry.get('event_type') not in event_types:
                continue
            
            entry_time = datetime.fromisoformat(entry['timestamp'])
            if start_time and entry_time < start_time:
                continue
            
            if end_time and entry_time > end_time:
                continue
            
            filtered_log.append(entry)
            
            if len(filtered_log) >= limit:
                break
        
        return filtered_log
    
    # Privacy Analytics
    
    def get_privacy_metrics(self) -> Dict[str, Any]:
        """Get privacy system metrics"""
        total_budgets = len(self.privacy_budgets)
        exhausted_budgets = sum(
            1 for budget in self.privacy_budgets.values()
            if budget.remaining_epsilon <= 0.01
        )
        
        budget_utilization = [
            budget.used_epsilon / budget.total_epsilon if budget.total_epsilon > 0 else 0
            for budget in self.privacy_budgets.values()
        ]
        
        avg_utilization = np.mean(budget_utilization) if budget_utilization else 0
        
        return {
            'privacy_policies': len(self.policies),
            'active_budgets': total_budgets,
            'exhausted_budgets': exhausted_budgets,
            'average_budget_utilization': avg_utilization,
            'total_audit_events': len(self.audit_log),
            'access_permissions': sum(len(perms) for perms in self.access_permissions.values()),
            'anonymization_cache_size': len(self.anonymizer.anonymization_cache)
        }
    
    def generate_privacy_report(self, entity_id: str) -> Dict[str, Any]:
        """Generate privacy compliance report for entity"""
        policy = self._get_entity_policy(entity_id)
        budget_status = self.get_privacy_budget_status(entity_id)
        audit_events = self.get_audit_log(entity_id=entity_id)
        
        return {
            'entity_id': entity_id,
            'privacy_policy': asdict(policy) if policy else None,
            'budget_status': budget_status,
            'audit_events_count': len(audit_events),
            'recent_audit_events': audit_events[:10],
            'compliance_status': self._assess_compliance(entity_id),
            'recommendations': self._generate_privacy_recommendations(entity_id)
        }
    
    def _assess_compliance(self, entity_id: str) -> Dict[str, bool]:
        """Assess privacy compliance for entity"""
        policy = self._get_entity_policy(entity_id)
        if not policy:
            return {'has_policy': False}
        
        budget = self.privacy_budgets.get(entity_id)
        audit_events = self.get_audit_log(entity_id=entity_id, limit=50)
        
        return {
            'has_policy': True,
            'has_privacy_budget': budget is not None,
            'budget_not_exhausted': budget and budget.remaining_epsilon > 0 if budget else False,
            'audit_trail_active': len(audit_events) > 0,
            'requires_anonymization': policy.require_anonymization,
            'anonymization_applied': any(
                event['event_type'] == 'data_anonymized' 
                for event in audit_events
            )
        }
    
    def _generate_privacy_recommendations(self, entity_id: str) -> List[str]:
        """Generate privacy recommendations for entity"""
        recommendations = []
        
        compliance = self._assess_compliance(entity_id)
        budget = self.privacy_budgets.get(entity_id)
        
        if not compliance.get('has_policy'):
            recommendations.append("Assign a privacy policy to this entity")
        
        if budget and budget.remaining_epsilon < 0.1:
            recommendations.append("Privacy budget is nearly exhausted - consider budget reset or reduction in queries")
        
        if not compliance.get('anonymization_applied'):
            recommendations.append("No data anonymization events found - ensure sensitive data is being anonymized")
        
        if not compliance.get('audit_trail_active'):
            recommendations.append("No recent audit events - verify audit logging is working correctly")
        
        return recommendations