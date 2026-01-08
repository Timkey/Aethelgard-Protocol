#!/usr/bin/env python3
"""
Query Dependency Graph for Impact Analysis

Provides command-line interface to query dependency relationships
and identify what needs updating when premises or chapters change.

Usage:
    python scripts/query_dependencies.py --chapter <chapter_name>
    python scripts/query_dependencies.py --premise <premise_id>
    python scripts/query_dependencies.py --concept <concept_name>
    python scripts/query_dependencies.py --interactive
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Set


class DependencyQuery:
    """Query interface for dependency graph"""
    
    def __init__(self, deps_file: str = 'reports/dependencies.json'):
        self.deps_file = Path(deps_file)
        self.data = None
        self.load_dependencies()
    
    def load_dependencies(self):
        """Load dependency data"""
        if not self.deps_file.exists():
            print(f"❌ Dependency file not found: {self.deps_file}")
            print("   Run: python scripts/build_dependency_graph.py")
            sys.exit(1)
        
        with open(self.deps_file, 'r') as f:
            self.data = json.load(f)
    
    def query_chapter_impact(self, chapter: str) -> Dict:
        """Query what would be affected if a chapter changes"""
        
        if chapter not in self.data['documents']:
            return {'error': f'Chapter {chapter} not found'}
        
        # Direct dependencies
        direct = self.data['reverse_dependencies'].get(chapter, [])
        
        # Find shared concepts
        shared_concepts = []
        for concept, docs in self.data['concept_usage'].items():
            if chapter in docs:
                shared_concepts.append({
                    'concept': concept,
                    'also_in': [d for d in docs if d != chapter]
                })
        
        # Get cross-references
        refs = self.data['cross_references'].get(chapter, [])
        
        return {
            'chapter': chapter,
            'directly_affected': direct,
            'affected_count': len(direct),
            'shared_concepts': shared_concepts,
            'incoming_references': len(refs)
        }
    
    def query_premise_impact(self, premise: str) -> Dict:
        """Query what would be affected if a premise changes"""
        
        if premise not in self.data['premise_chains']:
            return {'error': f'Premise {premise} not found'}
        
        affected = self.data['premise_chains'][premise]
        
        # Sort by strength
        affected_sorted = sorted(affected, key=lambda x: x['strength'], reverse=True)
        
        return {
            'premise': premise,
            'affected_documents': affected_sorted,
            'total_affected': len(affected_sorted),
            'high_impact': [d for d in affected_sorted if d['strength'] > 5],
            'medium_impact': [d for d in affected_sorted if 2 < d['strength'] <= 5],
            'low_impact': [d for d in affected_sorted if d['strength'] <= 2]
        }
    
    def query_concept_usage(self, concept: str) -> Dict:
        """Query where a concept is used"""
        
        # Find concept (case-insensitive)
        matching_concepts = [
            c for c in self.data['concept_usage'].keys()
            if concept.lower() in c.lower()
        ]
        
        if not matching_concepts:
            return {'error': f'Concept "{concept}" not found'}
        
        results = {}
        for matched_concept in matching_concepts:
            docs = self.data['concept_usage'][matched_concept]
            results[matched_concept] = {
                'documents': docs,
                'usage_count': len(docs)
            }
        
        return {
            'query': concept,
            'matches': results,
            'total_matches': len(matching_concepts)
        }
    
    def find_update_path(self, from_chapter: str, to_chapter: str) -> List[str]:
        """Find dependency path between two chapters"""
        
        if from_chapter not in self.data['documents'] or to_chapter not in self.data['documents']:
            return []
        
        # BFS to find shortest path
        queue = [(from_chapter, [from_chapter])]
        visited = {from_chapter}
        
        while queue:
            current, path = queue.pop(0)
            
            if current == to_chapter:
                return path
            
            # Check dependencies
            for dep in self.data['dependencies'].get(current, []):
                if dep not in visited:
                    visited.add(dep)
                    queue.append((dep, path + [dep]))
        
        return []  # No path found
    
    def list_available_premises(self) -> List[str]:
        """List all available premises"""
        return list(self.data['premise_chains'].keys())
    
    def list_available_concepts(self) -> List[str]:
        """List all tracked concepts"""
        return list(self.data['concept_usage'].keys())
    
    def interactive_mode(self):
        """Interactive query mode"""
        print("\n" + "=" * 80)
        print("🔍 INTERACTIVE DEPENDENCY QUERY MODE")
        print("=" * 80)
        print("\nCommands:")
        print("  chapter <name>   - Show impact if chapter changes")
        print("  premise <id>     - Show impact if premise changes")
        print("  concept <name>   - Show where concept is used")
        print("  path <from> <to> - Find dependency path between chapters")
        print("  list premises    - List all premises")
        print("  list concepts    - List all concepts")
        print("  list chapters    - List all chapters")
        print("  help            - Show this help")
        print("  exit            - Exit interactive mode")
        print()
        
        while True:
            try:
                cmd = input("📊 > ").strip()
                
                if not cmd:
                    continue
                
                if cmd == 'exit':
                    break
                
                if cmd == 'help':
                    continue
                
                if cmd == 'list premises':
                    premises = self.list_available_premises()
                    print(f"\n📋 Available premises ({len(premises)}):")
                    for p in premises:
                        print(f"   - {p}")
                    print()
                    continue
                
                if cmd == 'list concepts':
                    concepts = self.list_available_concepts()
                    print(f"\n📋 Available concepts ({len(concepts)}):")
                    for c in concepts[:30]:  # Show first 30
                        print(f"   - {c}")
                    if len(concepts) > 30:
                        print(f"   ... and {len(concepts) - 30} more")
                    print()
                    continue
                
                if cmd == 'list chapters':
                    chapters = self.data['documents']
                    print(f"\n📋 Available chapters ({len(chapters)}):")
                    for c in chapters:
                        print(f"   - {c}")
                    print()
                    continue
                
                parts = cmd.split(maxsplit=1)
                if len(parts) < 2:
                    print("❌ Invalid command. Type 'help' for usage.\n")
                    continue
                
                command, args = parts[0], parts[1]
                
                if command == 'chapter':
                    result = self.query_chapter_impact(args)
                    self._print_chapter_impact(result)
                
                elif command == 'premise':
                    result = self.query_premise_impact(args)
                    self._print_premise_impact(result)
                
                elif command == 'concept':
                    result = self.query_concept_usage(args)
                    self._print_concept_usage(result)
                
                elif command == 'path':
                    path_parts = args.split()
                    if len(path_parts) != 2:
                        print("❌ Usage: path <from_chapter> <to_chapter>\n")
                        continue
                    path = self.find_update_path(path_parts[0], path_parts[1])
                    self._print_path(path_parts[0], path_parts[1], path)
                
                else:
                    print(f"❌ Unknown command: {command}\n")
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")
    
    def _print_chapter_impact(self, result: Dict):
        """Pretty print chapter impact"""
        if 'error' in result:
            print(f"\n❌ {result['error']}\n")
            return
        
        print(f"\n📖 Impact Analysis: {result['chapter']}")
        print("=" * 80)
        
        if result['directly_affected']:
            print(f"\n🔴 Directly Affected ({result['affected_count']} documents):")
            for doc in result['directly_affected']:
                print(f"   - {doc}")
        else:
            print("\n✅ No direct dependencies found")
        
        if result['shared_concepts']:
            print(f"\n🟡 Shared Concepts ({len(result['shared_concepts'])} concepts):")
            for item in result['shared_concepts'][:10]:
                print(f"   - {item['concept']}")
                for doc in item['also_in'][:3]:
                    print(f"      └─ {doc}")
                if len(item['also_in']) > 3:
                    print(f"      └─ ... and {len(item['also_in']) - 3} more")
        
        print()
    
    def _print_premise_impact(self, result: Dict):
        """Pretty print premise impact"""
        if 'error' in result:
            print(f"\n❌ {result['error']}\n")
            return
        
        print(f"\n🧠 Premise Impact Analysis: {result['premise']}")
        print("=" * 80)
        print(f"\nTotal affected: {result['total_affected']} documents")
        
        if result['high_impact']:
            print(f"\n🔴 HIGH IMPACT ({len(result['high_impact'])} documents):")
            for doc in result['high_impact']:
                print(f"   - {doc['document']} (strength: {doc['strength']})")
        
        if result['medium_impact']:
            print(f"\n🟡 MEDIUM IMPACT ({len(result['medium_impact'])} documents):")
            for doc in result['medium_impact'][:5]:
                print(f"   - {doc['document']} (strength: {doc['strength']})")
            if len(result['medium_impact']) > 5:
                print(f"   ... and {len(result['medium_impact']) - 5} more")
        
        if result['low_impact']:
            print(f"\n🟢 LOW IMPACT ({len(result['low_impact'])} documents)")
        
        print()
    
    def _print_concept_usage(self, result: Dict):
        """Pretty print concept usage"""
        if 'error' in result:
            print(f"\n❌ {result['error']}\n")
            return
        
        print(f"\n🔑 Concept Usage: '{result['query']}'")
        print("=" * 80)
        print(f"\nFound {result['total_matches']} matching concept(s)")
        
        for concept, data in result['matches'].items():
            print(f"\n📌 {concept} (used in {data['usage_count']} documents):")
            for doc in data['documents']:
                print(f"   - {doc}")
        
        print()
    
    def _print_path(self, from_ch: str, to_ch: str, path: List[str]):
        """Pretty print dependency path"""
        print(f"\n🛤️  Dependency Path: {from_ch} → {to_ch}")
        print("=" * 80)
        
        if path:
            print(f"\nPath found ({len(path)} steps):")
            for i, chapter in enumerate(path):
                if i == 0:
                    print(f"   {chapter}")
                else:
                    print(f"   └─→ {chapter}")
        else:
            print("\n❌ No dependency path found")
        
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Query documentation dependency graph'
    )
    parser.add_argument(
        '--chapter',
        help='Query impact if chapter changes'
    )
    parser.add_argument(
        '--premise',
        help='Query impact if premise changes'
    )
    parser.add_argument(
        '--concept',
        help='Query where concept is used'
    )
    parser.add_argument(
        '--path',
        nargs=2,
        metavar=('FROM', 'TO'),
        help='Find dependency path between two chapters'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Enter interactive query mode'
    )
    parser.add_argument(
        '--deps-file',
        default='reports/dependencies.json',
        help='Path to dependencies JSON file'
    )
    
    args = parser.parse_args()
    
    query = DependencyQuery(args.deps_file)
    
    if args.interactive:
        query.interactive_mode()
    
    elif args.chapter:
        result = query.query_chapter_impact(args.chapter)
        query._print_chapter_impact(result)
    
    elif args.premise:
        result = query.query_premise_impact(args.premise)
        query._print_premise_impact(result)
    
    elif args.concept:
        result = query.query_concept_usage(args.concept)
        query._print_concept_usage(result)
    
    elif args.path:
        path = query.find_update_path(args.path[0], args.path[1])
        query._print_path(args.path[0], args.path[1], path)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
