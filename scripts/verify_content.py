#!/usr/bin/env python3
"""
Aethelgard Protocol - Content Verification Tool
Cross-references generated content against source metadata
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set

class ContentVerifier:
    """Verifies generated documents against source metadata"""
    
    def __init__(self, metadata_dir: Path):
        self.metadata_dir = metadata_dir
        self.metadata = self.load_metadata()
        self.issues = []
    
    def load_metadata(self) -> Dict:
        """Load verification metadata"""
        metadata = {}
        
        # Load key files
        files = ['technical_constants', 'key_concepts', 'oracles', 'quotes']
        
        for filename in files:
            filepath = self.metadata_dir / f'{filename}.json'
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    metadata[filename] = json.load(f)
        
        return metadata
    
    def verify_document(self, doc_path: Path) -> Dict:
        """Verify a generated document"""
        print(f"\nVerifying: {doc_path.name}")
        
        if not doc_path.exists():
            return {'status': 'error', 'message': 'File not found'}
        
        content = doc_path.read_text(encoding='utf-8')
        
        results = {
            'document': str(doc_path),
            'checks': {
                'key_concepts': self.verify_key_concepts(content),
                'technical_accuracy': self.verify_technical_constants(content),
                'oracle_references': self.verify_oracle_definitions(content),
                'consistency': self.verify_internal_consistency(content),
            },
            'issues': [],
            'warnings': []
        }
        
        # Collect issues
        for check_name, check_result in results['checks'].items():
            if not check_result['passed']:
                results['issues'].extend(check_result.get('errors', []))
            if check_result.get('warnings'):
                results['warnings'].extend(check_result['warnings'])
        
        results['passed'] = len(results['issues']) == 0
        
        return results
    
    def verify_key_concepts(self, content: str) -> Dict:
        """Verify key concepts are used correctly"""
        concepts = self.metadata.get('key_concepts', {})
        
        found = {}
        errors = []
        
        # Check for presence of key concepts
        important_concepts = [
            'Aethelgard Protocol',
            'Poly-Centric Oracle',
            'The Rug',
            'Moon-Tug',
            'Synthesis Engine'
        ]
        
        for concept in important_concepts:
            if concept in concepts:
                count = content.lower().count(concept.lower())
                found[concept] = count
                
                if count == 0 and concept in ['Aethelgard Protocol', 'Poly-Centric Oracle']:
                    errors.append(f"Missing critical concept: {concept}")
        
        return {
            'passed': len(errors) == 0,
            'found_concepts': found,
            'errors': errors
        }
    
    def verify_technical_constants(self, content: str) -> Dict:
        """Verify technical constants are accurate"""
        constants = self.metadata.get('technical_constants', {})
        
        errors = []
        warnings = []
        
        # Check for common technical values
        checks = [
            (r'10\s*billion', 'population_target', 'Population target'),
            (r'5,?000\s*year', 'journey_duration', 'Journey duration'),
        ]
        
        for pattern, key, description in checks:
            if re.search(pattern, content, re.IGNORECASE):
                # Found the constant mentioned
                pass
            else:
                if key in constants:
                    warnings.append(f"{description} not mentioned in document")
        
        return {
            'passed': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def verify_oracle_definitions(self, content: str) -> Dict:
        """Verify Oracle definitions are consistent"""
        oracles = self.metadata.get('oracles', {})
        
        found = {}
        errors = []
        
        oracle_names = ['Sentinel', 'Humanist', 'Evolutionist', 'Navigator']
        
        for oracle in oracle_names:
            count = content.count(oracle)
            found[oracle] = count
        
        # If document mentions Oracles, all four should be present
        total_mentions = sum(found.values())
        if total_mentions > 0:
            for oracle, count in found.items():
                if count == 0:
                    errors.append(f"Missing Oracle: {oracle}")
        
        return {
            'passed': len(errors) == 0,
            'found_oracles': found,
            'errors': errors
        }
    
    def verify_internal_consistency(self, content: str) -> Dict:
        """Check for internal consistency issues"""
        errors = []
        warnings = []
        
        # Check for contradictory statements
        contradictions = [
            ('10 billion', '8 billion', 'Inconsistent population numbers'),
            ('5,000 year', '4,000 year', 'Inconsistent journey duration'),
        ]
        
        for pattern1, pattern2, description in contradictions:
            if re.search(pattern1, content) and re.search(pattern2, content):
                warnings.append(description)
        
        return {
            'passed': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def generate_report(self, results: List[Dict], output_file: Path):
        """Generate verification report"""
        
        total_docs = len(results)
        passed_docs = sum(1 for r in results if r.get('passed', False))
        total_issues = sum(len(r.get('issues', [])) for r in results)
        total_warnings = sum(len(r.get('warnings', [])) for r in results)
        
        report = f"""# Aethelgard Protocol - Content Verification Report

**Date:** 2026-01-05  
**Documents Verified:** {total_docs}  
**Passed:** {passed_docs}  
**Failed:** {total_docs - passed_docs}  
**Total Issues:** {total_issues}  
**Total Warnings:** {total_warnings}

---

## Summary

"""
        
        if passed_docs == total_docs:
            report += "✅ **All documents passed verification!**\n\n"
        else:
            report += f"⚠️ **{total_docs - passed_docs} document(s) failed verification.**\n\n"
        
        # Individual results
        report += "## Document Results\n\n"
        
        for result in results:
            doc_name = Path(result['document']).name
            status = "✅ PASS" if result.get('passed') else "❌ FAIL"
            
            report += f"### {doc_name} - {status}\n\n"
            
            # Issues
            if result.get('issues'):
                report += "**Issues:**\n"
                for issue in result['issues']:
                    report += f"- ❌ {issue}\n"
                report += "\n"
            
            # Warnings
            if result.get('warnings'):
                report += "**Warnings:**\n"
                for warning in result['warnings']:
                    report += f"- ⚠️ {warning}\n"
                report += "\n"
            
            # Check details
            report += "**Check Details:**\n"
            for check_name, check_result in result.get('checks', {}).items():
                check_status = "✅" if check_result.get('passed') else "❌"
                report += f"- {check_status} {check_name.replace('_', ' ').title()}\n"
            report += "\n"
        
        report += "---\n\n*Generated by Content Verifier v1.0*\n"
        
        # Save
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(report, encoding='utf-8')
        
        print(f"\nVerification report saved to: {output_file}")
        
        return output_file


def main():
    metadata_dir = Path('/Volumes/mnt/LAB/Planetary Exodus/metadata')
    docs_dir = Path('/Volumes/mnt/LAB/Planetary Exodus/docs')
    output_file = Path('/Volumes/mnt/LAB/Planetary Exodus/reports/verification_report.md')
    
    print("=" * 60)
    print("Aethelgard Protocol - Content Verification")
    print("=" * 60)
    
    verifier = ContentVerifier(metadata_dir)
    
    # Find all documents to verify
    docs_to_verify = list(docs_dir.glob('*.md'))
    
    if not docs_to_verify:
        print("\nNo documents found to verify.")
        return
    
    print(f"\nFound {len(docs_to_verify)} document(s) to verify.")
    
    results = []
    for doc in docs_to_verify:
        result = verifier.verify_document(doc)
        results.append(result)
    
    # Generate report
    print("\nGenerating verification report...")
    verifier.generate_report(results, output_file)
    
    print("\n" + "=" * 60)
    print("Verification Complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
