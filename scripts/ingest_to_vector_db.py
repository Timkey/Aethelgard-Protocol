#!/usr/bin/env python3
"""
Ingest Planetary Exodus documents into Qdrant vector database.

This script:
1. Reads all markdown files from docs/
2. Chunks them by sections (preserving headers)
3. Generates embeddings using sentence-transformers
4. Stores in Qdrant with metadata for consistency checking

Usage:
    python scripts/ingest_to_vector_db.py [--reset]
"""

import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = "planetary_exodus_docs"
DOCS_DIR = Path(__file__).parent.parent / "docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast, good quality, 384 dimensions

class DocumentChunker:
    """Chunks markdown documents by sections while preserving context."""
    
    @staticmethod
    def extract_phase_from_header(text: str) -> str:
        """Extract phase information from chapter headers."""
        phase_match = re.search(r'Phase (Zero|One|Two|Three|Four|Five|\d+)', text, re.IGNORECASE)
        if phase_match:
            return phase_match.group(1)
        return "Unknown"
    
    @staticmethod
    def extract_chapter_number(filename: str) -> int:
        """Extract chapter number from filename."""
        match = re.search(r'(\d+)_Chapter_', filename)
        return int(match.group(1)) if match else 0
    
    def chunk_by_sections(self, filepath: Path) -> List[Dict]:
        """Chunk document by markdown sections (## headers)."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chunks = []
        chapter_num = self.extract_chapter_number(filepath.name)
        phase = self.extract_phase_from_header(content[:1000])
        
        # Split by ## headers (sections)
        sections = re.split(r'\n## ', content)
        
        for i, section in enumerate(sections):
            if not section.strip():
                continue
            
            # Add back the ## if not first section
            if i > 0:
                section = "## " + section
            
            # Extract section title
            title_match = re.search(r'^#+ (.+)$', section, re.MULTILINE)
            section_title = title_match.group(1) if title_match else "Introduction"
            
            # Count line number (approximate)
            lines_before = content[:content.find(section)].count('\n') if i > 0 else 0
            lines_in_section = section.count('\n')
            
            chunks.append({
                'text': section,
                'metadata': {
                    'file': filepath.name,
                    'chapter': chapter_num,
                    'section': section_title,
                    'phase': phase,
                    'start_line': lines_before,
                    'end_line': lines_before + lines_in_section,
                    'char_count': len(section)
                }
            })
        
        return chunks

class VectorDBIngester:
    """Handles ingestion of documents into Qdrant."""
    
    def __init__(self, reset: bool = False):
        self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.chunker = DocumentChunker()
        self.reset = reset
        
        print(f"🔌 Connected to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")
        print(f"🤖 Loading embedding model: {EMBEDDING_MODEL}")
    
    def setup_collection(self):
        """Create or reset the vector collection."""
        collections = self.client.get_collections().collections
        collection_exists = any(c.name == COLLECTION_NAME for c in collections)
        
        if collection_exists and self.reset:
            print(f"🗑️  Deleting existing collection: {COLLECTION_NAME}")
            self.client.delete_collection(COLLECTION_NAME)
            collection_exists = False
        
        if not collection_exists:
            print(f"📦 Creating collection: {COLLECTION_NAME}")
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=384,  # all-MiniLM-L6-v2 embedding size
                    distance=Distance.COSINE
                )
            )
        else:
            print(f"✅ Collection already exists: {COLLECTION_NAME}")
    
    def ingest_documents(self):
        """Ingest all markdown documents from docs/."""
        doc_files = sorted(DOCS_DIR.glob("*.md"))
        print(f"\n📚 Found {len(doc_files)} documents to process")
        
        all_points = []
        point_id = 0
        
        for doc_file in doc_files:
            print(f"\n📄 Processing: {doc_file.name}")
            chunks = self.chunker.chunk_by_sections(doc_file)
            print(f"   └─ {len(chunks)} sections found")
            
            # Generate embeddings in batches
            texts = [chunk['text'] for chunk in chunks]
            embeddings = self.model.encode(texts, show_progress_bar=False)
            
            # Create points
            for chunk, embedding in zip(chunks, embeddings):
                point = PointStruct(
                    id=point_id,
                    vector=embedding.tolist(),
                    payload={
                        'text': chunk['text'][:1000] + '...' if len(chunk['text']) > 1000 else chunk['text'],
                        'text_full': chunk['text'],
                        **chunk['metadata']
                    }
                )
                all_points.append(point)
                point_id += 1
        
        # Upload in batches
        batch_size = 100
        total_points = len(all_points)
        print(f"\n⬆️  Uploading {total_points} vectors in batches of {batch_size}")
        
        for i in range(0, total_points, batch_size):
            batch = all_points[i:i+batch_size]
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=batch
            )
            print(f"   ✓ Uploaded batch {i//batch_size + 1}/{(total_points-1)//batch_size + 1}")
        
        print(f"\n✅ Successfully ingested {total_points} document sections!")
    
    def verify_ingestion(self):
        """Verify the collection and show stats."""
        collection_info = self.client.get_collection(COLLECTION_NAME)
        print(f"\n📊 Collection Stats:")
        print(f"   Total vectors: {collection_info.points_count}")
        print(f"   Vector size: {collection_info.config.params.vectors.size}")
        print(f"   Distance metric: {collection_info.config.params.vectors.distance}")

def main():
    parser = argparse.ArgumentParser(description='Ingest documents into Qdrant vector database')
    parser.add_argument('--reset', action='store_true', help='Reset collection before ingestion')
    args = parser.parse_args()
    
    print("=" * 60)
    print("📖 Planetary Exodus Document Ingestion")
    print("=" * 60)
    
    try:
        ingester = VectorDBIngester(reset=args.reset)
        ingester.setup_collection()
        ingester.ingest_documents()
        ingester.verify_ingestion()
        
        print("\n" + "=" * 60)
        print("✨ Ingestion Complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("  • Run: python scripts/search_docs.py 'your query'")
        print("  • Run: python scripts/check_consistency_vector.py")
        
    except Exception as e:
        print(f"\n❌ Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
