# Dependency Analysis Tools

## Overview

The dependency analysis system helps track **what needs to be updated when core premises or chapters change**. This is critical for maintaining consistency across the 28-document Planetary Exodus white paper.

The system combines three layers:

1. **Dependency Graph** - Structural relationships between chapters
2. **Premise Tracking** - Logical assumptions that chapters depend on
3. **Vector Database** - Semantic similarity for targeted searches

## Why This Matters

When we changed the **timeline premise** (from 5,500 years to 500 million years), we had to:
- Rewrite Chapters 20-21 completely
- Update the Conclusion chapter
- Verify no other documents referenced the old timeline

**With dependency analysis**, we can instantly identify:
- Which 3 chapters have HIGH impact from timeline changes (vs. reading all 28)
- Which sections contain specific phrases like "year 2500"
- What concepts are shared across affected chapters

## Quick Start

### 1. Build Dependency Graph

```bash
./exec/build_dependency_graph
```

**Output:**
- `reports/dependencies.json` - Machine-readable dependency data
- `reports/dependency_report.md` - Human-readable analysis

**What it extracts:**
- Cross-references between chapters (e.g., "see Chapter 5")
- Key concept usage (Dyson Swarm, Moon-Tug, Oracle, etc.)
- Premise dependencies (timeline, infrastructure assumptions, etc.)

### 2. Query Dependencies

#### Find chapter impact
```bash
./exec/query_dependencies --chapter "21_Chapter_20"
```

Shows:
- Which chapters depend on Chapter 20
- Which concepts Chapter 20 shares with other chapters
- Impact assessment if Chapter 20 changes

#### Find premise impact
```bash
./exec/query_dependencies --premise timeline_deep_time
```

Shows:
- All 23 documents affected by deep-time timeline premise
- Strength of dependency (HIGH/MEDIUM/LOW)
- Priority order for review

#### Find concept usage
```bash
./exec/query_dependencies --concept "Moon-Tug"
```

Shows:
- All 21 documents mentioning Moon-Tug
- Useful for ensuring consistency of technical terms

#### Interactive mode
```bash
./exec/query_dependencies --interactive
```

Provides a shell for exploring dependencies:
```
📊 > premise timeline_deep_time
📊 > concept Dyson Swarm
📊 > chapter 26_Conclusion
📊 > list premises
📊 > exit
```

### 3. Integrated Vector Search

Combines dependency analysis with semantic search for **targeted queries**:

```bash
./exec/integrated_query --premise timeline_deep_time --search "year 2500 departure"
```

This:
1. Identifies 23 documents affected by deep-time premise
2. Prioritizes 3 HIGH-impact documents
3. Searches only those documents for "year 2500 departure"
4. Returns semantically similar sections ranked by relevance

**Why this is powerful:**
- Regular vector search would scan all 28 documents
- Dependency-aware search focuses on the 3 most relevant
- Combines structural (dependency) with semantic (meaning) analysis

#### More examples:

```bash
# Find evacuation references in chapters related to Chapter 22
./exec/integrated_query --chapter "23_Chapter_22" --search "evacuation sequence"

# Find propulsion references in documents using Moon-Tug concept
./exec/integrated_query --concept "Moon-Tug" --search "propulsion xenon drives"

# Find governance references in oracle-dependent documents
./exec/integrated_query --premise oracle_governance --search "distributed consensus"
```

## Workflow: When a Premise Changes

### Example: Timeline reconceptualization

**Step 1: Identify impact scope**
```bash
./exec/query_dependencies --premise timeline_deep_time
```

Result:
- 3 HIGH priority documents (Chapters 20, 21, TOC)
- 7 MEDIUM priority documents
- 13 LOW priority documents

**Step 2: Search for specific problem phrases**
```bash
./exec/integrated_query --premise timeline_deep_time --search "year 2500 2600 3000"
```

Result:
- Targeted semantic search in 23 affected documents
- Finds sections actually using near-term years
- Ranked by relevance score

**Step 3: Update high-priority documents**
- Manually rewrite Chapters 20-21 (high impact, 6 references each)
- Update Conclusion (medium impact)
- Verify TOC alignment

**Step 4: Verify consistency**
```bash
./exec/full_consistency_check
```

## Tracked Premises

The system currently tracks 9 key premises:

1. **timeline_deep_time** - 500M year timeline
2. **timeline_near_term** - 2026-10K year timeline  
3. **dyson_infrastructure** - Dyson Swarm exists
4. **moon_tug_capability** - Moon-Tug transport functional
5. **hive_habitability** - Underground cities operational
6. **oracle_governance** - Oracle system active
7. **proxima_target** - Proxima Centauri b destination
8. **ten_billion_population** - 10B population baseline
9. **solar_physics** - Solar evolution physics

### Viewing premise details

```bash
./exec/query_dependencies --premise oracle_governance
```

Shows strength of dependency for each document (number of keyword matches).

## Tracked Concepts

The system tracks 35+ key concepts across all documents:

- **Infrastructure:** Dyson Swarm, Moon-Tug, Hive Cities, Oracle, Synthesis Engine
- **Timeline:** Phase Zero/One/Two/Three/Four, deep time, geological timescales
- **Technical:** solar brightening, cryogenic, transit, evacuation
- **Governance:** Aethelgard Protocol, Living Manifesto, distributed consensus

### Finding where concepts are used

```bash
# Find all mentions of Dyson Swarm
./exec/query_dependencies --concept "Dyson Swarm"

# Find all mentions of Phase Two
./exec/query_dependencies --concept "Phase Two"
```

## Integration with Vector DB

The dependency graph and vector DB are complementary:

| Tool | Best For | Limitation |
|------|----------|------------|
| **Dependency Graph** | Finding structural relationships, cross-references, explicit dependencies | Doesn't understand meaning or context |
| **Vector DB** | Finding semantic similarity, understanding context | Searches all documents equally, no priority |
| **Integrated Query** | **Best of both**: Prioritize by dependency, search by meaning | Requires both systems operational |

### When to use each:

**Use dependency graph when:**
- "What chapters reference Chapter 5?"
- "What documents depend on the timeline premise?"
- "Where is Moon-Tug mentioned?"

**Use vector DB when:**
- "Find sections about propulsion physics"
- "What mentions climate engineering?"
- "Explain the Oracle system"

**Use integrated query when:**
- "Find timeline inconsistencies in deep-time chapters" ← Combines both!
- "Search for governance issues in Oracle-dependent documents"
- "Find propulsion details in Moon-Tug-related chapters"

## Output Files

All outputs are saved to `reports/`:

```
reports/
├── dependencies.json          # Machine-readable dependency data
├── dependency_report.md       # Human-readable dependency analysis
├── consistency_issues.json    # Vector DB consistency check results
├── consistency_issues.md      # Readable consistency report
└── timeline_analysis.txt      # Timeline-specific analysis
```

## Advanced Usage

### Building custom queries

The dependency JSON structure:

```json
{
  "metadata": { "total_documents": 28, ... },
  "dependencies": {
    "21_Chapter_20": ["03_Chapter_02_Physics", "09_Chapter_08_Moon_Tug"]
  },
  "reverse_dependencies": {
    "03_Chapter_02_Physics": ["21_Chapter_20", "22_Chapter_21", ...]
  },
  "concept_usage": {
    "Dyson Swarm": ["21_Chapter_20", "10_Chapter_09_Dyson_Swarm", ...]
  },
  "premise_chains": {
    "timeline_deep_time": [
      {"document": "21_Chapter_20", "strength": 6},
      ...
    ]
  }
}
```

You can load this JSON and write custom Python scripts for specific analysis needs.

### Visualizing the graph (optional)

Install visualization libraries:
```bash
docker compose exec worker pip install networkx matplotlib
```

Then rebuild with visualization:
```bash
./exec/build_dependency_graph --visualize
```

This generates `reports/dependency_graph.png` showing visual network of chapter relationships.

## Maintenance

### When to rebuild the graph

Rebuild after:
- Adding new chapters
- Major rewrites changing chapter structure
- Introducing new key concepts
- Changing premise definitions

```bash
./exec/build_dependency_graph
```

### Updating tracked concepts

Edit `scripts/build_dependency_graph.py`, section `extract_key_concepts()`:

```python
key_concepts = [
    'Dyson Swarm', 'Moon-Tug', ...  # Add your concepts here
]
```

### Updating tracked premises

Edit `scripts/build_dependency_graph.py`, section `extract_premise_dependencies()`:

```python
premises = {
    'your_premise_id': {
        'keywords': ['keyword1', 'keyword2', ...],
        'description': 'Human-readable description'
    },
    ...
}
```

## Troubleshooting

**"Dependency file not found"**
```bash
./exec/build_dependency_graph  # Build it first
```

**"Could not connect to Qdrant"**
```bash
./exec/start  # Ensure containers are running
```

**"No results found"**
- Check premise/concept spelling (case-insensitive but must match)
- Use `list premises` or `list concepts` in interactive mode
- Rebuild graph if documents changed: `./exec/build_dependency_graph`

## Examples from Timeline Reconceptualization

### Before dependency analysis:
1. Changed Chapters 20-21 manually
2. Guessed Conclusion might need updates
3. Read entire Conclusion looking for problems
4. Missed some references initially

### With dependency analysis:
```bash
# Step 1: Find impact
./exec/query_dependencies --premise timeline_deep_time
# → 3 HIGH priority: Chapters 20, 21, TOC
# → 7 MEDIUM priority: Conclusion, Chapter 22, etc.

# Step 2: Targeted search
./exec/integrated_query --premise timeline_deep_time --search "5500 years 2500 7526"
# → Finds specific year references in affected documents only

# Step 3: Verify fix
./exec/full_consistency_check
# → 0 timeline issues ✅
```

Result: Systematic, comprehensive, no missed references.

## See Also

- [Vector Database Setup](../README.md#vector-database)
- [Consistency Checking](../exec/README.md)
- [Timeline Analysis](./analyze_timeline.py)

---

**Questions?** The tools are self-documenting:
```bash
./exec/query_dependencies --help
./exec/integrated_query --help
./exec/build_dependency_graph --help
```
