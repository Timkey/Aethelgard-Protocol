# Vector Database Setup for Planetary Exodus

## Overview

This system provides semantic search and consistency checking across the Planetary Exodus documentation using a fully containerized vector database (Qdrant).

**✅ Zero host dependencies** - Everything runs in Docker containers  
**✅ Portable** - Works on any machine with Docker installed  
**✅ Isolated** - No Python environment conflicts

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Host Machine                                       │
│  ┌───────────────────────────────────────────────┐ │
│  │  exec/ (Shell Scripts)                        │ │
│  │    ├─ start     ├─ ingest    ├─ search       │ │
│  │    ├─ stop      ├─ rebuild   └─ check_...    │ │
│  └──────────────┬──────────────────────────────┬─┘ │
│                 │                              │   │
│    ┌────────────▼──────────┐      ┌──────────▼───┐ │
│    │  worker container     │──────│  qdrant      │ │
│    │  (Python + Scripts)   │      │  (Vector DB) │ │
│    └───────────────────────┘      └──────────────┘ │
└─────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Start Services

```bash
./exec/start
```

This starts:
- **Qdrant** - Vector database on port 6333
- **Worker** - Python environment with scripts

### 2. Ingest Documents

```bash
# First time setup
./exec/ingest --reset

# Update after changes
./exec/ingest
```

### 3. Search

```bash
# Semantic search
./exec/search "what is the energy requirement to move Earth?"

# More results
./exec/search "Phase Four timeline" --top-k 5
```

### 4. Check Consistency

```bash
./exec/check_consistency
```

## Command Reference

### Service Management

**Start services:**
```bash
./exec/start
```

**Stop services:**
```bash
./exec/stop
```

**Rebuild containers (after code changes):**
```bash
./exec/rebuild
```

**View logs:**
```bash
./exec/logs          # All services
./exec/logs worker   # Worker only
./exec/logs qdrant   # Qdrant only
```

### Document Operations

**Ingest documents:**
```bash
./exec/ingest [--reset]
```
- `--reset`: Delete and recreate collection (fresh start)
- Without flags: Update existing collection

**Search documents:**
```bash
./exec/search "query" [--top-k N]
```
- Returns top N semantically similar sections
- Default: top 3 results

**Check consistency:**
```bash
./exec/check_consistency
```
- Runs predefined consistency checks
- Outputs: `consistency_report.json`
- Checks energy values, velocities, timelines, population, etc.

## Example Workflows

### Initial Setup (New Machine)

```bash
# 1. Clone repo
git clone <repo>
cd "Planetary Exodus"

# 2. Start services
./exec/start

# 3. Ingest documents
./exec/ingest --reset

# 4. Test search
./exec/search "Moon-Tug propulsion"
```

### After Editing Documents

```bash
# 1. Update vector DB
./exec/ingest

# 2. Verify changes
./exec/search "your edited content"

# 3. Check for inconsistencies
./exec/check_consistency
```

### Systematic Consistency Review

```bash
# 1. Run full consistency check
./exec/check_consistency

# 2. Review report
cat consistency_report.json | jq '.["Energy Values"]'

# 3. Search specific values
./exec/search "4.3 × 10^32 joules"

# 4. Fix inconsistencies in markdown files

# 5. Re-ingest and verify
./exec/ingest
./exec/check_consistency
```

## What Gets Checked

The consistency checker runs semantic searches for:

**Energy Values:**
- Total energy to move Earth
- Dyson Swarm power output
- Sun's energy output

**Velocities:**
- Earth escape velocity
- Moon escape velocity
- Solar system escape velocity

**Phase Timelines:**
- Year ranges for each phase (Zero through Five)

**Population:**
- 10 billion mandate
- Hive City capacity
- Distribution statistics

**Moon Mass:**
- Total mass
- Consumption rate
- Percentage used for propulsion

**Cross-Phase Contradictions:**
- Similar sections with conflicting information
- Phase boundary inconsistencies

## Technical Details

### Container Architecture

**Qdrant Container:**
- Image: `qdrant/qdrant:latest`
- Ports: 6333 (REST), 6334 (gRPC)
- Storage: Named Docker volume (persists between restarts)

**Worker Container:**
- Base: Python 3.11-slim
- Dependencies: sentence-transformers, qdrant-client
- Mounts: Read-only access to `docs/` and `scripts/`

### Embedding Model

