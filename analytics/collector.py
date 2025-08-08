"""
Agent Usage Analytics Data Collection Interface

This module provides a non-intrusive way to collect agent usage analytics
for optimizing recommendations and tracking effectiveness.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from contextlib import asynccontextmanager
import asyncio
import logging
from pathlib import Path

try:
    import asyncpg
    import aioredis
except ImportError:
    # Graceful degradation for environments without async dependencies
    asyncpg = None
    aioredis = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProjectContext:
    """Captures project context for agent selection optimization"""
    tech_stack: List[str] = field(default_factory=list)
    file_types: List[str] = field(default_factory=list)
    project_size: str = "unknown"  # small, medium, large, enterprise
    domain: str = "unknown"  # web, mobile, ai_ml, security, devops, data
    complexity_indicators: Dict[str, Any] = field(default_factory=dict)
    git_repo: bool = False
    has_tests: bool = False
    has_docs: bool = False
    deployment_config: List[str] = field(default_factory=list)

@dataclass
class UserRequest:
    """Standardized user request structure"""
    text: str
    intent_type: str = "unknown"  # implementation, review, debug, optimization
    confidence: float = 0.0
    tech_keywords: List[str] = field(default_factory=list)
    complexity_score: float = 0.0
    urgency: str = "normal"  # low, normal, high, critical

@dataclass
class AgentInvocation:
    """Tracks individual agent usage"""
    invocation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    agent_name: str = ""
    invocation_reason: str = ""  # automatic, user_selected, recommended, fallback
    user_request: UserRequest = field(default_factory=lambda: UserRequest(""))
    context_match_score: float = 0.0
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    tokens_used: int = 0
    success_status: str = "pending"  # success, partial, failed, cancelled
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    files_modified: int = 0
    lines_added: int = 0
    lines_removed: int = 0
    quality_score: Optional[float] = None

@dataclass
class AgentSession:
    """Tracks complete user sessions with agents"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    project_context: ProjectContext = field(default_factory=ProjectContext)
    session_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    session_end: Optional[datetime] = None
    total_duration_seconds: Optional[int] = None
    final_outcome: str = "in_progress"  # completed, abandoned, error, timeout
    user_satisfaction_score: Optional[int] = None
    invocations: List[AgentInvocation] = field(default_factory=list)

