"""
Agent Integration Layer for Workflow Engine

This module provides the integration between the workflow engine and the existing
Claude Code agent system, enabling seamless execution of agents within workflows.
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import logging

from engine import TaskResult, TaskStatus, AgentInterface

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class AgentMetadata:
    """Metadata about an available agent"""
    name: str
    description: str
    expertise_areas: List[str] = field(default_factory=list)
    input_parameters: List[str] = field(default_factory=list)
    output_artifacts: List[str] = field(default_factory=list)
    estimated_duration: Optional[int] = None  # seconds
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # Other agents this one commonly follows

class ClaudeCodeAgentInterface(AgentInterface):
    """Integration with Claude Code agent system"""
    
    def __init__(self, agents_directory: str = "./agents"):
        self.agents_directory = Path(agents_directory)
        self.agent_metadata: Dict[str, AgentMetadata] = {}
        self.load_agent_metadata()
    
    def load_agent_metadata(self):
        """Load metadata about available agents"""
        self.agent_metadata.clear()
        
        # Load agent definitions from markdown files
        for agent_file in self.agents_directory.glob("*.md"):
            try:
                agent_name = agent_file.stem
                metadata = self._extract_agent_metadata(agent_file)
                self.agent_metadata[agent_name] = metadata
                logger.debug(f"Loaded metadata for agent: {agent_name}")
                
            except Exception as e:
                logger.warning(f"Failed to load metadata for {agent_file}: {e}")
    
    def _extract_agent_metadata(self, agent_file: Path) -> AgentMetadata:
        """Extract metadata from agent markdown file"""
        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract YAML frontmatter if present
        frontmatter = {}
        if content.startswith('---\n'):
            try:
                end_pos = content.find('\n---\n', 4)
                if end_pos > 0:
                    import yaml
                    frontmatter_text = content[4:end_pos]
                    frontmatter = yaml.safe_load(frontmatter_text)
                    content = content[end_pos + 5:]
            except Exception as e:
                logger.warning(f"Failed to parse frontmatter in {agent_file}: {e}")
        
        # Extract description from content
        description_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        description = description_match.group(1) if description_match else frontmatter.get('description', '')
        
        # Extract expertise areas from content
        expertise_areas = []
        
        # Look for common patterns in agent descriptions
        expertise_patterns = [
            r'expert in ([^.]+)',
            r'specializes in ([^.]+)',
            r'focuses on ([^.]+)',
            r'\*\*([^*]+)\*\*'  # Bold text often indicates expertise
        ]
        
        for pattern in expertise_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            expertise_areas.extend([match.strip() for match in matches])
        
        # Look for technology stack mentions
        tech_keywords = [
            'React', 'Next.js', 'JavaScript', 'TypeScript', 'Python', 'Rust', 'Go',
            'Docker', 'Kubernetes', 'AWS', 'GCP', 'Azure', 'PostgreSQL', 'MongoDB',
            'security', 'testing', 'accessibility', 'performance', 'AI', 'ML',
            'mobile', 'iOS', 'Android', 'DevOps', 'CI/CD'
        ]
        
        for keyword in tech_keywords:
            if keyword.lower() in content.lower():
                expertise_areas.append(keyword)
        
        # Deduplicate and clean up expertise areas
        expertise_areas = list(set([area.strip() for area in expertise_areas if area.strip()]))
        
        # Estimate duration based on agent complexity (simple heuristic)
        content_length = len(content)
        if content_length < 2000:
            estimated_duration = 300  # 5 minutes
        elif content_length < 5000:
            estimated_duration = 900  # 15 minutes
        else:
            estimated_duration = 1800  # 30 minutes
        
        return AgentMetadata(
            name=frontmatter.get('name', agent_file.stem),
            description=description or frontmatter.get('description', ''),
            expertise_areas=expertise_areas,
            estimated_duration=estimated_duration,
            input_parameters=['user_request', 'project_context'],
            output_artifacts=['modified_files', 'analysis_report']
        )
    
    def get_available_agents(self) -> List[AgentMetadata]:
        """Get list of all available agents"""
        return list(self.agent_metadata.values())
    
    def get_agent_metadata(self, agent_name: str) -> Optional[AgentMetadata]:
        """Get metadata for a specific agent"""
        return self.agent_metadata.get(agent_name)
    
    def recommend_agents(self, 
                        user_request: str, 
                        context: Dict[str, Any] = None) -> List[Tuple[str, float]]:
        """Recommend agents based on user request and context"""
        recommendations = []
        request_lower = user_request.lower()
        
        for agent_name, metadata in self.agent_metadata.items():
            score = 0.0
            
            # Score based on expertise areas
            for expertise in metadata.expertise_areas:
                if expertise.lower() in request_lower:
                    score += 1.0
            
            # Score based on description relevance
            description_words = metadata.description.lower().split()
            request_words = request_lower.split()
            
            common_words = set(description_words) & set(request_words)
            score += len(common_words) * 0.1
            
            # Context-based scoring
            if context:
                tech_stack = context.get('tech_stack', [])
                for tech in tech_stack:
                    if tech.lower() in [ea.lower() for ea in metadata.expertise_areas]:
                        score += 0.5
            
            if score > 0:
                recommendations.append((agent_name, score))
        
        # Sort by score (descending)
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations
    
    async def execute_agent(self, 
                           agent_name: str, 
                           parameters: Dict[str, Any],
                           context: Dict[str, Any] = None) -> TaskResult:
        """Execute an agent and return results"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Validate agent exists
            if agent_name not in self.agent_metadata:
                return TaskResult(
                    task_id=parameters.get('task_id', 'unknown'),
                    status=TaskStatus.FAILED,
                    error=f"Agent not found: {agent_name}"
                )
            
            metadata = self.agent_metadata[agent_name]
            
            # Prepare execution context
            execution_context = {
                'agent_name': agent_name,
                'user_request': parameters.get('user_request', ''),
                'project_context': context or {},
                'parameters': parameters
            }
            
            # Simulate agent execution (in real implementation, this would invoke Claude Code)
            logger.info(f"Executing agent: {agent_name}")
            
            # Simulate varying execution times based on agent complexity
            execution_time = min(metadata.estimated_duration or 300, 30)  # Cap at 30s for simulation
            await asyncio.sleep(execution_time / 100)  # Scale down for demo
            
            # Generate realistic output based on agent type
            output = self._generate_agent_output(agent_name, metadata, execution_context)
            
            # Simulate file modifications
            files_modified = self._simulate_file_modifications(agent_name, metadata)
            
            execution_duration = asyncio.get_event_loop().time() - start_time
            
            return TaskResult(
                task_id=parameters.get('task_id', 'unknown'),
                status=TaskStatus.COMPLETED,
                output=output,
                metadata={
                    'agent_name': agent_name,
                    'execution_time': execution_duration,
                    'expertise_areas': metadata.expertise_areas
                },
                execution_time=execution_duration,
                artifacts=files_modified
            )
            
        except Exception as e:
            execution_duration = asyncio.get_event_loop().time() - start_time
            logger.error(f"Agent execution failed: {agent_name} - {e}")
            
            return TaskResult(
                task_id=parameters.get('task_id', 'unknown'),
                status=TaskStatus.FAILED,
                error=str(e),
                execution_time=execution_duration
            )
    
    def _generate_agent_output(self, 
                              agent_name: str, 
                              metadata: AgentMetadata, 
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate realistic output based on agent type"""
        user_request = context.get('user_request', '')
        
        output = {
            'summary': f"Agent {agent_name} completed analysis of: {user_request[:100]}...",
            'recommendations': [],
            'actions_taken': [],
            'next_steps': []
        }
        
        # Customize output based on agent type
        if 'security' in agent_name.lower():
            output['security_issues'] = [
                'Validated input sanitization',
                'Checked for SQL injection vulnerabilities',
                'Verified authentication mechanisms'
            ]
            output['recommendations'] = [
                'Implement additional rate limiting',
                'Add security headers',
                'Enable audit logging'
            ]
        
        elif 'test' in agent_name.lower() or 'qa' in agent_name.lower():
            output['test_coverage'] = '85%'
            output['tests_added'] = 12
            output['test_results'] = 'All tests passing'
            output['recommendations'] = [
                'Add integration tests for new features',
                'Increase unit test coverage',
                'Implement performance regression tests'
            ]
        
        elif 'accessibility' in agent_name.lower():
            output['accessibility_score'] = 'WCAG 2.1 AA Compliant'
            output['issues_found'] = 3
            output['fixes_applied'] = 8
            output['recommendations'] = [
                'Add alt text for remaining images',
                'Improve keyboard navigation',
                'Enhance color contrast ratios'
            ]
        
        elif 'performance' in agent_name.lower() or 'systems' in agent_name.lower():
            output['performance_metrics'] = {
                'load_time': '1.2s',
                'memory_usage': '45MB',
                'cpu_utilization': '12%'
            }
            output['optimizations'] = [
                'Implemented caching layer',
                'Optimized database queries',
                'Reduced bundle size by 20%'
            ]
        
        elif 'devops' in agent_name.lower():
            output['infrastructure_changes'] = [
                'Updated CI/CD pipeline',
                'Configured monitoring and alerting',
                'Optimized deployment process'
            ]
            output['deployment_status'] = 'Ready for production'
        
        else:
            # Generic agent output
            output['analysis'] = f"Completed analysis for {agent_name}"
            output['recommendations'] = [
                'Review implementation approach',
                'Consider scalability implications',
                'Validate business requirements'
            ]
        
        return output
    
    def _simulate_file_modifications(self, 
                                   agent_name: str, 
                                   metadata: AgentMetadata) -> List[str]:
        """Simulate files that would be modified by the agent"""
        files = []
        
        if 'test' in agent_name.lower():
            files.extend([
                'tests/unit/test_new_feature.py',
                'tests/integration/test_api.py',
                'test_config.json'
            ])
        
        if 'security' in agent_name.lower():
            files.extend([
                'security/security_config.py',
                'middleware/auth_middleware.py',
                'security_report.md'
            ])
        
        if 'accessibility' in agent_name.lower():
            files.extend([
                'components/AccessibleButton.jsx',
                'styles/accessibility.css',
                'docs/accessibility_guide.md'
            ])
        
        if 'devops' in agent_name.lower():
            files.extend([
                '.github/workflows/deploy.yml',
                'docker-compose.yml',
                'k8s/deployment.yaml'
            ])
        
        # Default files for most agents
        if not files:
            files.extend([
                'src/main.py',
                'README.md',
                'requirements.txt'
            ])
        
        return files
    
    def validate_agent_chain(self, agent_sequence: List[str]) -> List[str]:
        """Validate that a sequence of agents makes logical sense"""
        issues = []
        
        # Check if all agents exist
        for agent_name in agent_sequence:
            if agent_name not in self.agent_metadata:
                issues.append(f"Unknown agent: {agent_name}")
        
        # Check for logical ordering
        for i in range(len(agent_sequence) - 1):
            current_agent = agent_sequence[i]
            next_agent = agent_sequence[i + 1]
            
            if current_agent in self.agent_metadata and next_agent in self.agent_metadata:
                current_meta = self.agent_metadata[current_agent]
                next_meta = self.agent_metadata[next_agent]
                
                # Check if there are common expertise areas (good for chaining)
                common_areas = set(current_meta.expertise_areas) & set(next_meta.expertise_areas)
                if not common_areas:
                    logger.info(f"Agents {current_agent} -> {next_agent} have no common expertise areas")
        
        return issues
    
    def suggest_missing_agents(self, agent_sequence: List[str], context: Dict[str, Any]) -> List[str]:
        """Suggest agents that might be missing from a workflow"""
        suggestions = []
        
        current_expertise = set()
        for agent_name in agent_sequence:
            if agent_name in self.agent_metadata:
                current_expertise.update(self.agent_metadata[agent_name].expertise_areas)
        
        # Common gaps to check for
        critical_areas = ['security', 'testing', 'accessibility', 'performance', 'documentation']
        
        for area in critical_areas:
            if not any(area.lower() in expertise.lower() for expertise in current_expertise):
                # Find agents that cover this area
                for agent_name, metadata in self.agent_metadata.items():
                    if any(area.lower() in expertise.lower() for expertise in metadata.expertise_areas):
                        if agent_name not in agent_sequence:
                            suggestions.append(f"Consider adding {agent_name} for {area} coverage")
                            break
        
        return suggestions

# Global instance for easy access
claude_agent_interface = ClaudeCodeAgentInterface()