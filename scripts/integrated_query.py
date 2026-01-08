#!/usr/bin/env python3
"""
Integrated Dependency + Vector DB Query Tool

Combines dependency graph analysis with vector database semantic search
to provide targeted, context-aware queries when premises change.

Usage:
    python scripts/integrated_query.py --premise timeline_deep_time --search "evacuation timeline"
    python scripts/integrated_query.py --chapter 21_Chapter_20 --search "Phase Two maintenance"
    python scripts/integrated_query.py --concept "Moon-Tug" --search "propulsion system"
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Set
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


class IntegratedQuery:
    """Combines dependency analysis with vector search"""
    
    def __init__(self, deps_file: str = 'reports/dependencies.json',
                 qdrant_host: str = 'localhost', qdrant_port: int = 6333):
        self.deps_file = Path(deps_file)
        self.dependencies = None
        self.qdrant_client = None
        self.model = None
        
        self.load_dependencies()
        self.connect_qdrant(qdrant_host, qdrant_port)
    
    def load_dependencies(self):
        """Load dependency graph"""
        if not self.deps_file.exists():
            print(f"❌ Dependency file not found: {self.deps_file}")
            print("   Run: ./exec/build_dependency_graph")
            sys.exit(1)
        
        with open(self.deps_file, 'r') as f:
            self.dependencies = json.load(f)
    
    def connect_qdrant(self, host: str, port: int):
        """Connect to Qdrant vector database"""
        try:
            self.qdrant_client = QdrantClient(host=host, port=port)
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print(f"✓ Connected to Qdrant at {host}:{port}")
        except Exception as e:
            print(f"⚠️  Could not connect to Qdrant: {e}")
            print("   Vector search will be unavailable")
    
    def query_with_context(self, query: str, target_docs: List[str], limit: int = 10) -> List[Dict]:
        """
        Perform vector search limited to specific documents
        
        Args:
            query: Search query text
            target_docs: List of document names to search within
            limit: Maximum results to return
        """
        if not self.qdrant_client:
            return []
        
        # Generate query embedding
        query_vector = self.model.encode(query).tolist()
        
        # Build filter for target documents
        # Qdrant filter syntax: match any of the target documents
        doc_filter = {
            "should": [
                {"key": "chapter", "match": {"value": doc}}
                for doc in target_docs
            ]
        }
        
        # Search with filter
        results = self.qdrant_client.search(
            collection_name="planetary_exodus_docs",
            query_vector=query_vector,
            limit=limit,
            query_filter=doc_filter
        )
        
        return [
            {
                'chapter': hit.payload['chapter'],
                'section': hit.payload.get('section', 'Unknown'),
                'content': hit.payload['content'][:200] + '...',
                'score': hit.score
            }
            for hit in results
        ]
    
    def premise_impact_search(self, premise_id: str, search_query: str) -> Dict:
        """
        Find impact of premise change + search for specific content
        
        Args:
            premise_id: Premise identifier (e.g., 'timeline_deep_time')
            search_query: Semantic search query
        """
        if premise_id not in self.dependencies['premise_chains']:
            return {'error': f'Premise {premise_id} not found'}
        
        # Get affected documents
        affected = self.dependencies['premise_chains'][premise_id]
        affected_docs = [doc['document'] for doc in affected]
        
        # Perform targeted search within affected documents
        search_results = self.query_with_context(search_query, affected_docs)
        
        # Sort affected by strength
        affected_sorted = sorted(affected, key=lambda x: x['strength'], reverse=True)
        
        return {
            'premise': premise_id,
            'affected_documents': affected_sorted,
            'total_affected': len(affected_sorted),
            'search_query': search_query,
            'search_results': search_results,
            'high_priority': [d for d in affected_sorted if d['strength'] > 5],
            'recommendations': self._generate_recommendations(affected_sorted, search_results)
        }
    
    def chapter_impact_search(self, chapter: str, search_query: str) -> Dict:
        """
        Find chapter dependencies + search for specific content
        
        Args:
            chapter: Chapter name
            search_query: Semantic search query
        """
        if chapter not in self.dependencies['documents']:
            return {'error': f'Chapter {chapter} not found'}
        
        # Get dependent chapters
        direct_deps = self.dependencies['reverse_dependencies'].get(chapter, [])
        
        # Get chapters sharing concepts
        shared_concept_docs = set()
        for concept, docs in self.dependencies['concept_usage'].items():
            if chapter in docs:
                shared_concept_docs.update(docs)
        shared_concept_docs.discard(chapter)
        
        # Combined target set
        all_targets = list(set(direct_deps) | shared_concept_docs)
        
        # Perform targeted search
        search_results = self.query_with_context(search_query, all_targets)
        
        return {
            'changed_chapter': chapter,
            'directly_affected': direct_deps,
            'conceptually_related': sorted(shared_concept_docs),
            'search_query': search_query,
            'search_results': search_results,
            'total_targets': len(all_targets),
            'recommendations': self._generate_recommendations(
                [{'document': d, 'strength': 5} for d in direct_deps],
                search_results
            )
        }
    
    def concept_search(self, concept: str, search_query: str) -> Dict:
        """
        Find concept usage + search for specific content
        
        Args:
            concept: Concept name
            search_query: Semantic search query
        """
        # Find matching concepts (case-insensitive)
        matching_concepts = [
            c for c in self.dependencies['concept_usage'].keys()
            if concept.lower() in c.lower()
        ]
        
        if not matching_concepts:
            return {'error': f'Concept "{concept}" not found'}
        
        # Get all documents using these concepts
        all_docs = set()
        for matched_concept in matching_concepts:
            all_docs.update(self.dependencies['concept_usage'][matched_concept])
        
        # Perform targeted search
        search_results = self.query_with_context(search_query, list(all_docs))
        
        return {
            'concept': concept,
            'matched_concepts': matching_concepts,
            'documents_using_concept': sorted(all_docs),
            'usage_count': len(all_docs),
            'search_query': search_query,
            'search_results': search_results
        }
    
    def _generate_recommendations(self, affected: List[Dict], search_results: List[Dict]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        if not affected and not search_results:
            recommendations.append("✅ No immediate impact detected")
            return recommendations
        
        # High-impact documents
        high_impact = [d for d in affected if d.get('strength', 0) > 5]
        if high_impact:
            recommendations.append(
                f"🔴 Review {len(high_impact)} high-impact document(s): " +
                ", ".join(d['document'] for d in high_impact[:3])
            )
        
        # Search results with high relevance
        high_relevance = [r for r in search_results if r['score'] > 0.7]
        if high_relevance:
            recommendations.append(
                f"🎯 Found {len(high_relevance)} highly relevant section(s) needing attention"
            )
        
        # Specific sections to review
        if search_results:
            top_result = search_results[0]
            recommendations.append(
                f"📖 Start with: {top_result['chapter']} - {top_result['section']}"
            )
        
        return recommendations
    
    def print_results(self, results: Dict):
        """Pretty print query results"""
        
        if 'error' in results:
            print(f"\n❌ {results['error']}\n")
            return
        
        print("\n" + "=" * 80)
        
        if 'premise' in results:
            print(f"🧠 PREMISE IMPACT ANALYSIS: {results['premise']}")
            print("=" * 80)
            print(f"\n📊 Total affected: {results['total_affected']} documents")
            
            if results['high_priority']:
                print(f"\n🔴 HIGH PRIORITY ({len(results['high_priority'])} documents):")
                for doc in results['high_priority']:
                    print(f"   - {doc['document']} (strength: {doc['strength']})")
        
        elif 'changed_chapter' in results:
            print(f"📖 CHAPTER IMPACT ANALYSIS: {results['changed_chapter']}")
            print("=" * 80)
            print(f"\n📊 Direct dependencies: {len(results['directly_affected'])}")
            print(f"📊 Conceptually related: {len(results['conceptually_related'])}")
        
        elif 'concept' in results:
            print(f"🔑 CONCEPT ANALYSIS: {results['concept']}")
            print("=" * 80)
            print(f"\n📊 Usage count: {results['usage_count']} documents")
        
        # Search results
        if results.get('search_results'):
            print(f"\n🔍 SEMANTIC SEARCH RESULTS")
            print(f"Query: \"{results['search_query']}\"")
            print(f"Found: {len(results['search_results'])} relevant sections\n")
            
            for i, result in enumerate(results['search_results'], 1):
                print(f"{i}. [{result['chapter']}] {result['section']}")
                print(f"   Score: {result['score']:.3f}")
                print(f"   {result['content']}\n")
        
        # Recommendations
        if results.get('recommendations'):
            print("💡 RECOMMENDATIONS")
            for rec in results['recommendations']:
                print(f"   {rec}")
        
        print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Integrated dependency + vector DB query tool'
    )
    parser.add_argument(
        '--premise',
        help='Query impact if premise changes'
    )
    parser.add_argument(
        '--chapter',
        help='Query impact if chapter changes'
    )
    parser.add_argument(
        '--concept',
        help='Query concept usage'
    )
    parser.add_argument(
        '--search',
        required=True,
        help='Semantic search query to run on affected documents'
    )
    parser.add_argument(
        '--deps-file',
        default='/app/output/reports/dependencies.json',
        help='Path to dependencies JSON file'
    )
    parser.add_argument(
        '--qdrant-host',
        default='qdrant',
        help='Qdrant host (default: qdrant for Docker, localhost for local)'
    )
    parser.add_argument(
        '--qdrant-port',
        type=int,
        default=6333,
        help='Qdrant port (default: 6333)'
    )
    
    args = parser.parse_args()
    
    # Validate that exactly one of premise/chapter/concept is specified
    specified = sum([bool(args.premise), bool(args.chapter), bool(args.concept)])
    if specified != 1:
        parser.error("Specify exactly one of: --premise, --chapter, or --concept")
    
    # Create query engine
    query = IntegratedQuery(args.deps_file, args.qdrant_host, args.qdrant_port)
    
    # Execute query
    if args.premise:
        results = query.premise_impact_search(args.premise, args.search)
    elif args.chapter:
        results = query.chapter_impact_search(args.chapter, args.search)
    elif args.concept:
        results = query.concept_search(args.concept, args.search)
    
    # Print results
    query.print_results(results)


if __name__ == '__main__':
    main()
