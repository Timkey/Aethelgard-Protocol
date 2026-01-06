# Aethelgard Protocol - Script Documentation

This directory contains automation scripts for generating and verifying the Aethelgard Protocol White Paper.

## Scripts Overview

### 1. extract_metadata.py
**Purpose:** Extracts structured metadata from raw.txt to avoid hallucination

**Usage:**
```bash
python3 scripts/extract_metadata.py
```

**Output:**
- `metadata/metadata_complete.json` - Complete metadata dump
- `metadata/technical_constants.json` - Physical constants and specifications
- `metadata/key_concepts.json` - Core concepts with line references
- `metadata/sections.json` - Document structure analysis
- `metadata/timeline.json` - Timeline events and phases
- `metadata/oracles.json` - Oracle definitions and references
- `metadata/quotes.json` - Key definitional quotes
- `metadata/religious_references.json` - Theological discussion points

**What it extracts:**
- Technical constants (Earth mass, journey duration, population targets)
- Key concepts and their locations in source
- Section boundaries and topics
- Timeline events
- Oracle definitions
- Direct quotes for accuracy
- Religious references

### 2. generate_toc.py
**Purpose:** Creates hierarchical Master Table of Contents

**Usage:**
```bash
python3 scripts/generate_toc.py
```

**Output:**
- `docs/00_Master_TOC.md` - Complete table of contents with page estimates

**Structure:**
- Part 1: Foundations and Rationale (~100 pages)
- Part 2: Technical Architecture (~150 pages)
- Part 3: Governance and Social Systems (~100 pages)
- Part 4: Implementation Roadmap (~80 pages)
- Appendices (~50 pages)

**Total Estimated:** ~500 pages

### 3. verify_content.py
**Purpose:** Verifies generated documents against source metadata

**Usage:**
```bash
python3 scripts/verify_content.py
```

**Output:**
- `reports/verification_report.md` - Verification results

**Checks:**
- Key concepts presence and consistency
- Technical accuracy of constants
- Oracle definitions completeness
- Internal consistency
- Cross-reference validation

## Workflow

### Phase 1: Metadata Extraction
```bash
# Extract metadata from raw.txt
python3 scripts/extract_metadata.py
```

This creates the ground truth cache that prevents hallucination.

### Phase 2: TOC Generation
```bash
# Generate master table of contents
python3 scripts/generate_toc.py
```

This creates the document structure.

### Phase 3: Document Generation
(Manual or AI-assisted)
- Use metadata files as reference
- Follow TOC structure
- Generate section by section

### Phase 4: Verification
```bash
# Verify generated documents
python3 scripts/verify_content.py
```

This ensures accuracy against source material.

## Anti-Hallucination Strategy

### 1. Metadata Cache
All factual information is extracted once and stored in JSON files. During document generation:
- Reference `metadata/*.json` files
- Quote directly from source with line numbers
- Never make up technical specifications

### 2. Line References
Every metadata entry includes:
- Line number in raw.txt
- Context snippet
- Allows verification of facts

### 3. Verification Loop
After generating content:
- Run verifier to check accuracy
- Compare against metadata
- Flag inconsistencies

### 4. Incremental Generation
Generate documents in small sections:
- Load relevant metadata
- Generate one chapter at a time
- Verify before proceeding

## File Structure

```
Planetary Exodus/
├── data/
│   └── raw.txt                      # Source interrogation
├── metadata/                        # Extracted facts (cache)
│   ├── metadata_complete.json
│   ├── technical_constants.json
│   ├── key_concepts.json
│   ├── sections.json
│   ├── timeline.json
│   ├── oracles.json
│   ├── quotes.json
│   └── religious_references.json
├── docs/                            # Generated documents
│   ├── 00_Master_TOC.md
│   ├── 01_Executive_Summary.md
│   ├── 02_Part1_Foundations.md
│   └── ...
├── reports/                         # Verification reports
│   └── verification_report.md
└── scripts/                         # This directory
    ├── extract_metadata.py
    ├── generate_toc.py
    ├── verify_content.py
    └── README.md
```

## Best Practices

### When Generating Content:

1. **Always reference metadata first**
   ```python
   with open('metadata/technical_constants.json') as f:
       constants = json.load(f)
   ```

2. **Include source citations**
   ```markdown
   Earth's mass is 5.97×10²⁴ kg (raw.txt:43)
   ```

3. **Verify after each section**
   ```bash
   python3 scripts/verify_content.py
   ```

4. **Use direct quotes when possible**
   - Better to quote source than paraphrase
   - Reduces risk of introducing errors

5. **Cross-reference related sections**
   - Use metadata to find all mentions of a concept
   - Ensure consistency across document

## Next Steps

After running these scripts:

1. Review `docs/00_Master_TOC.md`
2. Start generating sections based on TOC
3. Reference metadata files continuously
4. Run verification after each major section
5. Address any verification issues before proceeding

## Notes

- Scripts are designed to run on macOS/Linux
- Requires Python 3.7+
- All paths are absolute to avoid confusion
- JSON files are human-readable for debugging
- Scripts are idempotent (safe to run multiple times)

---

*Part of the Aethelgard Protocol Documentation System*
