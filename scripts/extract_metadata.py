#!/usr/bin/env python3
"""
Aethelgard Protocol - Metadata Extraction Tool
Extracts key concepts, technical specs, and structure from raw.txt
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

class AethelgardExtractor:
    def __init__(self, source_file: Path):
        self.source_file = source_file
        self.content = source_file.read_text(encoding='utf-8')
        self.lines = self.content.split('\n')
        
        # Storage for extracted data
        self.metadata = {
            'source_file': str(source_file),
            'total_lines': len(self.lines),
            'extraction_date': '2026-01-05',
            'sections': [],
            'technical_constants': {},
            'key_concepts': {},
            'timeline': [],
            'oracles': {},
            'quotes': [],
            'religious_references': []
        }
    
    def extract_technical_constants(self):
        """Extract numerical constants and specifications"""
        constants = {}
        
        # Patterns for scientific notation and technical specs
        patterns = [
            (r'Mass of Earth.*?(\d+\.?\d*×10\^\d+)\s*kg', 'earth_mass'),
            (r'(\d+\.?\d*×10\^\d+)\s*kg', 'masses'),
            (r'(\d+\.?\d*)\s*km', 'distances_km'),
            (r'(\d+\.?\d*)\s*m/s', 'velocities'),
            (r'(\d+,?\d*)\s*years?', 'time_periods'),
            (r'(\d+)\s*billion', 'billion_scale'),
        ]
        
        for i, line in enumerate(self.lines):
            # Earth mass
            if 'mass of earth' in line.lower() or 'earth mass' in line.lower():
                match = re.search(r'(\d+\.?\d*×10\s*\d+|5\.97.*?10.*?24)', line, re.IGNORECASE)
                if match:
                    constants['earth_mass'] = {
                        'value': match.group(1),
                        'line': i + 1,
                        'context': line.strip()
                    }
            
            # Population targets
            if '10 billion' in line.lower() or '10b' in line.lower():
                constants.setdefault('population_target', []).append({
                    'line': i + 1,
                    'context': line.strip()
                })
            
            # Journey duration
            if '5,000 year' in line.lower() or '5000 year' in line.lower():
                constants.setdefault('journey_duration', []).append({
                    'line': i + 1,
                    'context': line.strip()
                })
        
        self.metadata['technical_constants'] = constants
    
    def extract_key_concepts(self):
        """Extract major concepts and their first occurrence"""
        concepts = {
            'Aethelgard Protocol': [],
            'Moon-Tug': [],
            'Dyson Swarm': [],
            'The Rug': [],
            'Poly-Centric Oracle': [],
            'Prime Directive': [],
            'Synthesis Engine': [],
            'Vanguard Fleet': [],
            'Underground Hives': [],
            'Genesis Block': [],
            'Red-Line': [],
            'Temporal Latency Gate': [],
            'Semantic Hashing': [],
            'The Parliament': [],
            'Oracle Delta': [],
            'Oracle Beta': [],
            'Oracle Alpha': [],
            'Oracle Gamma': []
        }
        
        for i, line in enumerate(self.lines):
            for concept in concepts.keys():
                if concept.lower() in line.lower():
                    concepts[concept].append({
                        'line': i + 1,
                        'context': line.strip()[:200]
                    })
        
        # Keep only first 5 occurrences of each concept
        for concept in concepts:
            concepts[concept] = concepts[concept][:5]
        
        self.metadata['key_concepts'] = concepts
    
    def extract_section_structure(self):
        """Identify major sections and topics"""
        sections = []
        current_section = None
        
        # Patterns that indicate section headers
        section_patterns = [
            r'^#+\s+(.+)$',  # Markdown headers
            r'^[A-Z][^.!?]*:$',  # Topic headers ending with colon
            r'^\d+\.\s+(.+)$',  # Numbered sections
            r'^Phase\s+\w+:',  # Phase markers
            r'^Section\s+\d+',  # Section markers
        ]
        
        for i, line in enumerate(self.lines):
            stripped = line.strip()
            
            # Check for section headers
            for pattern in section_patterns:
                match = re.match(pattern, stripped)
                if match:
                    if current_section:
                        current_section['end_line'] = i
                        sections.append(current_section)
                    
                    current_section = {
                        'title': stripped,
                        'start_line': i + 1,
                        'end_line': None,
                        'type': 'section'
                    }
                    break
            
            # Detect major topic shifts
            if any(keyword in stripped.lower() for keyword in [
                'moving earth', 'planetary', 'oracle', 'manifesto', 
                'religious', 'governance', 'technical', 'implementation'
            ]):
                if not current_section or (i - current_section['start_line']) > 50:
                    if current_section:
                        current_section['end_line'] = i
                        sections.append(current_section)
                    current_section = {
                        'title': stripped[:100],
                        'start_line': i + 1,
                        'end_line': None,
                        'type': 'topic'
                    }
        
        if current_section:
            current_section['end_line'] = len(self.lines)
            sections.append(current_section)
        
        self.metadata['sections'] = sections[:50]  # Limit to first 50 sections
    
    def extract_timeline(self):
        """Extract timeline events and phases"""
        timeline = []
        
        year_patterns = [
            r'Year\s+(\d+)',
            r'(\d+)\s*-\s*(\d+)',
            r'Phase\s+(\w+).*?Year[s]?\s+(\d+)',
            r'(\d+)\s+years?\s+(?:from|before|after)',
            r'billion\s+years?',
            r'million\s+years?'
        ]
        
        for i, line in enumerate(self.lines):
            for pattern in year_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    timeline.append({
                        'line': i + 1,
                        'match': match.group(0),
                        'context': line.strip()[:150]
                    })
        
        self.metadata['timeline'] = timeline[:100]  # Limit to first 100 timeline refs
    
    def extract_oracle_definitions(self):
        """Extract the four Oracle definitions"""
        oracles = {
            'Sentinel': {'aliases': ['Oracle Alpha', 'The Sentinel'], 'references': []},
            'Humanist': {'aliases': ['Oracle Beta', 'The Humanist'], 'references': []},
            'Evolutionist': {'aliases': ['Oracle Gamma', 'The Evolutionist'], 'references': []},
            'Navigator': {'aliases': ['Oracle Delta', 'The Navigator'], 'references': []}
        }
        
        for i, line in enumerate(self.lines):
            for oracle_name, oracle_data in oracles.items():
                for alias in [oracle_name] + oracle_data['aliases']:
                    if alias.lower() in line.lower():
                        oracles[oracle_name]['references'].append({
                            'line': i + 1,
                            'context': line.strip()[:200]
                        })
        
        # Limit references
        for oracle in oracles.values():
            oracle['references'] = oracle['references'][:10]
        
        self.metadata['oracles'] = oracles
    
    def extract_quotes(self):
        """Extract key quotes for later reference"""
        quotes = []
        
        # Look for lines that seem like important statements
        for i, line in enumerate(self.lines):
            stripped = line.strip()
            
            # Skip very short or very long lines
            if len(stripped) < 50 or len(stripped) > 500:
                continue
            
            # Look for definitional statements
            if any(keyword in stripped.lower() for keyword in [
                'is defined as', 'means that', 'requires', 'must', 'ensures',
                'the goal is', 'the purpose', 'we call this'
            ]):
                quotes.append({
                    'line': i + 1,
                    'text': stripped,
                    'type': 'definition'
                })
        
        self.metadata['quotes'] = quotes[:50]  # Limit to 50 key quotes
    
    def extract_religious_references(self):
        """Extract religious and theological discussion points"""
        refs = []
        
        religious_keywords = [
            'bible', 'scripture', 'enoch', 'revelation', 'genesis',
            'god', 'divine', 'prophet', 'faith', 'theology',
            'christian', 'islam', 'dharma', 'buddhist'
        ]
        
        for i, line in enumerate(self.lines):
            if any(keyword in line.lower() for keyword in religious_keywords):
                refs.append({
                    'line': i + 1,
                    'context': line.strip()[:200]
                })
        
        self.metadata['religious_references'] = refs[:100]
    
    def extract_all(self):
        """Run all extraction methods"""
        print("Extracting technical constants...")
        self.extract_technical_constants()
        
        print("Extracting key concepts...")
        self.extract_key_concepts()
        
        print("Extracting section structure...")
        self.extract_section_structure()
        
        print("Extracting timeline...")
        self.extract_timeline()
        
        print("Extracting Oracle definitions...")
        self.extract_oracle_definitions()
        
        print("Extracting key quotes...")
        self.extract_quotes()
        
        print("Extracting religious references...")
        self.extract_religious_references()
        
        return self.metadata
    
    def save_metadata(self, output_dir: Path):
        """Save extracted metadata to JSON files"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save complete metadata
        with open(output_dir / 'metadata_complete.json', 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        
        # Save individual components
        components = [
            'technical_constants', 'key_concepts', 'sections',
            'timeline', 'oracles', 'quotes', 'religious_references'
        ]
        
        for component in components:
            with open(output_dir / f'{component}.json', 'w', encoding='utf-8') as f:
                json.dump(self.metadata[component], f, indent=2, ensure_ascii=False)
        
        print(f"\nMetadata saved to {output_dir}/")
        print(f"  - Total sections identified: {len(self.metadata['sections'])}")
        print(f"  - Key concepts tracked: {len(self.metadata['key_concepts'])}")
        print(f"  - Timeline events: {len(self.metadata['timeline'])}")
        print(f"  - Technical constants: {len(self.metadata['technical_constants'])}")


def main():
    # Paths
    source = Path('/Volumes/mnt/LAB/Planetary Exodus/data/raw.txt')
    output = Path('/Volumes/mnt/LAB/Planetary Exodus/metadata')
    
    if not source.exists():
        print(f"Error: Source file not found: {source}")
        return
    
    print("=" * 60)
    print("Aethelgard Protocol - Metadata Extraction")
    print("=" * 60)
    
    # Extract
    extractor = AethelgardExtractor(source)
    metadata = extractor.extract_all()
    
    # Save
    extractor.save_metadata(output)
    
    print("\n" + "=" * 60)
    print("Extraction complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
