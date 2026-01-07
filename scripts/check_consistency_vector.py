#!/usr/bin/env python3
"""
Check consistency across Planetary Exodus documents using vector search.

This script runs predefined queries to find potential inconsistencies:
- Technical constants (energy, mass, velocity)
- Phase timelines
- Technology availability
- Population numbers
"""

import json
import os
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = "planetary_exodus_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Consistency check queries
CONSISTENCY_CHECKS = {
    "Energy Values": [
        "total energy required to move Earth",
        "Dyson Swarm power output in watts",
        "Sun's energy output per second"
    ],
    "Velocities": [
        "Earth escape velocity",
        "Moon escape velocity",
        "solar system escape velocity"
    ],
    "Phase Timelines": [
        "Phase Zero timeline years",
        "Phase One timeline years",
        "Phase Two timeline years",
        "Phase Three timeline years",
        "Phase Four timeline years",
        "Phase Five timeline years"
    ],
    "Population": [
        "10 billion humans mandate",
        "Hive City capacity",
        "population distribution underground"
    ],
    "Moon Mass": [
        "Moon total mass",
        "Moon mass consumption rate",
        "percentage of Moon used for propulsion"
    ]
}

def run_consistency_check():
    """Run all consistency checks and report findings."""
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    model = SentenceTransformer(EMBEDDING_MODEL)
    
    print("=" * 80)
    print("🔬 PLANETARY EXODUS CONSISTENCY CHECKER")
    print("=" * 80)
    
    all_findings = {}
    
    for category, queries in CONSISTENCY_CHECKS.items():
        print(f"\n📋 Checking: {category}")
        print("-" * 80)
        
        category_findings = []
        
        for query in queries:
            query_vector = model.encode(query).tolist()
            results = client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_vector,
                limit=5
            ).points
            
            # Extract unique values mentioned
            findings = []
            for result in results:
                payload = result.payload
                findings.append({
                    'file': payload['file'],
                    'section': payload['section'],
                    'phase': payload['phase'],
                    'chapter': payload['chapter'],
                    'score': result.score,
                    'preview': payload['text'][:200]
                })
            
            category_findings.append({
                'query': query,
                'results': findings
            })
            
            # Display top result
            if findings:
                top = findings[0]
                print(f"\n  Q: {query}")
                print(f"     → [{top['file']}] {top['section']}")
                print(f"       Phase {top['phase']}, Score: {top['score']:.3f}")
        
        all_findings[category] = category_findings
    
    # Save detailed report
    report_path = "output/consistency_report.json"
    with open(report_path, 'w') as f:
        json.dump(all_findings, f, indent=2)
    
    print("\n" + "=" * 80)
    print(f"✅ Consistency check complete!")
    print(f"📄 Detailed report saved to: {report_path}")
    print("=" * 80)
    
    return all_findings

def find_contradictions(threshold: float = 0.7):
    """Find sections that are semantically similar but may contain contradictions."""
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    print("\n🔍 Searching for potential contradictions...")
    print("   (Sections with similar topics but different phases/chapters)")
    
    # Get a sample of points to check
    scroll_result = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=50,
        with_payload=True,
        with_vectors=True
    )
    
    points = scroll_result[0]
    contradictions = []
    
    for point in points:
        # Search for similar sections
        similar = client.query_points(
            collection_name=COLLECTION_NAME,
            query=point.vector,
            limit=3
        ).points
        
        # Check if similar sections are from different phases
        for result in similar[1:]:  # Skip first (itself)
            if (result.score > threshold and 
                result.payload['phase'] != point.payload['phase']):
                contradictions.append({
                    'section1': f"{point.payload['file']} - {point.payload['section']}",
                    'phase1': point.payload['phase'],
                    'section2': f"{result.payload['file']} - {result.payload['section']}",
                    'phase2': result.payload['phase'],
                    'similarity': result.score
                })
    
    if contradictions:
        print(f"\n⚠️  Found {len(contradictions)} potential cross-phase inconsistencies:")
        for c in contradictions[:10]:  # Show top 10
            print(f"\n  • {c['section1']} (Phase {c['phase1']})")
            print(f"    vs")
            print(f"    {c['section2']} (Phase {c['phase2']})")
            print(f"    Similarity: {c['similarity']:.3f}")
    else:
        print("\n✅ No obvious contradictions detected")

def main():
    try:
        run_consistency_check()
        find_contradictions()
        
        print("\n💡 Next steps:")
        print("  • Review consistency_report.json")
        print("  • Search specific values: python scripts/search_docs.py 'query'")
        print("  • Update inconsistent sections in markdown files")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
