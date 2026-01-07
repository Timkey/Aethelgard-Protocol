#!/usr/bin/env python3
"""
Timeline Consistency Audit Script
Scans all markdown files for timeline inconsistencies with the new realistic framework.
"""

import re
import os
from pathlib import Path
from collections import defaultdict

# Define patterns that indicate old timeline framing
INCONSISTENT_PATTERNS = {
    'old_mission_duration': [
        r'5,000-year (mission|journey|plan)',
        r'5000-year (mission|journey|plan)',
        r'over 5,000 years',
    ],
    'urgent_framing': [
        r'dying Sun',
        r'immediate (crisis|threat)',
        r'emergency evacuation',
        r'must flee',
        r'last chance',
        r'urgent.*depart',
    ],
    'old_phase_timelines': [
        r'Phase Zero.*2026.*2050(?!\+)',  # Should be 2026-2050+ or 2026-2150+
        r'Phase One.*2050.*2150(?!\+)',
        r'Phase Two.*2150.*2500',
        r'Phase Three.*2500.*3000',
        r'Phase Four.*3000.*6000',
        r'Year 2500[^0]',  # Year 2500 but not 25000 or similar
        r'Year 3000[^0]',
        r'Year 6000[^0]',
        r'Year 6200',
    ],
    'mission_completion': [
        r'mission complete(?!.*template)',
        r'final phase(?!.*cycle)',
        r'end of.*protocol(?!.*first)',
    ],
}

# Patterns that are CORRECT and should be preserved
CORRECT_PATTERNS = [
    r'~1 billion years',
    r'~5 billion years',
    r'500 million years',
    r'billion year',
    r'Phase Zero.*2026.*(?:2050\+|2150\+)',
    r'test mission',
    r'capability.{0,30}window',
    r'legacy infrastructure',
    r'multi-billion-year',
]

def scan_file(filepath):
    """Scan a single file for timeline inconsistencies."""
    issues = defaultdict(list)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            # Skip if line contains correct patterns
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in CORRECT_PATTERNS):
                continue
                
            # Check for inconsistent patterns
            for category, patterns in INCONSISTENT_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues[category].append({
                            'line': line_num,
                            'text': line.strip()[:100],  # First 100 chars
                            'pattern': pattern
                        })
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        
    return issues

def main():
    """Main audit function."""
    docs_dir = Path(__file__).parent.parent / 'docs'
    
    print("=" * 80)
    print("TIMELINE CONSISTENCY AUDIT")
    print("=" * 80)
    print()
    
    all_issues = defaultdict(lambda: defaultdict(list))
    total_issues = 0
    
    # Scan all markdown files
    for md_file in sorted(docs_dir.glob('*.md')):
        issues = scan_file(md_file)
        if issues:
            all_issues[md_file.name] = issues
            for category, items in issues.items():
                total_issues += len(items)
    
    # Print results by priority
    print(f"Found {total_issues} potential inconsistencies across {len(all_issues)} files\n")
    
    # Priority 1: Phase chapters (need most updating)
    print("\n" + "=" * 80)
    print("PRIORITY 1: PHASE CHAPTERS")
    print("=" * 80)
    phase_chapters = [f for f in all_issues.keys() if 'Chapter_18' in f or 'Chapter_19' in f or 
                      'Chapter_20' in f or 'Chapter_21' in f or 'Chapter_22' in f]
    for filename in phase_chapters:
        print(f"\n📄 {filename}")
        print("-" * 80)
        for category, items in all_issues[filename].items():
            print(f"\n  {category.upper().replace('_', ' ')} ({len(items)} issues):")
            for item in items[:3]:  # Show first 3
                print(f"    Line {item['line']}: {item['text']}")
            if len(items) > 3:
                print(f"    ... and {len(items) - 3} more")
    
    # Priority 2: Foundation chapters
    print("\n\n" + "=" * 80)
    print("PRIORITY 2: FOUNDATION CHAPTERS")
    print("=" * 80)
    foundation = [f for f in all_issues.keys() if any(x in f for x in 
                  ['TOC', 'Executive', 'Chapter_02', 'Chapter_03', 'Chapter_04', 'Chapter_05'])]
    for filename in foundation:
        if filename not in phase_chapters:
            print(f"\n📄 {filename}")
            print("-" * 80)
            for category, items in all_issues[filename].items():
                print(f"  {category.replace('_', ' ')}: {len(items)} issues")
    
    # Priority 3: Technical chapters
    print("\n\n" + "=" * 80)
    print("PRIORITY 3: TECHNICAL CHAPTERS")
    print("=" * 80)
    technical = [f for f in all_issues.keys() if any(x in f for x in 
                ['Chapter_08', 'Chapter_09', 'Chapter_10', 'Chapter_11', 'Chapter_12', 'Appendix'])]
    for filename in technical:
        if filename not in phase_chapters and filename not in foundation:
            print(f"\n📄 {filename}")
            print("-" * 80)
            for category, items in all_issues[filename].items():
                print(f"  {category.replace('_', ' ')}: {len(items)} issues")
    
    # Priority 4: Other chapters
    print("\n\n" + "=" * 80)
    print("PRIORITY 4: OTHER CHAPTERS")
    print("=" * 80)
    other = [f for f in all_issues.keys() 
             if f not in phase_chapters and f not in foundation and f not in technical]
    for filename in other:
        print(f"\n📄 {filename}")
        for category, items in all_issues[filename].items():
            print(f"  {category.replace('_', ' ')}: {len(items)} issues")
    
    # Summary recommendations
    print("\n\n" + "=" * 80)
    print("RECOMMENDED UPDATE ORDER")
    print("=" * 80)
    print("""
1. Phase Chapters (19_Chapter_18.md through 23_Chapter_22.md)
   - Update phase descriptions to match realistic timeline
   - Add timeline context callouts
   - Clarify testing/capability building focus

2. Master TOC (00_Master_TOC.md)
   - Update mission description
   - Fix phase timeline references

3. Technical Chapters (06-13)
   - Update references to mission duration
   - Contextualize with "test phase" language

4. Conclusion and Appendices
   - Update summary statements
   - Ensure mathematical models align with multi-billion-year framework
    """)
    
    # Generate fix script template
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("""
Run the following to begin systematic fixes:

    # Start with highest priority files
    code docs/19_Chapter_18.md
    code docs/20_Chapter_19.md
    code docs/21_Chapter_20.md
    
Or use multi_replace_string_in_file for batch corrections.
    """)

if __name__ == '__main__':
    main()
