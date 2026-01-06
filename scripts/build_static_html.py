#!/usr/bin/env python3
"""
Build a fully self-contained static HTML file with embedded markdown content.
This avoids CORS issues when opening from file:// protocol.
"""

import json
from pathlib import Path

# Document structure
documents = [
    {'file': 'docs/00_Master_TOC.md', 'title': 'Table of Contents', 'section': 'Overview', 'icon': '📑'},
    {'file': 'docs/01_Executive_Summary.md', 'title': 'Executive Summary', 'section': 'Overview', 'icon': '📋'},
    {'file': 'docs/02_Chapter_01_Solar_Imperative.md', 'title': 'Ch 1: The Solar Imperative', 'section': 'Part 1: Foundations', 'icon': '☀️'},
    {'file': 'docs/03_Chapter_02_Physics.md', 'title': 'Ch 2: Physics of Planetary Motion', 'section': 'Part 1: Foundations', 'icon': '🌍'},
    {'file': 'docs/04_Chapter_03_Alternatives.md', 'title': 'Ch 3: Alternative Strategies', 'section': 'Part 1: Foundations', 'icon': '🔀'},
    {'file': 'docs/05_Chapter_04_Ten_Billion_Mandate.md', 'title': 'Ch 4: The 10 Billion Mandate', 'section': 'Part 1: Foundations', 'icon': '👥'},
    {'file': 'docs/06_Chapter_05_Oracle_System.md', 'title': 'Ch 5: Oracle System', 'section': 'Part 2: Technical Architecture', 'icon': '🤖'},
    {'file': 'docs/07_Chapter_06_Synthesis_Engine.md', 'title': 'Ch 6: Synthesis Engine', 'section': 'Part 2: Technical Architecture', 'icon': '⚙️'},
    {'file': 'docs/08_Chapter_07_Living_Manifesto.md', 'title': 'Ch 7: Living Manifesto', 'section': 'Part 2: Technical Architecture', 'icon': '📜'},
    {'file': 'docs/09_Chapter_08_Moon_Tug.md', 'title': 'Ch 8: Moon-Tug Propulsion', 'section': 'Part 2: Technical Architecture', 'icon': '🌙'},
    {'file': 'docs/10_Chapter_09_Dyson_Swarm.md', 'title': 'Ch 9: Dyson Swarm', 'section': 'Part 2: Technical Architecture', 'icon': '⭐'},
    {'file': 'docs/11_Chapter_10_Defense.md', 'title': 'Ch 10: Defense Network', 'section': 'Part 2: Technical Architecture', 'icon': '🛡️'},
    {'file': 'docs/12_Chapter_11_Hive_Cities.md', 'title': 'Ch 11: Underground Hive Cities', 'section': 'Part 2: Technical Architecture', 'icon': '🏙️'},
    {'file': 'docs/13_Chapter_12_Cryogenic.md', 'title': 'Ch 12: Cryogenic Management', 'section': 'Part 2: Technical Architecture', 'icon': '❄️'},
    {'file': 'docs/14_Chapter_13.md', 'title': 'Ch 13: Democracy to Protocol', 'section': 'Part 3: Governance & Social', 'icon': '⚖️'},
    {'file': 'docs/15_Chapter_14.md', 'title': 'Ch 14: Geopolitical Integration', 'section': 'Part 3: Governance & Social', 'icon': '🌐'},
    {'file': 'docs/16_Chapter_15.md', 'title': 'Ch 15: Theological Reconciliation', 'section': 'Part 3: Governance & Social', 'icon': '🕊️'},
    {'file': 'docs/17_Chapter_16.md', 'title': 'Ch 16: Social Cohesion', 'section': 'Part 3: Governance & Social', 'icon': '🤝'},
    {'file': 'docs/18_Chapter_17.md', 'title': 'Ch 17: Economic Models', 'section': 'Part 3: Governance & Social', 'icon': '💰'},
    {'file': 'docs/19_Chapter_18.md', 'title': 'Ch 18: Phase Zero (2026-2050)', 'section': 'Part 4: Implementation Roadmap', 'icon': '🚀'},
    {'file': 'docs/20_Chapter_19.md', 'title': 'Ch 19: Phase One (2050-2150)', 'section': 'Part 4: Implementation Roadmap', 'icon': '🏗️'},
    {'file': 'docs/21_Chapter_20.md', 'title': 'Ch 20: Phase Two (2150-2500)', 'section': 'Part 4: Implementation Roadmap', 'icon': '🌑'},
    {'file': 'docs/22_Chapter_21.md', 'title': 'Ch 21: Phase Three (2500-4500)', 'section': 'Part 4: Implementation Roadmap', 'icon': '🌌'},
    {'file': 'docs/23_Chapter_22.md', 'title': 'Ch 22: Phase Four (4500-5200+)', 'section': 'Part 4: Implementation Roadmap', 'icon': '🏡'},
    {'file': 'docs/24_Appendix_A_Constants.md', 'title': 'Appendix A: Technical Constants', 'section': 'Part 5: Appendices', 'icon': '📐'},
    {'file': 'docs/25_Appendix_B_Math.md', 'title': 'Appendix B: Mathematical Proofs', 'section': 'Part 5: Appendices', 'icon': '📊'},
    {'file': 'docs/26_Conclusion.md', 'title': 'Conclusion: Species-Level Commitment', 'section': 'Conclusion', 'icon': '🌟'}
]

