#!/usr/bin/env python3
"""
Comprehensive Timeline Consistency Analyzer
Identifies year references and maps them to correct phases
"""

import re
import json
from collections import defaultdict
from pathlib import Path

class TimelineAnalyzer:
    def __init__(self):
        self.docs_path = Path('/app/output/docs')
        self.timeline_issues = defaultdict(list)
        
        # Define phase boundaries
        self.phases = {
            'Phase Zero': {
                'timeframe': '2026-2150',
                'years_range': (2026, 2150),
                'description': 'Testing era (near-term)',
                'valid_year_refs': True  # Near-term years are valid
            },
            'Phase One': {
                'timeframe': '2150-10,000',
                'years_range': (2150, 10000),
                'description': 'Scaling era (near-term)',
                'valid_year_refs': True  # Near-term years are valid
            },
            'Phase Two': {
                'timeframe': '10,000-100M years',
                'years_range': (10000, 100_000_000),
                'description': 'Maintenance era (deep-time)',
                'valid_year_refs': False  # Should use "millions of years", not specific years
            },
            'Phase Three': {
                'timeframe': '100M-500M years',
                'years_range': (100_000_000, 500_000_000),
                'description': 'Preparation era (deep-time)',
                'valid_year_refs': False  # Should use "millions of years", not specific years
            },
            'Phase Four': {
                'timeframe': '500M-600M years',
                'years_range': (500_000_000, 600_000_000),
                'description': 'Evacuation era (deep-time)',
                'valid_year_refs': False  # Should use "millions of years", not specific years
            }
        }
        
        # Keywords that indicate departure/evacuation (should only be in Phase Four)
        self.phase_four_keywords = [
            'departure', 'evacuation', 'exodus', 'leave Earth', 
            'surface abandonment', 'last human on surface', 'uninhabitable',
            'ocean evaporation', 'final evacuation'
        ]
    
    def extract_year_references(self, text, filepath):
        """Extract all year references (2XXX-9XXX range)"""
        # Pattern for years: 2XXX-9XXX
        year_pattern = r'\b([2-9]\d{3})\b'
        
        matches = []
        for match in re.finditer(year_pattern, text):
            year = int(match.group(1))
            context_start = max(0, match.start() - 100)
            context_end = min(len(text), match.end() + 100)
            context = text[context_start:context_end]
            
            matches.append({
                'year': year,
                'position': match.start(),
                'context': context.strip(),
                'line_number': text[:match.start()].count('\n') + 1
            })
        
        return matches
    
    def detect_chapter_phase(self, filepath):
        """Detect which phase a chapter belongs to"""
        filename = filepath.name
        
        if '18' in filename or 'Phase_Zero' in filename:
            return 'Phase Zero'
        elif '19' in filename or 'Phase_One' in filename:
            return 'Phase One'
        elif '20' in filename or 'Phase_Two' in filename:
            return 'Phase Two'
        elif '21' in filename or 'Phase_Three' in filename:
            return 'Phase Three'
        elif '22' in filename or 'Phase_Four' in filename:
            return 'Phase Four'
        
        return None
    
    def check_context_for_phase_four_content(self, context):
        """Check if context contains Phase Four keywords"""
        context_lower = context.lower()
        found_keywords = [kw for kw in self.phase_four_keywords if kw in context_lower]
        return found_keywords
    
    def analyze_all_documents(self):
        """Analyze all markdown documents for timeline issues"""
        print("🔍 Analyzing timeline consistency across all documents...\n")
        
        issues = {
            'near_term_in_deep_time': [],  # Years like 2500 used in Phase 2/3/4
            'phase_four_content_in_wrong_phase': [],  # Evacuation content in wrong phase
            'valid_references': [],  # Correct year usage
        }
        
        for doc_file in sorted(self.docs_path.glob('*.md')):
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            phase = self.detect_chapter_phase(doc_file)
            if not phase:
                continue
            
            year_refs = self.extract_year_references(content, doc_file)
            
            for ref in year_refs:
                year = ref['year']
                context = ref['context']
                
                # Check if this is a deep-time phase using near-term years
                if phase in ['Phase Two', 'Phase Three', 'Phase Four']:
                    if 2000 <= year <= 10000:
                        # Check if it's describing Phase Four content
                        phase_four_kws = self.check_context_for_phase_four_content(context)
                        
                        issues['near_term_in_deep_time'].append({
                            'file': str(doc_file.name),
                            'phase': phase,
                            'year': year,
                            'line': ref['line_number'],
                            'context': context[:150],
                            'phase_four_keywords': phase_four_kws,
                            'severity': 'HIGH' if phase_four_kws else 'MEDIUM'
                        })
                    else:
                        issues['valid_references'].append({
                            'file': str(doc_file.name),
                            'phase': phase,
                            'year': year,
                            'line': ref['line_number']
                        })
                else:
                    # Phase Zero or One - near-term years are valid
                    issues['valid_references'].append({
                        'file': str(doc_file.name),
                        'phase': phase,
                        'year': year,
                        'line': ref['line_number']
                    })
        
        return issues
    
    def generate_report(self, issues):
        """Generate comprehensive report"""
        report = []
        
        report.append("="*80)
        report.append("TIMELINE CONSISTENCY ANALYSIS REPORT")
        report.append("="*80)
        report.append("")
        
        # Summary
        near_term_issues = len(issues['near_term_in_deep_time'])
        high_severity = sum(1 for i in issues['near_term_in_deep_time'] if i['severity'] == 'HIGH')
        
        report.append("## SUMMARY")
        report.append("")
        report.append(f"Total Issues Found: {near_term_issues}")
        report.append(f"  - HIGH Severity: {high_severity} (Phase Four content with near-term years)")
        report.append(f"  - MEDIUM Severity: {near_term_issues - high_severity} (Near-term years in deep-time phases)")
        report.append(f"Valid References: {len(issues['valid_references'])}")
        report.append("")
        
        # Core Problem Explanation
        report.append("## THE PROBLEM")
        report.append("")
        report.append("The document mixes two incompatible timelines:")
        report.append("")
        report.append("1. **Near-Term Timeline (CORRECT for Phase 0-1):**")
        report.append("   - Phase Zero: 2026-2150 (testing)")
        report.append("   - Phase One: 2150-10,000 (scaling)")
        report.append("   - These phases use specific years (✅ CORRECT)")
        report.append("")
        report.append("2. **Deep-Time Timeline (CORRECT for Phase 2-4):**")
        report.append("   - Phase Two: 10,000-100M years (maintenance)")
        report.append("   - Phase Three: 100M-500M years (preparation)")
        report.append("   - Phase Four: 500M-600M years (ACTUAL evacuation)")
        report.append("   - These phases should NOT use specific years like 2500, 3000, etc.")
        report.append("")
        report.append("❌ **ISSUE:** Chapters 20-21 use years like 2347, 2500, 3026 for")
        report.append("   evacuation/departure events that should happen in Phase Four")
        report.append("   (500M+ years from now), not in the 2000s-3000s.")
        report.append("")
        
        # Detailed Issues
        report.append("## DETAILED ISSUES")
        report.append("")
        
        # Group by file
        by_file = defaultdict(list)
        for issue in issues['near_term_in_deep_time']:
            by_file[issue['file']].append(issue)
        
        for filename, file_issues in sorted(by_file.items()):
            report.append(f"### {filename}")
            report.append("")
            
            phase = file_issues[0]['phase']
            report.append(f"**Phase:** {phase}")
            report.append(f"**Issues:** {len(file_issues)}")
            report.append("")
            
            # Sort by severity
            high_issues = [i for i in file_issues if i['severity'] == 'HIGH']
            med_issues = [i for i in file_issues if i['severity'] == 'MEDIUM']
            
            if high_issues:
                report.append("#### HIGH SEVERITY (Phase Four content with wrong years)")
                report.append("")
                for issue in high_issues[:5]:  # Show first 5
                    report.append(f"**Line {issue['line']}: Year {issue['year']}**")
                    report.append(f"Keywords: {', '.join(issue['phase_four_keywords'])}")
                    report.append(f"Context: ...{issue['context']}...")
                    report.append("")
                if len(high_issues) > 5:
                    report.append(f"... and {len(high_issues) - 5} more HIGH severity issues")
                    report.append("")
            
            if med_issues:
                report.append("#### MEDIUM SEVERITY (Near-term years in deep-time phase)")
                report.append("")
                for issue in med_issues[:3]:  # Show first 3
                    report.append(f"**Line {issue['line']}: Year {issue['year']}**")
                    report.append(f"Context: ...{issue['context']}...")
                    report.append("")
                if len(med_issues) > 3:
                    report.append(f"... and {len(med_issues) - 3} more MEDIUM severity issues")
                    report.append("")
            
            report.append("---")
            report.append("")
        
        # Resolution Strategy
        report.append("## RESOLUTION STRATEGY")
        report.append("")
        report.append("### Option 1: Complete Phase Reconceptualization (RECOMMENDED)")
        report.append("")
        report.append("Rewrite Chapters 20-21 to match their deep-time phase definitions:")
        report.append("")
        report.append("- **Chapter 20 (Phase Two: 10K-100M years):**")
        report.append("  - Remove all 2XXX-year references")
        report.append("  - Focus on: Legacy infrastructure maintenance over millions of years")
        report.append("  - No evacuation content (Earth still habitable)")
        report.append("")
        report.append("- **Chapter 21 (Phase Three: 100M-500M years):**")
        report.append("  - Remove all 2XXX-year references")
        report.append("  - Focus on: Solar brightening preparation, accelerated migration")
        report.append("  - Pre-evacuation activities (but not actual departure)")
        report.append("")
        report.append("- **Chapter 22 (Phase Four: 500M-600M years):**")
        report.append("  - Already correctly conceptualized ✅")
        report.append("  - Keep focus on actual evacuation")
        report.append("")
        report.append("### Option 2: Rename Phases to Match Content")
        report.append("")
        report.append("If near-term departure (year 2500-7500) is intended:")
        report.append("- Rename Phase Two to 'Early Departure Era (2500-7500)'")
        report.append("- Rename Phase Three to 'Transit Era (2500-7000)'")
        report.append("- Rename Phase Four to something else")
        report.append("- BUT: This conflicts with solar physics (oceans don't evaporate until 500M+ years)")
        report.append("")
        report.append("### Option 3: Hybrid Approach")
        report.append("")
        report.append("Keep Phase 0-1 content as-is, but clarify that:")
        report.append("- Years 2500-10,000: Optional test missions to nearby systems")
        report.append("- Years 500M-600M: Actual forced evacuation when Sun brightens")
        report.append("- Rewrite Chapters 20-21 to reflect this distinction")
        report.append("")
        
        return "\n".join(report)
    
    def save_report(self, issues):
        """Save reports to files"""
        # Generate text report
        report_text = self.generate_report(issues)
        
        with open('/app/output/reports/timeline_analysis.txt', 'w') as f:
            f.write(report_text)
        
        # Save JSON data
        with open('/app/output/reports/timeline_analysis.json', 'w') as f:
            json.dump(issues, f, indent=2)
        
        print(report_text)
        print("\n" + "="*80)
        print(f"✅ Reports saved:")
        print(f"   - reports/timeline_analysis.txt")
        print(f"   - reports/timeline_analysis.json")


def main():
    analyzer = TimelineAnalyzer()
    issues = analyzer.analyze_all_documents()
    analyzer.save_report(issues)


if __name__ == '__main__':
    main()
