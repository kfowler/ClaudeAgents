"""
Non-intrusive Feedback Collection System

This module implements various mechanisms to collect user feedback
without disrupting the development workflow.
"""

import json
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)

class FeedbackTrigger(Enum):
    """When to collect feedback"""
    SESSION_END = "session_end"
    TASK_COMPLETION = "task_completion"
    ERROR_RECOVERY = "error_recovery"
    MILESTONE = "milestone"
    PERIODIC = "periodic"
    USER_INITIATED = "user_initiated"
    IMPLICIT_BEHAVIOR = "implicit_behavior"

class FeedbackType(Enum):
    """Types of feedback we can collect"""
    RATING = "rating"
    TEXT = "text"
    CHOICE = "choice"
    IMPLICIT = "implicit"
    CORRECTION = "correction"
    SUGGESTION = "suggestion"

@dataclass
class FeedbackPrompt:
    """Configuration for a feedback collection prompt"""
    trigger: FeedbackTrigger
    feedback_type: FeedbackType
    prompt_text: str
    options: Optional[List[str]] = None
    min_wait_time: int = 300  # 5 minutes minimum between similar prompts
    max_per_session: int = 2
    context_requirements: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0  # Importance weight for analytics

@dataclass
class ImplicitSignal:
    """Tracks implicit user behavior signals"""
    signal_type: str
    context: Dict[str, Any]
    timestamp: datetime
    confidence: float  # 0.0 to 1.0
    value: Any
    session_id: str