def escape_js_string(text):
    """Escape text for embedding in JavaScript string"""
    return text.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

def load_markdown_content():
    """Load all markdown files and return as JSON-safe structure"""
    content_map = {}
    # Use relative path from script location
    base_path = Path(__file__).parent.parent
    
    for doc in documents:
        file_path = base_path / doc['file']
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                content_map[doc['file']] = escape_js_string(content)
                print(f"✓ Loaded {doc['file']} ({len(content)} chars)")
        except FileNotFoundError:
            print(f"✗ Not found: {doc['file']}")
            content_map[doc['file']] = f"# Document Not Found\n\nThe file `{doc['file']}` could not be loaded."
    
    return content_map

def generate_html(content_map):
    """Generate the complete HTML with embedded content"""
    
    # Convert to JavaScript object
    js_content = "const EMBEDDED_CONTENT = {\n"
    for file_path, content in content_map.items():
        js_content += f"    '{file_path}': `{content}`,\n"
    js_content += "};\n\n"
    
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aethelgard Protocol - White Paper</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
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

        .container {
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        /* Mobile Menu Toggle */
        .mobile-header {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 56px;
            background: #141b2d;
            border-bottom: 1px solid #2a3f5f;
            z-index: 1001;
            align-items: center;
            padding: 0 16px;
        }

        .menu-toggle {
            background: none;
            border: none;
            color: #fff;
            font-size: 24px;
            cursor: pointer;
            padding: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
        }

        .mobile-title {
            flex: 1;
            text-align: center;
            font-size: 16px;
            font-weight: 600;
            color: #fff;
        }

        .home-button {
            background: none;
            border: none;
            color: #4a90e2;
            font-size: 20px;
            cursor: pointer;
            padding: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
        }

        /* Overlay for mobile menu */
        .sidebar-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 999;
        }

        /* Sidebar Navigation */
        .sidebar {
            width: 320px;
            background: #141b2d;
            border-right: 1px solid #2a3f5f;
            overflow-y: auto;
            flex-shrink: 0;
        }

        .sidebar-header {
            padding: 24px 20px;
            background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
            border-bottom: 1px solid #3a5f8f;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        .sidebar-header h1 {
            font-size: 20px;
            font-weight: 600;
            color: #fff;
            margin-bottom: 4px;
        }

        .sidebar-header .subtitle {
            font-size: 13px;
            color: #a0c4ff;
            opacity: 0.9;
        }

        .nav-section {
            padding: 12px 0;
            border-bottom: 1px solid #1e2940;
        }

        .nav-section-title {
            padding: 8px 20px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #6b8caf;
        }

        .nav-item {
            padding: 10px 20px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 10px;
            border-left: 3px solid transparent;
        }

        .nav-item:hover {
            background: #1a2332;
            border-left-color: #4a90e2;
        }

        .nav-item.active {
            background: #1e2a3a;
            border-left-color: #4a90e2;
        }

        .nav-item .icon {
            font-size: 16px;
            width: 20px;
            text-align: center;
        }

        .nav-item .title {
            flex: 1;
            font-size: 14px;
            color: #c8d6e5;
        }

        .nav-item.active .title {
            color: #fff;
            font-weight: 500;
        }

        .nav-item .word-count {
            font-size: 11px;
            color: #6b8caf;
        }

        /* Content Area */
        .content {
            flex: 1;
            overflow-y: auto;
            background: #0f1419;
        }

        .content-inner {
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 60px 100px 60px;
        }

        /* Document Header */
        .doc-header {
            margin-bottom: 40px;
            padding-bottom: 24px;
            border-bottom: 2px solid #1e3a5f;
        }

        .doc-title {
            font-size: 36px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 12px;
            line-height: 1.2;
        }

        .doc-meta {
            display: flex;
            gap: 20px;
            font-size: 13px;
            color: #8899aa;
            flex-wrap: wrap;
        }

        .doc-meta .meta-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* Markdown Content Styles */
        .markdown-content {
            color: #d4d4d4;
            font-size: 16px;
            line-height: 1.8;
        }

        .markdown-content h1 {
            font-size: 32px;
            font-weight: 700;
            color: #fff;
            margin: 48px 0 24px 0;
            padding-bottom: 12px;
            border-bottom: 2px solid #2a3f5f;
        }

        .markdown-content h2 {
            font-size: 26px;
            font-weight: 600;
            color: #e8e8e8;
            margin: 40px 0 20px 0;
        }

        .markdown-content h3 {
            font-size: 21px;
            font-weight: 600;
            color: #d8d8d8;
            margin: 32px 0 16px 0;
        }

        .markdown-content h4 {
            font-size: 18px;
            font-weight: 600;
            color: #c8c8c8;
            margin: 24px 0 12px 0;
        }

        .markdown-content p {
            margin: 16px 0;
        }

        .markdown-content ul, .markdown-content ol {
            margin: 16px 0;
            padding-left: 28px;
        }

        .markdown-content li {
            margin: 8px 0;
        }

        .markdown-content strong {
            color: #fff;
            font-weight: 600;
        }

        .markdown-content em {
            color: #b8c5d6;
            font-style: italic;
        }

        .markdown-content code {
            background: #1a2332;
            color: #ffa07a;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 14px;
            font-family: 'Monaco', 'Courier New', monospace;
        }

        .markdown-content pre {
            background: #141b2d;
            border: 1px solid #2a3f5f;
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
            margin: 20px 0;
        }

        .markdown-content pre code {
            background: none;
            padding: 0;
            color: #d4d4d4;
        }

        .markdown-content blockquote {
            border-left: 4px solid #4a90e2;
            background: #141b2d;
            padding: 16px 20px;
            margin: 20px 0;
            font-style: italic;
            color: #b8c5d6;
        }

        .markdown-content table {
            width: 100%;
            border-collapse: collapse;
            margin: 24px 0;
            background: #141b2d;
            border-radius: 6px;
            overflow: hidden;
        }

        .markdown-content th {
            background: #1e3a5f;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #fff;
            border-bottom: 2px solid #2a3f5f;
        }

        .markdown-content td {
            padding: 12px;
            border-bottom: 1px solid #1e2940;
        }

        .markdown-content tr:last-child td {
            border-bottom: none;
        }

        .markdown-content hr {
            border: none;
            border-top: 1px solid #2a3f5f;
            margin: 40px 0;
        }

        .markdown-content a {
            color: #4a90e2;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-color 0.2s;
        }

        .markdown-content a:hover {
            border-bottom-color: #4a90e2;
        }

        /* Citation styling */
        .markdown-content em:has(a[href*="raw.txt"]) {
            color: #6b8caf;
            font-size: 14px;
        }

        /* Welcome Screen */
        .welcome {
            text-align: center;
            padding: 100px 40px;
        }

        .welcome h1 {
            font-size: 48px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 16px;
        }

        .welcome .subtitle {
            font-size: 20px;
            color: #8899aa;
            margin-bottom: 40px;
        }

        .welcome .description {
            font-size: 16px;
            color: #b8c5d6;
            max-width: 600px;
            margin: 0 auto 40px auto;
            line-height: 1.8;
        }

        .welcome .stats {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 60px;
            flex-wrap: wrap;
        }

        .welcome .stat {
            text-align: center;
            min-width: 120px;
        }

        .welcome .stat-value {
            font-size: 36px;
            font-weight: 700;
            color: #4a90e2;
            display: block;
        }

        .welcome .stat-label {
            font-size: 13px;
            color: #8899aa;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 8px;
        }

        .welcome .start-hint {
            margin-top: 60px;
            font-size: 14px;
            color: #6b8caf;
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
        }

        ::-webkit-scrollbar-track {
            background: #0a0e27;
        }

        ::-webkit-scrollbar-thumb {
            background: #2a3f5f;
            border-radius: 5px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #3a5f8f;
        }

        /* Responsive */
        @media (max-width: 1024px) {
            .content-inner {
                padding: 40px 40px 100px 40px;
            }
        }

        @media (max-width: 768px) {
            .mobile-header {
                display: flex;
            }

            .sidebar {
                position: fixed;
                left: -100%;
                top: 0;
                bottom: 0;
                z-index: 1000;
                transition: left 0.3s ease;
            }

            .sidebar.open {
                left: 0;
            }

            .sidebar-overlay.show {
                display: block;
            }

            .content {
                padding-top: 56px;
            }

            .content-inner {
                padding: 30px 20px 80px 20px;
            }

            .doc-title {
                font-size: 28px;
            }

            .welcome {
                padding: 60px 20px;
            }

            .welcome h1 {
                font-size: 32px;
            }

            .welcome .subtitle {
                font-size: 18px;
            }

            .welcome .stats {
                gap: 20px;
            }

            .welcome .stat-value {
                font-size: 28px;
            }

            .markdown-content {
                font-size: 15px;
            }

            .markdown-content h1 {
                font-size: 26px;
            }

            .markdown-content h2 {
                font-size: 22px;
            }

            .markdown-content h3 {
                font-size: 19px;
            }

            .markdown-content pre {
                padding: 12px;
                font-size: 13px;
            }
        }

        @media (max-width: 480px) {
            .welcome h1 {
                font-size: 28px;
            }

            .welcome .stats {
                flex-direction: column;
                gap: 30px;
            }

            .doc-meta {
                font-size: 12px;
            }
        }
    </style>
