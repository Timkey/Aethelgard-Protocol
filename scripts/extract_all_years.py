#!/usr/bin/env python3
"""
Extract ALL year references from documents

Systematically finds every year mention (not guessing), categorizes them,
and identifies potential timeline inconsistencies using semantic graph context.

Usage:
    python scripts/extract_all_years.py
"""

import re
import json
from pathlib import Path
from collections import defaultdict


class YearExtractor:
    """Extract and analyze all year references"""
    
    def __init__(self, docs_dir: str = '/app/docs'):
        self.docs_dir = Path(docs_dir)
        self.year_references = []
        self.semantic_graph = None
        
    def load_semantic_graph(self):
        """Load semantic graph if available"""
        graph_file = Path('/app/output/reports/semantic_graph.json')
        if graph_file.exists():
            with open(graph_file, 'r') as f:
                self.semantic_graph = json.load(f)
            print(f"✓ Loaded semantic graph with {len(self.semantic_graph['paragraphs'])} paragraphs")
        else:
            print("⚠️  Semantic graph not found - run ./exec/build_semantic_graph first")
    
    def extract_all_years(self):
        """Extract every temporal reference from all documents"""
        print(f"\n📅 Extracting all temporal references from {self.docs_dir}")
        
        # Multiple patterns for different temporal references
        patterns = {
            'numeric_year': re.compile(r'\b([12]\d{3})\b'),  # 1000-2999
            'written_number_time': re.compile(r'\b(one|two|three|four|five|six|seven|eight|nine|ten|twenty|thirty|forty|fifty|hundred|thousand|million|billion)\s+(year|years|century|centuries|millennium|millennia|decade|decades)\b', re.IGNORECASE),
            'numeric_time': re.compile(r'\b(\d+(?:,\d+)*(?:\.\d+)?)\s*(year|years|century|centuries|millennium|millennia|decade|decades|M\s*year|million\s+year)', re.IGNORECASE),
            'ordinal_time': re.compile(r'\b(\d+(?:st|nd|rd|th))\s+(century|millennium)\b', re.IGNORECASE),
            'year_range': re.compile(r'(\d{4})[–-](\d{4})'),  # 2500-3000
            'relative_time': re.compile(r'\b(after|before|during|by|within)\s+(\d+)\s*(year|years|century|centuries)\b', re.IGNORECASE),
            'temporal_phrases': re.compile(r'\b(centuries\s+later|decades\s+after|years\s+hence|millennia\s+from|mid-century|turn\s+of\s+the\s+century|by\s+then)\b', re.IGNORECASE)
        }
        
        source_pattern = re.compile(r'raw\.txt:\d+-\d+')  # Matches source citations
        
        for md_file in sorted(self.docs_dir.glob("*.md")):
            doc_name = md_file.stem
            
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Skip source citations (raw.txt references)
                if source_pattern.search(line):
                    continue
                
                # Skip lines that reference raw.txt line numbers (e.g., "Lines 2447-2449")
                if 'lines ' in line.lower() and 'raw.txt' not in line.lower():
                    # Check if it looks like a line number reference
                    if re.search(r'\blines?\s+\d{3,4}[-–]\d{3,4}\b', line, re.IGNORECASE):
                        continue
                
                # Get context (surrounding lines - wider window to catch section headers)
                start = max(0, line_num - 10)
                end = min(len(lines), line_num + 10)
                context = '\n'.join(lines[start:end])
                
                # Check all patterns
                for pattern_name, pattern in patterns.items():
                    for match in pattern.finditer(line):
                        temporal_ref = match.group(0)
                        
                        # Extract year if it's a numeric year
                        year = None
                        if pattern_name == 'numeric_year':
                            year = int(match.group(1))
                            # Filter out unlikely years
                            if year < 1900 or year > 9999:
                                continue
                        
                        # Determine category
                        category = self._categorize_temporal_ref(temporal_ref, line, context, pattern_name)
                        
                        self.year_references.append({
                            'year': year,
                            'temporal_reference': temporal_ref,
                            'pattern_type': pattern_name,
                            'document': doc_name,
                            'line_number': line_num,
                            'line_text': line.strip(),
                            'context': context,
                            'category': category,
                            'match_position': match.start()
                        })
        
        print(f"   ✓ Found {len(self.year_references)} temporal references")
    
    def _categorize_temporal_ref(self, temporal_ref, line, context, pattern_type):
        """Categorize what type of temporal reference this is"""
        context_lower = context.lower()
        line_lower = line.lower()
        ref_lower = temporal_ref.lower()
        
        # Source citations (should already be filtered but double-check)
        if 'raw.txt' in line or 'source:' in line_lower:
            return 'source_citation'
        
        # Check if this is a deep-time reference (millions/billions of years)
        if any(term in ref_lower for term in ['million', 'billion', 'm year']):
            # This is expected in deep-time phases
            if any(p in context_lower for p in ['phase two', 'phase 2', 'phase three', 'phase 3', 'phase four', 'phase 4']):
                return 'deep_time_appropriate'
            else:
                return 'deep_time_reference'
        
        # Check for near-term specific years
        if pattern_type == 'numeric_year':
            year_match = re.search(r'(\d{4})', temporal_ref)
            if year_match:
                year = int(year_match.group(1))
                
                # Phase definitions
                if 'phase zero' in context_lower or 'phase 0' in context_lower:
                    if year >= 2026 and year <= 2150:
                        return 'phase_zero_definition'
                    else:
                        return 'phase_zero_content'
                
                if 'phase one' in context_lower or 'phase 1' in context_lower:
                    if year > 2150 and year <= 10000:
                        return 'phase_one_definition'
                    else:
                        return 'phase_one_content'
                
                # Phase Two/Three/Four content (should NOT have specific calendar years)
                if any(p in context_lower for p in ['phase two', 'phase 2', 'phase three', 'phase 3', 'phase four', 'phase 4']):
                    return 'deep_time_phase_ERROR'
                
                # Event descriptions - check for clarifying context first
                if any(kw in context_lower for kw in ['evacuation', 'departure', 'exodus', 'arrival', 'migration']):
                    # Check if context clarifies this is testing/infrastructure, not actual evacuation
                    clarifying_phrases = [
                        'timeline context', 'this is not evacuation', 'testing', 
                        'validation', 'infrastructure development', 'infrastructure validation',
                        'testing and validation', 'prototype', 'voluntary migration for testing',
                        'phase zero/one testing', 'construction', 'capability development',
                        'not the phase four evacuation', 'infrastructure testing',
                        'voluntary migration for infrastructure'
                    ]
                    has_clarification = any(phrase in context_lower for phrase in clarifying_phrases)
                    
                    # Phase Zero/One dates with clarification are OK
                    if year >= 2026 and year <= 10000:
                        if has_clarification:
                            return 'operational_phase_zero_clarified'
                        else:
                            return 'event_near_term_ERROR'  # Evacuation should be ~500M years
                    else:
                        return 'event_description'
                
                # Historical references (past)
                if year < 2026:
                    return 'historical_reference'
                
                # Near-term operational timeline
                if year >= 2026 and year <= 2150:
                    return 'operational_phase_zero'
                elif year > 2150 and year <= 10000:
                    return 'operational_phase_one'
        
        # Short durations (years, decades, centuries without million/billion)
        if pattern_type in ['written_number_time', 'numeric_time', 'relative_time']:
            # Check if in deep-time context
            if any(p in context_lower for p in ['phase two', 'phase 2', 'phase three', 'phase 3', 'phase four', 'phase 4']):
                # Short durations in deep-time phases might be OK (e.g., "100 years of testing")
                # But be suspicious if talking about events
                if any(kw in context_lower for kw in ['evacuation', 'departure', 'exodus', 'arrival', 'complete']):
                    return 'short_duration_deep_time_WARNING'
                return 'duration_deep_time'
            return 'duration_reference'
        
        # Default
        return 'uncategorized'
    
    def find_problematic_years(self):
        """Identify potentially inconsistent year references"""
        print(f"\n🔍 Analyzing for inconsistencies...")
        
        problems = []
        
        for ref in self.year_references:
            # Skip safe categories
            if ref['category'] in ['historical_reference', 'source_citation', 
                                   'phase_zero_definition', 'phase_one_definition',
                                   'operational_phase_zero', 'operational_phase_one',
                                   'operational_phase_zero_clarified',  # Added: Phase Zero dates with proper context
                                   'deep_time_appropriate', 'deep_time_reference',
                                   'duration_reference', 'duration_deep_time',
                                   'uncategorized']:
                continue
            
            # Flag errors
            if 'ERROR' in ref['category']:
                problems.append({
                    'severity': 'HIGH',
                    'reason': 'Near-term year in deep-time context or evacuation event',
                    **ref
                })
            
            # Flag warnings
            elif 'WARNING' in ref['category']:
                problems.append({
                    'severity': 'MEDIUM',
                    'reason': 'Short duration reference in deep-time phase',
                    **ref
                })
            
            # Flag suspicious patterns (only check if year is not None)
            elif ref['year'] is not None and ref['year'] >= 2200 and ref['year'] <= 9999:
                # Years between 2200-9999 are suspicious if not in Phase definitions
                if ref['category'] not in ['timeline_future', 'event_description']:
                    problems.append({
                        'severity': 'MEDIUM',
                        'reason': 'Year in suspicious range (2200-9999)',
                        **ref
                    })
        
        print(f"   ✓ Found {len(problems)} potentially problematic temporal references")
        return problems
    
    def map_to_paragraphs(self, problems):
        """Map problematic years to semantic graph paragraphs"""
        if not self.semantic_graph:
            return problems
        
        print(f"\n🗺️  Mapping to semantic graph paragraphs...")
        
        for problem in problems:
            # Find corresponding paragraph
            for para in self.semantic_graph['paragraphs']:
                if (para['document'] == problem['document'] and 
                    problem['line_text'][:50] in para['content']):
                    
                    problem['paragraph_id'] = para['id']
                    problem['section'] = para['section']
                    
                    # Find related paragraphs
                    related_count = sum(1 for edge in self.semantic_graph['edges']
                                      if edge['para1_id'] == para['id'] or edge['para2_id'] == para['id'])
                    problem['related_paragraphs'] = related_count
                    break
        
        return problems
    
    def generate_report(self, problems, output_file: str):
        """Generate comprehensive report"""
        print(f"\n📄 Generating report...")
        
        with open(output_file, 'w') as f:
            f.write("# Comprehensive Year Reference Analysis\n\n")
            f.write(f"**Total year references found:** {len(self.year_references)}\n")
            f.write(f"**Problematic references:** {len(problems)}\n\n")
            
            # Summary by category
            f.write("## Year References by Category\n\n")
            by_category = defaultdict(int)
            for ref in self.year_references:
                by_category[ref['category']] += 1
            
            for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
                marker = "❌" if "ERROR" in cat else "✅"
                f.write(f"- {marker} **{cat}**: {count} references\n")
            
            f.write("\n## Year Distribution\n\n")
            by_year = defaultdict(int)
            for ref in self.year_references:
                by_year[ref['year']] += 1
            
            # Most common years
            top_years = sorted(by_year.items(), key=lambda x: x[1], reverse=True)[:20]
            for year, count in top_years:
                f.write(f"- **{year}**: {count} references\n")
            
            # Problematic years
            f.write("\n## Problematic Year References\n\n")
            
            high_priority = [p for p in problems if p['severity'] == 'HIGH']
            medium_priority = [p for p in problems if p['severity'] == 'MEDIUM']
            
            if high_priority:
                f.write(f"### 🔴 HIGH Priority ({len(high_priority)} issues)\n\n")
                for prob in high_priority:
                    f.write(f"#### Year {prob['year']} in [{prob['document']}]\n\n")
                    f.write(f"**Line {prob['line_number']}:** {prob['line_text']}\n\n")
                    f.write(f"**Reason:** {prob['reason']}\n\n")
                    if 'section' in prob:
                        f.write(f"**Section:** {prob['section']}\n\n")
                    if 'related_paragraphs' in prob:
                        f.write(f"**Related paragraphs:** {prob['related_paragraphs']}\n\n")
                    f.write(f"**Context:**\n```\n{prob['context']}\n```\n\n")
            
            if medium_priority:
                f.write(f"### 🟡 MEDIUM Priority ({len(medium_priority)} issues)\n\n")
                for prob in medium_priority[:10]:  # Limit to top 10
                    f.write(f"#### Year {prob['year']} in [{prob['document']}]\n\n")
                    f.write(f"**Line {prob['line_number']}:** {prob['line_text']}\n\n")
                    f.write(f"**Context:** {prob['context'][:200]}...\n\n")
        
        print(f"   ✓ Saved report to {output_file}")
    
    def export_json(self, problems, output_file: str):
        """Export as JSON for programmatic access"""
        data = {
            'metadata': {
                'total_references': len(self.year_references),
                'problematic_references': len(problems),
                'high_priority': len([p for p in problems if p['severity'] == 'HIGH']),
                'medium_priority': len([p for p in problems if p['severity'] == 'MEDIUM'])
            },
            'all_references': self.year_references,
            'problems': problems
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"   ✓ Saved JSON to {output_file}")


def main():
    print("=" * 80)
    print("📅 COMPREHENSIVE YEAR REFERENCE EXTRACTOR")
    print("=" * 80)
    
    extractor = YearExtractor()
    extractor.load_semantic_graph()
    extractor.extract_all_years()
    problems = extractor.find_problematic_years()
    problems = extractor.map_to_paragraphs(problems)
    
    output_dir = Path('/app/output/reports')
    extractor.generate_report(problems, output_dir / 'year_analysis.md')
    extractor.export_json(problems, output_dir / 'year_analysis.json')
    
    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\n📊 Summary:")
    print(f"   - Total years found: {len(extractor.year_references)}")
    print(f"   - Problematic: {len(problems)}")
    print(f"   - HIGH priority: {len([p for p in problems if p['severity'] == 'HIGH'])}")
    print(f"   - MEDIUM priority: {len([p for p in problems if p['severity'] == 'MEDIUM'])}")
    print(f"\n📁 Reports:")
    print(f"   - {output_dir / 'year_analysis.md'}")
    print(f"   - {output_dir / 'year_analysis.json'}\n")


if __name__ == '__main__':
    main()
