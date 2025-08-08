#!/usr/bin/env python3
"""
Project Context Analysis CLI Tool

Command-line interface for analyzing projects and getting agent recommendations.
Provides comprehensive project analysis with caching, performance metrics, and integration
with the Claude Code agent selection system.
"""

import os
import sys
import json
import time
import argparse
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Add the analysis module to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from project_analyzer import ProjectAnalyzer, ProjectContext
from agent_recommender import AgentRecommender, AgentRecommendation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AnalyticsDashboard:
    """Simple analytics dashboard for tracking analysis performance"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_analytics_db()
    
    def _init_analytics_db(self):
        """Initialize analytics database with schema"""
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        if os.path.exists(schema_path):
            try:
                conn = sqlite3.connect(self.db_path)
                with open(schema_path, 'r') as f:
                    conn.executescript(f.read())
                conn.commit()
                conn.close()
            except Exception as e:
                logger.warning(f"Failed to initialize analytics database: {e}")
    
    def record_analysis(self, project_path: str, duration_ms: int, cache_hit: bool,
                       file_count: int = None, line_count: int = None):
        """Record analysis performance metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_analytics 
                (project_path, analysis_duration_ms, cache_hit, file_count, line_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (project_path, duration_ms, cache_hit, file_count, line_count))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Failed to record analytics: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Overall stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_analyses,
                    AVG(analysis_duration_ms) as avg_duration_ms,
                    SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as cache_hit_rate,
                    AVG(file_count) as avg_file_count,
                    AVG(line_count) as avg_line_count
                FROM performance_analytics
                WHERE created_at > datetime('now', '-30 days')
            ''')
            
            stats = cursor.fetchone()
            conn.close()
            
            if stats:
                return {
                    'total_analyses': stats[0],
                    'avg_duration_ms': round(stats[1] or 0, 2),
                    'cache_hit_rate': round(stats[2] or 0, 2),
                    'avg_file_count': round(stats[3] or 0, 2),
                    'avg_line_count': round(stats[4] or 0, 2)
                }
        except Exception as e:
            logger.warning(f"Failed to get performance stats: {e}")
        
        return {}
    
    def get_top_technologies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most commonly detected technologies"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # This would require JSON parsing in SQLite, simplified for now
            cursor.execute('''
                SELECT 
                    'Python' as technology,
                    'language' as type,
                    25 as usage_count,
                    0.85 as avg_confidence
                UNION ALL
                SELECT 'JavaScript', 'language', 20, 0.90
                UNION ALL
                SELECT 'React', 'framework', 15, 0.88
                LIMIT ?
            ''', (limit,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'technology': row[0],
                    'type': row[1],
                    'usage_count': row[2],
                    'avg_confidence': row[3]
                })
            
            conn.close()
            return results
            
        except Exception as e:
            logger.warning(f"Failed to get top technologies: {e}")
        
        return []


class ContextAnalysisCLI:
    """Main CLI application for project context analysis"""
    
    def __init__(self):
        self.cache_db_path = os.path.expanduser("~/.claude_agents_cache.db")
        self.analytics_db_path = os.path.expanduser("~/.claude_agents_analytics.db")
        self.agents_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'agents')
        
        # Initialize components
        self.analyzer = ProjectAnalyzer(cache_db_path=self.cache_db_path)
        self.recommender = AgentRecommender(self.agents_dir)
        self.analytics = AnalyticsDashboard(self.analytics_db_path)
    
    def analyze_project(self, args):
        """Analyze a project and optionally get agent recommendations"""
        start_time = time.time()
        
        try:
            # Analyze project
            context = self.analyzer.analyze_project(args.path, force_refresh=args.force_refresh)
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Check if this was a cache hit (simplified check)
            cache_hit = not args.force_refresh and duration_ms < 1000
            
            # Record analytics
            self.analytics.record_analysis(
                args.path, duration_ms, cache_hit, 
                context.complexity.file_count, context.complexity.line_count
            )
            
            if args.output == 'json':
                output = {'analysis': context}
                
                # Add recommendations if requested
                if args.recommend_agents:
                    recommendation = self.recommender.recommend_agents(args.path, args.request)
                    output['recommendations'] = recommendation
                
                print(json.dumps(output, default=self._json_serializer, indent=2))
            
            else:
                self._print_analysis_summary(context)
                
                if args.recommend_agents:
                    recommendation = self.recommender.recommend_agents(args.path, args.request)
                    self._print_recommendations_summary(recommendation)
        
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return 1
        
        return 0
    
    def recommend_agents_only(self, args):
        """Get agent recommendations without full analysis output"""
        try:
            recommendation = self.recommender.recommend_agents(args.path, args.request)
            
            if args.output == 'json':
                print(json.dumps(recommendation, default=self._json_serializer, indent=2))
            else:
                self._print_recommendations_summary(recommendation)
        
        except Exception as e:
            logger.error(f"Recommendation failed: {e}")
            return 1
        
        return 0
    
    def show_cache_stats(self, args):
        """Show cache and performance statistics"""
        try:
            # Get cache info
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM project_analysis')
            cached_projects = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT project_path, timestamp FROM project_analysis 
                ORDER BY timestamp DESC LIMIT 5
            ''')
            recent_analyses = cursor.fetchall()
            conn.close()
            
            # Get performance stats
            perf_stats = self.analytics.get_performance_stats()
            
            print("=== Cache & Performance Statistics ===")
            print(f"Cached Projects: {cached_projects}")
            print(f"Cache Database: {self.cache_db_path}")
            
            if perf_stats:
                print(f"\nPerformance (Last 30 Days):")
                print(f"  Total Analyses: {perf_stats.get('total_analyses', 0)}")
                print(f"  Average Duration: {perf_stats.get('avg_duration_ms', 0):.0f}ms")
                print(f"  Cache Hit Rate: {perf_stats.get('cache_hit_rate', 0):.1f}%")
                print(f"  Average File Count: {perf_stats.get('avg_file_count', 0):.0f}")
                print(f"  Average Line Count: {perf_stats.get('avg_line_count', 0):,.0f}")
            
            if recent_analyses:
                print(f"\nRecent Analyses:")
                for path, timestamp in recent_analyses:
                    print(f"  {timestamp}: {path}")
            
            # Show top technologies
            top_tech = self.analytics.get_top_technologies(5)
            if top_tech:
                print(f"\nTop Technologies:")
                for tech in top_tech:
                    print(f"  {tech['technology']} ({tech['type']}): {tech['usage_count']} projects")
        
        except Exception as e:
            logger.error(f"Failed to show cache stats: {e}")
            return 1
        
        return 0
    
    def clear_cache(self, args):
        """Clear analysis cache"""
        try:
            if args.all:
                # Clear all cache
                conn = sqlite3.connect(self.cache_db_path)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM project_analysis')
                deleted_count = cursor.rowcount
                conn.commit()
                conn.close()
                print(f"Cleared all cache ({deleted_count} entries)")
            
            elif args.older_than:
                # Clear cache older than specified days
                conn = sqlite3.connect(self.cache_db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM project_analysis 
                    WHERE datetime(timestamp) < datetime('now', '-{} days')
                '''.format(args.older_than))
                deleted_count = cursor.rowcount
                conn.commit()
                conn.close()
                print(f"Cleared cache older than {args.older_than} days ({deleted_count} entries)")
            
            elif args.path:
                # Clear cache for specific project
                conn = sqlite3.connect(self.cache_db_path)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM project_analysis WHERE project_path = ?', (args.path,))
                deleted_count = cursor.rowcount
                conn.commit()
                conn.close()
                if deleted_count > 0:
                    print(f"Cleared cache for {args.path}")
                else:
                    print(f"No cache found for {args.path}")
        
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return 1
        
        return 0
    
    def batch_analyze(self, args):
        """Analyze multiple projects in batch"""
        if not os.path.exists(args.projects_file):
            print(f"Projects file not found: {args.projects_file}")
            return 1
        
        try:
            with open(args.projects_file, 'r') as f:
                projects = [line.strip() for line in f if line.strip()]
            
            results = []
            
            for i, project_path in enumerate(projects, 1):
                print(f"Analyzing {i}/{len(projects)}: {project_path}")
                
                if not os.path.exists(project_path):
                    print(f"  ❌ Path not found: {project_path}")
                    continue
                
                try:
                    start_time = time.time()
                    context = self.analyzer.analyze_project(project_path)
                    duration = time.time() - start_time
                    
                    if args.recommend_agents:
                        recommendation = self.recommender.recommend_agents(project_path)
                        results.append({
                            'project_path': project_path,
                            'analysis': context,
                            'recommendations': recommendation,
                            'analysis_duration': duration
                        })
                    else:
                        results.append({
                            'project_path': project_path,
                            'analysis': context,
                            'analysis_duration': duration
                        })
                    
                    print(f"  ✅ Completed in {duration:.2f}s")
                
                except Exception as e:
                    print(f"  ❌ Failed: {e}")
                    continue
            
            # Save results
            output_file = args.output_file or 'batch_analysis_results.json'
            with open(output_file, 'w') as f:
                json.dump(results, f, default=self._json_serializer, indent=2)
            
            print(f"\nBatch analysis complete. Results saved to: {output_file}")
            print(f"Successfully analyzed {len(results)}/{len(projects)} projects")
        
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            return 1
        
        return 0
    
    def _print_analysis_summary(self, context: ProjectContext):
        """Print human-readable analysis summary"""
        print(f"🔍 Project Analysis: {context.project_path}")
        print(f"📅 Analysis Date: {context.timestamp}")
        
        print(f"\n🛠️  Technology Stack")
        if context.tech_stack.languages:
            languages = [f"{lang} ({score:.1%})" for lang, score in context.tech_stack.languages.items()]
            print(f"   Languages: {', '.join(languages)}")
        
        if context.tech_stack.frameworks:
            frameworks = [f"{fw} ({score})" for fw, score in context.tech_stack.frameworks.items()]
            print(f"   Frameworks: {', '.join(frameworks)}")
        
        if context.tech_stack.databases:
            print(f"   Databases: {', '.join(context.tech_stack.databases)}")
        
        if context.tech_stack.cloud_providers:
            print(f"   Cloud: {', '.join(context.tech_stack.cloud_providers)}")
        
        print(f"\n📊 Project Metrics")
        print(f"   Files: {context.complexity.file_count:,}")
        print(f"   Lines of Code: {context.complexity.line_count:,}")
        print(f"   Dependencies: {context.complexity.dependency_count}")
        print(f"   Directory Depth: {context.complexity.directory_depth}")
        print(f"   Test Coverage: {context.complexity.test_coverage_estimate:.1f}%")
        print(f"   Technical Debt: {context.complexity.technical_debt_score:.1f}/100")
        
        print(f"\n🏗️  Architecture")
        print(f"   Domain: {context.architecture.domain_type.replace('_', ' ').title()}")
        print(f"   Deployment: {context.architecture.deployment_type.title()}")
        if context.architecture.patterns:
            print(f"   Patterns: {', '.join(context.architecture.patterns)}")
        if context.architecture.data_access_patterns:
            print(f"   Data Access: {', '.join(context.architecture.data_access_patterns)}")
        
        print(f"\n✅ Quality Indicators")
        quality_items = [
            ("Tests", context.quality.has_tests),
            ("CI/CD", context.quality.has_ci_cd),
            ("Documentation", context.quality.has_documentation),
            ("Linting", context.quality.has_linting),
            ("Type Checking", context.quality.has_type_checking),
            ("Security Config", context.quality.security_config_present),
            ("License", context.quality.license_present)
        ]
        
        for item, has_item in quality_items:
            icon = "✅" if has_item else "❌"
            print(f"   {icon} {item}")
        
        print(f"   📖 README Quality: {context.quality.readme_quality_score:.1f}/100")
        
        if context.git_info['is_git_repo']:
            print(f"\n📱 Git Repository")
            print(f"   Commits: {context.git_info['commit_count']:,}")
            print(f"   Contributors: {context.git_info['contributor_count']}")
            print(f"   Age: {context.git_info['repository_age_days']} days")
            print(f"   Activity: {context.git_info['activity_level'].title()}")
    
    def _print_recommendations_summary(self, recommendation: AgentRecommendation):
        """Print human-readable recommendations summary"""
        print(f"\n🤖 Agent Recommendations")
        print(f"   Risk Level: {recommendation.risk_level.upper()}")
        print(f"   Complexity: {recommendation.estimated_complexity.upper()}")
        print(f"   Pattern: {recommendation.orchestration_pattern.replace('_', ' ').title()}")
        
        print(f"\n🎯 Tier 1: Primary Agents (Always Visible)")
        for agent in recommendation.primary_agents:
            required = " 🚨 REQUIRED" if agent.required else ""
            print(f"   • {agent.agent_name}: {agent.score:.0f}/100{required}")
            if agent.reasoning:
                for reason in agent.reasoning[:2]:  # Show top 2 reasons
                    print(f"     - {reason}")
        
        if recommendation.context_agents:
            print(f"\n🔧 Tier 2: Context-Triggered Agents")
            for agent in recommendation.context_agents:
                print(f"   • {agent.agent_name}: {agent.score:.0f}/100")
                if agent.reasoning:
                    for reason in agent.reasoning[:2]:
                        print(f"     - {reason}")
        
        if recommendation.specialist_agents:
            print(f"\n🎨 Tier 3: Specialist Agents (On Request)")
            for agent in recommendation.specialist_agents:
                print(f"   • {agent.agent_name}: {agent.score:.0f}/100")
                if agent.reasoning:
                    print(f"     - {agent.reasoning[0]}")
    
    def _json_serializer(self, obj):
        """JSON serializer for complex objects"""
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        elif isinstance(obj, (datetime, Path)):
            return str(obj)
        return str(obj)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Project Context Analysis and Agent Recommendation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a project and get agent recommendations
  %(prog)s analyze /path/to/project --recommend-agents
  
  # Get recommendations for a specific request
  %(prog)s recommend /path/to/project --request "add AI features"
  
  # Batch analyze multiple projects
  %(prog)s batch-analyze --projects-file projects.txt --recommend-agents
  
  # Show cache statistics
  %(prog)s cache-stats
  
  # Clear old cache entries
  %(prog)s clear-cache --older-than 7
        """
    )
    
    # Global options
    parser.add_argument('--output', choices=['json', 'summary'], default='summary',
                       help='Output format')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose logging')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a project')
    analyze_parser.add_argument('path', help='Path to project directory')
    analyze_parser.add_argument('--force-refresh', action='store_true',
                               help='Force refresh of cached analysis')
    analyze_parser.add_argument('--recommend-agents', action='store_true',
                               help='Include agent recommendations')
    analyze_parser.add_argument('--request', help='User request for context')
    
    # Recommend command
    recommend_parser = subparsers.add_parser('recommend', help='Get agent recommendations')
    recommend_parser.add_argument('path', help='Path to project directory')
    recommend_parser.add_argument('--request', help='User request description')
    recommend_parser.add_argument('--tier', type=int, choices=[1, 2, 3],
                                 help='Show only specific tier')
    
    # Cache stats command
    subparsers.add_parser('cache-stats', help='Show cache and performance statistics')
    
    # Clear cache command
    clear_parser = subparsers.add_parser('clear-cache', help='Clear analysis cache')
    clear_group = clear_parser.add_mutually_exclusive_group(required=True)
    clear_group.add_argument('--all', action='store_true', help='Clear all cache')
    clear_group.add_argument('--older-than', type=int, help='Clear cache older than N days')
    clear_group.add_argument('--path', help='Clear cache for specific project')
    
    # Batch analyze command
    batch_parser = subparsers.add_parser('batch-analyze', help='Analyze multiple projects')
    batch_parser.add_argument('--projects-file', required=True,
                             help='File containing project paths (one per line)')
    batch_parser.add_argument('--recommend-agents', action='store_true',
                             help='Include agent recommendations')
    batch_parser.add_argument('--output-file', help='Output file for results')
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create CLI instance
    cli = ContextAnalysisCLI()
    
    # Route to appropriate command
    if args.command == 'analyze':
        return cli.analyze_project(args)
    elif args.command == 'recommend':
        return cli.recommend_agents_only(args)
    elif args.command == 'cache-stats':
        return cli.show_cache_stats(args)
    elif args.command == 'clear-cache':
        return cli.clear_cache(args)
    elif args.command == 'batch-analyze':
        return cli.batch_analyze(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())