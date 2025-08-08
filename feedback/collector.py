#!/usr/bin/env python3
"""
User Feedback Collection System for Claude Code Enhancement Rollout.
Comprehensive feedback collection, analysis, and reporting capabilities.
"""

import asyncio
import json
import logging
import time
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import hashlib
import uuid
import re


class FeedbackType(Enum):
    """Types of feedback."""
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    USER_EXPERIENCE = "user_experience"
    PERFORMANCE = "performance"
    GENERAL = "general"
    SURVEY_RESPONSE = "survey_response"


class FeedbackSentiment(Enum):
    """Sentiment analysis results."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class FeedbackPriority(Enum):
    """Feedback priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class FeedbackEntry:
    """Individual feedback entry."""
    id: str
    user_id: str
    type: FeedbackType
    title: str
    content: str
    sentiment: FeedbackSentiment
    priority: FeedbackPriority
    rating: Optional[int]  # 1-5 scale
    timestamp: str
    resolved: bool = False
    resolved_timestamp: Optional[str] = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class SurveyResponse:
    """Survey response data."""
    id: str
    survey_id: str
    user_id: str
    responses: Dict[str, Any]
    completion_time: float  # seconds
    timestamp: str
    metadata: Dict[str, Any] = None


@dataclass
class UsageMetric:
    """User usage analytics metric."""
    user_id: str
    action: str
    feature: str
    duration: Optional[float]
    success: bool
    timestamp: str
    metadata: Dict[str, Any] = None


class SentimentAnalyzer:
    """Basic sentiment analysis for feedback."""
    
    def __init__(self):
        self.positive_keywords = [
            'good', 'great', 'excellent', 'amazing', 'love', 'like', 'helpful',
            'useful', 'easy', 'intuitive', 'fast', 'efficient', 'awesome',
            'fantastic', 'brilliant', 'perfect', 'wonderful', 'impressed'
        ]
        
        self.negative_keywords = [
            'bad', 'terrible', 'awful', 'hate', 'dislike', 'broken', 'bug',
            'error', 'slow', 'confusing', 'difficult', 'frustrating', 'annoying',
            'useless', 'horrible', 'disappointing', 'poor', 'worst'
        ]
        
    def analyze_sentiment(self, text: str) -> FeedbackSentiment:
        """Analyze sentiment of text."""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.positive_keywords if word in text_lower)
        negative_count = sum(1 for word in self.negative_keywords if word in text_lower)
        
        if positive_count > negative_count * 1.5:
            return FeedbackSentiment.POSITIVE
        elif negative_count > positive_count * 1.5:
            return FeedbackSentiment.NEGATIVE
        elif positive_count > 0 and negative_count > 0:
            return FeedbackSentiment.MIXED
        else:
            return FeedbackSentiment.NEUTRAL
            
    def get_confidence_score(self, text: str) -> float:
        """Get confidence score for sentiment analysis."""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.positive_keywords if word in text_lower)
        negative_count = sum(1 for word in self.negative_keywords if word in text_lower)
        
        total_indicators = positive_count + negative_count
        if total_indicators == 0:
            return 0.5  # Neutral confidence
            
        # Higher difference = higher confidence
        difference = abs(positive_count - negative_count)
        return min(0.9, 0.5 + (difference / (total_indicators * 2)))