- Model: `all-MiniLM-L6-v2`
- Dimensions: 384
- Speed: Fast (~500 sentences/sec on CPU)
- Quality: Good for semantic document search

### Data Persistence

Vector data stored in Docker volume `planetaryexodus_qdrant_data`. Persists between container restarts.

**To reset completely:**
```bash
./exec/stop
docker volume rm planetaryexodus_qdrant_data
./exec/start
./exec/ingest --reset
```

## Troubleshooting

### Containers won't start

```bash
# Check Docker is running
docker ps

# View logs
./exec/logs

# Rebuild from scratch
./exec/rebuild
```

### "Collection not found" error

```bash
# Re-ingest documents
./exec/ingest --reset
```

### Slow first search

First search loads the embedding model (~90MB). Subsequent searches are fast (model cached in memory).

### Port already in use

Check if another service is using port 6333:
```bash
lsof -i :6333
```

Stop conflicting service or change port in `docker-compose.yml`

## Benefits Over Manual Search

✅ **Semantic Understanding** - Finds conceptually related content, not just keywords  
✅ **Cross-Reference Detection** - Automatically finds similar sections  
✅ **Inconsistency Detection** - Identifies contradictions by similarity  
✅ **Fast** - Sub-second searches across 27 documents  
✅ **Portable** - Works identically on any machine with Docker  
✅ **No Dependencies** - No Python/pip conflicts on host  

## File Structure

```
Planetary Exodus/
├── exec/               # Executable commands (run these)
│   ├── start
│   ├── stop
│   ├── rebuild
│   ├── ingest
│   ├── search
│   ├── check_consistency
│   └── logs
├── scripts/            # Python code (don't run directly)
│   ├── ingest_to_vector_db.py
│   ├── search_docs.py
│   └── check_consistency_vector.py
├── docs/              # Markdown documents (ingested)
├── docker-compose.yml  # Service definitions
├── Dockerfile         # Worker container build
└── requirements.txt   # Python dependencies
```

## Advanced: Direct Container Access

If you need to run custom Python code:

```bash
# Enter worker container
docker-compose exec worker bash

# Now you're inside the container
python3
>>> from qdrant_client import QdrantClient
>>> client = QdrantClient(host="qdrant", port=6333)
>>> # ... your code ...
```

## Maintenance

**After significant document changes:**
```bash
./exec/ingest
./exec/check_consistency
```

**View database stats:**
```bash
curl http://localhost:6333/collections/planetary_exodus_docs
```

**Backup vector data:**
```bash
docker run --rm -v planetaryexodus_qdrant_data:/data \
  -v $(pwd):/backup alpine tar czf /backup/qdrant_backup.tar.gz -C /data .
```

**Restore vector data:**
```bash
docker volume create planetaryexodus_qdrant_data
docker run --rm -v planetaryexodus_qdrant_data:/data \
  -v $(pwd):/backup alpine tar xzf /backup/qdrant_backup.tar.gz -C /data
```

---

**For questions or issues:**
- Qdrant docs: https://qdrant.tech/documentation/
- sentence-transformers: https://www.sbert.net/


