"""
Context Synthesis Engine - LLM-powered semantic search and answer generation.

This module provides tools to:
- Build searchable semantic indexes from enriched history
- Perform natural language queries across git + GitHub data
- Generate coherent answers from fragmented sources
- Track citations and confidence scores
- Correlate multi-source information
"""

import os
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Set
from pathlib import Path
import hashlib

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import numpy as np
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

from .git_analyzer import Commit, RepositoryHistory
from .github_integrator import EnrichedHistory, EnrichedCommit


@dataclass
class Citation:
    """Source citation for an answer."""

    commit_sha: str
    commit_message: str
    commit_date: datetime
    author: str
    source_type: str  # "commit", "pr", "issue", "comment"
    source_id: Optional[str] = None  # PR/issue number
    relevance_score: float = 0.0
    excerpt: str = ""
    url: str = ""

    def __hash__(self):
        return hash(self.commit_sha + (self.source_id or ""))


@dataclass
class Answer:
    """Generated answer with citations and confidence."""

    question: str
    answer: str
    citations: List[Citation]
    confidence: float  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    reasoning: str = ""  # Internal reasoning/chain of thought

    @property
    def credibility_score(self) -> float:
        """
        Calculate credibility based on citations and confidence.

        High credibility requires:
        - Multiple citations (3+)
        - Recent commits preferred
        - High relevance scores
        - High confidence
        """
        if not self.citations:
            return 0.0

        # Base score from confidence
        score = self.confidence

        # Boost for multiple citations
        if len(self.citations) >= 3:
            score += 0.2
        elif len(self.citations) >= 2:
            score += 0.1

        # Average relevance of top 3 citations
        top_relevance = sum(c.relevance_score for c in self.citations[:3]) / min(3, len(self.citations))
        score += top_relevance * 0.2

        return min(1.0, score)


@dataclass
class SearchResult:
    """Single search result with score."""

    commit: EnrichedCommit
    relevance_score: float
    matched_content: str  # The specific content that matched


@dataclass
class SearchableIndex:
    """Searchable index of repository history."""

    enriched_history: EnrichedHistory
    embeddings: Optional[np.ndarray] = None  # type: ignore
    documents: List[str] = field(default_factory=list)
    document_metadata: List[Dict] = field(default_factory=list)
    faiss_index: Optional[object] = None  # FAISS index

    @property
    def size(self) -> int:
        """Number of indexed documents."""
        return len(self.documents)


class EmbeddingProvider:
    """Abstract embedding provider interface."""

    def embed(self, texts: List[str]) -> np.ndarray:  # type: ignore
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        raise NotImplementedError

    @property
    def dimension(self) -> int:
        """Embedding dimension."""
        raise NotImplementedError


class ClaudeEmbeddingProvider(EmbeddingProvider):
    """Use Claude (Anthropic) for embeddings via text summarization."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Claude embedding provider."""
        if not HAS_ANTHROPIC:
            raise ImportError("anthropic package required. Install: pip install anthropic")

        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY required")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def embed(self, texts: List[str]) -> np.ndarray:  # type: ignore
        """
        Generate embeddings using Claude.

        Note: Anthropic doesn't provide embeddings API yet, so we use
        a workaround with text hashing and similarity. This is a placeholder
        for future proper embedding support.
        """
        # Placeholder: Use simple hash-based "embeddings"
        # In production, use a proper embedding model or wait for Anthropic embeddings API
        import hashlib

        embeddings = []
        for text in texts:
            # Simple hash-based embedding (not semantic, just for demo)
            hash_bytes = hashlib.sha256(text.encode()).digest()
            # Convert to 256-dimensional vector
            vec = np.frombuffer(hash_bytes[:256], dtype=np.uint8).astype(np.float32)
            vec = vec / 255.0  # Normalize to [0, 1]
            embeddings.append(vec)

        return np.array(embeddings)

    @property
    def dimension(self) -> int:
        """Embedding dimension (256 for hash-based)."""
        return 256


class SimpleEmbeddingProvider(EmbeddingProvider):
    """Simple TF-IDF based embeddings (no external dependencies)."""

    def __init__(self, max_features: int = 512):
        """Initialize simple embedding provider."""
        self.max_features = max_features
        self._vocabulary: Optional[Dict[str, int]] = None

    def _build_vocabulary(self, texts: List[str]) -> Dict[str, int]:
        """Build vocabulary from texts."""
        from collections import Counter
        import re

        # Tokenize all texts
        all_tokens = []
        for text in texts:
            tokens = re.findall(r'\w+', text.lower())
            all_tokens.extend(tokens)

        # Get top N most common tokens
        counter = Counter(all_tokens)
        top_tokens = [token for token, _ in counter.most_common(self.max_features)]

        # Create vocabulary mapping
        vocab = {token: i for i, token in enumerate(top_tokens)}
        return vocab

    def embed(self, texts: List[str]) -> np.ndarray:  # type: ignore
        """Generate simple TF-IDF embeddings."""
        import re

        # Build vocabulary if needed
        if self._vocabulary is None:
            self._vocabulary = self._build_vocabulary(texts)

        embeddings = []
        for text in texts:
            # Tokenize
            tokens = re.findall(r'\w+', text.lower())

            # Create vector
            vec = np.zeros(len(self._vocabulary), dtype=np.float32)
            for token in tokens:
                if token in self._vocabulary:
                    vec[self._vocabulary[token]] += 1.0

            # Simple normalization
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm

            embeddings.append(vec)

        return np.array(embeddings)

    @property
    def dimension(self) -> int:
        """Embedding dimension."""
        return self.max_features


