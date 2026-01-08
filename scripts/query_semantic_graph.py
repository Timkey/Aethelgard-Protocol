#!/usr/bin/env python3
"""
Query Semantic Dependency Graph

Find which paragraphs are semantically related to a given paragraph.
When you update content, this tells you exactly what else to review.

Usage:
    python scripts/query_semantic_graph.py --document "21_Chapter_20" --section "Phase Two"
    python scripts/query_semantic_graph.py --paragraph-id 152
    python scripts/query_semantic_graph.py --search "solar brightening evacuation"
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List
from sentence_transformers import SentenceTransformer


class SemanticGraphQuery:
    """Query interface for semantic dependency graph"""
    
    def __init__(self, graph_file: str = '/app/output/reports/semantic_graph.json'):
        self.graph_file = Path(graph_file)
        self.graph_data = None
        self.model = None
        self.load_graph()
    
    def load_graph(self):
        """Load semantic graph data"""
        if not self.graph_file.exists():
            print(f"❌ Semantic graph not found: {self.graph_file}")
            print("   Run: ./exec/build_semantic_graph")
            sys.exit(1)
        
        with open(self.graph_file, 'r') as f:
            self.graph_data = json.load(f)
        
        print(f"✓ Loaded semantic graph:")
        print(f"  - {self.graph_data['metadata']['total_paragraphs']} paragraphs")
        print(f"  - {self.graph_data['metadata']['total_edges']} connections")
        print(f"  - Threshold: {self.graph_data['metadata']['similarity_threshold']}")
    
    def find_related_paragraphs(self, paragraph_id: int, min_similarity: float = None) -> List[Dict]:
        """Find all paragraphs semantically related to given paragraph"""
        
        if min_similarity is None:
            min_similarity = self.graph_data['metadata']['similarity_threshold']
        
        # Find edges involving this paragraph
        related = []
        for edge in self.graph_data['edges']:
            if edge['para1_id'] == paragraph_id or edge['para2_id'] == paragraph_id:
                if edge['similarity'] >= min_similarity:
                    # Get the other paragraph ID
                    other_id = edge['para2_id'] if edge['para1_id'] == paragraph_id else edge['para1_id']
                    other_para = self._get_paragraph(other_id)
                    
                    related.append({
                        'paragraph': other_para,
                        'similarity': edge['similarity'],
                        'edge': edge
                    })
        
        # Sort by similarity
        related.sort(key=lambda x: x['similarity'], reverse=True)
        
        return related
    
    def find_by_document_section(self, document: str, section: str = None) -> List[Dict]:
        """Find paragraphs in a specific document/section and their relations"""
        
        matches = []
        for para in self.graph_data['paragraphs']:
            if para['document'] == document:
                if section is None or section.lower() in para['section'].lower():
                    # Find related paragraphs
                    related = self.find_related_paragraphs(para['id'])
                    
                    matches.append({
                        'paragraph': para,
                        'related_count': len(related),
                        'related': related[:5]  # Top 5 most similar
                    })
        
        # Sort by number of relations
        matches.sort(key=lambda x: x['related_count'], reverse=True)
        
        return matches
    
    def search_by_content(self, query: str, top_k: int = 10) -> List[Dict]:
        """Find paragraphs semantically similar to query text"""
        
        if self.model is None:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Encode query
        query_embedding = self.model.encode(query)
        
        # Compare with all paragraphs (need to recompute embeddings)
        # For efficiency, we'll just do text search in this version
        results = []
        query_lower = query.lower()
        
        for para in self.graph_data['paragraphs']:
            # Simple text matching for now
            if query_lower in para['content'].lower():
                related = self.find_related_paragraphs(para['id'])
                results.append({
                    'paragraph': para,
                    'related_count': len(related),
                    'related': related[:5]
                })
        
        results.sort(key=lambda x: x['related_count'], reverse=True)
        return results[:top_k]
    
    def get_cluster_members(self, cluster_id: int) -> List[Dict]:
        """Get all paragraphs in a semantic cluster"""
        
        cluster_id_str = str(cluster_id)
        if cluster_id_str not in self.graph_data['clusters']:
            return []
        
        member_ids = self.graph_data['clusters'][cluster_id_str]
        
        members = []
        for para_id in member_ids:
            para = self._get_paragraph(para_id)
            members.append(para)
        
        return members
    
    def _get_paragraph(self, para_id: int) -> Dict:
        """Get paragraph by ID"""
        for para in self.graph_data['paragraphs']:
            if para['id'] == para_id:
                return para
        return None
    
    def print_results(self, results: List[Dict], title: str):
        """Pretty print query results"""
        
        print("\n" + "=" * 80)
        print(f"🔍 {title}")
        print("=" * 80)
        
        if not results:
            print("\n❌ No results found\n")
            return
        
        for i, result in enumerate(results[:10], 1):
            para = result['paragraph']
            
            print(f"\n### Result {i}: {result['related_count']} related paragraphs")
            print(f"**Document:** {para['document']}")
            print(f"**Section:** {para['section']}")
            print(f"**Paragraph ID:** {para['id']}")
            print(f"\n**Content:**")
            print(f"{para['content'][:300]}...")
            
            if result.get('related'):
                print(f"\n**Top related paragraphs:**")
                for rel in result['related'][:3]:
                    rel_para = rel['paragraph']
                    print(f"\n  - [{rel_para['document']}] {rel_para['section']}")
                    print(f"    Similarity: {rel['similarity']:.3f}")
                    print(f"    {rel_para['content'][:150]}...")
        
        print("\n" + "=" * 80 + "\n")
    
    def print_paragraph_impact(self, paragraph_id: int, related: List[Dict]):
        """Print impact analysis for a specific paragraph"""
        
        para = self._get_paragraph(paragraph_id)
        if not para:
            print(f"\n❌ Paragraph {paragraph_id} not found\n")
            return
        
        print("\n" + "=" * 80)
        print(f"📊 IMPACT ANALYSIS: Paragraph {paragraph_id}")
        print("=" * 80)
        
        print(f"\n**Source:**")
        print(f"Document: {para['document']}")
        print(f"Section: {para['section']}")
        print(f"\n**Content:**")
        print(f"{para['content'][:400]}...")
        
        print(f"\n\n**Impact: {len(related)} related paragraphs across {len(set(r['paragraph']['document'] for r in related))} documents**")
        
        # Group by document
        by_doc = {}
        for rel in related:
            doc = rel['paragraph']['document']
            if doc not in by_doc:
                by_doc[doc] = []
            by_doc[doc].append(rel)
        
        print(f"\n**Affected Documents:**")
        for doc in sorted(by_doc.keys()):
            rels = by_doc[doc]
            avg_sim = sum(r['similarity'] for r in rels) / len(rels)
            print(f"\n  🔴 {doc}: {len(rels)} paragraphs (avg similarity: {avg_sim:.3f})")
            
            # Show top 2
            for rel in sorted(rels, key=lambda x: x['similarity'], reverse=True)[:2]:
                rel_para = rel['paragraph']
                print(f"     - [{rel_para['section']}] similarity: {rel['similarity']:.3f}")
                print(f"       {rel_para['content'][:100]}...")
        
        print("\n" + "=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Query semantic dependency graph'
    )
    parser.add_argument(
        '--paragraph-id',
        type=int,
        help='Find related paragraphs for specific paragraph ID'
    )
    parser.add_argument(
        '--document',
        help='Find paragraphs in specific document'
    )
    parser.add_argument(
        '--section',
        help='Filter by section name (use with --document)'
    )
    parser.add_argument(
        '--search',
        help='Search for paragraphs by content'
    )
    parser.add_argument(
        '--cluster',
        type=int,
        help='Show members of semantic cluster'
    )
    parser.add_argument(
        '--graph-file',
        default='/app/output/reports/semantic_graph.json',
        help='Path to semantic graph JSON'
    )
    
    args = parser.parse_args()
    
    query = SemanticGraphQuery(args.graph_file)
    
    if args.paragraph_id is not None:
        related = query.find_related_paragraphs(args.paragraph_id)
        query.print_paragraph_impact(args.paragraph_id, related)
    
    elif args.document:
        results = query.find_by_document_section(args.document, args.section)
        title = f"Paragraphs in {args.document}"
        if args.section:
            title += f" / {args.section}"
        query.print_results(results, title)
    
    elif args.search:
        results = query.search_by_content(args.search)
        query.print_results(results, f"Search: '{args.search}'")
    
    elif args.cluster is not None:
        members = query.get_cluster_members(args.cluster)
        print(f"\n📊 Cluster {args.cluster}: {len(members)} paragraphs\n")
        for para in members:
            print(f"- [{para['document']}] {para['section']}")
            print(f"  {para['content'][:150]}...\n")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
