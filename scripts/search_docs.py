#!/usr/bin/env python3
"""
Search Planetary Exodus documents using semantic vector search.

Usage:
    python scripts/search_docs.py "what is the energy requirement to move Earth?"
    python scripts/search_docs.py "Phase Four timeline" --top-k 5
"""

import argparse
import os
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = "planetary_exodus_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def search_documents(query: str, top_k: int = 3):
    """Search documents using semantic similarity."""
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    model = SentenceTransformer(EMBEDDING_MODEL)
    
    # Generate query embedding
    query_vector = model.encode(query).tolist()
    
    # Search using query method (qdrant-client >= 1.7.0)
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    ).points
    
    print(f"\n🔍 Query: '{query}'")
    print(f"📊 Top {top_k} results:\n")
    print("=" * 80)
    
    for i, result in enumerate(results, 1):
        payload = result.payload
        score = result.score
        
        print(f"\n{i}. [{payload['file']}] {payload['section']}")
        print(f"   Phase: {payload['phase']} | Chapter: {payload['chapter']}")
        print(f"   Lines: {payload['start_line']}-{payload['end_line']}")
        print(f"   Similarity: {score:.4f}")
        print(f"\n   Preview:")
        preview = payload['text'][:300].replace('\n', ' ')
        print(f"   {preview}...")
        print("-" * 80)
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Semantic search across Planetary Exodus documents')
    parser.add_argument('query', type=str, help='Search query')
    parser.add_argument('--top-k', type=int, default=3, help='Number of results to return')
    args = parser.parse_args()
    
    try:
        results = search_documents(args.query, args.top_k)
        print(f"\n✅ Found {len(results)} relevant sections")
    except Exception as e:
        print(f"\n❌ Search error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
