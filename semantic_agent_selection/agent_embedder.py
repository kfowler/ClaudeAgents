"""
Agent Capability Embedding Generator

This module processes agent markdown files to extract capabilities and generate
semantic embeddings for intelligent agent selection.
"""

import os
import re
import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import asyncio
import aiofiles
import yaml
from datetime import datetime

# ML/AI imports
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

# Database imports
import asyncpg
import json


logger = logging.getLogger(__name__)


@dataclass
class AgentCapability:
    """Structured representation of agent capabilities."""
    name: str
    description: str
    technologies: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    expertise_areas: List[str] = field(default_factory=list)
    tier: int = 1  # From AGENT_DECISION_TREE.md (1=core, 2=specialized, 3=niche)
    color: str = "blue"
    keywords: List[str] = field(default_factory=list)
    anti_patterns: List[str] = field(default_factory=list)
    
    def to_embedding_text(self) -> str:
        """Convert capability to text for embedding generation."""
        parts = [
            f"Agent: {self.name}",
            f"Description: {self.description}",
        ]
        
        if self.technologies:
            parts.append(f"Technologies: {', '.join(self.technologies)}")
            
        if self.domains:
            parts.append(f"Domains: {', '.join(self.domains)}")
            
        if self.expertise_areas:
            parts.append(f"Expertise: {', '.join(self.expertise_areas)}")
            
        if self.patterns:
            parts.append(f"Patterns: {', '.join(self.patterns)}")
            
        if self.examples:
            parts.append(f"Examples: {' '.join(self.examples)}")
            
        return "\n".join(parts)


@dataclass
class EmbeddingResult:
    """Result of embedding generation."""
    agent_name: str
    embedding: np.ndarray
    model_name: str
    metadata: Dict[str, Any]
    content_hash: str
    created_at: datetime = field(default_factory=datetime.now)


