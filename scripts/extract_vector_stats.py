#!/usr/bin/env python3
"""
Extract statistics from vector database for reporting
"""

import re
import json
from collections import defaultdict, Counter
from typing import Dict, List
from qdrant_client import QdrantClient

client = QdrantClient(host="qdrant", port=6333)
COLLECTION_NAME = "planetary_exodus_docs"

class VectorDBStats:
    def __init__(self):
        self.sections = []
        self.stats = {}
        self.load_all_sections()
    
    def load_all_sections(self):
        """Load all sections from vector DB"""
        print("Loading sections from vector DB...")
        result = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=1000,
            with_payload=True,
            with_vectors=False
        )
        self.sections = result[0]
        print(f"Loaded {len(self.sections)} sections")
    
    def compute_document_stats(self):
        """Compute per-document statistics"""
        doc_stats = defaultdict(lambda: {
            'section_count': 0,
            'total_words': 0,
            'sections': []
        })
        
        for section in self.sections:
            payload = section.payload
            doc = payload.get('document', 'Unknown')
            text = payload.get('text', '')
            word_count = len(text.split())
            
            doc_stats[doc]['section_count'] += 1
            doc_stats[doc]['total_words'] += word_count
            doc_stats[doc]['sections'].append({
                'title': payload.get('section_title', ''),
                'number': payload.get('section_number', ''),
                'word_count': word_count
            })
        
        return dict(doc_stats)
    
    def extract_timeline_stats(self):
        """Extract timeline-related statistics"""
        timeline_stats = {
            'phase_mentions': Counter(),
            'year_ranges': [],
            'temporal_keywords': Counter()
        }
        
        temporal_keywords = ['years', 'decades', 'centuries', 'millennia', 
                            'million years', 'billion years']
        
        for section in self.sections:
            text = section.payload.get('text', '')
            
            # Count phase mentions
            phases = re.findall(r'Phase\s+(Zero|One|Two|Three|Four)', text)
            timeline_stats['phase_mentions'].update(phases)
            
            # Find year ranges
            year_ranges = re.findall(r'\b(\d{4})\s*[-–]\s*(\d{4})\b', text)
            timeline_stats['year_ranges'].extend(year_ranges)
            
            # Count temporal keywords
            text_lower = text.lower()
            for keyword in temporal_keywords:
                count = text_lower.count(keyword)
                if count > 0:
                    timeline_stats['temporal_keywords'][keyword] += count
        
        return timeline_stats
    
    def extract_technical_stats(self):
        """Extract technical/scientific statistics"""
        technical_stats = {
            'energy_mentions': 0,
            'mass_mentions': 0,
            'distance_mentions': 0,
            'population_mentions': 0,
            'numerical_constants': Counter()
        }
        
        patterns = {
            'energy': r'\b\d+(?:\.\d+)?\s*(?:joules?|J|watts?|W|terawatts?|TW)\b',
            'mass': r'\b\d+(?:\.\d+)?\s*(?:kg|kilograms?|tons?)\b',
            'distance': r'\b\d+(?:\.\d+)?\s*(?:light[\s-]?years?|ly|parsecs?|pc|AU)\b',
            'population': r'\b\d+(?:\.\d+)?\s*(?:billion|million)\s+(?:people|humans?)\b'
        }
        
        for section in self.sections:
            text = section.payload.get('text', '')
            
            for stat_type, pattern in patterns.items():
                matches = re.findall(pattern, text, re.IGNORECASE)
                technical_stats[f'{stat_type}_mentions'] += len(matches)
        
        return technical_stats
    
    def extract_keyword_frequency(self, top_n=50):
        """Extract most frequent meaningful keywords"""
        # Combine all text
        all_text = ' '.join([s.payload.get('text', '') for s in self.sections])
        
        # Remove common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'be',
                    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
                    'can', 'could', 'may', 'might', 'must', 'this', 'that', 'these', 'those',
                    'it', 'its', 'they', 'their', 'them', 'we', 'our', 'us', 'you', 'your'}
        
        # Extract words
        words = re.findall(r'\b[a-z]{4,}\b', all_text.lower())
        
        # Filter and count
        filtered_words = [w for w in words if w not in stopwords]
        keyword_freq = Counter(filtered_words).most_common(top_n)
        
        return keyword_freq
    
    def extract_cross_references(self):
        """Extract chapter cross-reference statistics"""
        cross_refs = defaultdict(list)
        
        for section in self.sections:
            payload = section.payload
            doc = payload.get('document', '')
            text = payload.get('text', '')
            
            # Find references to other chapters
            chapter_refs = re.findall(r'Chapter\s+(\d+)', text, re.IGNORECASE)
            
            for ref in chapter_refs:
                cross_refs[doc].append(f"Chapter {ref}")
        
        return dict(cross_refs)
    
    def extract_concept_stats(self):
        """Extract statistics about key concepts"""
        concepts = {
            'Oracle System': 0,
            'Dyson Swarm': 0,
            'Moon Tug': 0,
            'Hive Cities': 0,
            'Cryogenic': 0,
            'Proxima Centauri': 0,
            'Alpha Centauri': 0,
            'Solar System': 0,
            'Synthesis Engine': 0,
            'Aethelgard Protocol': 0
        }
        
        for section in self.sections:
            text = section.payload.get('text', '')
            
            for concept in concepts:
                concepts[concept] += text.count(concept)
        
        return concepts
    
    def generate_comprehensive_stats(self):
        """Generate all statistics"""
        print("\nComputing comprehensive statistics...")
        
        self.stats = {
            'overview': {
                'total_sections': len(self.sections),
                'total_documents': len(set(s.payload.get('document', '') for s in self.sections)),
                'total_words': sum(len(s.payload.get('text', '').split()) for s in self.sections),
                'avg_section_length': int(sum(len(s.payload.get('text', '').split()) for s in self.sections) / len(self.sections))
            },
            'document_breakdown': self.compute_document_stats(),
            'timeline_stats': self.extract_timeline_stats(),
            'technical_stats': self.extract_technical_stats(),
            'concept_frequency': self.extract_concept_stats(),
            'top_keywords': dict(self.extract_keyword_frequency(30)),
            'cross_references': self.extract_cross_references()
        }
        
        return self.stats
    
    def generate_markdown_appendix(self):
        """Generate Appendix C: Statistical Analysis"""
        stats = self.stats
        
        md = "# Appendix C: Statistical Analysis\n\n"
        md += "*Generated from vector database analysis*\n\n"
        md += "---\n\n"
        
        # Overview
        md += "## Document Overview\n\n"
        md += f"- **Total Sections:** {stats['overview']['total_sections']:,}\n"
        md += f"- **Total Documents:** {stats['overview']['total_documents']}\n"
        md += f"- **Total Words:** {stats['overview']['total_words']:,}\n"
        md += f"- **Average Section Length:** {stats['overview']['avg_section_length']:,} words\n"
        md += f"- **Estimated Reading Time:** {int(stats['overview']['total_words'] / 250)} minutes (~{int(stats['overview']['total_words'] / 250 / 60)} hours)\n\n"
        
        # Document breakdown
        md += "## Document Breakdown\n\n"
        md += "| Document | Sections | Words | Avg Section |\n"
        md += "|----------|----------|-------|-------------|\n"
        
        for doc, doc_stats in sorted(stats['document_breakdown'].items()):
            avg_section = int(doc_stats['total_words'] / doc_stats['section_count']) if doc_stats['section_count'] > 0 else 0
            doc_name = doc.replace('docs/', '').replace('.md', '')
            md += f"| {doc_name} | {doc_stats['section_count']} | {doc_stats['total_words']:,} | {avg_section:,} |\n"
        
        md += "\n"
        
        # Timeline statistics
        md += "## Timeline Statistics\n\n"
        md += "### Phase Mentions\n\n"
        
        for phase, count in sorted(stats['timeline_stats']['phase_mentions'].items()):
            md += f"- **Phase {phase}:** {count} mentions\n"
        
        md += "\n### Temporal Scale References\n\n"
        
        for keyword, count in stats['timeline_stats']['temporal_keywords'].most_common():
            md += f"- **{keyword.title()}:** {count} references\n"
        
        md += "\n"
        
        # Technical statistics
        md += "## Technical References\n\n"
        tech = stats['technical_stats']
        md += f"- **Energy/Power Values:** {tech['energy_mentions']} mentions\n"
        md += f"- **Mass Values:** {tech['mass_mentions']} mentions\n"
        md += f"- **Distance Values:** {tech['distance_mentions']} mentions\n"
        md += f"- **Population Figures:** {tech['population_mentions']} mentions\n\n"
        
        # Concept frequency
        md += "## Key Concept Frequency\n\n"
        
        for concept, count in sorted(stats['concept_frequency'].items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                md += f"- **{concept}:** {count} mentions\n"
        
        md += "\n"
        
        # Top keywords
        md += "## Most Frequent Technical Terms\n\n"
        md += "*Top 30 meaningful keywords (excluding common words)*\n\n"
        
        for i, (keyword, count) in enumerate(list(stats['top_keywords'].items())[:30], 1):
            md += f"{i}. **{keyword}** ({count} occurrences)\n"
            if i % 10 == 0:
                md += "\n"
        
        md += "\n"
        
        # Cross-references
        md += "## Cross-Reference Analysis\n\n"
        md += "*Documents that reference other chapters*\n\n"
        
        cross_refs_with_counts = [(doc, refs) for doc, refs in stats['cross_references'].items() if refs]
        cross_refs_with_counts.sort(key=lambda x: len(x[1]), reverse=True)
        
        for doc, refs in cross_refs_with_counts[:10]:
            doc_name = doc.replace('docs/', '').replace('.md', '')
            ref_counts = Counter(refs)
            md += f"### {doc_name}\n\n"
            for ref, count in ref_counts.most_common(5):
                md += f"- {ref} ({count} times)\n"
            md += "\n"
        
        md += "---\n\n"
        md += "*This appendix was automatically generated from the vector database on {}*\n".format(
            __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        return md
    
    def generate_welcome_stats(self):
        """Generate compact stats for welcome page"""
        stats = self.stats
        
        return {
            'total_sections': stats['overview']['total_sections'],
            'total_words': stats['overview']['total_words'],
            'total_documents': stats['overview']['total_documents'],
            'reading_time_hours': int(stats['overview']['total_words'] / 250 / 60),
            'top_concepts': [
                (concept, count) 
                for concept, count in sorted(stats['concept_frequency'].items(), 
                                            key=lambda x: x[1], reverse=True)[:5]
                if count > 0
            ],
            'phase_coverage': dict(stats['timeline_stats']['phase_mentions'])
        }
    
    def save_to_files(self):
        """Save stats to files"""
        # Save JSON
        json_file = '/app/output/metadata/vector_stats.json'
        with open(json_file, 'w') as f:
            json.dump(self.stats, f, indent=2, default=str)
        print(f"✅ Saved JSON stats to {json_file}")
        
        # Save Appendix C markdown
        md_file = '/app/output/docs/27_Appendix_C_Statistics.md'
        md_content = self.generate_markdown_appendix()
        with open(md_file, 'w') as f:
            f.write(md_content)
        print(f"✅ Saved Appendix C to {md_file}")
        
        # Save welcome stats
        welcome_file = '/app/output/metadata/welcome_stats.json'
        welcome_stats = self.generate_welcome_stats()
        with open(welcome_file, 'w') as f:
            json.dump(welcome_stats, f, indent=2)
        print(f"✅ Saved welcome stats to {welcome_file}")
        
        return md_content, welcome_stats


def main():
    print("🔍 Extracting statistics from vector database...\n")
    
    analyzer = VectorDBStats()
    analyzer.generate_comprehensive_stats()
    
    print("\n" + "="*60)
    print("GENERATING REPORTS")
    print("="*60 + "\n")
    
    md_content, welcome_stats = analyzer.save_to_files()
    
    print("\n" + "="*60)
    print("WELCOME PAGE STATS PREVIEW")
    print("="*60 + "\n")
    print(f"Total Sections: {welcome_stats['total_sections']}")
    print(f"Total Words: {welcome_stats['total_words']:,}")
    print(f"Reading Time: ~{welcome_stats['reading_time_hours']} hours")
    print(f"\nTop Concepts:")
    for concept, count in welcome_stats['top_concepts']:
        print(f"  - {concept}: {count} mentions")
    
    print("\n✅ Complete! Check:")
    print("   - docs/27_Appendix_C_Statistics.md (full analysis)")
    print("   - metadata/vector_stats.json (raw data)")
    print("   - metadata/welcome_stats.json (for welcome page)")


if __name__ == '__main__':
    main()
