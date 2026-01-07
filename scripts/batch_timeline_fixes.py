#!/usr/bin/env python3
"""
Batch Timeline Corrections
Applies systematic find-replace operations across all markdown files.
"""

import re
from pathlib import Path

# Define replacement patterns
REPLACEMENTS = [
    # Pattern 1: "5,000-year mission/journey/plan" → "multi-billion-year framework" or context-appropriate
    (r'5,000-year mission', 'multi-billion-year survival framework'),
    (r'5000-year mission', 'multi-billion-year survival framework'),
    (r'5,000-year journey', 'deep-time journey (millions of years)'),
    (r'5,000-year plan', 'multi-billion-year strategy'),
    (r'over 5,000 years', 'across deep time (millions of years)'),
    (r'across 5,000 years', 'across deep time'),
    
    # Pattern 2: Contextual "5,000" replacements (keep if referring to test phase)
    (r'5,000 years\.', 'deep time.'),
    
    # Pattern 3: Phase Timeline Headers (be cautious - only update where appropriate)
    (r'Phase Zero \(2026-2050\)(?!\+)', 'Phase Zero (2026-2150+)'),
    (r'Phase One \(2050-2150\)(?!\+)', 'Phase One (2150-10,000+)'),
    
    # Pattern 4: Urgent framing
    (r'dying Sun(?!\'s eventual)', "Sun's eventual brightening"),
    (r'immediate crisis', 'long-term challenge'),
    (r'emergency evacuation', 'planned capability development'),
    (r'must flee', 'will eventually need to relocate'),
    
    # Pattern 5: Year references (be very selective)
    # Keep these as manual review items
]

def apply_replacements(file_path, dry_run=True):
    """Apply replacements to a single file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    for pattern, replacement in REPLACEMENTS:
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if new_content != content:
            # Count changes
            count = len(re.findall(pattern, content, re.IGNORECASE))
            changes.append((pattern, count))
            content = new_content
    
    if content != original_content:
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        return changes
    return None

def main():
    docs_dir = Path(__file__).parent.parent / 'docs'
    
    print("Timeline Batch Corrections - DRY RUN")
    print("=" * 80)
    
    total_files = 0
    total_changes = 0
    
    for md_file in sorted(docs_dir.glob('*.md')):
        changes = apply_replacements(md_file, dry_run=True)
        if changes:
            total_files += 1
            print(f"\n{md_file.name}:")
            for pattern, count in changes:
                print(f"  - {pattern}: {count} replacements")
                total_changes += count
    
    print(f"\n{'-' * 80}")
    print(f"Would modify {total_files} files with {total_changes} total changes")
    print(f"\nTo apply these changes, run with dry_run=False")

if __name__ == '__main__':
    main()
