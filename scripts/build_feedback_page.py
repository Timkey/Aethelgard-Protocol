#!/usr/bin/env python3
"""
Build feedback review page that reads localStorage notes
and generates GitHub-ready markdown export.
"""

from pathlib import Path

def generate_feedback_html():
    """Generate the feedback review and export HTML"""
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Feedback Notes - Aethelgard Protocol</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #0a0e27;
            color: #e0e0e0;
            line-height: 1.6;
        }

        .header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 64px;
            background: #141b2d;
            border-bottom: 2px solid #2a3f5f;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            z-index: 1000;
        }

        .header-title {
            font-size: 20px;
            font-weight: 600;
            color: #4a90e2;
        }

        .header-nav {
            display: flex;
            gap: 16px;
        }

        .nav-link {
            color: #e0e0e0;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 6px;
            transition: all 0.2s;
            background: rgba(74, 144, 226, 0.1);
        }

        .nav-link:hover {
            background: rgba(74, 144, 226, 0.2);
            color: #4a90e2;
        }

        .container {
            margin-top: 64px;
            padding: 24px;
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
        }

        .section {
            background: #141b2d;
            border: 1px solid #2a3f5f;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }

        .section-title {
            font-size: 24px;
            font-weight: 600;
            color: #4a90e2;
            margin-bottom: 16px;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #a0a0a0;
        }

        .empty-state-icon {
            font-size: 48px;
            margin-bottom: 16px;
        }

        .note-item {
            background: #0f1419;
            border: 1px solid #2a3f5f;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 16px;
        }

        .note-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .note-title {
            font-size: 16px;
            font-weight: 600;
            color: #e0e0e0;
        }

        .note-meta {
            font-size: 12px;
            color: #a0a0a0;
        }

        .note-content {
            color: #c0c0c0;
            line-height: 1.8;
            white-space: pre-wrap;
            background: #06090f;
            padding: 12px;
            border-radius: 6px;
            border-left: 3px solid #4a90e2;
        }

        .note-actions {
            margin-top: 12px;
            display: flex;
            gap: 8px;
        }

        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-delete {
            background: #dc3545;
            color: white;
        }

        .btn-delete:hover {
            background: #c82333;
        }

        .btn-primary {
            background: #4a90e2;
            color: white;
            font-size: 14px;
            padding: 12px 24px;
        }

        .btn-primary:hover {
            background: #357abd;
        }

        .btn-secondary {
            background: #2a3f5f;
            color: #e0e0e0;
            font-size: 14px;
            padding: 12px 24px;
        }

        .btn-secondary:hover {
            background: #3a4f6f;
        }

        .export-actions {
            display: flex;
            gap: 12px;
            margin-top: 20px;
        }

        .markdown-preview {
            background: #06090f;
            border: 1px solid #2a3f5f;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
            max-height: 400px;
            overflow-y: auto;
            white-space: pre-wrap;
            color: #c0c0c0;
        }

        .stats {
            display: flex;
            gap: 24px;
            margin-bottom: 20px;
        }

        .stat-card {
            background: rgba(74, 144, 226, 0.1);
            padding: 16px 24px;
            border-radius: 8px;
            border-left: 4px solid #4a90e2;
        }

        .stat-value {
            font-size: 32px;
            font-weight: 700;
            color: #4a90e2;
        }

        .stat-label {
            font-size: 12px;
            color: #a0a0a0;
            text-transform: uppercase;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-title">📋 Feedback Notes - Aethelgard Protocol</div>
        <div class="header-nav">
            <a href="index.html" class="nav-link">← Back to Document</a>
        </div>
    </div>

    <div class="container">
        <!-- Stats -->
        <div class="section">
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value" id="noteCount">0</div>
                    <div class="stat-label">Total Notes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="chapterCount">0</div>
                    <div class="stat-label">Chapters with Notes</div>
                </div>
            </div>
            <div class="export-actions">
                <button class="btn btn-primary" onclick="exportToMarkdown()">📥 Export GitHub Markdown</button>
                <button class="btn btn-secondary" onclick="clearAllNotes()">🗑️ Clear All Notes</button>
            </div>
        </div>

        <!-- Notes List -->
        <div class="section">
            <div class="section-title">Your Notes</div>
            <div id="notesList"></div>
        </div>

        <!-- Markdown Preview -->
        <div class="section" id="previewSection" style="display:none">
            <div class="section-title">GitHub Markdown Preview</div>
            <div class="markdown-preview" id="markdownPreview"></div>
            <button class="btn btn-primary" onclick="copyToClipboard()" style="margin-top:12px">📋 Copy to Clipboard</button>
        </div>
    </div>

    <script>
        function getNotes() {
            const notes = localStorage.getItem('aethelgard_notes');
            if (!notes) return {};
            
            const parsed = JSON.parse(notes);
            
            // Handle both old and new compressed format
            const normalized = {};
            Object.keys(parsed).forEach(key => {
                const note = parsed[key];
                normalized[key] = {
                    note: note.n || note.note || '',
                    document: note.d || note.document || '',
                    title: note.t || note.title || '',
                    timestamp: note.ts || note.timestamp || new Date().toISOString()
                };
            });
            
            return normalized;
        }

        function saveNotes(notes) {
            localStorage.setItem('aethelgard_notes', JSON.stringify(notes));
            loadNotes();
        }

        function deleteNote(key) {
            if (!confirm('Delete this note?')) return;
            const notes = getNotes();
            delete notes[key];
            saveNotes(notes);
        }

        function clearAllNotes() {
            if (!confirm('Delete ALL notes? This cannot be undone.')) return;
            localStorage.removeItem('aethelgard_notes');
            loadNotes();
        }

        function loadNotes() {
            const notes = getNotes();
            const notesList = document.getElementById('notesList');
            const noteKeys = Object.keys(notes);

            // Update stats
            document.getElementById('noteCount').textContent = noteKeys.length;
            const uniqueChapters = new Set(noteKeys.map(k => k.split(':')[0]));
            document.getElementById('chapterCount').textContent = uniqueChapters.size;

            if (noteKeys.length === 0) {
                notesList.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📝</div>
                        <div>No notes yet</div>
                        <div style="margin-top:8px;font-size:14px">Go to the document and click the note button to add feedback</div>
                    </div>
                `;
                return;
            }

            // Sort by timestamp (newest first)
            const sortedKeys = noteKeys.sort((a, b) => {
                const timeA = new Date(notes[a].timestamp || 0);
                const timeB = new Date(notes[b].timestamp || 0);
                return timeB - timeA;
            });

            notesList.innerHTML = sortedKeys.map(key => {
                const note = notes[key];
                const date = new Date(note.timestamp);
                const dateStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();

                return `
                    <div class="note-item">
                        <div class="note-header">
                            <div>
                                <div class="note-title">${note.title}</div>
                                <div class="note-meta">${dateStr}</div>
                            </div>
                        </div>
                        <div class="note-content">${note.note}</div>
                        <div class="note-actions">
                            <button class="btn btn-delete" onclick="deleteNote('${key.replace(/'/g, "\\'")}')">🗑️ Delete</button>
                        </div>
                    </div>
                `;
            }).join('');
        }

        function exportToMarkdown() {
            const notes = getNotes();
            const noteKeys = Object.keys(notes);

            if (noteKeys.length === 0) {
                alert('No notes to export');
                return;
            }

            // Group by document
            const byDocument = {};
            noteKeys.forEach(key => {
                const note = notes[key];
                const docFile = note.document;
                if (!byDocument[docFile]) {
                    byDocument[docFile] = [];
                }
                byDocument[docFile].push({ key, ...note });
            });

            // Generate markdown
            let markdown = `# Feedback on Aethelgard Protocol\\n\\n`;
            markdown += `**Generated:** ${new Date().toLocaleDateString()}\\n`;
            markdown += `**Total Notes:** ${noteKeys.length}\\n\\n`;
            markdown += `---\\n\\n`;

            Object.entries(byDocument).forEach(([docFile, docNotes]) => {
                const title = docNotes[0].title;
                markdown += `## ${title}\\n\\n`;

                docNotes.forEach(note => {
                    markdown += `### Note\\n`;
                    markdown += `**Added:** ${new Date(note.timestamp).toLocaleDateString()}\\n\\n`;
                    markdown += `${note.note}\\n\\n`;
                    markdown += `---\\n\\n`;
                });
            });

            markdown += `\\n---\\n`;
            markdown += `*Generated from ${noteKeys.length} notes across ${Object.keys(byDocument).length} chapters*\\n`;
            markdown += `*Repository: https://github.com/timkey/Aethelgard-Protocol*\\n`;

            // Show preview
            document.getElementById('markdownPreview').textContent = markdown;
            document.getElementById('previewSection').style.display = 'block';
            document.getElementById('previewSection').scrollIntoView({ behavior: 'smooth' });

            // Store for clipboard
            window.exportedMarkdown = markdown;
        }

        function copyToClipboard() {
            const markdown = window.exportedMarkdown;
            if (!markdown) return;

            navigator.clipboard.writeText(markdown).then(() => {
                const btn = event.target;
                const originalText = btn.textContent;
                btn.textContent = '✓ Copied!';
                setTimeout(() => btn.textContent = originalText, 2000);
            }).catch(err => {
                // Fallback for older browsers
                const textarea = document.createElement('textarea');
                textarea.value = markdown;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                alert('Copied to clipboard!');
            });
        }

        // Load notes on page load
        window.addEventListener('DOMContentLoaded', loadNotes);
    </script>
</body>
</html>
"""
    
    return html

def main():
    print("Building feedback page...")
    
    # Generate HTML
    html = generate_feedback_html()
    
    # Write to output file
    output_path = Path(__file__).parent.parent / 'feedback.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    # Get file size
    size_kb = output_path.stat().st_size / 1024
    
    print(f"✓ Generated {output_path}")
    print(f"  File size: {size_kb:.1f} KB")

if __name__ == '__main__':
    main()