**What it does:**
- Reads all `docs/*.md` files
- Chunks by sections (## headers)
- Extracts metadata (file, chapter, phase, line range)
- Generates embeddings
- Stores in Qdrant

### 4. Search Documents

```bash
# Semantic search
python scripts/search_docs.py "what is the energy requirement to move Earth?"

# More results
python scripts/search_docs.py "Phase Four timeline" --top-k 5
```

### 5. Check Consistency

```bash
python scripts/check_consistency_vector.py
```

**Checks:**
- Energy values across chapters
- Velocity constants
- Phase timeline definitions
- Population numbers
- Moon mass references
- Cross-phase contradictions

**Output:** `consistency_report.json` with detailed findings

## Scripts Reference

### `ingest_to_vector_db.py`

Ingests documents into vector database.

```bash
python scripts/ingest_to_vector_db.py [--reset]
```

**Options:**
- `--reset`: Delete and recreate collection (fresh start)

**Process:**
1. Connects to Qdrant
2. Loads embedding model
3. Chunks documents by section
4. Generates embeddings
5. Uploads to Qdrant in batches

### `search_docs.py`

Semantic search interface.

```bash
python scripts/search_docs.py "query" [--top-k N]
```

**Arguments:**
- `query`: Search query (natural language)
- `--top-k`: Number of results (default: 3)

**Example queries:**
```bash
# Technical constants
python scripts/search_docs.py "Moon escape velocity"

# Timelines
python scripts/search_docs.py "when does Phase Three begin"

# Systems
python scripts/search_docs.py "Dyson Swarm construction timeline"

# Concepts
python scripts/search_docs.py "Oracle decision making process"
```

### `check_consistency_vector.py`

Automated consistency checker.

```bash
python scripts/check_consistency_vector.py
```

**Checks performed:**
1. **Energy Values**: Dyson Swarm output, energy to move Earth, Sun output
2. **Velocities**: Escape velocities for Earth, Moon, solar system
3. **Phase Timelines**: Year ranges for each phase
4. **Population**: 10 billion mandate, Hive capacity
5. **Moon Mass**: Total mass, consumption rate, percentage used

**Outputs:**
- Console summary
- `consistency_report.json`: Detailed findings with file locations

**Cross-phase analysis:**
- Finds similar sections across different phases
- Flags potential contradictions (same topic, different phase claims)

## Workflow for Inconsistency Fixes

### Before Manual Checking:

```bash
# 1. Ensure DB is current
python scripts/ingest_to_vector_db.py

# 2. Run consistency check
python scripts/check_consistency_vector.py

# 3. Review report
cat consistency_report.json | jq '.["Energy Values"]'

# 4. Search specific values
python scripts/search_docs.py "4.3 × 10^32 joules"
```

### After Making Changes:

```bash
# 1. Re-ingest updated documents
python scripts/ingest_to_vector_db.py

# 2. Verify fix
python scripts/search_docs.py "your changed value"

# 3. Re-run consistency check
python scripts/check_consistency_vector.py
```

## Troubleshooting

### Qdrant not accessible

```bash
# Check if running
docker ps | grep qdrant

# Start if stopped
docker-compose up -d

# Check logs
docker logs planetary_exodus_qdrant
```

### Python dependencies missing

```bash
pip install qdrant-client sentence-transformers
```

### Collection not found

```bash
# Re-ingest with reset
python scripts/ingest_to_vector_db.py --reset
```

### Slow searches

Embeddings are generated on first search. Subsequent searches are fast (cached model).

## Data Persistence

Vector data is stored in `qdrant_data/` (Docker volume). This directory is gitignored.

**To reset completely:**
```bash
docker-compose down
rm -rf qdrant_data/
docker-compose up -d
python scripts/ingest_to_vector_db.py --reset
```

## Advanced Usage

### Custom Queries via Python

```python
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient(host="localhost", port=6333)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Search
query_vector = model.encode("your query").tolist()
results = client.search(
    collection_name="planetary_exodus_docs",
    query_vector=query_vector,
    limit=5,
    query_filter={
        "must": [
            {"key": "phase", "match": {"value": "Four"}}
        ]
    }
)
```

### Filter by Metadata

```python
# Search only Phase Four content
results = client.search(
    collection_name="planetary_exodus_docs",
    query_vector=query_vector,
    query_filter={"must": [{"key": "phase", "match": {"value": "Four"}}]}
)

# Search specific chapter
results = client.search(
    collection_name="planetary_exodus_docs",
    query_vector=query_vector,
    query_filter={"must": [{"key": "chapter", "match": {"value": 22}}]}
)
```

## Benefits Over grep/Manual Search

✅ **Semantic Understanding**: Finds conceptually related content, not just keyword matches  
✅ **Cross-Reference**: Automatically finds similar sections across chapters  
✅ **Inconsistency Detection**: Identifies contradictions by embedding similarity  
✅ **Fast**: Sub-second searches across entire corpus  
✅ **Contextual**: Returns surrounding text with metadata  

## Maintenance

### Regular Updates

After significant document changes:
```bash
python scripts/ingest_to_vector_db.py
python scripts/check_consistency_vector.py
```

### Database Stats

```python
from qdrant_client import QdrantClient
client = QdrantClient(host="localhost", port=6333)
info = client.get_collection("planetary_exodus_docs")
print(f"Total vectors: {info.points_count}")
```

## Notes

- Embeddings use `all-MiniLM-L6-v2`: Fast, 384 dimensions, good quality for document search
- Chunking by sections preserves context hierarchy
- Metadata includes file, chapter, phase, line ranges for easy reference
- Qdrant runs locally - no external API calls or data leaving your machine

---

**For questions or issues, check:**
- Qdrant docs: https://qdrant.tech/documentation/
- sentence-transformers: https://www.sbert.net/