class FeedbackDatabase:
    """Database manager for feedback data."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize feedback database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Feedback entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                priority TEXT NOT NULL,
                rating INTEGER,
                timestamp TEXT NOT NULL,
                resolved INTEGER DEFAULT 0,
                resolved_timestamp TEXT,
                tags TEXT,
                metadata TEXT
            )
        """)
        
        # Survey responses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS survey_responses (
                id TEXT PRIMARY KEY,
                survey_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                responses TEXT NOT NULL,
                completion_time REAL,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        # Usage metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_metrics (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                feature TEXT NOT NULL,
                duration REAL,
                success INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON feedback(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_sentiment ON feedback(sentiment)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_survey_survey_id ON survey_responses(survey_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_user_id ON usage_metrics(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_feature ON usage_metrics(feature)")
        
        conn.commit()
        conn.close()
        
    def store_feedback(self, feedback: FeedbackEntry):
        """Store feedback entry."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        tags_json = json.dumps(feedback.tags) if feedback.tags else None
        metadata_json = json.dumps(feedback.metadata) if feedback.metadata else None
        
        cursor.execute("""
            INSERT OR REPLACE INTO feedback 
            (id, user_id, type, title, content, sentiment, priority, rating, 
             timestamp, resolved, resolved_timestamp, tags, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            feedback.id, feedback.user_id, feedback.type.value, feedback.title,
            feedback.content, feedback.sentiment.value, feedback.priority.value,
            feedback.rating, feedback.timestamp, int(feedback.resolved),
            feedback.resolved_timestamp, tags_json, metadata_json
        ))
        
        conn.commit()
        conn.close()
        
    def store_survey_response(self, response: SurveyResponse):
        """Store survey response."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        responses_json = json.dumps(response.responses)
        metadata_json = json.dumps(response.metadata) if response.metadata else None
        
        cursor.execute("""
            INSERT OR REPLACE INTO survey_responses 
            (id, survey_id, user_id, responses, completion_time, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            response.id, response.survey_id, response.user_id, responses_json,
            response.completion_time, response.timestamp, metadata_json
        ))
        
        conn.commit()
        conn.close()
        
    def store_usage_metric(self, metric: UsageMetric):
        """Store usage metric."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        metric_id = str(uuid.uuid4())
        metadata_json = json.dumps(metric.metadata) if metric.metadata else None
        
        cursor.execute("""
            INSERT INTO usage_metrics 
            (id, user_id, action, feature, duration, success, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metric_id, metric.user_id, metric.action, metric.feature,
            metric.duration, int(metric.success), metric.timestamp, metadata_json
        ))
        
        conn.commit()
        conn.close()
        
    def get_feedback(self, limit: int = 100, filters: Dict[str, Any] = None) -> List[FeedbackEntry]:
        """Get feedback entries with optional filters."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = """
            SELECT id, user_id, type, title, content, sentiment, priority, rating,
                   timestamp, resolved, resolved_timestamp, tags, metadata
            FROM feedback
        """
        
        params = []
        if filters:
            conditions = []
            if 'type' in filters:
                conditions.append("type = ?")
                params.append(filters['type'])
            if 'sentiment' in filters:
                conditions.append("sentiment = ?")
                params.append(filters['sentiment'])
            if 'resolved' in filters:
                conditions.append("resolved = ?")
                params.append(int(filters['resolved']))
            if 'since' in filters:
                conditions.append("timestamp >= ?")
                params.append(filters['since'])
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        feedback_entries = []
        for row in rows:
            tags = json.loads(row[11]) if row[11] else None
            metadata = json.loads(row[12]) if row[12] else None
            
            feedback_entries.append(FeedbackEntry(
                id=row[0],
                user_id=row[1],
                type=FeedbackType(row[2]),
                title=row[3],
                content=row[4],
                sentiment=FeedbackSentiment(row[5]),
                priority=FeedbackPriority(row[6]),
                rating=row[7],
                timestamp=row[8],
                resolved=bool(row[9]),
                resolved_timestamp=row[10],
                tags=tags,
                metadata=metadata
            ))
            
        return feedback_entries


class FeedbackCollector:
    """Main feedback collection orchestrator."""
    
    def __init__(self, data_dir: Path = Path("feedback/data")):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.data_dir / "feedback.db"
        self.database = FeedbackDatabase(self.db_path)
        self.sentiment_analyzer = SentimentAnalyzer()
        
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging for feedback system."""
        log_dir = self.data_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'feedback.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def generate_user_id(self, identifier: Optional[str] = None) -> str:
        """Generate anonymous user ID."""
        if identifier:
            # Create consistent hash for same identifier
            return hashlib.sha256(identifier.encode()).hexdigest()[:16]
        else:
            # Generate random ID
            return str(uuid.uuid4())[:8]
            
    def collect_feedback(self, 
                        user_id: str,
                        feedback_type: FeedbackType,
                        title: str,
                        content: str,
                        rating: Optional[int] = None,
                        tags: List[str] = None,
                        metadata: Dict[str, Any] = None) -> FeedbackEntry:
        """Collect user feedback."""
        
        # Analyze sentiment
        sentiment = self.sentiment_analyzer.analyze_sentiment(content)
        
        # Determine priority based on type and sentiment
        priority = self._determine_priority(feedback_type, sentiment, rating)
        
        # Create feedback entry
        feedback = FeedbackEntry(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type=feedback_type,
            title=title,
            content=content,
            sentiment=sentiment,
            priority=priority,
            rating=rating,
            timestamp=datetime.now().isoformat(),
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Store feedback
        self.database.store_feedback(feedback)
        
        self.logger.info(f"Collected {feedback_type.value} feedback from user {user_id[:8]}...")
        
        return feedback
        
    def collect_survey_response(self,
                              survey_id: str,
                              user_id: str,
                              responses: Dict[str, Any],
                              completion_time: float,
                              metadata: Dict[str, Any] = None) -> SurveyResponse:
        """Collect survey response."""
        
        response = SurveyResponse(
            id=str(uuid.uuid4()),
            survey_id=survey_id,
            user_id=user_id,
            responses=responses,
            completion_time=completion_time,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        self.database.store_survey_response(response)
        
        self.logger.info(f"Collected survey response for {survey_id} from user {user_id[:8]}...")
        
        return response
        
    def track_usage(self,
                   user_id: str,
                   action: str,
                   feature: str,
                   duration: Optional[float] = None,
                   success: bool = True,
                   metadata: Dict[str, Any] = None) -> UsageMetric:
        """Track user usage metrics."""
        
        metric = UsageMetric(
            user_id=user_id,
            action=action,
            feature=feature,
            duration=duration,
            success=success,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        self.database.store_usage_metric(metric)
        
        return metric
        
    def _determine_priority(self, 
                          feedback_type: FeedbackType,
                          sentiment: FeedbackSentiment,
                          rating: Optional[int]) -> FeedbackPriority:
        """Determine feedback priority based on type, sentiment, and rating."""
        
        # Bug reports are generally high priority
        if feedback_type == FeedbackType.BUG_REPORT:
            if sentiment == FeedbackSentiment.NEGATIVE:
                return FeedbackPriority.CRITICAL
            else:
                return FeedbackPriority.HIGH
                
        # Performance issues are important
        if feedback_type == FeedbackType.PERFORMANCE:
            if sentiment == FeedbackSentiment.NEGATIVE or (rating and rating <= 2):
                return FeedbackPriority.HIGH
            else:
                return FeedbackPriority.MEDIUM
                
        # Rating-based priority
        if rating:
            if rating <= 2:
                return FeedbackPriority.HIGH
            elif rating <= 3:
                return FeedbackPriority.MEDIUM
            else:
                return FeedbackPriority.LOW
                
        # Sentiment-based priority
        if sentiment == FeedbackSentiment.NEGATIVE:
            return FeedbackPriority.MEDIUM
        elif sentiment == FeedbackSentiment.POSITIVE:
            return FeedbackPriority.LOW
        else:
            return FeedbackPriority.MEDIUM
            
    def create_sample_feedback(self) -> List[FeedbackEntry]:
        """Create sample feedback for testing."""
        sample_feedback = [
            {
                "type": FeedbackType.USER_EXPERIENCE,
                "title": "Love the new agent recommendation system",
                "content": "The new agent recommendations are fantastic! They're much more accurate and save me a lot of time finding the right specialist for my projects.",
                "rating": 5,
                "tags": ["agent-recommendation", "positive"]
            },
            {
                "type": FeedbackType.BUG_REPORT,
                "title": "Error when loading project analysis",
                "content": "I keep getting an error message when trying to load project analysis. It says 'Database connection failed' and then crashes.",
                "rating": 1,
                "tags": ["project-analysis", "database", "error"]
            },
            {
                "type": FeedbackType.FEATURE_REQUEST,
                "title": "Add dark mode support",
                "content": "Would be great to have dark mode support for the dashboard. Working late hours and the bright interface is hard on the eyes.",
                "rating": 4,
                "tags": ["ui", "dark-mode", "accessibility"]
            },
            {
                "type": FeedbackType.PERFORMANCE,
                "title": "Agent selection is slow",
                "content": "The agent selection process takes too long, especially when analyzing large projects. Sometimes it takes over 30 seconds to get recommendations.",
                "rating": 2,
                "tags": ["performance", "agent-selection", "speed"]
            },
            {
                "type": FeedbackType.GENERAL,
                "title": "Great improvement overall",
                "content": "The recent updates have made the system much more user-friendly. The workflow orchestration is particularly helpful for complex projects.",
                "rating": 5,
                "tags": ["workflow", "user-friendly", "improvement"]
            }
        ]
        
        feedback_entries = []
        for i, fb_data in enumerate(sample_feedback):
            user_id = self.generate_user_id(f"sample_user_{i}")
            
            feedback = self.collect_feedback(
                user_id=user_id,
                feedback_type=fb_data["type"],
                title=fb_data["title"],
                content=fb_data["content"],
                rating=fb_data["rating"],
                tags=fb_data["tags"]
            )
            feedback_entries.append(feedback)
            
        return feedback_entries
        
    def get_feedback_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get feedback summary for specified days."""
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        feedback_entries = self.database.get_feedback(
            limit=1000,
            filters={"since": since_date}
        )
        
        # Categorize feedback
        by_type = {}
        by_sentiment = {}
        by_priority = {}
        ratings = []
        
        for feedback in feedback_entries:
            # By type
            type_key = feedback.type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1
            
            # By sentiment
            sentiment_key = feedback.sentiment.value
            by_sentiment[sentiment_key] = by_sentiment.get(sentiment_key, 0) + 1
            
            # By priority
            priority_key = feedback.priority.value
            by_priority[priority_key] = by_priority.get(priority_key, 0) + 1
            
            # Ratings
            if feedback.rating:
                ratings.append(feedback.rating)
                
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        return {
            "total_feedback": len(feedback_entries),
            "period_days": days,
            "by_type": by_type,
            "by_sentiment": by_sentiment,
            "by_priority": by_priority,
            "average_rating": round(avg_rating, 2),
            "ratings_count": len(ratings),
            "timestamp": datetime.now().isoformat()
        }
        
    def simulate_user_interaction(self, user_id: str, action: str) -> None:
        """Simulate user interaction for testing."""
        interactions = {
            "agent_recommendation": {
                "feature": "agent-selection",
                "duration": 2.5,
                "success": True
            },
            "project_analysis": {
                "feature": "project-analysis",
                "duration": 8.3,
                "success": True
            },
            "workflow_execution": {
                "feature": "workflow-orchestration",
                "duration": 15.7,
                "success": True
            },
            "dashboard_view": {
                "feature": "dashboard",
                "duration": 45.2,
                "success": True
            }
        }
        
        if action in interactions:
            self.track_usage(
                user_id=user_id,
                action=action,
                **interactions[action]
            )


def main():
    """Main entry point for feedback collector."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Code Enhancement Feedback Collector")
    parser.add_argument("--start", action="store_true", help="Start feedback collection")
    parser.add_argument("--sample", action="store_true", help="Generate sample feedback")
    parser.add_argument("--summary", action="store_true", help="Show feedback summary")
    parser.add_argument("--days", type=int, default=30, help="Days for summary (default: 30)")
    parser.add_argument("--data-dir", default="feedback/data", help="Data directory")
    
    args = parser.parse_args()
    
    collector = FeedbackCollector(Path(args.data_dir))
    
    if args.start:
        print("Feedback collection system started.")
        print("Use the collector API to submit feedback programmatically.")
        print("Database initialized at:", collector.db_path)
        
    elif args.sample:
        print("Generating sample feedback...")
        sample_feedback = collector.create_sample_feedback()
        print(f"Generated {len(sample_feedback)} sample feedback entries")
        
        # Generate sample usage metrics
        for i in range(10):
            user_id = collector.generate_user_id(f"test_user_{i}")
            for action in ["agent_recommendation", "project_analysis", "workflow_execution"]:
                collector.simulate_user_interaction(user_id, action)
                
        print("Generated sample usage metrics")
        
    elif args.summary:
        summary = collector.get_feedback_summary(args.days)
        print(f"\\nFeedback Summary (Last {args.days} days):")
        print(f"Total Feedback: {summary['total_feedback']}")
        print(f"Average Rating: {summary['average_rating']}/5 ({summary['ratings_count']} ratings)")
        
        print("\\nBy Type:")
        for type_name, count in summary['by_type'].items():
            print(f"  {type_name.replace('_', ' ').title()}: {count}")
            
        print("\\nBy Sentiment:")
        for sentiment, count in summary['by_sentiment'].items():
            print(f"  {sentiment.title()}: {count}")
            
        print("\\nBy Priority:")
        for priority, count in summary['by_priority'].items():
            print(f"  {priority.title()}: {count}")
            
    else:
        parser.print_help()


if __name__ == "__main__":
    main()