class AnalyticsCollector:
    """
    Main analytics collection interface with multiple storage backends
    """
    
    def __init__(self, 
                 db_url: Optional[str] = None,
                 redis_url: Optional[str] = None,
                 local_storage_path: Optional[str] = None,
                 buffer_size: int = 100,
                 flush_interval: int = 60):
        """
        Initialize the analytics collector
        
        Args:
            db_url: PostgreSQL connection URL (optional)
            redis_url: Redis connection URL for caching (optional)
            local_storage_path: Path for local file storage fallback
            buffer_size: Number of events to buffer before flushing
            flush_interval: Seconds between automatic flushes
        """
        self.db_url = db_url
        self.redis_url = redis_url
        self.local_storage_path = Path(local_storage_path) if local_storage_path else Path.cwd() / "analytics_data"
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        
        # In-memory buffers for batch processing
        self.session_buffer = []
        self.invocation_buffer = []
        self.feedback_buffer = []
        
        # Connection pools
        self.db_pool = None
        self.redis_pool = None
        
        # Background tasks
        self._flush_task = None
        self._running = False
        
        # Ensure local storage directory exists
        self.local_storage_path.mkdir(exist_ok=True)
    
    async def initialize(self):
        """Initialize database connections and background tasks"""
        try:
            if self.db_url and asyncpg:
                self.db_pool = await asyncpg.create_pool(self.db_url, min_size=2, max_size=10)
                logger.info("Database connection pool initialized")
            
            if self.redis_url and aioredis:
                self.redis_pool = await aioredis.from_url(self.redis_url)
                logger.info("Redis connection initialized")
            
            # Start background flush task
            self._running = True
            self._flush_task = asyncio.create_task(self._periodic_flush())
            
        except Exception as e:
            logger.warning(f"Failed to initialize some analytics backends: {e}")
            logger.info("Falling back to local storage only")
    
    async def shutdown(self):
        """Clean shutdown of analytics collector"""
        self._running = False
        
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        # Flush remaining data
        await self.flush_all()
        
        # Close connections
        if self.db_pool:
            await self.db_pool.close()
        if self.redis_pool:
            await self.redis_pool.close()
    
    def detect_project_context(self, project_path: str = ".") -> ProjectContext:
        """
        Analyze project directory to extract context
        """
        path = Path(project_path)
        context = ProjectContext()
        
        # Detect tech stack from common files
        tech_indicators = {
            "package.json": ["nodejs", "javascript"],
            "Cargo.toml": ["rust"],
            "requirements.txt": ["python"],
            "pyproject.toml": ["python"],
            "go.mod": ["golang"],
            "pom.xml": ["java", "maven"],
            "build.gradle": ["java", "kotlin", "gradle"],
            "Gemfile": ["ruby"],
            "composer.json": ["php"],
            "pubspec.yaml": ["dart", "flutter"],
            "Package.swift": ["swift"],
            "Podfile": ["ios", "swift", "objective-c"]
        }
        
        for file, techs in tech_indicators.items():
            if (path / file).exists():
                context.tech_stack.extend(techs)
        
        # Detect file types
        file_types = set()
        for ext in [".py", ".js", ".ts", ".rs", ".go", ".java", ".swift", ".rb", ".php", ".dart"]:
            if list(path.rglob(f"*{ext}")):
                file_types.add(ext[1:])  # Remove leading dot
        context.file_types = list(file_types)
        
        # Detect project characteristics
        context.git_repo = (path / ".git").exists()
        context.has_tests = bool(list(path.rglob("*test*"))) or bool(list(path.rglob("*spec*")))
        context.has_docs = (path / "README.md").exists() or bool(list(path.rglob("docs/*")))
        
        # Estimate project size
        total_files = len(list(path.rglob("*.py"))) + len(list(path.rglob("*.js"))) + len(list(path.rglob("*.ts")))
        if total_files < 10:
            context.project_size = "small"
        elif total_files < 100:
            context.project_size = "medium"
        elif total_files < 1000:
            context.project_size = "large"
        else:
            context.project_size = "enterprise"
        
        # Detect deployment configurations
        deployment_files = [
            "Dockerfile", "docker-compose.yml", "k8s", "kubernetes",
            ".github/workflows", ".gitlab-ci.yml", "Procfile", "serverless.yml"
        ]
        for file in deployment_files:
            if (path / file).exists():
                context.deployment_config.append(file)
        
        return context
    
    def classify_user_request(self, request_text: str, project_context: ProjectContext) -> UserRequest:
        """
        Analyze user request to extract intent and metadata
        """
        request = UserRequest(text=request_text)
        
        # Simple keyword-based intent detection
        intent_patterns = {
            "implementation": ["create", "build", "implement", "add", "develop", "code"],
            "review": ["review", "audit", "check", "analyze", "evaluate"],
            "debug": ["debug", "fix", "error", "bug", "issue", "problem"],
            "optimization": ["optimize", "improve", "performance", "speed", "memory"],
            "testing": ["test", "spec", "coverage", "unit test", "integration"],
            "security": ["security", "auth", "permission", "vulnerability", "encrypt"],
            "deployment": ["deploy", "ci/cd", "docker", "kubernetes", "production"]
        }
        
        text_lower = request_text.lower()
        for intent, keywords in intent_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                request.intent_type = intent
                break
        
        # Extract technology keywords
        all_techs = set(project_context.tech_stack + project_context.file_types)
        request.tech_keywords = [tech for tech in all_techs if tech.lower() in text_lower]
        
        # Simple complexity scoring
        complexity_indicators = [
            "multiple", "complex", "enterprise", "scalable", "distributed",
            "microservices", "architecture", "system", "framework"
        ]
        request.complexity_score = sum(1 for indicator in complexity_indicators if indicator in text_lower) / len(complexity_indicators)
        
        return request
    
    async def start_session(self, user_id: str, project_path: str = ".") -> AgentSession:
        """Start a new agent session"""
        project_context = self.detect_project_context(project_path)
        session = AgentSession(user_id=user_id, project_context=project_context)
        
        # Cache session for immediate use
        if self.redis_pool:
            try:
                await self.redis_pool.setex(
                    f"session:{session.session_id}",
                    3600,  # 1 hour TTL
                    json.dumps(asdict(session), default=str)
                )
            except Exception as e:
                logger.warning(f"Failed to cache session: {e}")
        
        return session
    
    async def record_invocation(self, 
                              session_id: str,
                              agent_name: str,
                              user_request_text: str,
                              invocation_reason: str = "automatic",
                              context_match_score: float = 0.0) -> AgentInvocation:
        """Record the start of an agent invocation"""
        
        # Get project context from session
        project_context = ProjectContext()  # Default fallback
        if self.redis_pool:
            try:
                session_data = await self.redis_pool.get(f"session:{session_id}")
                if session_data:
                    session_dict = json.loads(session_data)
                    project_context = ProjectContext(**session_dict.get("project_context", {}))
            except Exception as e:
                logger.warning(f"Failed to retrieve session context: {e}")
        
        user_request = self.classify_user_request(user_request_text, project_context)
        
        invocation = AgentInvocation(
            session_id=session_id,
            agent_name=agent_name,
            invocation_reason=invocation_reason,
            user_request=user_request,
            context_match_score=context_match_score
        )
        
        self.invocation_buffer.append(invocation)
        await self._maybe_flush()
        
        return invocation
    
    async def complete_invocation(self,
                                invocation_id: str,
                                success_status: str,
                                tokens_used: int = 0,
                                files_modified: int = 0,
                                lines_added: int = 0,
                                lines_removed: int = 0,
                                quality_score: Optional[float] = None,
                                error_type: Optional[str] = None,
                                error_message: Optional[str] = None):
        """Mark an invocation as complete and record metrics"""
        
        # Find invocation in buffer
        for invocation in self.invocation_buffer:
            if invocation.invocation_id == invocation_id:
                invocation.end_time = datetime.now(timezone.utc)
                invocation.duration_seconds = int((invocation.end_time - invocation.start_time).total_seconds())
                invocation.success_status = success_status
                invocation.tokens_used = tokens_used
                invocation.files_modified = files_modified
                invocation.lines_added = lines_added
                invocation.lines_removed = lines_removed
                invocation.quality_score = quality_score
                invocation.error_type = error_type
                invocation.error_message = error_message
                break
        
        await self._maybe_flush()
    
    async def record_feedback(self,
                            session_id: Optional[str] = None,
                            invocation_id: Optional[str] = None,
                            feedback_type: str = "explicit_rating",
                            rating: Optional[int] = None,
                            feedback_text: Optional[str] = None,
                            suggested_agent: Optional[str] = None,
                            user_correction: Optional[Dict] = None):
        """Record user feedback"""
        
        feedback = {
            "feedback_id": str(uuid.uuid4()),
            "session_id": session_id,
            "invocation_id": invocation_id,
            "feedback_type": feedback_type,
            "rating": rating,
            "feedback_text": feedback_text,
            "suggested_agent": suggested_agent,
            "user_correction": user_correction,
            "timestamp": datetime.now(timezone.utc)
        }
        
        self.feedback_buffer.append(feedback)
        await self._maybe_flush()
    
    async def end_session(self,
                        session_id: str,
                        final_outcome: str = "completed",
                        user_satisfaction_score: Optional[int] = None):
        """End an agent session"""
        
        # Find session in buffer or create completion record
        session_completion = {
            "session_id": session_id,
            "session_end": datetime.now(timezone.utc),
            "final_outcome": final_outcome,
            "user_satisfaction_score": user_satisfaction_score
        }
        
        self.session_buffer.append(session_completion)
        await self._maybe_flush()
    
    async def _maybe_flush(self):
        """Flush buffers if they exceed threshold"""
        total_items = len(self.session_buffer) + len(self.invocation_buffer) + len(self.feedback_buffer)
        if total_items >= self.buffer_size:
            await self.flush_all()
    
    async def _periodic_flush(self):
        """Background task for periodic flushing"""
        while self._running:
            try:
                await asyncio.sleep(self.flush_interval)
                if not self._running:
                    break
                await self.flush_all()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic flush: {e}")
    
    async def flush_all(self):
        """Flush all buffered data to storage backends"""
        if not any([self.session_buffer, self.invocation_buffer, self.feedback_buffer]):
            return
        
        try:
            # Try database first
            if self.db_pool:
                await self._flush_to_database()
            else:
                # Fallback to local storage
                await self._flush_to_local_storage()
                
        except Exception as e:
            logger.error(f"Failed to flush to primary storage, using local fallback: {e}")
            await self._flush_to_local_storage()
        
        # Clear buffers after successful flush
        self.session_buffer.clear()
        self.invocation_buffer.clear()
        self.feedback_buffer.clear()
    
    async def _flush_to_database(self):
        """Flush data to PostgreSQL database"""
        if not self.db_pool:
            return
        
        async with self.db_pool.acquire() as conn:
            # Flush sessions
            if self.session_buffer:
                session_data = [
                    (
                        item["session_id"],
                        item.get("session_end"),
                        item.get("final_outcome"),
                        item.get("user_satisfaction_score")
                    )
                    for item in self.session_buffer
                ]
                await conn.executemany(
                    """UPDATE agent_sessions SET 
                       session_end = $2, 
                       final_outcome = $3, 
                       user_satisfaction_score = $4,
                       total_duration_seconds = EXTRACT(EPOCH FROM (session_end - session_start)),
                       updated_at = NOW()
                       WHERE session_id = $1""",
                    session_data
                )
            
            # Flush invocations
            if self.invocation_buffer:
                invocation_data = [
                    (
                        inv.invocation_id, inv.session_id, inv.agent_name,
                        inv.invocation_reason, inv.user_request.text,
                        inv.context_match_score, inv.start_time, inv.end_time,
                        inv.duration_seconds, inv.tokens_used, inv.success_status,
                        inv.error_type, inv.error_message, inv.files_modified,
                        inv.lines_added, inv.lines_removed, inv.quality_score
                    )
                    for inv in self.invocation_buffer
                ]
                await conn.executemany(
                    """INSERT INTO agent_invocations (
                        invocation_id, session_id, agent_name, invocation_reason,
                        user_request, context_match_score, start_time, end_time,
                        duration_seconds, tokens_used, success_status,
                        error_type, error_message, files_modified,
                        lines_added, lines_removed, quality_score
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                    ON CONFLICT (invocation_id) DO UPDATE SET
                        end_time = EXCLUDED.end_time,
                        duration_seconds = EXCLUDED.duration_seconds,
                        success_status = EXCLUDED.success_status,
                        tokens_used = EXCLUDED.tokens_used,
                        files_modified = EXCLUDED.files_modified,
                        lines_added = EXCLUDED.lines_added,
                        lines_removed = EXCLUDED.lines_removed,
                        quality_score = EXCLUDED.quality_score,
                        error_type = EXCLUDED.error_type,
                        error_message = EXCLUDED.error_message""",
                    invocation_data
                )
            
            # Flush feedback
            if self.feedback_buffer:
                feedback_data = [
                    (
                        item["feedback_id"], item["session_id"], item["invocation_id"],
                        item["feedback_type"], item["rating"], item["feedback_text"],
                        item["suggested_agent"], json.dumps(item["user_correction"]) if item["user_correction"] else None,
                        item["timestamp"]
                    )
                    for item in self.feedback_buffer
                ]
                await conn.executemany(
                    """INSERT INTO user_feedback (
                        feedback_id, session_id, invocation_id, feedback_type,
                        rating, feedback_text, suggested_agent, user_correction, timestamp
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)""",
                    feedback_data
                )
    
    async def _flush_to_local_storage(self):
        """Fallback: flush data to local JSON files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.session_buffer:
            with open(self.local_storage_path / f"sessions_{timestamp}.json", "w") as f:
                json.dump(self.session_buffer, f, default=str, indent=2)
        
        if self.invocation_buffer:
            invocation_data = [asdict(inv) for inv in self.invocation_buffer]
            with open(self.local_storage_path / f"invocations_{timestamp}.json", "w") as f:
                json.dump(invocation_data, f, default=str, indent=2)
        
        if self.feedback_buffer:
            with open(self.local_storage_path / f"feedback_{timestamp}.json", "w") as f:
                json.dump(self.feedback_buffer, f, default=str, indent=2)

# Singleton instance for easy access
analytics = AnalyticsCollector()

@asynccontextmanager
async def analytics_session(user_id: str, project_path: str = "."):
    """Async context manager for agent sessions"""
    session = await analytics.start_session(user_id, project_path)
    try:
        yield session
    except Exception as e:
        await analytics.end_session(session.session_id, "error")
        raise
    else:
        await analytics.end_session(session.session_id, "completed")

# Convenience functions for common operations
async def track_agent_use(session_id: str, agent_name: str, request: str, **kwargs):
    """Simple function to track agent usage"""
    return await analytics.record_invocation(session_id, agent_name, request, **kwargs)

async def record_user_rating(invocation_id: str, rating: int, feedback: str = ""):
    """Simple function to record user satisfaction"""
    await analytics.record_feedback(
        invocation_id=invocation_id,
        feedback_type="explicit_rating",
        rating=rating,
        feedback_text=feedback
    )