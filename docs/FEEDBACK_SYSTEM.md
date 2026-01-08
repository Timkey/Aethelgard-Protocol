# Feedback System Documentation

## Overview
Complete client-side feedback/note-taking system for the Aethelgard Protocol document. Allows reviewers to add notes to any chapter, stores them in localStorage, and exports to GitHub-ready markdown.

## Features

### 1. **Note-Taking**
- 📝 Floating button (bottom-right) to add notes on any chapter
- Notes stored per document in localStorage
- Persistent across browser sessions
- Each note includes:
  - Document title and file path
  - Note content
  - Timestamp (ISO format)

### 2. **Review Page** (`feedback.html`)
- Shows all notes organized by chapter
- Statistics: Total notes, chapters with notes
- Click-to-delete individual notes
- Clear all notes button (with confirmation)
- Recent notes shown first (sorted by timestamp)

### 3. **GitHub Export**
- One-click markdown generation
- Formatted for GitHub issues/comments
- Includes:
  - Total note count
  - Generation date
  - Notes grouped by chapter
  - Timestamps for each note
  - Repository link
- Copy to clipboard functionality
- Preview before copying

## User Flow

### Adding Notes
1. Open `index.html` in browser
2. Navigate to any chapter
3. Click the 📝 button (bottom-right)
4. Type your note
5. Click "💾 Save Note"
6. See ✓ confirmation

### Reviewing Notes
1. From welcome screen, click "📋 Review Notes (X)"
2. OR open `feedback.html` directly
3. See all notes sorted by recency
4. Delete individual notes or clear all

### Exporting to GitHub
1. Open `feedback.html`
2. Click "📥 Export GitHub Markdown"
3. Review the formatted markdown preview
4. Click "📋 Copy to Clipboard"
5. Paste into GitHub issue/PR/comment

## Technical Details

### Storage Format (localStorage)
```json
{
  "aethelgard_notes": {
    "docs/02_Chapter_01_Solar_Imperative.md:main": {
      "note": "Timeline needs clarification on Phase 0",
      "document": "docs/02_Chapter_01_Solar_Imperative.md",
      "title": "Ch 1: The Solar Imperative",
      "timestamp": "2025-01-08T12:34:56.789Z"
    },
    "docs/06_Chapter_05_Oracle_System.md:main": {
      "note": "How does voting weight change over time?",
      "document": "docs/06_Chapter_05_Oracle_System.md",
      "title": "Ch 5: Oracle System",
      "timestamp": "2025-01-08T13:45:12.345Z"
    }
  }
}
```

### Key Functions

#### In `index.html`
- `getNotes()` - Retrieve all notes from localStorage
- `saveNotes(notes)` - Persist notes and update counts
- `addNoteToCurrentSection()` - Open modal for current chapter
- `saveNote()` - Save note to localStorage
- `deleteNote()` - Remove note from localStorage
- `closeNoteModal()` - Close note modal
- `updateNoteCounts()` - Update note count in UI

#### In `feedback.html`
- `loadNotes()` - Display all notes
- `exportToMarkdown()` - Generate GitHub markdown
- `copyToClipboard()` - Copy markdown to clipboard
- `clearAllNotes()` - Delete all notes (with confirmation)

### Export Format Example
```markdown
# Feedback on Aethelgard Protocol

**Generated:** 1/8/2025
**Total Notes:** 3

---

## Ch 1: The Solar Imperative

### Note
**Added:** 1/8/2025

Timeline needs clarification on Phase 0

---

## Ch 5: Oracle System

### Note
**Added:** 1/8/2025

How does voting weight change over time?

---

---
*Generated from 3 notes across 2 chapters*
*Repository: https://github.com/timkey/Aethelgard-Protocol*
```

## Build Scripts

### Rebuild Index with Notes
```bash
python3 scripts/build_static_html.py
# OR
./exec/build_html
```

### Rebuild Feedback Page
```bash
python3 scripts/build_feedback_page.py
# OR
./exec/build_feedback
```

### Rebuild Both
```bash
python3 scripts/build_static_html.py && python3 scripts/build_feedback_page.py
```

## File Sizes
- `index.html`: 495.1 KB (includes note-taking UI)
- `feedback.html`: 12.4 KB (review and export page)

## Browser Compatibility
- ✅ Chrome/Edge (localStorage, clipboard API)
- ✅ Firefox (localStorage, clipboard API)
- ✅ Safari (localStorage, clipboard fallback)
- ✅ Works from `file://` protocol (no server needed)

## Limitations
- localStorage limit: ~5-10MB per domain (thousands of notes)
- Notes stored per-browser (not synced across devices)
- No backend/database (intentional design choice)
- No real-time collaboration
- Markdown export is one-way (can't import back)

## Future Enhancements (Optional)
- [ ] Add note indicators in document navigation
- [ ] Tag notes (bug, question, suggestion)
- [ ] Filter notes by tag or chapter
- [ ] Export individual chapter feedback
- [ ] JSON export/import for note sharing
- [ ] Paragraph-level notes (not just chapter-level)
- [ ] Note threading/replies

## Privacy & Data
- All data stored locally in browser
- No server communication
- No tracking or analytics
- Clear all notes anytime from feedback page
- Browser cache clear removes all notes
