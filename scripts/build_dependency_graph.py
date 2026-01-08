#!/usr/bin/env python3
"""
Dependency Graph Builder for Planetary Exodus Documentation

Analyzes cross-references, concept dependencies, and premise chains
to build a comprehensive dependency graph showing what needs to be
updated when foundational assumptions change.

Usage:
    python scripts/build_dependency_graph.py [--output DIR] [--visualize]
"""

import os
import re
import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import argparse

# Try to import visualization libraries (optional)
try:
    import networkx as nx
    import matplotlib.pyplot as plt
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("⚠️  NetworkX/Matplotlib not available. Install for visualization: pip install networkx matplotlib")


class DependencyGraph:
    """Builds and manages documentation dependency graph"""
    
    def __init__(self, docs_dir: str):
        self.docs_dir = Path(docs_dir)
        self.documents = {}
        self.dependencies = defaultdict(set)  # chapter -> set of chapters it depends on
        self.reverse_deps = defaultdict(set)  # chapter -> set of chapters that depend on it
        self.concept_usage = defaultdict(set)  # concept -> set of chapters using it
        self.premise_chains = defaultdict(list)  # premise -> list of dependent sections
        self.cross_references = defaultdict(list)  # chapter -> list of (target, context)
        
    def load_documents(self):
        """Load all markdown documents"""
        print(f"📚 Loading documents from {self.docs_dir}")
        
        for md_file in sorted(self.docs_dir.glob("*.md")):
            doc_name = md_file.stem
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.documents[doc_name] = {
                    'path': md_file,
                    'content': content,
                    'lines': content.split('\n')
                }
        
        print(f"   ✓ Loaded {len(self.documents)} documents")
    
    def extract_cross_references(self):
        """Extract explicit cross-references between chapters"""
        print("\n🔗 Extracting cross-references...")
        
        # Patterns to detect chapter references
        patterns = [
            r'Chapter\s+(\d+)',  # "Chapter 5"
            r'Ch\.\s*(\d+)',      # "Ch. 5"
            r'§\s*(\d+)',         # "§5"
            r'\[Chapter\s+(\d+)\]',  # "[Chapter 5]"
            r'see\s+(?:Chapter\s+)?(\d+)',  # "see Chapter 5" or "see 5"
        ]
        
        for doc_name, doc_data in self.documents.items():
            content = doc_data['content']
            
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    chapter_num = match.group(1)
                    target_chapter = self._find_chapter_by_number(chapter_num)
                    
                    if target_chapter and target_chapter != doc_name:
                        # Extract context (surrounding text)
                        start = max(0, match.start() - 50)
                        end = min(len(content), match.end() + 50)
                        context = content[start:end].replace('\n', ' ')
                        
                        self.dependencies[doc_name].add(target_chapter)
                        self.reverse_deps[target_chapter].add(doc_name)
                        self.cross_references[doc_name].append({
                            'target': target_chapter,
                            'context': context.strip(),
                            'type': 'explicit'
                        })
        
        total_refs = sum(len(refs) for refs in self.cross_references.values())
        print(f"   ✓ Found {total_refs} cross-references")
    
    def extract_key_concepts(self):
        """Extract key concepts and track their usage"""
        print("\n🔑 Extracting key concepts...")
        
        # Define key concepts to track
        key_concepts = [
            # Infrastructure
            'Dyson Swarm', 'Dyson', 'Moon-Tug', 'Moon Tug', 'Hive Cities', 'Hive City',
            'Lunar Vault', 'Oracle System', 'Oracle', 'Synthesis Engine',
            
            # Timeline/Phases
            'Phase Zero', 'Phase One', 'Phase Two', 'Phase Three', 'Phase Four',
            'Phase 0', 'Phase 1', 'Phase 2', 'Phase 3', 'Phase 4',
            
            # Physics/Technical
            'solar brightening', 'solar luminosity', 'Proxima Centauri',
            'cryogenic', 'cryosleep', 'transit', 'evacuation', 'departure',
            
            # Governance
            'Aethelgard Protocol', 'Living Manifesto', 'Mythos Committee',
            'distributed consensus', 'governance',
            
            # Mission milestones
            'deep time', 'deep-time', 'geological timescales', 'million years',
            'ten billion', '10 billion',
        ]
        
        for doc_name, doc_data in self.documents.items():
            content = doc_data['content'].lower()
            
            for concept in key_concepts:
                if concept.lower() in content:
                    self.concept_usage[concept].add(doc_name)
        
        print(f"   ✓ Tracked {len(key_concepts)} concepts across documents")
    
    def extract_premise_dependencies(self):
        """Extract logical premise chains (what assumptions each chapter relies on)"""
        print("\n🧠 Extracting premise dependencies...")
        
        # Define key premises and their indicators
        premises = {
            'timeline_deep_time': {
                'keywords': ['500 million years', '500M years', 'geological', 'deep time', 'Phase Two', 'Phase Three'],
                'description': 'Deep-time timeline (500M years)'
            },
            'timeline_near_term': {
                'keywords': ['Phase Zero', 'Phase One', '2026', '2150', 'near-term'],
                'description': 'Near-term timeline (2026-10K years)'
            },
            'dyson_infrastructure': {
                'keywords': ['Dyson Swarm', 'solar collectors', '25 petawatts', 'power generation'],
                'description': 'Dyson Swarm infrastructure exists'
            },
            'moon_tug_capability': {
                'keywords': ['Moon-Tug', 'propulsion', '10^20', 'xenon', 'transfer orbit'],
                'description': 'Moon-Tug transport capability'
            },
            'hive_habitability': {
                'keywords': ['Hive Cities', 'underground', '15 billion', 'habitability', 'life support'],
                'description': 'Underground Hive Cities functional'
            },
            'oracle_governance': {
                'keywords': ['Oracle', 'synthesis', 'distributed consensus', 'governance'],
                'description': 'Oracle governance system operational'
            },
            'proxima_target': {
                'keywords': ['Proxima Centauri b', 'Prox b', '4.24 light-years', 'destination'],
                'description': 'Proxima Centauri b as destination'
            },
            'ten_billion_population': {
                'keywords': ['10 billion', 'ten billion', 'population', 'humanity'],
                'description': '10 billion population baseline'
            },
            'solar_physics': {
                'keywords': ['solar brightening', 'solar luminosity', 'red giant', 'main sequence'],
                'description': 'Solar evolution physics'
            },
        }
        
        for doc_name, doc_data in self.documents.items():
            content = doc_data['content'].lower()
            
            for premise_id, premise_data in premises.items():
                # Count keyword matches
                matches = sum(1 for kw in premise_data['keywords'] if kw.lower() in content)
                
                if matches > 0:
                    self.premise_chains[premise_id].append({
                        'document': doc_name,
                        'strength': matches,
                        'description': premise_data['description']
                    })
        
        print(f"   ✓ Identified {len(premises)} key premises")
    
    def analyze_impact(self, changed_chapter: str) -> Dict:
        """Analyze impact if a specific chapter changes"""
        
        if changed_chapter not in self.documents:
            return {'error': f'Chapter {changed_chapter} not found'}
        
        # Direct dependencies (chapters that reference this one)
        direct_impact = self.reverse_deps.get(changed_chapter, set())
        
        # Indirect dependencies (transitive closure)
        indirect_impact = set()
        to_check = list(direct_impact)
        checked = {changed_chapter}
        
        while to_check:
            current = to_check.pop()
            if current in checked:
                continue
            checked.add(current)
            
            for dependent in self.reverse_deps.get(current, set()):
                if dependent not in checked:
                    indirect_impact.add(dependent)
                    to_check.append(dependent)
        
        # Shared concepts (chapters using same concepts)
        shared_concepts = set()
        for concept, users in self.concept_usage.items():
            if changed_chapter in users:
                shared_concepts.update(users)
        shared_concepts.discard(changed_chapter)
        
        return {
            'changed': changed_chapter,
            'direct_impact': sorted(direct_impact),
            'indirect_impact': sorted(indirect_impact),
            'shared_concepts': sorted(shared_concepts),
            'total_affected': len(direct_impact | indirect_impact | shared_concepts)
        }
    
    def analyze_premise_impact(self, premise_id: str) -> Dict:
        """Analyze what needs updating if a premise changes"""
        
        if premise_id not in self.premise_chains:
            return {'error': f'Premise {premise_id} not found'}
        
        affected_docs = self.premise_chains[premise_id]
        
        # Sort by dependency strength
        affected_docs.sort(key=lambda x: x['strength'], reverse=True)
        
        return {
            'premise': premise_id,
            'description': affected_docs[0]['description'] if affected_docs else 'Unknown',
            'affected_documents': [
                {
                    'document': doc['document'],
                    'strength': doc['strength'],
                    'priority': 'HIGH' if doc['strength'] > 5 else 'MEDIUM' if doc['strength'] > 2 else 'LOW'
                }
                for doc in affected_docs
            ],
            'total_affected': len(affected_docs)
        }
    
    def generate_visual_graph(self, output_file: str):
        """Generate visual dependency graph using NetworkX"""
        
        if not VISUALIZATION_AVAILABLE:
            print("⚠️  Visualization libraries not available")
            return
        
        print(f"\n📊 Generating visual graph...")
        
        G = nx.DiGraph()
        
        # Add nodes
        for doc_name in self.documents.keys():
            # Simplify names for visualization
            label = doc_name.replace('_Chapter_', ' Ch').replace('_Appendix_', ' App')
            G.add_node(doc_name, label=label)
        
        # Add edges
        for source, targets in self.dependencies.items():
            for target in targets:
                G.add_edge(source, target)
        
        # Layout and draw
        plt.figure(figsize=(20, 14))
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                              node_size=1000, alpha=0.9)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='gray', 
                              arrows=True, arrowsize=15, alpha=0.5)
        
        # Draw labels
        labels = nx.get_node_attributes(G, 'label')
        nx.draw_networkx_labels(G, pos, labels, font_size=8)
        
        plt.title("Documentation Dependency Graph", fontsize=16)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"   ✓ Saved graph to {output_file}")
    
    def export_json(self, output_file: str):
        """Export dependency data as JSON"""
        
        print(f"\n💾 Exporting dependency data...")
        
        data = {
            'metadata': {
                'total_documents': len(self.documents),
                'total_dependencies': sum(len(deps) for deps in self.dependencies.values()),
                'total_concepts': len(self.concept_usage),
                'total_premises': len(self.premise_chains)
            },
            'documents': list(self.documents.keys()),
            'dependencies': {
                doc: list(deps) for doc, deps in self.dependencies.items()
            },
            'reverse_dependencies': {
                doc: list(deps) for doc, deps in self.reverse_deps.items()
            },
            'concept_usage': {
                concept: list(docs) for concept, docs in self.concept_usage.items()
            },
            'premise_chains': {
                premise: [
                    {'document': d['document'], 'strength': d['strength']}
                    for d in docs
                ]
                for premise, docs in self.premise_chains.items()
            },
            'cross_references': {
                doc: refs for doc, refs in self.cross_references.items()
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"   ✓ Saved dependency data to {output_file}")
    
    def generate_report(self, output_file: str):
        """Generate human-readable dependency report"""
        
        print(f"\n📄 Generating dependency report...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Documentation Dependency Report\n\n")
            f.write(f"**Generated:** {Path.cwd().name}\n\n")
            
            # Summary
            f.write("## Summary\n\n")
            f.write(f"- **Total Documents:** {len(self.documents)}\n")
            f.write(f"- **Total Dependencies:** {sum(len(deps) for deps in self.dependencies.values())}\n")
            f.write(f"- **Cross-References:** {sum(len(refs) for refs in self.cross_references.values())}\n")
            f.write(f"- **Key Concepts Tracked:** {len(self.concept_usage)}\n")
            f.write(f"- **Premises Identified:** {len(self.premise_chains)}\n\n")
            
            # Most referenced documents
            f.write("## Most Referenced Documents\n\n")
            ref_counts = [(doc, len(deps)) for doc, deps in self.reverse_deps.items()]
            ref_counts.sort(key=lambda x: x[1], reverse=True)
            
            for doc, count in ref_counts[:10]:
                f.write(f"- **{doc}**: Referenced by {count} other documents\n")
            f.write("\n")
            
            # Most dependent documents
            f.write("## Documents with Most Dependencies\n\n")
            dep_counts = [(doc, len(deps)) for doc, deps in self.dependencies.items()]
            dep_counts.sort(key=lambda x: x[1], reverse=True)
            
            for doc, count in dep_counts[:10]:
                f.write(f"- **{doc}**: Depends on {count} other documents\n")
            f.write("\n")
            
            # Concept usage
            f.write("## Key Concepts Usage\n\n")
            concept_counts = [(concept, len(docs)) for concept, docs in self.concept_usage.items()]
            concept_counts.sort(key=lambda x: x[1], reverse=True)
            
            for concept, count in concept_counts[:20]:
                f.write(f"- **{concept}**: Used in {count} documents\n")
            f.write("\n")
            
            # Premise dependencies
            f.write("## Premise Dependencies\n\n")
            for premise_id, docs in self.premise_chains.items():
                f.write(f"### {premise_id.replace('_', ' ').title()}\n\n")
                f.write(f"*{docs[0]['description']}*\n\n")
                f.write(f"**Affected documents:** {len(docs)}\n\n")
                
                # Sort by strength
                docs_sorted = sorted(docs, key=lambda x: x['strength'], reverse=True)
                for doc in docs_sorted[:5]:
                    strength = "🔴 HIGH" if doc['strength'] > 5 else "🟡 MEDIUM" if doc['strength'] > 2 else "🟢 LOW"
                    f.write(f"- {doc['document']} - {strength} ({doc['strength']} references)\n")
                f.write("\n")
        
        print(f"   ✓ Saved report to {output_file}")
    
    def _find_chapter_by_number(self, chapter_num: str) -> str:
        """Find document name by chapter number"""
        # Try to find matching chapter
        pattern = f"Chapter_{int(chapter_num):02d}"
        for doc_name in self.documents.keys():
            if pattern in doc_name:
                return doc_name
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Build dependency graph for Planetary Exodus documentation'
    )
    parser.add_argument(
        '--docs-dir',
        default='docs',
        help='Directory containing markdown documents (default: docs)'
    )
    parser.add_argument(
        '--output-dir',
        default='reports',
        help='Output directory for reports (default: reports)'
    )
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='Generate visual graph (requires networkx and matplotlib)'
    )
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 80)
    print("📊 DOCUMENTATION DEPENDENCY GRAPH BUILDER")
    print("=" * 80)
    
    # Build graph
    graph = DependencyGraph(args.docs_dir)
    graph.load_documents()
    graph.extract_cross_references()
    graph.extract_key_concepts()
    graph.extract_premise_dependencies()
    
    # Export results
    graph.export_json(output_dir / 'dependencies.json')
    graph.generate_report(output_dir / 'dependency_report.md')
    
    if args.visualize and VISUALIZATION_AVAILABLE:
        graph.generate_visual_graph(output_dir / 'dependency_graph.png')
    
    print("\n" + "=" * 80)
    print("✅ DEPENDENCY GRAPH GENERATION COMPLETE")
    print("=" * 80)
    print("\n📁 Output files:")
    print(f"   - {output_dir / 'dependencies.json'}")
    print(f"   - {output_dir / 'dependency_report.md'}")
    if args.visualize and VISUALIZATION_AVAILABLE:
        print(f"   - {output_dir / 'dependency_graph.png'}")
    
    print("\n💡 Usage examples:")
    print("   - Query impact: python scripts/query_dependencies.py --chapter '21_Chapter_20'")
    print("   - Premise impact: python scripts/query_dependencies.py --premise timeline_deep_time")
    print("   - Vector DB query: Use dependency data to target relevant chapters\n")


if __name__ == '__main__':
    main()
