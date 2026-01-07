# Consistency Fix Workflow Guide

## Overview

This guide explains how to use the iterative consistency checking and fixing workflow, including when and how to update the vector database.

## The Core Workflow Loop

```
┌─────────────────────────────────────────┐
│  1. Run Consistency Check               │
│     ./exec/full_consistency_check       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  2. Review Issues                       │
│     reports/consistency_issues.md       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  3. Apply Fixes                         │
│     Edit files in docs/                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  4. Update Vector DB (CRITICAL!)        │
│     ./exec/quick_reingest               │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  5. Re-check                            │
│     Go back to step 1                   │
└─────────────────────────────────────────┘
```

## Commands

### Option A: Automated Loop (Recommended)

The **automated loop** handles everything for you:

```bash
./exec/fix_loop
```

This will:
1. ✅ Run consistency check
2. ✅ Show issues in terminal
3. ⏸️  Pause and wait for you to fix docs
4. ✅ Automatically re-ingest documents
5. ✅ Re-check with updated data
6. 🔄 Repeat until issues are resolved

**Usage:**
```bash
# Standard mode (max 10 iterations, stop at 5 issues)
./exec/fix_loop

# Custom thresholds
./exec/fix_loop --max-iterations 20 --threshold 10

# Manual control over re-ingestion
./exec/fix_loop --no-auto-reingest
```

### Option B: Manual Control

If you prefer manual control over each step:

```bash
# Step 1: Check for issues
./exec/full_consistency_check

# Step 2: Review the reports
cat reports/consistency_issues.md

# Step 3: Apply fixes
# Edit files in docs/ folder...

# Step 4: Update vector DB (DON'T SKIP THIS!)
./exec/quick_reingest

# Step 5: Re-check
./exec/full_consistency_check
```

## Why Re-ingestion is Critical

The vector database stores **embedded representations** of all document sections for semantic search. When you edit documents:

- ❌ **Without re-ingestion:** Consistency checks use old/stale content
- ✅ **With re-ingestion:** Consistency checks use your latest edits

### Example Problem:

```
1. Consistency check finds: "Chapter 22 says 100 years until uninhabitable"
2. You fix it to: "tens of millions of years until uninhabitable"
3. You run check again WITHOUT re-ingesting
4. Result: Same issue appears! (Vector DB has old data)
```

### Correct Workflow:

```
1. Consistency check finds: "Chapter 22 says 100 years until uninhabitable"
2. You fix it to: "tens of millions of years until uninhabitable"
3. Run: ./exec/quick_reingest
4. Run check again
5. Result: Issue is gone ✅
```

## Performance Considerations

### Re-ingestion Speed

- **Initial ingestion:** ~30-60 seconds (271 sections)
- **Re-ingestion:** Same time (full rebuild)
- **Why not incremental?** Ensuring consistency is more important than speed

### When to Re-ingest

**Always re-ingest after:**
- ✅ Editing any file in `docs/`
- ✅ Completing a batch of fixes
- ✅ Before running consistency checks
- ✅ After merging changes from others

**No need to re-ingest after:**
- ❌ Changing scripts or exec files
- ❌ Updating metadata files
- ❌ Modifying index.html

## Monitoring Progress

### Check Iteration History

```bash
cat reports/iteration_history.json
```

This shows:
- Number of issues per iteration
- Issue breakdown by severity
- Progress over time

### View Latest Issues

```bash
# Human-readable
cat reports/consistency_issues.md

# Structured data
cat reports/consistency_issues.json
```

## Best Practices

### 1. Focus on High-Severity Issues First

```bash
# View only HIGH severity issues
grep -A 20 "### .* \[HIGH\]" reports/consistency_issues.md
```

### 2. Batch Related Fixes

Fix all timeline issues in one batch, then re-ingest once:

```
Fix Chapter 18 timeline → 
Fix Chapter 19 timeline → 
Fix Chapter 20 timeline → 
Run ./exec/quick_reingest → 
Re-check
```

### 3. Track Your Progress

Keep notes of what you've fixed:

```bash
# Add notes to your fixes
echo "Fixed Phase Zero timeline in Ch 18-20" >> reports/fix_notes.txt
```

### 4. Verify Before Moving On

After fixing HIGH severity issues, always re-check before moving to MEDIUM:

```
Fix HIGH issues → Re-ingest → Re-check → 
Fix MEDIUM issues → Re-ingest → Re-check
```

## Consistency Check Types

The system runs **5 passes**:

### Pass 1: Timeline Consistency
- Checks phase boundaries (Zero, One, Two, Three, Four)
- Validates year ranges
- Detects timeline conflicts

### Pass 2: Technical Constants
- Extracts numerical values
- Compares across documents
- Flags potential mismatches

### Pass 3: Semantic Contradictions
- Uses vector search for similar content
- Detects contradictory statements
- Finds conflicting numbers

### Pass 4: Phase Boundary Validation
- Ensures phase chapters have appropriate content
- Detects content in wrong phase

### Pass 5: Cross-Reference Validation
- Checks chapter references
- Validates links between sections

## Troubleshooting

### "Vector DB returns old data"

**Solution:** Re-ingest immediately
```bash
./exec/quick_reingest
```

### "Too many issues, overwhelming"

**Solution:** Filter by severity
```bash
# Run fix loop but only stop at 20 issues
./exec/fix_loop --threshold 20
```

### "Can't tell if fixes worked"

**Solution:** Check iteration history
```bash
cat reports/iteration_history.json | grep total_issues
```

### "Want to start fresh"

**Solution:** Rebuild everything
```bash
./exec/rebuild  # Recreates vector DB from scratch
```

## Advanced: Custom Checks

You can add custom consistency queries in `scripts/comprehensive_consistency_check.py`:

```python
verification_queries = [
    "How long until the Sun becomes uninhabitable",
    "YOUR CUSTOM QUERY HERE",  # Add here
]
```

Then re-run checks.

## Summary: The Golden Rule

> **After editing any document, ALWAYS run `./exec/quick_reingest` before running consistency checks.**

This ensures your consistency checks reflect your latest changes.
