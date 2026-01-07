#!/usr/bin/env python3
"""
Iterative Consistency Fix Loop

This script manages the full workflow:
1. Run consistency checks on current vector DB
2. Generate fix recommendations
3. Apply fixes (manual or assisted)
4. Re-ingest updated documents
5. Re-check for new/remaining issues
6. Repeat until threshold met
"""

import os
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

class IterativeConsistencyFixer:
    def __init__(self, max_iterations=10, min_issues_threshold=5):
        self.max_iterations = max_iterations
        self.min_issues_threshold = min_issues_threshold
        self.iteration = 0
        self.history = []
        self.reports_dir = Path('/app/output/reports')
        self.reports_dir.mkdir(exist_ok=True, parents=True)
    
    def run_consistency_check(self):
        """Run comprehensive consistency check"""
        print(f"\n{'='*60}")
        print(f"ITERATION {self.iteration + 1}: Running consistency check...")
        print(f"{'='*60}\n")
        
        # Run the comprehensive check
        result = subprocess.run(
            ['python3', '/app/scripts/comprehensive_consistency_check.py'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Consistency check failed: {result.stderr}")
            return None
        
        # Load the results
        report_file = self.reports_dir / 'consistency_issues.json'
        with open(report_file, 'r') as f:
            report = json.load(f)
        
        return report
    
    def reingest_documents(self):
        """Re-ingest all documents to update vector DB"""
        print(f"\n🔄 Re-ingesting documents to update vector DB...")
        
        result = subprocess.run(
            ['python3', '/app/scripts/ingest_to_vector_db.py'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Re-ingestion failed: {result.stderr}")
            return False
        
        print("✅ Vector DB updated with latest document content")
        return True
    
    def generate_iteration_summary(self, report):
        """Generate summary for this iteration"""
        summary = {
            'iteration': self.iteration + 1,
            'timestamp': datetime.now().isoformat(),
            'total_issues': report['total_issues'],
            'by_severity': report['by_severity'],
            'by_type': report['by_type'],
        }
        
        self.history.append(summary)
        
        # Save iteration history
        history_file = self.reports_dir / 'iteration_history.json'
        with open(history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
        
        print(f"\n📊 Iteration {self.iteration + 1} Summary:")
        print(f"   Total Issues: {report['total_issues']}")
        print(f"   HIGH:   {report['by_severity']['HIGH']}")
        print(f"   MEDIUM: {report['by_severity']['MEDIUM']}")
        print(f"   LOW:    {report['by_severity']['LOW']}")
        
        if self.iteration > 0:
            prev = self.history[-2]
            change = report['total_issues'] - prev['total_issues']
            print(f"   Change: {change:+d} issues")
    
    def should_continue(self, report):
        """Determine if another iteration is needed"""
        if self.iteration >= self.max_iterations:
            print(f"\n⚠️  Reached max iterations ({self.max_iterations})")
            return False
        
        if report['total_issues'] <= self.min_issues_threshold:
            print(f"\n✅ Issues below threshold ({self.min_issues_threshold})")
            return False
        
        if self.iteration > 0:
            prev = self.history[-2]
            if report['total_issues'] >= prev['total_issues']:
                print(f"\n⚠️  No progress made in this iteration")
                print(f"   Manual intervention may be required")
                return False
        
        return True
    
    def prompt_for_fixes(self, report):
        """Show issues and prompt user to apply fixes"""
        print(f"\n{'='*60}")
        print("APPLY FIXES")
        print(f"{'='*60}\n")
        
        # Show top issues by severity
        high_issues = [i for i in report['issues'] if i['severity'] == 'HIGH']
        medium_issues = [i for i in report['issues'] if i['severity'] == 'MEDIUM']
        
        print(f"HIGH Priority Issues ({len(high_issues)}):")
        for i, issue in enumerate(high_issues[:5], 1):
            print(f"  {i}. {issue['type']}: {issue['description'][:80]}...")
        
        if len(high_issues) > 5:
            print(f"  ... and {len(high_issues) - 5} more")
        
        print(f"\nMEDIUM Priority Issues ({len(medium_issues)}):")
        for i, issue in enumerate(medium_issues[:3], 1):
            print(f"  {i}. {issue['type']}: {issue['description'][:80]}...")
        
        if len(medium_issues) > 3:
            print(f"  ... and {len(medium_issues) - 3} more")
        
        print("\n📋 Full details in:")
        print(f"   - reports/consistency_issues.md")
        print(f"   - reports/consistency_issues.json")
        
        print("\n" + "="*60)
        print("Now apply fixes to the documents in docs/ folder")
        print("Press ENTER when ready to re-check (or Ctrl+C to stop)")
        print("="*60 + "\n")
        
        try:
            input()
            return True
        except KeyboardInterrupt:
            print("\n\n⚠️  Process interrupted by user")
            return False
    
    def run_loop(self, auto_reingest=True):
        """Run the iterative fix loop"""
        print("🚀 Starting Iterative Consistency Fix Loop")
        print(f"   Max iterations: {self.max_iterations}")
        print(f"   Min issues threshold: {self.min_issues_threshold}")
        print(f"   Auto re-ingest: {auto_reingest}")
        
        while True:
            # Run consistency check
            report = self.run_consistency_check()
            if not report:
                break
            
            # Generate summary
            self.generate_iteration_summary(report)
            
            # Check if we should continue
            if not self.should_continue(report):
                break
            
            # Prompt for fixes
            if not self.prompt_for_fixes(report):
                break
            
            # Re-ingest documents to update vector DB
            if auto_reingest:
                if not self.reingest_documents():
                    break
            
            self.iteration += 1
        
        # Final summary
        self.print_final_summary()
    
    def print_final_summary(self):
        """Print final summary of all iterations"""
        print(f"\n{'='*60}")
        print("FINAL SUMMARY")
        print(f"{'='*60}\n")
        
        print(f"Total Iterations: {len(self.history)}")
        
        if len(self.history) > 0:
            first = self.history[0]
            last = self.history[-1]
            
            print(f"\nInitial Issues:  {first['total_issues']}")
            print(f"Final Issues:    {last['total_issues']}")
            print(f"Total Fixed:     {first['total_issues'] - last['total_issues']}")
            print(f"Improvement:     {((first['total_issues'] - last['total_issues']) / first['total_issues'] * 100):.1f}%")
            
            print("\nProgress by iteration:")
            for i, iteration in enumerate(self.history, 1):
                print(f"  {i}. {iteration['total_issues']} issues (HIGH: {iteration['by_severity']['HIGH']}, MEDIUM: {iteration['by_severity']['MEDIUM']}, LOW: {iteration['by_severity']['LOW']})")
        
        print(f"\n📂 All reports saved in reports/")
        print(f"   - iteration_history.json (progress tracking)")
        print(f"   - consistency_issues.json (latest issues)")
        print(f"   - consistency_issues.md (human-readable)")
        print(f"\n{'='*60}\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Iterative consistency fix loop')
    parser.add_argument('--max-iterations', type=int, default=10, help='Maximum iterations')
    parser.add_argument('--threshold', type=int, default=5, help='Minimum issues threshold to stop')
    parser.add_argument('--no-auto-reingest', action='store_true', help='Disable automatic re-ingestion')
    
    args = parser.parse_args()
    
    fixer = IterativeConsistencyFixer(
        max_iterations=args.max_iterations,
        min_issues_threshold=args.threshold
    )
    
    fixer.run_loop(auto_reingest=not args.no_auto_reingest)


if __name__ == '__main__':
    main()
