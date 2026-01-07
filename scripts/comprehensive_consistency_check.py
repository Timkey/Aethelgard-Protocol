#!/usr/bin/env python3
"""
Comprehensive Consistency Checker
Uses vector DB + pattern matching to identify inconsistencies across all documents
"""

import re
import json
from collections import defaultdict
from typing import List, Dict, Tuple, Set
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Initialize
client = QdrantClient(host="qdrant", port=6333)
model = SentenceTransformer('all-MiniLM-L6-v2')
COLLECTION_NAME = "planetary_exodus_docs"

class ConsistencyIssue:
    def __init__(self, issue_type, severity, section1, section2, description, evidence):
        self.issue_type = issue_type
        self.severity = severity  # HIGH, MEDIUM, LOW
        self.section1 = section1
        self.section2 = section2
        self.description = description
        self.evidence = evidence
    
    def to_dict(self):
        return {
            "type": self.issue_type,
            "severity": self.severity,
            "section1": self.section1,
            "section2": self.section2,
            "description": self.description,
            "evidence": self.evidence
        }

class ConsistencyChecker:
    def __init__(self):
        self.issues = []
        self.all_sections = []
        self.load_all_sections()
    
    def load_all_sections(self):
        """Load all sections from vector DB"""
        print("Loading all sections from vector DB...")
        result = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=1000,
            with_payload=True,
            with_vectors=False
        )
        self.all_sections = result[0]
        print(f"Loaded {len(self.all_sections)} sections")
    
    def add_issue(self, issue_type, severity, section1, section2, description, evidence):
        """Add a consistency issue"""
        issue = ConsistencyIssue(issue_type, severity, section1, section2, description, evidence)
        self.issues.append(issue)
    
    # ========================================
    # PASS 1: TIMELINE CONSISTENCY
    # ========================================
    
    def extract_timeline_references(self, text: str) -> List[Dict]:
        """Extract all timeline references from text"""
        patterns = [
            # Year patterns
            (r'\b(\d{4})\s*(?:CE|AD|year)?\b', 'year'),
            # Year ranges
            (r'\b(\d{4})\s*[-–]\s*(\d{4})\b', 'year_range'),
            # Million years
            (r'\b(\d+(?:\.\d+)?)\s*million\s+years?\b', 'million_years'),
            # Billion years
            (r'\b(\d+(?:\.\d+)?)\s*billion\s+years?\b', 'billion_years'),
            # Phase references
            (r'Phase\s+(Zero|One|Two|Three|Four|0|1|2|3|4)\b', 'phase'),
            # Duration patterns
            (r'\b(\d+)\s*(years?|decades?|centuries?|millennia)\b', 'duration'),
        ]
        
        references = []
        for pattern, ref_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                references.append({
                    'type': ref_type,
                    'value': match.group(0),
                    'position': match.start()
                })
        
        return references
    
    def check_timeline_consistency(self):
        """Check for timeline inconsistencies"""
        print("\n=== PASS 1: Timeline Consistency ===")
        
        timeline_data = defaultdict(list)
        
        # Collect all timeline references by document
        for section in self.all_sections:
            payload = section.payload
            text = payload.get('text', '')
            doc = payload.get('document', '')
            
            refs = self.extract_timeline_references(text)
            if refs:
                timeline_data[doc].append({
                    'section_title': payload.get('section_title', ''),
                    'section_number': payload.get('section_number', ''),
                    'references': refs,
                    'text_snippet': text[:200]
                })
        
        # Check for phase boundary conflicts
        phase_boundaries = {
            'Phase Zero': (2026, 2150),
            'Phase One': (2150, 10000),
            'Phase Two': (10000, 100000000),  # 100M years
            'Phase Three': (100000000, 500000000),  # 500M years
            'Phase Four': (500000000, 600000000),  # 600M years
        }
        
        # Look for statements that violate phase boundaries
        for doc, sections in timeline_data.items():
            for section in sections:
                text = section['text_snippet']
                
                # Check if section is in a phase chapter
                phase_match = re.search(r'Phase\s+(Zero|One|Two|Three|Four)', doc)
                if phase_match:
                    phase_name = f"Phase {phase_match.group(1)}"
                    
                    # Look for year references that fall outside the phase boundary
                    for ref in section['references']:
                        if ref['type'] == 'year':
                            year = int(re.search(r'\d+', ref['value']).group())
                            if phase_name in phase_boundaries:
                                start, end = phase_boundaries[phase_name]
                                if year < start or year > end:
                                    self.add_issue(
                                        'TIMELINE_PHASE_MISMATCH',
                                        'HIGH',
                                        f"{doc} - {section['section_title']}",
                                        phase_name,
                                        f"Year {year} mentioned in {phase_name} but falls outside phase bounds ({start}-{end})",
                                        {'year': year, 'phase': phase_name, 'text': text}
                                    )
        
        print(f"Found {sum(1 for i in self.issues if i.issue_type == 'TIMELINE_PHASE_MISMATCH')} timeline issues")
    
    # ========================================
    # PASS 2: TECHNICAL CONSTANTS
    # ========================================
    
    def extract_technical_values(self, text: str) -> List[Dict]:
        """Extract technical constants and values"""
        patterns = [
            # Scientific notation
            (r'\b(\d+(?:\.\d+)?)\s*[×x]\s*10\^(\d+)\b', 'scientific'),
            # Energy values
            (r'\b(\d+(?:\.\d+)?)\s*(joules?|J|watts?|W|terawatts?|TW)\b', 'energy'),
            # Mass values
            (r'\b(\d+(?:\.\d+)?)\s*(?:×\s*)?10\^(\d+)\s*(kg|kilograms?|tons?)\b', 'mass'),
            # Distance values
            (r'\b(\d+(?:\.\d+)?)\s*(light[\s-]?years?|ly|parsecs?|pc|AU|astronomical\s+units?)\b', 'distance'),
            # Temperature values
            (r'\b(\d+(?:\.\d+)?)\s*(K|kelvin|°C|celsius)\b', 'temperature'),
            # Population values
            (r'\b(\d+(?:\.\d+)?)\s*(billion|million|thousand)\s+(?:people|humans?|population)\b', 'population'),
        ]
        
        values = []
        for pattern, value_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                values.append({
                    'type': value_type,
                    'value': match.group(0),
                    'position': match.start()
                })
        
        return values
    
    def check_technical_consistency(self):
        """Check for conflicting technical constants"""
        print("\n=== PASS 2: Technical Constants ===")
        
        # Collect all technical values by concept
        constant_map = defaultdict(list)
        
        for section in self.all_sections:
            payload = section.payload
            text = payload.get('text', '')
            
            values = self.extract_technical_values(text)
            
            # Look for common constants
            if 'Earth' in text and 'mass' in text.lower():
                constant_map['earth_mass'].append({
                    'document': payload.get('document', ''),
                    'section': payload.get('section_title', ''),
                    'values': values,
                    'text': text[:300]
                })
            
            if 'population' in text.lower() and any(v['type'] == 'population' for v in values):
                constant_map['population'].append({
                    'document': payload.get('document', ''),
                    'section': payload.get('section_title', ''),
                    'values': values,
                    'text': text[:300]
                })
            
            if 'Sun' in text and ('luminosity' in text.lower() or 'lifetime' in text.lower()):
                constant_map['sun_properties'].append({
                    'document': payload.get('document', ''),
                    'section': payload.get('section_title', ''),
                    'values': values,
                    'text': text[:300]
                })
        
        # Check for conflicting values
        for constant_name, occurrences in constant_map.items():
            if len(occurrences) > 1:
                # Compare values across occurrences
                for i in range(len(occurrences)):
                    for j in range(i + 1, len(occurrences)):
                        occ1, occ2 = occurrences[i], occurrences[j]
                        
                        # If both have values of the same type, compare them
                        types1 = {v['type'] for v in occ1['values']}
                        types2 = {v['type'] for v in occ2['values']}
                        
                        common_types = types1 & types2
                        if common_types:
                            # Found same type of value in both - potential conflict
                            self.add_issue(
                                'TECHNICAL_CONSTANT_CHECK',
                                'MEDIUM',
                                f"{occ1['document']} - {occ1['section']}",
                                f"{occ2['document']} - {occ2['section']}",
                                f"Both sections discuss {constant_name} with numerical values - verify consistency",
                                {
                                    'constant': constant_name,
                                    'text1': occ1['text'],
                                    'text2': occ2['text'],
                                    'values1': occ1['values'],
                                    'values2': occ2['values']
                                }
                            )
        
        print(f"Found {sum(1 for i in self.issues if i.issue_type == 'TECHNICAL_CONSTANT_CHECK')} technical value checks needed")
    
    # ========================================
    # PASS 3: SEMANTIC CONTRADICTIONS
    # ========================================
    
    def check_semantic_consistency(self):
        """Use vector search to find contradictory statements"""
        print("\n=== PASS 3: Semantic Contradictions ===")
        
        # Key claims to verify across documents
        verification_queries = [
            "How long until the Sun becomes uninhabitable",
            "When does Phase Zero begin and end",
            "How many people will be saved",
            "What is the final destination star system",
            "How will Earth be moved",
            "What is the purpose of the Oracle system",
            "When will the Moon tug be constructed",
            "How long is the interstellar journey",
            "What happens during Phase Three",
            "What happens during Phase Four",
            "How is the population managed",
            "What is the Dyson swarm used for",
            "How are resources allocated",
            "What is the governance structure",
        ]
        
        for query in verification_queries:
            # Search for relevant sections
            query_vector = model.encode(query).tolist()
            
            results = client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_vector,
                limit=5,
                score_threshold=0.5
            )
            
            if len(results) >= 2:
                # Compare top results for consistency
                texts = []
                sources = []
                
                for result in results[:3]:
                    payload = result.payload
                    texts.append(payload.get('text', '')[:500])
                    sources.append(f"{payload.get('document', '')} - {payload.get('section_title', '')}")
                
                # Look for contradiction keywords
                contradiction_indicators = [
                    (r'\bnot\b', r'\bis\b'),
                    (r'\bno\b', r'\byes\b'),
                    (r'\bimpossible\b', r'\bpossible\b'),
                    (r'\bcannot\b', r'\bcan\b'),
                    (r'\bnever\b', r'\balways\b'),
                ]
                
                # Check for numeric contradictions
                numbers_in_texts = []
                for text in texts:
                    nums = re.findall(r'\b\d+(?:\.\d+)?(?:\s*[×x]\s*10\^\d+)?\b', text)
                    numbers_in_texts.append(set(nums))
                
                # If different numbers appear in similar contexts, flag it
                if len(numbers_in_texts) >= 2:
                    unique_nums = set()
                    for nums in numbers_in_texts:
                        if nums:
                            unique_nums.update(nums)
                    
                    if len(unique_nums) > 1 and len(results) >= 2:
                        self.add_issue(
                            'SEMANTIC_CONTRADICTION_CHECK',
                            'MEDIUM',
                            sources[0],
                            sources[1] if len(sources) > 1 else sources[0],
                            f"Query '{query}' returns sections with different numerical values",
                            {
                                'query': query,
                                'texts': texts[:2],
                                'sources': sources[:2],
                                'numbers': list(unique_nums)
                            }
                        )
        
        print(f"Found {sum(1 for i in self.issues if i.issue_type == 'SEMANTIC_CONTRADICTION_CHECK')} semantic checks needed")
    
    # ========================================
    # PASS 4: PHASE BOUNDARY VALIDATION
    # ========================================
    
    def check_phase_boundaries(self):
        """Validate that phase chapters contain appropriate content"""
        print("\n=== PASS 4: Phase Boundary Validation ===")
        
        phase_keywords = {
            'Phase Zero': ['2026', '2150', 'present', 'near-term', 'initial', 'foundation'],
            'Phase One': ['2150', '10,000', 'millennia', 'construction', 'infrastructure'],
            'Phase Two': ['10,000', '100 million', 'Moon tug', 'orbital mechanics'],
            'Phase Three': ['100 million', '500 million', 'preparation', 'evacuation planning'],
            'Phase Four': ['500 million', '600 million', 'evacuation', 'departure', 'Earth departure'],
        }
        
        for section in self.all_sections:
            payload = section.payload
            doc = payload.get('document', '')
            text = payload.get('text', '')
            section_title = payload.get('section_title', '')
            
            # Check if this is a phase chapter
            phase_match = re.search(r'Phase\s+(Zero|One|Two|Three|Four)', doc)
            if phase_match:
                phase_name = f"Phase {phase_match.group(1)}"
                
                # Check for inappropriate keywords
                for other_phase, keywords in phase_keywords.items():
                    if other_phase != phase_name:
                        # Count how many keywords from other phases appear
                        keyword_count = sum(1 for kw in keywords if kw.lower() in text.lower())
                        
                        if keyword_count >= 3:
                            self.add_issue(
                                'PHASE_CONTENT_MISMATCH',
                                'HIGH',
                                f"{doc} - {section_title}",
                                phase_name,
                                f"Section in {phase_name} contains significant content about {other_phase}",
                                {
                                    'expected_phase': phase_name,
                                    'detected_phase': other_phase,
                                    'keyword_count': keyword_count,
                                    'text_snippet': text[:400]
                                }
                            )
        
        print(f"Found {sum(1 for i in self.issues if i.issue_type == 'PHASE_CONTENT_MISMATCH')} phase content mismatches")
    
    # ========================================
    # PASS 5: CROSS-REFERENCE VALIDATION
    # ========================================
    
    def check_cross_references(self):
        """Check that cross-references between chapters are consistent"""
        print("\n=== PASS 5: Cross-Reference Validation ===")
        
        # Extract references to other chapters
        for section in self.all_sections:
            payload = section.payload
            text = payload.get('text', '')
            doc = payload.get('document', '')
            
            # Find references to other chapters
            chapter_refs = re.findall(r'Chapter\s+(\d+)', text, re.IGNORECASE)
            
            for ref_num in chapter_refs:
                # Search for what this chapter says about the referenced chapter
                query = f"Chapter {ref_num}"
                query_vector = model.encode(query).tolist()
                
                # Find the actual referenced chapter
                results = client.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=query_vector,
                    limit=3,
                    query_filter={
                        "must": [
                            {
                                "key": "document",
                                "match": {"any": [f"Chapter_{ref_num}", f"Chapter {ref_num}"]}
                            }
                        ]
                    }
                )
                
                if not results:
                    self.add_issue(
                        'BROKEN_REFERENCE',
                        'LOW',
                        f"{doc}",
                        f"Chapter {ref_num}",
                        f"References Chapter {ref_num} but chapter may not exist or is empty",
                        {'reference': f"Chapter {ref_num}", 'source': doc}
                    )
        
        print(f"Found {sum(1 for i in self.issues if i.issue_type == 'BROKEN_REFERENCE')} cross-reference issues")
    
    # ========================================
    # REPORTING
    # ========================================
    
    def generate_report(self, output_file: str = '/app/output/reports/consistency_issues.json'):
        """Generate detailed consistency report"""
        print(f"\n=== Generating Report ===")
        
        report = {
            'total_issues': len(self.issues),
            'by_severity': {
                'HIGH': sum(1 for i in self.issues if i.severity == 'HIGH'),
                'MEDIUM': sum(1 for i in self.issues if i.severity == 'MEDIUM'),
                'LOW': sum(1 for i in self.issues if i.severity == 'LOW'),
            },
            'by_type': {},
            'issues': [i.to_dict() for i in self.issues]
        }
        
        # Count by type
        for issue in self.issues:
            report['by_type'][issue.issue_type] = report['by_type'].get(issue.issue_type, 0) + 1
        
        # Save JSON report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nReport saved to {output_file}")
        print(f"\nTotal Issues: {report['total_issues']}")
        print(f"  HIGH severity: {report['by_severity']['HIGH']}")
        print(f"  MEDIUM severity: {report['by_severity']['MEDIUM']}")
        print(f"  LOW severity: {report['by_severity']['LOW']}")
        print(f"\nIssues by type:")
        for issue_type, count in sorted(report['by_type'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {issue_type}: {count}")
        
        return report
    
    def generate_markdown_report(self, output_file: str = '/app/output/reports/consistency_issues.md'):
        """Generate human-readable markdown report"""
        issues_by_type = defaultdict(list)
        for issue in self.issues:
            issues_by_type[issue.issue_type].append(issue)
        
        with open(output_file, 'w') as f:
            f.write("# Consistency Issues Report\n\n")
            f.write(f"**Generated:** {__import__('datetime').datetime.now().isoformat()}\n\n")
            f.write(f"**Total Issues:** {len(self.issues)}\n\n")
            
            f.write("## Summary by Severity\n\n")
            for severity in ['HIGH', 'MEDIUM', 'LOW']:
                count = sum(1 for i in self.issues if i.severity == severity)
                f.write(f"- **{severity}:** {count}\n")
            
            f.write("\n## Summary by Type\n\n")
            for issue_type, issues in sorted(issues_by_type.items(), key=lambda x: len(x[1]), reverse=True):
                f.write(f"- **{issue_type}:** {len(issues)}\n")
            
            f.write("\n---\n\n")
            
            # Detailed issues by type
            for issue_type, issues in sorted(issues_by_type.items()):
                f.write(f"## {issue_type}\n\n")
                
                for i, issue in enumerate(issues, 1):
                    f.write(f"### {i}. [{issue.severity}] {issue.description}\n\n")
                    f.write(f"**Location 1:** {issue.section1}\n\n")
                    if issue.section2 and issue.section2 != issue.section1:
                        f.write(f"**Location 2:** {issue.section2}\n\n")
                    
                    f.write("**Evidence:**\n\n")
                    if isinstance(issue.evidence, dict):
                        for key, value in issue.evidence.items():
                            if isinstance(value, str) and len(value) > 200:
                                value = value[:200] + "..."
                            f.write(f"- **{key}:** {value}\n")
                    else:
                        f.write(f"{issue.evidence}\n")
                    
                    f.write("\n---\n\n")
        
        print(f"Markdown report saved to {output_file}")
    
    def run_all_checks(self):
        """Run all consistency checks"""
        print("Starting comprehensive consistency check...")
        print(f"Analyzing {len(self.all_sections)} sections\n")
        
        self.check_timeline_consistency()
        self.check_technical_consistency()
        self.check_semantic_consistency()
        self.check_phase_boundaries()
        self.check_cross_references()
        
        self.generate_report()
        self.generate_markdown_report()
        
        print("\n✅ Consistency check complete!")
        return self.issues


def main():
    checker = ConsistencyChecker()
    checker.run_all_checks()


if __name__ == '__main__':
    main()