class FeedbackCollector:
    """
    Smart feedback collection that adapts to user behavior and preferences
    """
    
    def __init__(self, analytics_collector=None):
        self.analytics_collector = analytics_collector
        self.prompts = self._initialize_prompts()
        self.user_preferences = {}  # User ID -> preferences
        self.session_feedback_count = {}  # Session ID -> count
        self.last_prompt_times = {}  # User ID + prompt hash -> timestamp
        self.implicit_signals = []
        self.active_sessions = {}  # Session ID -> session start time
        
    def _initialize_prompts(self) -> List[FeedbackPrompt]:
        """Initialize standard feedback prompts"""
        return [
            # Quick satisfaction rating after successful tasks
            FeedbackPrompt(
                trigger=FeedbackTrigger.TASK_COMPLETION,
                feedback_type=FeedbackType.RATING,
                prompt_text="How satisfied are you with this solution? (1-5)",
                min_wait_time=600,  # 10 minutes
                max_per_session=1,
                context_requirements={'success_status': 'success'},
                weight=1.0
            ),
            
            # Detailed feedback after complex multi-agent workflows
            FeedbackPrompt(
                trigger=FeedbackTrigger.SESSION_END,
                feedback_type=FeedbackType.TEXT,
                prompt_text="Any thoughts on how this workflow could be improved?",
                min_wait_time=1800,  # 30 minutes
                max_per_session=1,
                context_requirements={'agent_count': {'$gte': 2}, 'duration_minutes': {'$gte': 10}},
                weight=1.5
            ),
            
            # Agent selection feedback when user overrides recommendations
            FeedbackPrompt(
                trigger=FeedbackTrigger.USER_INITIATED,
                feedback_type=FeedbackType.CHOICE,
                prompt_text="Why did you choose a different agent?",
                options=[
                    "Recommended agent wasn't suitable",
                    "I prefer this agent for this task type",
                    "Recommended agent had issues before",
                    "Other"
                ],
                min_wait_time=0,  # Immediate when relevant
                max_per_session=3,
                weight=2.0  # High importance for recommendation engine
            ),
            
            # Recovery feedback after errors
            FeedbackPrompt(
                trigger=FeedbackTrigger.ERROR_RECOVERY,
                feedback_type=FeedbackType.TEXT,
                prompt_text="What went wrong? This helps us improve.",
                min_wait_time=300,
                max_per_session=1,
                context_requirements={'had_error': True},
                weight=1.8
            ),
            
            # Periodic check-in for long-term users
            FeedbackPrompt(
                trigger=FeedbackTrigger.PERIODIC,
                feedback_type=FeedbackType.RATING,
                prompt_text="Overall, how effective have the agents been lately? (1-5)",
                min_wait_time=86400 * 7,  # Weekly
                max_per_session=1,
                weight=1.2
            )
        ]
    
    def add_custom_prompt(self, prompt: FeedbackPrompt):
        """Add a custom feedback prompt"""
        self.prompts.append(prompt)
    
    def set_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """
        Set user feedback preferences
        
        preferences can include:
        - frequency: 'minimal', 'normal', 'detailed'
        - types: list of preferred feedback types
        - triggers: list of preferred triggers
        - max_per_day: maximum prompts per day
        """
        self.user_preferences[user_id] = {
            'frequency': preferences.get('frequency', 'normal'),
            'preferred_types': preferences.get('types', []),
            'preferred_triggers': preferences.get('triggers', []),
            'max_per_day': preferences.get('max_per_day', 5),
            'disabled': preferences.get('disabled', False),
            'updated_at': datetime.now(timezone.utc)
        }
    
    async def should_collect_feedback(self, 
                                    user_id: str, 
                                    session_id: str,
                                    prompt: FeedbackPrompt, 
                                    context: Dict[str, Any]) -> bool:
        """
        Intelligent decision on whether to show feedback prompt
        """
        
        # Check if user has disabled feedback
        user_prefs = self.user_preferences.get(user_id, {})
        if user_prefs.get('disabled', False):
            return False
        
        # Check session limits
        session_count = self.session_feedback_count.get(session_id, 0)
        if session_count >= prompt.max_per_session:
            return False
        
        # Check time limits
        prompt_hash = hashlib.md5(f"{prompt.prompt_text}{prompt.trigger.value}".encode()).hexdigest()
        last_time = self.last_prompt_times.get(f"{user_id}_{prompt_hash}")
        if last_time:
            if (datetime.now(timezone.utc) - last_time).total_seconds() < prompt.min_wait_time:
                return False
        
        # Check daily limits
        daily_limit = user_prefs.get('max_per_day', 5)
        if await self._count_daily_feedback(user_id) >= daily_limit:
            return False
        
        # Check context requirements
        if not self._context_matches(context, prompt.context_requirements):
            return False
        
        # Check user frequency preference
        frequency = user_prefs.get('frequency', 'normal')
        if frequency == 'minimal' and prompt.weight < 1.5:
            return False
        elif frequency == 'detailed' or prompt.weight >= 1.5:
            return True
        
        # For normal frequency, use a probability based on prompt weight
        import random
        probability = min(prompt.weight / 2.0, 0.8)  # Max 80% chance
        return random.random() < probability
    
    def _context_matches(self, context: Dict[str, Any], requirements: Dict[str, Any]) -> bool:
        """Check if context matches requirements"""
        for key, requirement in requirements.items():
            if key not in context:
                return False
            
            value = context[key]
            
            if isinstance(requirement, dict):
                # MongoDB-style operators
                if '$gte' in requirement and value < requirement['$gte']:
                    return False
                if '$lte' in requirement and value > requirement['$lte']:
                    return False
                if '$in' in requirement and value not in requirement['$in']:
                    return False
            else:
                # Direct value comparison
                if value != requirement:
                    return False
        
        return True
    
    async def _count_daily_feedback(self, user_id: str) -> int:
        """Count feedback collected from user today"""
        # This would query the database in a real implementation
        # For now, return a conservative estimate
        return 0
    
    async def collect_feedback(self, 
                             user_id: str,
                             session_id: str, 
                             trigger: FeedbackTrigger,
                             context: Dict[str, Any],
                             invocation_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Main feedback collection entry point
        """
        
        # Find applicable prompts
        applicable_prompts = [
            prompt for prompt in self.prompts
            if prompt.trigger == trigger and 
            await self.should_collect_feedback(user_id, session_id, prompt, context)
        ]
        
        if not applicable_prompts:
            return None
        
        # Select highest weight prompt
        selected_prompt = max(applicable_prompts, key=lambda p: p.weight)
        
        # Present feedback prompt (this would integrate with the UI)
        feedback_response = await self._present_prompt(selected_prompt, context)
        
        if feedback_response:
            # Record the feedback
            await self._record_feedback(
                user_id=user_id,
                session_id=session_id,
                invocation_id=invocation_id,
                prompt=selected_prompt,
                response=feedback_response,
                context=context
            )
            
            # Update counters
            self.session_feedback_count[session_id] = self.session_feedback_count.get(session_id, 0) + 1
            prompt_hash = hashlib.md5(f"{selected_prompt.prompt_text}{selected_prompt.trigger.value}".encode()).hexdigest()
            self.last_prompt_times[f"{user_id}_{prompt_hash}"] = datetime.now(timezone.utc)
            
            return feedback_response
        
        return None
    
    async def _present_prompt(self, prompt: FeedbackPrompt, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Present feedback prompt to user (mock implementation)
        
        In a real implementation, this would integrate with the UI system
        to show non-intrusive prompts (notifications, sidebar, etc.)
        """
        
        # Mock different response patterns based on context
        if prompt.feedback_type == FeedbackType.RATING:
            # Simulate rating based on success indicators
            if context.get('success_status') == 'success' and context.get('quality_score', 0.5) > 0.7:
                rating = 4 if context.get('duration_seconds', 300) < 180 else 3
            else:
                rating = 2
            
            return {
                'type': 'rating',
                'rating': rating,
                'prompt_text': prompt.prompt_text
            }
        
        elif prompt.feedback_type == FeedbackType.CHOICE and prompt.options:
            # Simulate choice selection
            return {
                'type': 'choice',
                'selected_option': prompt.options[0],  # Usually first option
                'prompt_text': prompt.prompt_text
            }
        
        elif prompt.feedback_type == FeedbackType.TEXT:
            # Simulate text feedback
            return {
                'type': 'text',
                'text': "The workflow worked well overall",
                'prompt_text': prompt.prompt_text
            }
        
        return None
    
    async def _record_feedback(self,
                             user_id: str,
                             session_id: str,
                             invocation_id: Optional[str],
                             prompt: FeedbackPrompt,
                             response: Dict[str, Any],
                             context: Dict[str, Any]):
        """Record feedback in analytics system"""
        
        if self.analytics_collector:
            await self.analytics_collector.record_feedback(
                session_id=session_id,
                invocation_id=invocation_id,
                feedback_type=prompt.feedback_type.value,
                rating=response.get('rating'),
                feedback_text=response.get('text') or response.get('selected_option'),
                suggested_agent=context.get('suggested_agent'),
                user_correction=context.get('user_correction')
            )
    
    def track_implicit_signal(self, 
                            signal_type: str, 
                            session_id: str, 
                            context: Dict[str, Any],
                            confidence: float = 1.0):
        """
        Track implicit behavioral signals
        
        Examples:
        - User immediately corrects agent output
        - User abandons task mid-way
        - User repeatedly uses same agent
        - User frequently switches agents
        """
        
        signal = ImplicitSignal(
            signal_type=signal_type,
            context=context,
            timestamp=datetime.now(timezone.utc),
            confidence=confidence,
            value=context.get('value'),
            session_id=session_id
        )
        
        self.implicit_signals.append(signal)
        
        # Analyze patterns and create feedback records
        asyncio.create_task(self._analyze_implicit_patterns(session_id))
    
    async def _analyze_implicit_patterns(self, session_id: str):
        """
        Analyze implicit signals to infer user satisfaction
        """
        
        session_signals = [s for s in self.implicit_signals if s.session_id == session_id]
        
        # Pattern: Immediate corrections suggest dissatisfaction
        correction_signals = [s for s in session_signals if s.signal_type == 'immediate_correction']
        if len(correction_signals) >= 2:  # Pattern detected
            
            if self.analytics_collector:
                await self.analytics_collector.record_feedback(
                    session_id=session_id,
                    feedback_type='implicit_behavior',
                    rating=2,  # Low satisfaction inferred
                    feedback_text='Multiple immediate corrections detected',
                    user_correction={'pattern': 'immediate_corrections', 'count': len(correction_signals)}
                )
        
        # Pattern: Task abandonment
        abandonment_signals = [s for s in session_signals if s.signal_type == 'task_abandonment']
        if abandonment_signals:
            
            if self.analytics_collector:
                await self.analytics_collector.record_feedback(
                    session_id=session_id,
                    feedback_type='implicit_behavior',
                    rating=1,  # Very low satisfaction
                    feedback_text='Task abandoned',
                    user_correction={'pattern': 'abandonment', 'context': abandonment_signals[-1].context}
                )
        
        # Pattern: Rapid success indicates good agent match
        success_signals = [s for s in session_signals if s.signal_type == 'rapid_completion']
        if success_signals and success_signals[0].confidence > 0.8:
            
            if self.analytics_collector:
                await self.analytics_collector.record_feedback(
                    session_id=session_id,
                    feedback_type='implicit_behavior',
                    rating=5,  # High satisfaction inferred
                    feedback_text='Rapid successful completion',
                    user_correction=None
                )
    
    def start_session_tracking(self, session_id: str):
        """Start tracking a session for implicit signals"""
        self.active_sessions[session_id] = datetime.now(timezone.utc)
        self.session_feedback_count[session_id] = 0
    
    def end_session_tracking(self, session_id: str, outcome: str):
        """End session tracking and analyze overall patterns"""
        
        if session_id not in self.active_sessions:
            return
        
        session_start = self.active_sessions[session_id]
        session_duration = (datetime.now(timezone.utc) - session_start).total_seconds()
        
        # Analyze session-level patterns
        context = {
            'duration_seconds': session_duration,
            'outcome': outcome,
            'feedback_count': self.session_feedback_count.get(session_id, 0)
        }
        
        # Long sessions with no feedback might indicate flow state (good)
        # or frustration (bad) - use outcome to disambiguate
        if session_duration > 1800 and self.session_feedback_count.get(session_id, 0) == 0:  # 30+ minutes, no feedback
            signal_type = 'flow_state' if outcome == 'completed' else 'silent_frustration'
            confidence = 0.7 if outcome == 'completed' else 0.8
            
            self.track_implicit_signal(signal_type, session_id, context, confidence)
        
        # Clean up
        del self.active_sessions[session_id]
        if session_id in self.session_feedback_count:
            del self.session_feedback_count[session_id]

# Common implicit signal tracking functions
class ImplicitTracker:
    """Helper class for tracking common implicit feedback signals"""
    
    @staticmethod
    def track_code_modification(collector: FeedbackCollector, 
                              session_id: str, 
                              agent_name: str,
                              time_to_modify: int,
                              modification_extent: str):
        """Track when user modifies agent-generated code"""
        
        # Immediate modification (< 60 seconds) suggests poor quality
        if time_to_modify < 60:
            collector.track_implicit_signal(
                'immediate_correction',
                session_id,
                {
                    'agent': agent_name,
                    'time_to_modify': time_to_modify,
                    'extent': modification_extent
                },
                confidence=0.9
            )
        
        # Extensive modifications suggest mismatch
        elif modification_extent == 'major':
            collector.track_implicit_signal(
                'major_correction',
                session_id,
                {
                    'agent': agent_name,
                    'time_to_modify': time_to_modify,
                    'extent': modification_extent
                },
                confidence=0.8
            )
    
    @staticmethod
    def track_agent_switching(collector: FeedbackCollector,
                            session_id: str,
                            from_agent: str,
                            to_agent: str,
                            reason: str):
        """Track when user switches agents mid-task"""
        
        collector.track_implicit_signal(
            'agent_switch',
            session_id,
            {
                'from_agent': from_agent,
                'to_agent': to_agent,
                'reason': reason
            },
            confidence=0.7
        )
    
    @staticmethod
    def track_task_completion_speed(collector: FeedbackCollector,
                                  session_id: str,
                                  agent_name: str,
                                  duration_seconds: int,
                                  expected_duration: int):
        """Track task completion relative to expected time"""
        
        ratio = duration_seconds / max(expected_duration, 1)
        
        if ratio < 0.5:  # Much faster than expected
            collector.track_implicit_signal(
                'rapid_completion',
                session_id,
                {
                    'agent': agent_name,
                    'duration': duration_seconds,
                    'expected': expected_duration,
                    'ratio': ratio
                },
                confidence=0.8
            )
        elif ratio > 3.0:  # Much slower than expected
            collector.track_implicit_signal(
                'slow_completion',
                session_id,
                {
                    'agent': agent_name,
                    'duration': duration_seconds,
                    'expected': expected_duration,
                    'ratio': ratio
                },
                confidence=0.9
            )

# Integration helpers
async def setup_feedback_collection(analytics_collector) -> FeedbackCollector:
    """Set up feedback collection with reasonable defaults"""
    
    collector = FeedbackCollector(analytics_collector)
    
    # Add some domain-specific prompts
    collector.add_custom_prompt(FeedbackPrompt(
        trigger=FeedbackTrigger.TASK_COMPLETION,
        feedback_type=FeedbackType.RATING,
        prompt_text="How well did the security audit meet your needs? (1-5)",
        context_requirements={'agent_name': 'security-audit-specialist'},
        weight=1.5
    ))
    
    collector.add_custom_prompt(FeedbackPrompt(
        trigger=FeedbackTrigger.ERROR_RECOVERY,
        feedback_type=FeedbackType.CHOICE,
        prompt_text="What type of error occurred?",
        options=[
            "Agent couldn't understand the request",
            "Agent chose wrong approach",
            "Technical/infrastructure error",
            "Agent produced incorrect code",
            "Other"
        ],
        weight=2.0
    ))
    
    return collector

def create_feedback_hooks(collector: FeedbackCollector) -> Dict[str, Callable]:
    """Create hooks for integration with the agent system"""
    
    return {
        'on_agent_start': lambda session_id, agent, request: 
            collector.start_session_tracking(session_id),
            
        'on_agent_complete': lambda session_id, agent, success, context:
            asyncio.create_task(collector.collect_feedback(
                context.get('user_id', 'unknown'),
                session_id,
                FeedbackTrigger.TASK_COMPLETION,
                {**context, 'agent_name': agent, 'success_status': 'success' if success else 'failed'}
            )),
            
        'on_user_correction': lambda session_id, agent, time_delta, extent:
            ImplicitTracker.track_code_modification(collector, session_id, agent, time_delta, extent),
            
        'on_agent_switch': lambda session_id, from_agent, to_agent, reason:
            ImplicitTracker.track_agent_switching(collector, session_id, from_agent, to_agent, reason),
            
        'on_session_end': lambda session_id, outcome:
            collector.end_session_tracking(session_id, outcome)
    }