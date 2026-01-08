#!/usr/bin/env python3
"""
Semantic Dependency Graph Builder

Builds fine-grained paragraph-level dependency graph using vector similarity.
Goes beyond keyword matching to find implicit semantic connections.

When you update a paragraph, this tells you exactly which other paragraphs
across ALL documents are semantically related and may need review.

Usage:
    python scripts/build_semantic_graph.py [--similarity-threshold 0.7]
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


class SemanticGraphBuilder:
    """Builds paragraph-level semantic dependency graph"""
    
    def __init__(self, docs_dir: str, similarity_threshold: float = 0.7):
        self.docs_dir = Path(docs_dir)
        self.similarity_threshold = similarity_threshold
        self.documents = {}
        self.paragraphs = []  # List of all paragraphs with metadata
        self.similarity_edges = []  # (para_id1, para_id2, score)
        self.paragraph_clusters = defaultdict(list)  # Similar paragraphs grouped
        
        # Connect to services
        self.qdrant_client = QdrantClient(host='qdrant', port=6333)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print(f"✓ Connected to Qdrant")
        print(f"✓ Loaded embedding model")
        print(f"✓ Similarity threshold: {similarity_threshold}")
    
    def load_and_chunk_documents(self):
        """Load documents and split into semantic units (paragraphs/sections)"""
        print(f"\n📚 Loading and chunking documents from {self.docs_dir}")
        
        para_id = 0
        for md_file in sorted(self.docs_dir.glob("*.md")):
            doc_name = md_file.stem
            
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into sections by headers
            sections = self._split_by_headers(content, doc_name)
            
            for section in sections:
                # Further split sections into paragraphs
                paragraphs = self._split_into_paragraphs(section['content'])
                
                for i, para_text in enumerate(paragraphs):
                    if len(para_text.strip()) < 50:  # Skip very short paragraphs
                        continue
                    
                    self.paragraphs.append({
                        'id': para_id,
                        'document': doc_name,
                        'section': section['header'],
                        'section_level': section['level'],
                        'paragraph_index': i,
                        'content': para_text.strip(),
                        'char_position': section['char_pos']
                    })
                    para_id += 1
        
        print(f"   ✓ Extracted {len(self.paragraphs)} paragraphs from {len(list(self.docs_dir.glob('*.md')))} documents")
    
    def _split_by_headers(self, content: str, doc_name: str) -> List[Dict]:
        """Split document by markdown headers"""
        sections = []
        lines = content.split('\n')
        
        current_section = {
            'header': f'{doc_name} (Preamble)',
            'level': 0,
            'content': '',
            'char_pos': 0
        }
        
        char_pos = 0
        for line in lines:
            # Check for markdown header
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if header_match:
                # Save previous section
                if current_section['content'].strip():
                    sections.append(current_section)
                
                # Start new section
                level = len(header_match.group(1))
                header_text = header_match.group(2)
                
                current_section = {
                    'header': header_text,
                    'level': level,
                    'content': '',
                    'char_pos': char_pos
                }
            else:
                current_section['content'] += line + '\n'
            
            char_pos += len(line) + 1
        
        # Add final section
        if current_section['content'].strip():
            sections.append(current_section)
        
        return sections
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs (double newline separated)"""
        # Remove code blocks to avoid splitting them
        text = re.sub(r'```.*?```', '[CODE_BLOCK]', text, flags=re.DOTALL)
        
        # Split on double newlines
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Filter out empty, very short, or special paragraphs
        filtered = []
        for para in paragraphs:
            para = para.strip()
            if len(para) < 50:  # Skip very short
                continue
            if para.startswith('*Source:'):  # Skip source citations
                continue
            if para == '[CODE_BLOCK]':  # Skip code block markers
                continue
            filtered.append(para)
        
        return filtered
    
    def build_similarity_graph(self):
        """Build graph of semantically similar paragraphs"""
        print(f"\n🧠 Building semantic similarity graph...")
        print(f"   Computing embeddings for {len(self.paragraphs)} paragraphs...")
        
        # Generate embeddings for all paragraphs
        texts = [p['content'] for p in self.paragraphs]
        embeddings = self.model.encode(texts, show_progress_bar=True, batch_size=32)
        
        # Store embeddings
        for i, para in enumerate(self.paragraphs):
            para['embedding'] = embeddings[i]
        
        print(f"\n   Computing pairwise similarities...")
        
        # For each paragraph, find similar paragraphs in OTHER documents
        edge_count = 0
        for i, para in enumerate(self.paragraphs):
            if (i + 1) % 100 == 0:
                print(f"   Progress: {i+1}/{len(self.paragraphs)} paragraphs processed, {edge_count} edges found", end='\r')
            
            # Compare with all other paragraphs
            for j in range(i + 1, len(self.paragraphs)):
                other_para = self.paragraphs[j]
                
                # Skip if same document (we care about cross-document dependencies)
                if para['document'] == other_para['document']:
                    continue
                
                # Compute cosine similarity
                similarity = self._cosine_similarity(para['embedding'], other_para['embedding'])
                
                if similarity >= self.similarity_threshold:
                    self.similarity_edges.append({
                        'para1_id': para['id'],
                        'para2_id': other_para['id'],
                        'similarity': float(similarity),
                        'para1_doc': para['document'],
                        'para2_doc': other_para['document'],
                        'para1_section': para['section'],
                        'para2_section': other_para['section'],
                        'para1_preview': para['content'][:100],
                        'para2_preview': other_para['content'][:100]
                    })
                    edge_count += 1
        
        print(f"\n   ✓ Found {len(self.similarity_edges)} semantic connections (similarity ≥ {self.similarity_threshold})")
    
    def _cosine_similarity(self, vec1, vec2):
        """Compute cosine similarity between two vectors"""
        import numpy as np
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def cluster_similar_paragraphs(self):
        """Group paragraphs into semantic clusters"""
        print(f"\n📊 Clustering similar paragraphs...")
        
        # Build adjacency list
        adjacency = defaultdict(set)
        for edge in self.similarity_edges:
            adjacency[edge['para1_id']].add(edge['para2_id'])
            adjacency[edge['para2_id']].add(edge['para1_id'])
        
        # Find connected components (clusters)
        visited = set()
        cluster_id = 0
        
        for para in self.paragraphs:
            if para['id'] in visited:
                continue
            
            # BFS to find all connected paragraphs
            cluster = []
            queue = [para['id']]
            
            while queue:
                current_id = queue.pop(0)
                if current_id in visited:
                    continue
                
                visited.add(current_id)
                cluster.append(current_id)
                
                # Add neighbors
                for neighbor_id in adjacency[current_id]:
                    if neighbor_id not in visited:
                        queue.append(neighbor_id)
            
            if len(cluster) > 1:  # Only store clusters with multiple paragraphs
                self.paragraph_clusters[cluster_id] = cluster
                cluster_id += 1
        
        print(f"   ✓ Found {len(self.paragraph_clusters)} semantic clusters")
    
    def export_graph(self, output_dir: str):
        """Export semantic graph data"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        print(f"\n💾 Exporting semantic graph...")
        
        # Export full graph data
        graph_data = {
            'metadata': {
                'total_paragraphs': len(self.paragraphs),
                'total_edges': len(self.similarity_edges),
                'similarity_threshold': self.similarity_threshold,
                'total_clusters': len(self.paragraph_clusters)
            },
            'paragraphs': [
                {
                    'id': p['id'],
                    'document': p['document'],
                    'section': p['section'],
                    'content': p['content'],
                    'char_position': p['char_position']
                }
                for p in self.paragraphs
            ],
            'edges': self.similarity_edges,
            'clusters': {
                str(cluster_id): members
                for cluster_id, members in self.paragraph_clusters.items()
            }
        }
        
        with open(output_dir / 'semantic_graph.json', 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        print(f"   ✓ Saved to {output_dir / 'semantic_graph.json'}")
        
        # Export human-readable report
        self._generate_report(output_dir / 'semantic_graph_report.md')
    
    def _generate_report(self, output_file: Path):
        """Generate human-readable report"""
        
        with open(output_file, 'w') as f:
            f.write("# Semantic Dependency Graph Report\n\n")
            
            # Summary
            f.write("## Summary\n\n")
            f.write(f"- **Total Paragraphs:** {len(self.paragraphs)}\n")
            f.write(f"- **Semantic Connections:** {len(self.similarity_edges)}\n")
            f.write(f"- **Similarity Threshold:** {self.similarity_threshold}\n")
            f.write(f"- **Semantic Clusters:** {len(self.paragraph_clusters)}\n\n")
            
            # Most connected paragraphs
            f.write("## Most Connected Paragraphs\n\n")
            
            connections = defaultdict(int)
            for edge in self.similarity_edges:
                connections[edge['para1_id']] += 1
                connections[edge['para2_id']] += 1
            
            top_connected = sorted(connections.items(), key=lambda x: x[1], reverse=True)[:10]
            
            for para_id, count in top_connected:
                para = self.paragraphs[para_id]
                f.write(f"### Paragraph {para_id}: {count} connections\n\n")
                f.write(f"**Document:** {para['document']}\n\n")
                f.write(f"**Section:** {para['section']}\n\n")
                f.write(f"**Preview:** {para['content'][:200]}...\n\n")
            
            # Largest clusters
            f.write("## Largest Semantic Clusters\n\n")
            
            sorted_clusters = sorted(self.paragraph_clusters.items(), 
                                   key=lambda x: len(x[1]), reverse=True)[:5]
            
            for cluster_id, members in sorted_clusters:
                f.write(f"### Cluster {cluster_id}: {len(members)} paragraphs\n\n")
                
                # Show documents involved
                docs = set(self.paragraphs[pid]['document'] for pid in members)
                f.write(f"**Documents:** {', '.join(sorted(docs))}\n\n")
                
                # Show first paragraph as example
                first_para = self.paragraphs[members[0]]
                f.write(f"**Example content:**\n\n")
                f.write(f"> {first_para['content'][:300]}...\n\n")
            
            # Cross-document connections by document pair
            f.write("## Cross-Document Connections\n\n")
            
            doc_pairs = defaultdict(int)
            for edge in self.similarity_edges:
                pair = tuple(sorted([edge['para1_doc'], edge['para2_doc']]))
                doc_pairs[pair] += 1
            
            top_pairs = sorted(doc_pairs.items(), key=lambda x: x[1], reverse=True)[:20]
            
            for (doc1, doc2), count in top_pairs:
                f.write(f"- **{doc1}** ↔ **{doc2}**: {count} connections\n")
        
        print(f"   ✓ Saved report to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Build semantic dependency graph at paragraph level'
    )
    parser.add_argument(
        '--docs-dir',
        default='/app/docs',
        help='Directory containing markdown documents'
    )
    parser.add_argument(
        '--output-dir',
        default='/app/output/reports',
        help='Output directory for graph data'
    )
    parser.add_argument(
        '--similarity-threshold',
        type=float,
        default=0.7,
        help='Minimum cosine similarity to create edge (default: 0.7)'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🧠 SEMANTIC DEPENDENCY GRAPH BUILDER")
    print("=" * 80)
    
    builder = SemanticGraphBuilder(args.docs_dir, args.similarity_threshold)
    builder.load_and_chunk_documents()
    builder.build_similarity_graph()
    builder.cluster_similar_paragraphs()
    builder.export_graph(args.output_dir)
    
    print("\n" + "=" * 80)
    print("✅ SEMANTIC GRAPH COMPLETE")
    print("=" * 80)
    print("\n📁 Output files:")
    print(f"   - {args.output_dir}/semantic_graph.json")
    print(f"   - {args.output_dir}/semantic_graph_report.md")
    print("\n💡 Next: Use query_semantic_graph.py to find related paragraphs\n")


if __name__ == '__main__':
    main()