class ContextSynthesizer:
    """Main context synthesis engine."""

    def __init__(self, embedding_provider: Optional[EmbeddingProvider] = None):
        """
        Initialize context synthesizer.

        Args:
            embedding_provider: Provider for text embeddings (default: SimpleEmbeddingProvider)
        """
        self.embedding_provider = embedding_provider or SimpleEmbeddingProvider()

    def _extract_documents(self, enriched_history: EnrichedHistory) -> Tuple[List[str], List[Dict]]:
        """
        Extract searchable documents from enriched history.

        Returns:
            Tuple of (documents, metadata)
        """
        documents = []
        metadata = []

        for enriched_commit in enriched_history.enriched_commits:
            commit = enriched_commit.commit

            # Document 1: Commit message
            doc_text = f"{commit.message}\n\nAuthor: {commit.author}\nDate: {commit.date}"
            documents.append(doc_text)
            metadata.append({
                'type': 'commit',
                'sha': commit.sha,
                'author': commit.author,
                'date': commit.date.isoformat(),
                'enriched_commit': enriched_commit,
            })

            # Document 2: PR discussion (if available)
            if enriched_commit.pull_request:
                pr = enriched_commit.pull_request
                pr_text = f"PR #{pr.number}: {pr.title}\n\n{pr.body}\n\n{pr.discussion_summary}"
                documents.append(pr_text)
                metadata.append({
                    'type': 'pr',
                    'sha': commit.sha,
                    'pr_number': pr.number,
                    'enriched_commit': enriched_commit,
                })

            # Document 3: Related issues
            for issue in enriched_commit.related_issues:
                issue_text = f"Issue #{issue.number}: {issue.title}\n\n{issue.body}"
                issue_text += "\n\n" + "\n\n".join(c.body for c in issue.comments)
                documents.append(issue_text)
                metadata.append({
                    'type': 'issue',
                    'sha': commit.sha,
                    'issue_number': issue.number,
                    'enriched_commit': enriched_commit,
                })

        return documents, metadata

    def build_searchable_index(self, enriched_history: EnrichedHistory) -> SearchableIndex:
        """
        Build searchable semantic index from enriched history.

        Args:
            enriched_history: EnrichedHistory to index

        Returns:
            SearchableIndex ready for querying
        """
        print(f"Building searchable index...")

        # Extract documents
        documents, metadata = self._extract_documents(enriched_history)
        print(f"  Extracted {len(documents)} documents")

        # Generate embeddings
        print(f"  Generating embeddings...")
        if not HAS_FAISS:
            print("  Warning: FAISS not available, using simple search")
            embeddings = self.embedding_provider.embed(documents)
            faiss_index = None
        else:
            embeddings = self.embedding_provider.embed(documents)

            # Build FAISS index
            print(f"  Building FAISS index...")
            dimension = embeddings.shape[1]
            faiss_index = faiss.IndexFlatL2(dimension)
            faiss_index.add(embeddings)

        print(f"✓ Index built: {len(documents)} documents, {embeddings.shape[1]} dimensions")

        return SearchableIndex(
            enriched_history=enriched_history,
            embeddings=embeddings,
            documents=documents,
            document_metadata=metadata,
            faiss_index=faiss_index,
        )

    def search(self, index: SearchableIndex, query: str, k: int = 10) -> List[SearchResult]:
        """
        Search the index with a natural language query.

        Args:
            index: SearchableIndex to search
            query: Natural language query
            k: Number of results to return

        Returns:
            List of SearchResult objects, sorted by relevance
        """
        # Generate query embedding
        query_embedding = self.embedding_provider.embed([query])[0]

        if index.faiss_index is not None:
            # Use FAISS for fast search
            distances, indices = index.faiss_index.search(
                query_embedding.reshape(1, -1), k
            )

            results = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                meta = index.document_metadata[idx]
                enriched_commit = meta['enriched_commit']

                # Convert distance to similarity score (0-1)
                similarity = 1.0 / (1.0 + dist)

                results.append(SearchResult(
                    commit=enriched_commit,
                    relevance_score=similarity,
                    matched_content=index.documents[idx][:500],
                ))
        else:
            # Simple cosine similarity search
            similarities = []
            for doc_emb in index.embeddings:
                # Cosine similarity
                sim = np.dot(query_embedding, doc_emb) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(doc_emb) + 1e-10
                )
                similarities.append(sim)

            # Get top k
            top_indices = np.argsort(similarities)[::-1][:k]

            results = []
            for idx in top_indices:
                meta = index.document_metadata[idx]
                enriched_commit = meta['enriched_commit']

                results.append(SearchResult(
                    commit=enriched_commit,
                    relevance_score=float(similarities[idx]),
                    matched_content=index.documents[idx][:500],
                ))

        return results

    def synthesize_answer(self, index: SearchableIndex, question: str,
                          max_results: int = 10) -> Answer:
        """
        Generate a coherent answer from search results.

        Args:
            index: SearchableIndex to query
            question: Natural language question
            max_results: Maximum search results to consider

        Returns:
            Answer object with citations and confidence
        """
        print(f"Synthesizing answer for: {question}")

        # Search for relevant documents
        search_results = self.search(index, question, k=max_results)
        print(f"  Found {len(search_results)} relevant documents")

        if not search_results:
            return Answer(
                question=question,
                answer="No relevant information found in repository history.",
                citations=[],
                confidence=0.0,
            )

        # Extract citations
        citations = []
        for result in search_results[:5]:  # Top 5 for citations
            commit = result.commit.commit
            citation = Citation(
                commit_sha=commit.sha,
                commit_message=commit.summary,
                commit_date=commit.date,
                author=commit.author,
                source_type='commit',
                relevance_score=result.relevance_score,
                excerpt=result.matched_content[:200],
            )

            # Add PR citation if available
            if result.commit.pull_request:
                pr = result.commit.pull_request
                citation.source_type = 'pr'
                citation.source_id = str(pr.number)
                citation.url = pr.url
                citation.excerpt = pr.title

            citations.append(citation)

        # Generate answer from search results
        # For now, use simple heuristic-based answer generation
        # In production, this would use LLM with RAG
        answer_text = self._generate_answer_heuristic(question, search_results)
        confidence = self._calculate_confidence(search_results)

        return Answer(
            question=question,
            answer=answer_text,
            citations=citations,
            confidence=confidence,
            reasoning=f"Based on {len(search_results)} relevant commits and discussions",
        )

    def _generate_answer_heuristic(self, question: str, results: List[SearchResult]) -> str:
        """
        Generate answer using heuristics (placeholder for LLM generation).

        In production, this would use Claude/GPT-4 with RAG.
        """
        if not results:
            return "No relevant information found."

        # Extract key information
        top_result = results[0]
        commit = top_result.commit

        parts = []
        parts.append(f"Based on repository history analysis:")
        parts.append(f"")

        # Most relevant commit
        parts.append(f"The most relevant commit is {commit.commit.sha[:8]} by {commit.commit.author}:")
        parts.append(f"\"{commit.commit.summary}\"")
        parts.append(f"")

        # Add PR context if available
        if commit.pull_request:
            pr = commit.pull_request
            parts.append(f"This was part of PR #{pr.number}: \"{pr.title}\"")
            if pr.body:
                parts.append(f"{pr.body[:200]}...")
            parts.append(f"")

        # Summary
        parts.append(f"Found {len(results)} related commits spanning from {results[-1].commit.commit.date.date()} to {results[0].commit.commit.date.date()}.")

        return "\n".join(parts)

    def _calculate_confidence(self, results: List[SearchResult]) -> float:
        """Calculate confidence score for answer."""
        if not results:
            return 0.0

        # Simple heuristic: average of top 3 relevance scores
        top_scores = [r.relevance_score for r in results[:3]]
        avg_score = sum(top_scores) / len(top_scores)

        # Boost if multiple high-quality results
        if len(results) >= 3 and avg_score > 0.7:
            return min(1.0, avg_score + 0.1)

        return avg_score

    def export_index(self, index: SearchableIndex, output_path: str):
        """
        Export searchable index to disk.

        Args:
            index: SearchableIndex to export
            output_path: Path to write index
        """
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save documents and metadata
        with open(output_path / 'documents.json', 'w') as f:
            json.dump({
                'documents': index.documents,
                'metadata': [
                    {k: v for k, v in meta.items() if k != 'enriched_commit'}
                    for meta in index.document_metadata
                ],
            }, f, indent=2, default=str)

        # Save embeddings
        if index.embeddings is not None:
            np.save(output_path / 'embeddings.npy', index.embeddings)

        # Save FAISS index
        if index.faiss_index is not None:
            faiss.write_index(index.faiss_index, str(output_path / 'faiss.index'))

        print(f"Index exported to: {output_path}")


def main():
    """CLI entry point for testing."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python context_synthesizer.py <enriched_history.json> [query]")
        sys.exit(1)

    # For now, just demonstrate the API
    print("Context Synthesizer")
    print("=" * 60)
    print("This module provides semantic search and answer generation.")
    print("Full integration requires enriched history from Week 2.")


if __name__ == '__main__':
    main()