</head>
<body>
    <!-- Mobile Header -->
    <div class="mobile-header">
        <button class="menu-toggle" id="menuToggle" aria-label="Toggle menu">☰</button>
        <div class="mobile-title" id="mobileTitle">Aethelgard Protocol</div>
        <button class="home-button" id="homeButton" aria-label="Go to home">🏠</button>
    </div>

    <!-- Sidebar Overlay -->
    <div class="sidebar-overlay" id="sidebarOverlay"></div>

    <div class="container">
        <!-- Sidebar Navigation -->
        <nav class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <h1>Aethelgard Protocol</h1>
                <div class="subtitle">White Paper • 2026</div>
            </div>
            <div id="navigation"></div>
        </nav>

        <!-- Content Area -->
        <main class="content">
            <div class="content-inner" id="content">
                <div class="welcome">
                    <h1>Aethelgard Protocol</h1>
                    <div class="subtitle">A 5,000-Year Journey to Save Humanity</div>
                    <div class="description">
                        A comprehensive technical white paper detailing the plan to move Earth 
                        and Moon to a new star system, preserving 10 billion people and Earth's 
                        entire biosphere across interstellar space.
                    </div>
                    <div class="stats">
                        <div class="stat">
                            <span class="stat-value" id="total-chapters">—</span>
                            <span class="stat-label">Chapters</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value" id="total-words">—</span>
                            <span class="stat-label">Words</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value" id="total-pages">—</span>
                            <span class="stat-label">Pages</span>
                        </div>
                    </div>
                    <div class="start-hint">
                        ← Select a chapter from the sidebar to begin
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script>
        // Embedded markdown content (avoids CORS issues with file:// protocol)
        """ + js_content + """
        
        // Document structure
        const documents = [
            { file: 'docs/00_Master_TOC.md', title: 'Table of Contents', section: 'Overview', icon: '📑' },
            { file: 'docs/01_Executive_Summary.md', title: 'Executive Summary', section: 'Overview', icon: '📋' },
            { file: 'docs/02_Chapter_01_Solar_Imperative.md', title: 'Ch 1: The Solar Imperative', section: 'Part 1: Foundations', icon: '☀️' },
            { file: 'docs/03_Chapter_02_Physics.md', title: 'Ch 2: Physics of Planetary Motion', section: 'Part 1: Foundations', icon: '🌍' },
            { file: 'docs/04_Chapter_03_Alternatives.md', title: 'Ch 3: Alternative Strategies', section: 'Part 1: Foundations', icon: '🔀' },
            { file: 'docs/05_Chapter_04_Ten_Billion_Mandate.md', title: 'Ch 4: The 10 Billion Mandate', section: 'Part 1: Foundations', icon: '👥' },
            { file: 'docs/06_Chapter_05_Oracle_System.md', title: 'Ch 5: Oracle System', section: 'Part 2: Technical Architecture', icon: '🤖' },
            { file: 'docs/07_Chapter_06_Synthesis_Engine.md', title: 'Ch 6: Synthesis Engine', section: 'Part 2: Technical Architecture', icon: '⚙️' },
            { file: 'docs/08_Chapter_07_Living_Manifesto.md', title: 'Ch 7: Living Manifesto', section: 'Part 2: Technical Architecture', icon: '📜' },
            { file: 'docs/09_Chapter_08_Moon_Tug.md', title: 'Ch 8: Moon-Tug Propulsion', section: 'Part 2: Technical Architecture', icon: '🌙' },
            { file: 'docs/10_Chapter_09_Dyson_Swarm.md', title: 'Ch 9: Dyson Swarm', section: 'Part 2: Technical Architecture', icon: '⭐' },
            { file: 'docs/11_Chapter_10_Defense.md', title: 'Ch 10: Defense Network', section: 'Part 2: Technical Architecture', icon: '🛡️' },
            { file: 'docs/12_Chapter_11_Hive_Cities.md', title: 'Ch 11: Underground Hive Cities', section: 'Part 2: Technical Architecture', icon: '🏙️' },
            { file: 'docs/13_Chapter_12_Cryogenic.md', title: 'Ch 12: Cryogenic Management', section: 'Part 2: Technical Architecture', icon: '❄️' },
            { file: 'docs/14_Chapter_13.md', title: 'Ch 13: Democracy to Protocol', section: 'Part 3: Governance & Social', icon: '⚖️' },
            { file: 'docs/15_Chapter_14.md', title: 'Ch 14: Geopolitical Integration', section: 'Part 3: Governance & Social', icon: '🌐' },
            { file: 'docs/16_Chapter_15.md', title: 'Ch 15: Theological Reconciliation', section: 'Part 3: Governance & Social', icon: '🕊️' },
            { file: 'docs/17_Chapter_16.md', title: 'Ch 16: Social Cohesion', section: 'Part 3: Governance & Social', icon: '🤝' },
            { file: 'docs/18_Chapter_17.md', title: 'Ch 17: Economic Models', section: 'Part 3: Governance & Social', icon: '💰' },
            { file: 'docs/19_Chapter_18.md', title: 'Ch 18: Phase Zero (2026-2050)', section: 'Part 4: Implementation Roadmap', icon: '🚀' },
            { file: 'docs/20_Chapter_19.md', title: 'Ch 19: Phase One (2050-2150)', section: 'Part 4: Implementation Roadmap', icon: '🏗️' },
            { file: 'docs/21_Chapter_20.md', title: 'Ch 20: Phase Two (2150-2500)', section: 'Part 4: Implementation Roadmap', icon: '🌑' },
            { file: 'docs/22_Chapter_21.md', title: 'Ch 21: Phase Three (2500-4500)', section: 'Part 4: Implementation Roadmap', icon: '🌌' },
            { file: 'docs/23_Chapter_22.md', title: 'Ch 22: Phase Four (4500-5200+)', section: 'Part 4: Implementation Roadmap', icon: '🏡' },
            { file: 'docs/24_Appendix_A_Constants.md', title: 'Appendix A: Technical Constants', section: 'Part 5: Appendices', icon: '📐' },
            { file: 'docs/25_Appendix_B_Math.md', title: 'Appendix B: Mathematical Proofs', section: 'Part 5: Appendices', icon: '📊' },
            { file: 'docs/26_Conclusion.md', title: 'Conclusion: Species-Level Commitment', section: 'Conclusion', icon: '🌟' }
        ];

        let currentDoc = null;
        let wordCounts = {};

        // Mobile menu functionality
        const menuToggle = document.getElementById('menuToggle');
        const sidebar = document.getElementById('sidebar');
        const sidebarOverlay = document.getElementById('sidebarOverlay');
        const homeButton = document.getElementById('homeButton');

        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            sidebarOverlay.classList.toggle('show');
        });

        sidebarOverlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            sidebarOverlay.classList.remove('show');
        });

        homeButton.addEventListener('click', () => {
            showWelcome();
            sidebar.classList.remove('open');
            sidebarOverlay.classList.remove('show');
        });

        // Calculate word counts for all documents
        documents.forEach(doc => {
            const content = EMBEDDED_CONTENT[doc.file] || '';
            wordCounts[doc.file] = content.split(/\\s+/).filter(w => w.length > 0).length;
        });

        // Build navigation
        function buildNavigation() {
            const nav = document.getElementById('navigation');
            const sections = {};
            
            // Group documents by section
            documents.forEach(doc => {
                if (!sections[doc.section]) {
                    sections[doc.section] = [];
                }
                sections[doc.section].push(doc);
            });

            // Build HTML
            let html = '';
            for (const [section, docs] of Object.entries(sections)) {
                html += `<div class="nav-section">`;
                html += `<div class="nav-section-title">${section}</div>`;
                docs.forEach(doc => {
                    const words = wordCounts[doc.file] || 0;
                    const wordText = words > 0 ? `${Math.round(words/1000)}k` : '';
                    html += `
                        <div class="nav-item" data-file="${doc.file}">
                            <span class="icon">${doc.icon}</span>
                            <span class="title">${doc.title}</span>
                            <span class="word-count">${wordText}</span>
                        </div>
                    `;
                });
                html += `</div>`;
            }
            
            nav.innerHTML = html;

            // Add click handlers
            document.querySelectorAll('.nav-item').forEach(item => {
                item.addEventListener('click', () => {
                    const file = item.getAttribute('data-file');
                    loadDocument(file);
                    // Close mobile menu after selection
                    sidebar.classList.remove('open');
                    sidebarOverlay.classList.remove('show');
                });
            });
        }

        // Show welcome screen
        function showWelcome() {
            currentDoc = null;
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            
            const totalWords = Object.values(wordCounts).reduce((a, b) => a + b, 0);
            const totalPages = Math.round(totalWords / 250);
            
            document.getElementById('content').innerHTML = `
                <div class="welcome">
                    <h1>Aethelgard Protocol</h1>
                    <div class="subtitle">A 5,000-Year Journey to Save Humanity</div>
                    <div class="description">
                        A comprehensive technical white paper detailing the plan to move Earth 
                        and Moon to a new star system, preserving 10 billion people and Earth's 
                        entire biosphere across interstellar space.
                    </div>
                    <div class="stats">
                        <div class="stat">
                            <span class="stat-value">${documents.length}</span>
                            <span class="stat-label">Chapters</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">${totalWords.toLocaleString()}</span>
                            <span class="stat-label">Words</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">${totalPages}</span>
                            <span class="stat-label">Pages</span>
                        </div>
                    </div>
                    <div class="start-hint">
                        ← Select a chapter from the sidebar to begin
                    </div>
                </div>
            `;
            
            document.getElementById('mobileTitle').textContent = 'Aethelgard Protocol';
        }

        // Load and render a document
        function loadDocument(file) {
            currentDoc = file;
            
            // Update active state
            document.querySelectorAll('.nav-item').forEach(item => {
                if (item.getAttribute('data-file') === file) {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });

            // Get document info
            const doc = documents.find(d => d.file === file);
            const content = EMBEDDED_CONTENT[file] || '# Document Not Found';
            const words = wordCounts[file] || 0;

            // Render markdown
            const htmlContent = marked.parse(content);

            // Display
            document.getElementById('content').innerHTML = `
                <div class="doc-header">
                    <div class="doc-title">${doc.icon} ${doc.title}</div>
                    <div class="doc-meta">
                        <div class="meta-item">
                            <span>📁</span>
                            <span>${doc.section}</span>
                        </div>
                        <div class="meta-item">
                            <span>📊</span>
                            <span>${words.toLocaleString()} words • ~${Math.round(words/250)} pages</span>
                        </div>
                    </div>
                </div>
                <div class="markdown-content">
                    ${htmlContent}
                </div>
            `;

            // Update mobile title
            document.getElementById('mobileTitle').textContent = doc.title;

            // Scroll to top
            document.querySelector('.content').scrollTop = 0;
        }

        // Initialize
        buildNavigation();
        showWelcome();
    </script>
</body>
</html>
"""
    
    return html_template

def main():
    print("Building self-contained static HTML...")
    print("=" * 60)
    
    # Load content
    content_map = load_markdown_content()
    
    print("=" * 60)
    print(f"Loaded {len(content_map)} documents")
    
    # Generate HTML
    html = generate_html(content_map)
    
    # Write to output file (in project root)
    output_path = Path(__file__).parent.parent / 'index.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    # Get file size
    size_kb = output_path.stat().st_size / 1024
    
    print(f"✓ Generated {output_path}")
    print(f"  File size: {size_kb:.1f} KB")
    print()
    print("You can now open index.html directly in any browser!")
    print("No CORS issues - works from file:// protocol.")

if __name__ == '__main__':
    main()