class AgentMarkdownParser:
    """Parse agent markdown files to extract capabilities."""
    
    # Technology keywords organized by category
    TECH_PATTERNS = {
        'frontend': [
            'React', 'Next.js', 'Vue', 'Svelte', 'Angular', 'TypeScript', 'JavaScript',
            'HTML', 'CSS', 'Tailwind', 'Bootstrap', 'Sass', 'SCSS', 'styled-components'
        ],
        'backend': [
            'Node.js', 'Python', 'FastAPI', 'Django', 'Flask', 'Go', 'Rust', 'Java',
            'Spring', 'Express', 'Koa', 'Bun', 'Deno', '.NET', 'C#', 'PHP', 'Ruby'
        ],
        'mobile': [
            'iOS', 'Android', 'Swift', 'Kotlin', 'React Native', 'Flutter', 'Xamarin',
            'Objective-C', 'Java', 'Dart', 'app store', 'mobile app'
        ],
        'database': [
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'SQLite', 'DynamoDB',
            'Elasticsearch', 'Supabase', 'PlanetScale', 'Prisma', 'Drizzle'
        ],
        'ai_ml': [
            'AI', 'ML', 'LLM', 'ChatGPT', 'Claude', 'OpenAI', 'Anthropic', 'embedding',
            'vector', 'RAG', 'neural', 'transformer', 'PyTorch', 'TensorFlow',
            'scikit-learn', 'Hugging Face', 'BERT', 'GPT'
        ],
        'devops': [
            'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'CI/CD', 'GitHub Actions',
            'Jenkins', 'Terraform', 'Ansible', 'monitoring', 'logging'
        ],
        'security': [
            'authentication', 'authorization', 'OAuth', 'JWT', 'encryption', 'HTTPS',
            'security', 'vulnerability', 'penetration', 'audit', 'compliance'
        ]
    }
    
    # Domain patterns
    DOMAIN_PATTERNS = {
        'web_development': ['web app', 'web application', 'website', 'frontend', 'backend'],
        'mobile_development': ['mobile', 'iOS', 'Android', 'app store'],
        'ai_ml': ['artificial intelligence', 'machine learning', 'AI', 'ML', 'neural'],
        'data_engineering': ['data pipeline', 'analytics', 'ETL', 'data warehouse'],
        'security': ['security', 'audit', 'vulnerability', 'compliance', 'penetration'],
        'devops': ['deployment', 'infrastructure', 'CI/CD', 'monitoring', 'cloud'],
        'testing': ['test', 'testing', 'QA', 'quality assurance', 'TDD', 'BDD']
    }
    
    @classmethod
    async def parse_agent_file(cls, file_path: Path) -> Optional[AgentCapability]:
        """Parse a single agent markdown file."""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Extract YAML frontmatter
            frontmatter = cls._extract_frontmatter(content)
            if not frontmatter:
                logger.warning(f"No frontmatter found in {file_path}")
                return None
            
            # Extract agent content
            agent_content = cls._extract_content(content)
            
            # Build capability object
            capability = AgentCapability(
                name=frontmatter.get('name', file_path.stem),
                description=frontmatter.get('description', ''),
                color=frontmatter.get('color', 'blue')
            )
            
            # Extract technologies
            capability.technologies = cls._extract_technologies(agent_content)
            
            # Extract domains
            capability.domains = cls._extract_domains(agent_content)
            
            # Extract patterns and expertise
            capability.patterns = cls._extract_patterns(agent_content)
            capability.expertise_areas = cls._extract_expertise_areas(agent_content)
            
            # Extract examples from frontmatter
            if 'Examples' in frontmatter:
                capability.examples = cls._extract_examples_from_yaml(frontmatter['Examples'])
            
            # Determine tier based on agent name and decision tree
            capability.tier = cls._determine_tier(capability.name)
            
            # Extract keywords from content
            capability.keywords = cls._extract_keywords(agent_content)
            
            return capability
            
        except Exception as e:
            logger.error(f"Error parsing agent file {file_path}: {e}")
            return None
    
    @staticmethod
    def _extract_frontmatter(content: str) -> Optional[Dict]:
        """Extract YAML frontmatter from markdown content."""
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            return None
        
        try:
            return yaml.safe_load(frontmatter_match.group(1))
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML frontmatter: {e}")
            return None
    
    @staticmethod
    def _extract_content(content: str) -> str:
        """Extract main content after frontmatter."""
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[2].strip()
        return content
    
    @classmethod
    def _extract_technologies(cls, content: str) -> List[str]:
        """Extract technology keywords from agent content."""
        content_lower = content.lower()
        technologies = []
        
        for category, techs in cls.TECH_PATTERNS.items():
            for tech in techs:
                if tech.lower() in content_lower:
                    technologies.append(tech)
        
        return list(set(technologies))
    
    @classmethod
    def _extract_domains(cls, content: str) -> List[str]:
        """Extract domain keywords from agent content."""
        content_lower = content.lower()
        domains = []
        
        for domain, patterns in cls.DOMAIN_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in content_lower:
                    domains.append(domain)
                    break
        
        return list(set(domains))
    
    @staticmethod
    def _extract_patterns(content: str) -> List[str]:
        """Extract implementation patterns from content."""
        patterns = []
        
        # Look for pattern-related keywords
        pattern_indicators = [
            'pattern', 'architecture', 'design', 'approach', 'methodology',
            'framework', 'structure', 'organization', 'workflow'
        ]
        
        lines = content.lower().split('\n')
        for line in lines:
            for indicator in pattern_indicators:
                if indicator in line and len(line.strip()) > 20:
                    patterns.append(line.strip()[:100])  # Limit length
                    break
        
        return patterns[:10]  # Limit number of patterns
    
    @staticmethod
    def _extract_expertise_areas(content: str) -> List[str]:
        """Extract expertise areas from structured content."""
        expertise = []
        
        # Look for numbered or bulleted lists that indicate expertise
        expertise_patterns = [
            r'\*\*([^*]+)\*\*:',  # **Expertise**: pattern
            r'## ([^#\n]+)',      # ## Heading pattern
            r'### ([^#\n]+)',     # ### Subheading pattern
            r'- \*\*([^*]+)\*\*', # - **Item** pattern
        ]
        
        for pattern in expertise_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                cleaned = re.sub(r'[^a-zA-Z\s]', ' ', match).strip()
                if cleaned and len(cleaned.split()) <= 5:  # Avoid long sentences
                    expertise.append(cleaned)
        
        return list(set(expertise))[:15]  # Limit and deduplicate
    
    @staticmethod
    def _extract_examples_from_yaml(examples_data: Any) -> List[str]:
        """Extract examples from YAML frontmatter."""
        if not isinstance(examples_data, list):
            return []
        
        example_texts = []
        for example in examples_data:
            if isinstance(example, dict):
                # Extract user and assistant text from example
                if 'user' in example:
                    example_texts.append(example['user'])
                if 'assistant' in example:
                    example_texts.append(example['assistant'])
        
        return example_texts
    
    @staticmethod
    def _determine_tier(agent_name: str) -> int:
        """Determine agent tier based on decision tree mapping."""
        # Tier 1 (Core agents - always visible)
        tier_1_agents = {
            'full-stack-architect', 'mobile-developer', 'project-orchestrator',
            'security-audit-specialist', 'qa-test-engineer'
        }
        
        # Tier 2 (Specialized agents - context-triggered)
        tier_2_agents = {
            'ai-ml-engineer', 'data-engineer', 'devops-engineer', 'systems-engineer',
            'code-architect', 'accessibility-expert', 'the-critic', 'product-strategist',
            'legacy-specialist', 'platform-integrator'
        }
        
        if agent_name in tier_1_agents:
            return 1
        elif agent_name in tier_2_agents:
            return 2
        else:
            return 3  # Tier 3 (Niche/creative agents)
    
    @classmethod
    def _extract_keywords(cls, content: str) -> List[str]:
        """Extract relevant keywords using TF-IDF."""
        try:
            # Create TF-IDF vectorizer for keyword extraction
            vectorizer = TfidfVectorizer(
                max_features=50,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                token_pattern=r'\b[a-zA-Z][a-zA-Z0-9.-]*[a-zA-Z0-9]\b|\b[a-zA-Z]\b'
            )
            
            # Fit and transform content
            tfidf_matrix = vectorizer.fit_transform([content.lower()])
            
            # Get feature names and scores
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords
            top_indices = scores.argsort()[-20:][::-1]  # Top 20 keywords
            keywords = [feature_names[i] for i in top_indices if scores[i] > 0.1]
            
            return keywords
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []


class AgentCapabilityEmbedder:
    """Generate semantic embeddings for agent capabilities."""
    
    def __init__(self, 
                 model_name: str = 'all-MiniLM-L6-v2',
                 device: Optional[str] = None,
                 cache_dir: Optional[str] = None):
        """Initialize the embedder with specified model."""
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.cache_dir = cache_dir
        self.model = None
        
    async def initialize(self):
        """Initialize the embedding model."""
        try:
            logger.info(f"Loading embedding model {self.model_name} on {self.device}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            if self.cache_dir:
                self.model.cache_folder = self.cache_dir
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    def generate_embedding(self, capability: AgentCapability) -> EmbeddingResult:
        """Generate embedding for a single agent capability."""
        if not self.model:
            raise RuntimeError("Model not initialized. Call initialize() first.")
        
        try:
            # Prepare text for embedding
            embedding_text = capability.to_embedding_text()
            
            # Generate embedding
            embedding = self.model.encode(
                embedding_text,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            
            # Create content hash for change detection
            content_hash = hashlib.sha256(embedding_text.encode()).hexdigest()
            
            # Prepare metadata
            metadata = {
                'technologies': capability.technologies,
                'domains': capability.domains,
                'tier': capability.tier,
                'color': capability.color,
                'keywords': capability.keywords,
                'expertise_areas': capability.expertise_areas,
                'embedding_dimension': len(embedding),
                'content_length': len(embedding_text)
            }
            
            return EmbeddingResult(
                agent_name=capability.name,
                embedding=embedding,
                model_name=self.model_name,
                metadata=metadata,
                content_hash=content_hash
            )
            
        except Exception as e:
            logger.error(f"Error generating embedding for {capability.name}: {e}")
            raise
    
    async def generate_batch_embeddings(self, 
                                      capabilities: List[AgentCapability]) -> List[EmbeddingResult]:
        """Generate embeddings for multiple capabilities in batch."""
        if not self.model:
            raise RuntimeError("Model not initialized. Call initialize() first.")
        
        try:
            # Prepare texts
            texts = [cap.to_embedding_text() for cap in capabilities]
            
            # Generate embeddings in batch for efficiency
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=True,
                batch_size=32,
                show_progress_bar=True
            )
            
            # Create results
            results = []
            for i, capability in enumerate(capabilities):
                content_hash = hashlib.sha256(texts[i].encode()).hexdigest()
                
                metadata = {
                    'technologies': capability.technologies,
                    'domains': capability.domains,
                    'tier': capability.tier,
                    'color': capability.color,
                    'keywords': capability.keywords,
                    'expertise_areas': capability.expertise_areas,
                    'embedding_dimension': len(embeddings[i]),
                    'content_length': len(texts[i])
                }
                
                results.append(EmbeddingResult(
                    agent_name=capability.name,
                    embedding=embeddings[i],
                    model_name=self.model_name,
                    metadata=metadata,
                    content_hash=content_hash
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise


class AgentEmbeddingManager:
    """Manage agent embeddings with database persistence."""
    
    def __init__(self, 
                 db_url: str,
                 agents_dir: str = "agents",
                 model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the embedding manager."""
        self.db_url = db_url
        self.agents_dir = Path(agents_dir)
        self.model_name = model_name
        self.embedder = AgentCapabilityEmbedder(model_name)
        self.parser = AgentMarkdownParser()
        self.db_pool = None
        
    async def initialize(self):
        """Initialize database connection and embedder."""
        # Initialize database pool
        self.db_pool = await asyncpg.create_pool(
            self.db_url,
            min_size=2,
            max_size=10,
            command_timeout=30
        )
        
        # Initialize embedder
        await self.embedder.initialize()
        
        logger.info("Agent embedding manager initialized")
    
    async def close(self):
        """Close database connections."""
        if self.db_pool:
            await self.db_pool.close()
    
    async def scan_and_process_agents(self) -> Dict[str, EmbeddingResult]:
        """Scan agent directory and process all agent files."""
        if not self.agents_dir.exists():
            raise FileNotFoundError(f"Agents directory not found: {self.agents_dir}")
        
        logger.info(f"Scanning agents directory: {self.agents_dir}")
        
        # Find all agent markdown files
        agent_files = list(self.agents_dir.glob("*.md"))
        agent_files = [f for f in agent_files if not f.name.startswith("AGENT_")]
        
        logger.info(f"Found {len(agent_files)} agent files")
        
        # Parse capabilities
        capabilities = []
        for file_path in agent_files:
            capability = await self.parser.parse_agent_file(file_path)
            if capability:
                capabilities.append(capability)
        
        logger.info(f"Successfully parsed {len(capabilities)} agent capabilities")
        
        # Generate embeddings
        embedding_results = await self.embedder.generate_batch_embeddings(capabilities)
        
        # Store in database
        await self._store_embeddings(embedding_results)
        
        # Return results as dict
        return {result.agent_name: result for result in embedding_results}
    
    async def update_agent_embedding(self, agent_name: str) -> Optional[EmbeddingResult]:
        """Update embedding for a single agent."""
        agent_file = self.agents_dir / f"{agent_name}.md"
        if not agent_file.exists():
            logger.error(f"Agent file not found: {agent_file}")
            return None
        
        # Parse capability
        capability = await self.parser.parse_agent_file(agent_file)
        if not capability:
            return None
        
        # Generate embedding
        result = self.embedder.generate_embedding(capability)
        
        # Store in database
        await self._store_embeddings([result])
        
        return result
    
    async def _store_embeddings(self, results: List[EmbeddingResult]):
        """Store embedding results in database."""
        if not self.db_pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                for result in results:
                    # Convert numpy array to list for JSON storage
                    embedding_list = result.embedding.tolist()
                    
                    await conn.execute("""
                        INSERT INTO agent_embeddings 
                        (agent_name, embedding_model, capability_vector, metadata, content_hash, updated_at)
                        VALUES ($1, $2, $3, $4, $5, NOW())
                        ON CONFLICT (agent_name, embedding_model) 
                        DO UPDATE SET
                            capability_vector = EXCLUDED.capability_vector,
                            metadata = EXCLUDED.metadata,
                            content_hash = EXCLUDED.content_hash,
                            updated_at = NOW()
                    """, 
                        result.agent_name,
                        result.model_name,
                        embedding_list,
                        json.dumps(result.metadata),
                        result.content_hash
                    )
        
        logger.info(f"Stored {len(results)} agent embeddings in database")
    
    async def get_agent_embeddings(self, 
                                  agent_names: Optional[List[str]] = None) -> Dict[str, np.ndarray]:
        """Retrieve agent embeddings from database."""
        if not self.db_pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self.db_pool.acquire() as conn:
            if agent_names:
                rows = await conn.fetch("""
                    SELECT agent_name, capability_vector
                    FROM agent_embeddings
                    WHERE embedding_model = $1 AND agent_name = ANY($2)
                """, self.model_name, agent_names)
            else:
                rows = await conn.fetch("""
                    SELECT agent_name, capability_vector
                    FROM agent_embeddings
                    WHERE embedding_model = $1
                """, self.model_name)
        
        # Convert to numpy arrays
        embeddings = {}
        for row in rows:
            embeddings[row['agent_name']] = np.array(row['capability_vector'])
        
        return embeddings
    
    async def get_agent_metadata(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific agent."""
        if not self.db_pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT metadata, content_hash, updated_at
                FROM agent_embeddings
                WHERE agent_name = $1 AND embedding_model = $2
            """, agent_name, self.model_name)
        
        if row:
            metadata = json.loads(row['metadata'])
            metadata['content_hash'] = row['content_hash']
            metadata['updated_at'] = row['updated_at']
            return metadata
        
        return None


# CLI and utility functions
async def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate agent capability embeddings")
    parser.add_argument("--agents-dir", default="agents", help="Path to agents directory")
    parser.add_argument("--db-url", required=True, help="PostgreSQL database URL")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="Embedding model name")
    parser.add_argument("--agent", help="Process specific agent only")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize manager
    manager = AgentEmbeddingManager(
        db_url=args.db_url,
        agents_dir=args.agents_dir,
        model_name=args.model
    )
    
    try:
        await manager.initialize()
        
        if args.agent:
            # Process single agent
            result = await manager.update_agent_embedding(args.agent)
            if result:
                logger.info(f"Updated embedding for {args.agent}")
            else:
                logger.error(f"Failed to update embedding for {args.agent}")
        else:
            # Process all agents
            results = await manager.scan_and_process_agents()
            logger.info(f"Processed {len(results)} agents successfully")
            
            # Print summary
            for agent_name, result in results.items():
                print(f"✓ {agent_name}: {result.metadata.get('embedding_dimension')}D embedding")
        
    finally:
        await manager.close()


if __name__ == "__main__":
    asyncio.run(main())