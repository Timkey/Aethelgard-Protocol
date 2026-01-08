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
    {'file': 'docs/19_Chapter_18.md', 'title': 'Ch 18: Phase Zero (2026-2150+)', 'section': 'Part 4: Implementation Roadmap', 'icon': '🚀'},
    {'file': 'docs/20_Chapter_19.md', 'title': 'Ch 19: Phase One (2150-10,000+)', 'section': 'Part 4: Implementation Roadmap', 'icon': '🏗️'},
    {'file': 'docs/21_Chapter_20.md', 'title': 'Ch 20: Phase Two (10K-100M Years)', 'section': 'Part 4: Implementation Roadmap', 'icon': '🌑'},
    {'file': 'docs/22_Chapter_21.md', 'title': 'Ch 21: Phase Three (100M-500M Years)', 'section': 'Part 4: Implementation Roadmap', 'icon': '🌌'},
    {'file': 'docs/23_Chapter_22.md', 'title': 'Ch 22: Phase Four (500M-600M Years)', 'section': 'Part 4: Implementation Roadmap', 'icon': '🏡'},
    {'file': 'docs/24_Appendix_A_Constants.md', 'title': 'Appendix A: Technical Constants', 'section': 'Part 5: Appendices', 'icon': '📐'},
    {'file': 'docs/25_Appendix_B_Math.md', 'title': 'Appendix B: Mathematical Proofs', 'section': 'Part 5: Appendices', 'icon': '📊'},
    {'file': 'docs/27_Appendix_C_Statistics.md', 'title': 'Appendix C: Statistical Analysis', 'section': 'Part 5: Appendices', 'icon': '📈'},
    {'file': 'docs/26_Conclusion.md', 'title': 'Conclusion: Species-Level Commitment', 'section': 'Conclusion', 'icon': '🌟'}
]

def escape_js_string(text):
    """Escape text for embedding in JavaScript string"""
    return text.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

def load_welcome_stats():
    """Load statistics from metadata/welcome_stats.json"""
    base_path = Path(__file__).parent.parent
    stats_path = base_path / 'metadata' / 'welcome_stats.json'
    
    try:
        with open(stats_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"✗ Stats file not found: {stats_path}")
        return None

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

def generate_html(content_map, stats=None):
    """Generate the complete HTML with embedded content"""
    
    # Embed stats if available
    stats_js = ""
    if stats:
        stats_js = f"const WELCOME_STATS = {json.dumps(stats, indent=2)};\n\n"
    
    # Convert to JavaScript object
    js_content = stats_js + "const EMBEDDED_CONTENT = {\n"
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
            margin-top: 40px;
            padding: 20px;
            background: rgba(74, 144, 226, 0.1);
            border-left: 4px solid #4a90e2;
            border-radius: 8px;
            color: #a0c0e8;
            font-size: 15px;
        }

        /* Welcome Cards */
        .welcome-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 32px 0;
        }

        .welcome-card {
            background: #141b2d;
            border: 1px solid #2a3f5f;
            border-radius: 12px;
            padding: 24px;
            transition: all 0.3s ease;
        }

        .welcome-card:hover {
            border-color: #4a90e2;
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.2);
            transform: translateY(-2px);
        }

        .welcome-card-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
        }

        .welcome-card-icon {
            font-size: 28px;
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(74, 144, 226, 0.1);
            border-radius: 10px;
        }

        .welcome-card-title {
            font-size: 18px;
            font-weight: 600;
            color: #fff;
        }

        .welcome-card-content {
            color: #c0c0c0;
            font-size: 14px;
            line-height: 1.6;
        }

        .welcome-card-link {
            display: inline-block;
            margin-top: 12px;
            padding: 10px 20px;
            background: rgba(74, 144, 226, 0.15);
            color: #4a90e2;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.2s;
        }

        .welcome-card-link:hover {
            background: rgba(74, 144, 226, 0.25);
            transform: translateX(4px);
        }

        .card-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-top: 16px;
        }

        .card-stat {
            text-align: center;
            padding: 12px;
            background: rgba(74, 144, 226, 0.05);
            border-radius: 8px;
        }

        .card-stat-value {
            display: block;
            font-size: 24px;
            font-weight: 700;
            color: #4a90e2;
        }

        .card-stat-label {
            display: block;
            font-size: 11px;
            color: #8899aa;
            text-transform: uppercase;
            margin-top: 4px;
        }

        .card-actions {
            display: flex;
            gap: 8px;
            margin-top: 12px;
            flex-wrap: wrap;
        }

        .card-btn {
            padding: 8px 16px;
            font-size: 13px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 500;
        }

        .card-btn-primary {
            background: #4a90e2;
            color: white;
        }

        .card-btn-primary:hover {
            background: #357abd;
        }

        .card-btn-secondary {
            background: #2a3f5f;
            color: #e0e0e0;
        }

        .card-btn-secondary:hover {
            background: #3a4f6f;
        }

        .card-btn-danger {
            background: #dc3545;
            color: white;
        }

        .card-btn-danger:hover {
            background: #c82333;
        }

        .card-note {
            font-size: 12px;
            color: #6b8caf;
            margin-top: 12px;
            padding: 8px 12px;
            background: rgba(107, 140, 175, 0.1);
            border-radius: 6px;
        }

        @media (max-width: 768px) {
            .welcome-cards {
                grid-template-columns: 1fr;
            }
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

        /* Feedback System */
        .note-button {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: #4a90e2;
            color: white;
            border: none;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.4);
            transition: all 0.3s ease;
            z-index: 900;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .note-button:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(74, 144, 226, 0.6);
            background: #357abd;
        }

        .feedback-link {
            display: inline-block;
            margin: 8px 0;
            padding: 8px 16px;
            background: rgba(74, 144, 226, 0.1);
            border-radius: 6px;
            transition: all 0.2s;
        }

        .feedback-link:hover {
            background: rgba(74, 144, 226, 0.2);
        }

        .note-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.85);
            z-index: 10000;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .note-modal.active {
            display: flex;
        }

        .note-modal-content {
            background: #141b2d;
            border: 2px solid #2a3f5f;
            border-radius: 12px;
            padding: 24px;
            max-width: 700px;
            width: 100%;
            max-height: 85vh;
            overflow-y: auto;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        }

        .note-modal-content h3 {
            margin: 0 0 16px 0;
            color: #4a90e2;
            font-size: 20px;
        }

        .note-textarea {
            width: 100%;
            min-height: 120px;
            padding: 12px;
            background: #0f1419;
            border: 1px solid #2a3f5f;
            border-radius: 6px;
            color: #e0e0e0;
            font-family: inherit;
            font-size: 14px;
            line-height: 1.6;
            resize: vertical;
            margin-bottom: 16px;
        }

        .note-textarea:focus {
            outline: none;
            border-color: #4a90e2;
        }

        .existing-notes {
            margin: 20px 0;
            padding: 16px;
            background: #0f1419;
            border: 1px solid #2a3f5f;
            border-radius: 8px;
        }

        .existing-notes h4 {
            margin: 0 0 12px 0;
            color: #a0a0a0;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .note-item {
            background: #06090f;
            border: 1px solid #1e2940;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 8px;
        }

        .note-item-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .note-item-date {
            font-size: 11px;
            color: #6b8caf;
        }

        .note-item-text {
            color: #c0c0c0;
            font-size: 13px;
            line-height: 1.5;
            white-space: pre-wrap;
        }

        .note-buttons {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .note-btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 500;
        }

        .note-btn-primary {
            background: #4a90e2;
            color: white;
        }

        .note-btn-primary:hover {
            background: #357abd;
        }

        .note-btn-secondary {
            background: #2a3f5f;
            color: #e0e0e0;
        }

        .note-btn-secondary:hover {
            background: #3a4f6f;
        }

        .note-btn-danger {
            background: #dc3545;
            color: white;
            font-size: 13px;
            padding: 6px 12px;
        }

        .note-btn-danger:hover {
            background: #c82333;
        }

        .note-btn-small {
            font-size: 12px;
            padding: 6px 12px;
        }

        @media (max-width: 768px) {
            .note-button {
                bottom: 16px;
                right: 16px;
                width: 48px;
                height: 48px;
                font-size: 20px;
            }

            .note-modal-content {
                max-height: 90vh;
                padding: 20px;
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
            <!-- Floating Note Button -->
            <button class="note-button" onclick="addNoteToCurrentSection()" title="Add note for this section">
                📝
            </button>

            <div class="content-inner" id="content">
                <div class="welcome">
                    <h1>Aethelgard Protocol</h1>
                    <div class="subtitle">A 5,000-Year Journey to Save Humanity</div>
                    <div class="description">
                        A comprehensive technical white paper detailing the plan to move Earth 
                        and Moon to a new star system, preserving 10 billion people and Earth's 
                        entire biosphere across interstellar space.
                    </div>

                    <!-- Cards Layout -->
                    <div class="welcome-cards">
                        <!-- Document Stats + Analytics Card -->
                        <div class="welcome-card">
                            <div class="welcome-card-header">
                                <div class="welcome-card-icon">📊</div>
                                <div class="welcome-card-title">Document Overview</div>
                            </div>
                            <div class="welcome-card-content">
                                <div class="card-stats">
                                    <div class="card-stat">
                                        <span class="card-stat-value" id="total-chapters">—</span>
                                        <span class="card-stat-label">Chapters</span>
                                    </div>
                                    <div class="card-stat">
                                        <span class="card-stat-value" id="total-words">—</span>
                                        <span class="card-stat-label">Words</span>
                                    </div>
                                    <div class="card-stat">
                                        <span class="card-stat-value" id="total-pages">—</span>
                                        <span class="card-stat-label">Pages</span>
                                    </div>
                                    <div class="card-stat">
                                        <span class="card-stat-value" id="total-time">—</span>
                                        <span class="card-stat-label">Read Time</span>
                                    </div>
                                </div>
                                <a href="analytics.html" class="welcome-card-link">📈 View Analytics Dashboard →</a>
                            </div>
                        </div>

                        <!-- Feedback & Notes Card -->
                        <div class="welcome-card">
                            <div class="welcome-card-header">
                                <div class="welcome-card-icon">📝</div>
                                <div class="welcome-card-title">Feedback & Notes</div>
                            </div>
                            <div class="welcome-card-content">
                                <p style="margin-bottom: 12px;">Add notes while reading using the 📝 button (bottom-right). Notes are stored locally and can be exported.</p>
                                <a href="feedback.html" id="feedbackLink" class="welcome-card-link">📋 Review & Export Notes (0) →</a>
                                <div class="card-actions">
                                    <button onclick="checkStorageUsage()" class="card-btn card-btn-secondary">🔍 Check Storage</button>
                                    <button onclick="clearAllStorage()" class="card-btn card-btn-danger">🗑️ Clear Notes</button>
                                </div>
                                <div class="card-note">⚠️ If notes won't save, other projects may be using localStorage</div>
                            </div>
                        </div>

                        <!-- GitHub Card -->
                        <div class="welcome-card">
                            <div class="welcome-card-header">
                                <div class="welcome-card-icon">📦</div>
                                <div class="welcome-card-title">Open Source</div>
                            </div>
                            <div class="welcome-card-content">
                                <p style="margin-bottom: 12px;">This project is open source and available on GitHub. Contributions, issues, and feedback are welcome.</p>
                                <a href="https://github.com/timkey/Aethelgard-Protocol" target="_blank" rel="noopener noreferrer" class="welcome-card-link">⭐ View on GitHub →</a>
                            </div>
                        </div>

                        <!-- AI Citations Card -->
                        <div class="welcome-card">
                            <div class="welcome-card-header">
                                <div class="welcome-card-icon">🤖</div>
                                <div class="welcome-card-title">AI-Assisted Content</div>
                            </div>
                            <div class="welcome-card-content">
                                <p style="margin-bottom: 12px;">
                                    <strong>🧬 Origin:</strong> Framework generated by Google Gemini AI
                                </p>
                                <p style="margin-bottom: 12px;">
                                    <strong>🏗️ Structure:</strong> Document architecture & tooling by GitHub Copilot (Claude Sonnet 4.5)
                                </p>
                                <p style="margin-bottom: 12px; color: #a0a0a0; font-size: 13px;">
                                    This document was created with assistance from AI language models for research, analysis, and technical writing. All technical claims are based on established physics and engineering principles.
                                </p>
                                <a href="https://gemini.google.com/share/70d6ae8852cb" target="_blank" rel="noopener noreferrer" class="welcome-card-link">🔗 View Original Gemini Session →</a>
                            </div>
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
            { file: 'docs/19_Chapter_18.md', title: 'Ch 18: Phase Zero (2026-2150+)', section: 'Part 4: Implementation Roadmap', icon: '🚀' },
            { file: 'docs/20_Chapter_19.md', title: 'Ch 19: Phase One (2150-10,000+)', section: 'Part 4: Implementation Roadmap', icon: '🏗️' },
            { file: 'docs/21_Chapter_20.md', title: 'Ch 20: Phase Two (10K-100M Years)', section: 'Part 4: Implementation Roadmap', icon: '🌑' },
            { file: 'docs/22_Chapter_21.md', title: 'Ch 21: Phase Three (100M-500M Years)', section: 'Part 4: Implementation Roadmap', icon: '🌌' },
            { file: 'docs/23_Chapter_22.md', title: 'Ch 22: Phase Four (500M-600M Years)', section: 'Part 4: Implementation Roadmap', icon: '🏡' },
            { file: 'docs/24_Appendix_A_Constants.md', title: 'Appendix A: Technical Constants', section: 'Part 5: Appendices', icon: '📐' },
            { file: 'docs/25_Appendix_B_Math.md', title: 'Appendix B: Mathematical Proofs', section: 'Part 5: Appendices', icon: '📊' },
            { file: 'docs/27_Appendix_C_Statistics.md', title: 'Appendix C: Statistical Analysis', section: 'Part 5: Appendices', icon: '📈' },
            { file: 'docs/26_Conclusion.md', title: 'Conclusion: Species-Level Commitment', section: 'Conclusion', icon: '🌟' }
        ];

        let currentDoc = null;
        let wordCounts = {};
        let currentNoteKey = null;

        // Debug: Check localStorage usage
        function checkStorageUsage() {
            let total = 0;
            const items = {};
            for (let key in localStorage) {
                if (localStorage.hasOwnProperty(key)) {
                    const size = localStorage[key].length;
                    total += size;
                    items[key] = Math.round(size / 1024) + 'KB';
                }
            }
            console.log('=== localStorage Usage ===');
            console.log('Total:', Math.round(total / 1024) + 'KB');
            console.log('Items:', items);
            console.log('Limit: ~5-10MB depending on browser');
            
            // Alert if other projects are using space
            const otherProjects = Object.keys(items).filter(k => !k.includes('aethelgard'));
            if (otherProjects.length > 0) {
                const otherSize = otherProjects.reduce((sum, k) => sum + parseInt(items[k]), 0);
                alert('⚠️ Storage Alert\\n\\nOther projects are using ' + otherSize + 'KB of localStorage!\\n\\nItems: ' + otherProjects.join(', ') + '\\n\\nYou may need to clear storage from those projects or use a different browser/profile for Aethelgard notes.');
            }
            
            return items;
        }

        function clearAllStorage() {
            const hasOtherData = Object.keys(localStorage).some(k => !k.includes('aethelgard'));
            
            if (hasOtherData) {
                const choice = confirm('OTHER PROJECTS DETECTED!\\n\\nClick OK to clear ONLY Aethelgard notes\\nClick Cancel to clear ALL localStorage (including other projects)');
                
                if (choice) {
                    // Clear only aethelgard notes
                    localStorage.removeItem('aethelgard_notes');
                    alert('Aethelgard notes cleared. Other projects preserved.\\n\\nRefreshing page...');
                } else {
                    // Clear everything
                    if (confirm('Are you SURE? This will delete data from ALL projects in localStorage!')) {
                        localStorage.clear();
                        alert('All localStorage cleared.\\n\\nRefreshing page...');
                    } else {
                        return;
                    }
                }
            } else {
                if (confirm('Clear Aethelgard notes?')) {
                    localStorage.removeItem('aethelgard_notes');
                    alert('Notes cleared.\\n\\nRefreshing page...');
                }
            }
            
            location.reload();
        }

        // Feedback Notes System with compression
        function getNotes() {
            try {
                const notes = localStorage.getItem('aethelgard_notes');
                if (!notes) return {};
                
                const parsed = JSON.parse(notes);
                
                // Migrate old format to new compressed format
                let needsMigration = false;
                Object.keys(parsed).forEach(key => {
                    if (parsed[key].note !== undefined) {
                        needsMigration = true;
                        parsed[key] = {
                            n: parsed[key].note,
                            d: parsed[key].document,
                            t: parsed[key].title,
                            ts: parsed[key].timestamp
                        };
                    }
                });
                
                if (needsMigration) {
                    console.log('Migrating notes to compressed format');
                    localStorage.setItem('aethelgard_notes', JSON.stringify(parsed));
                }
                
                return parsed;
            } catch (e) {
                console.error('Error loading notes:', e);
                return {};
            }
        }

        function saveNotes(notes) {
            try {
                // Keep only last 30 notes to prevent quota issues
                const noteKeys = Object.keys(notes);
                if (noteKeys.length > 30) {
                    const sorted = noteKeys
                        .map(k => ({ key: k, time: new Date(notes[k].ts || notes[k].timestamp || 0) }))
                        .sort((a, b) => b.time - a.time)
                        .slice(0, 30);
                    
                    const trimmed = {};
                    sorted.forEach(item => {
                        trimmed[item.key] = notes[item.key];
                    });
                    notes = trimmed;
                    console.log('Auto-trimmed to 30 most recent notes');
                }

                localStorage.setItem('aethelgard_notes', JSON.stringify(notes));
                updateNoteCounts();
            } catch (e) {
                if (e.name === 'QuotaExceededError') {
                    console.error('Storage usage:', checkStorageUsage());
                    alert('Storage limit reached!\\n\\nClick "Check Storage" on home page to see what\\'s using space.\\nYou may need to clear storage and start fresh.');
                } else {
                    console.error('Error saving notes:', e);
                    alert('Failed to save note: ' + e.message);
                }
            }
        }

        function getNoteCount() {
            return Object.keys(getNotes()).length;
        }

        function updateNoteCounts() {
            const count = getNoteCount();
            const link = document.getElementById('feedbackLink');
            if (link) {
                link.textContent = `� Review & Export Notes (${count})`;
            }
        }

        function addNoteToCurrentSection() {
            if (!currentDoc) {
                alert('Please select a document first');
                return;
            }

            const doc = documents.find(d => d.file === currentDoc);
            currentNoteKey = `${doc.file}:main`;
            
            const modal = document.getElementById('noteModal');
            const header = document.getElementById('noteModalHeader');
            const meta = document.getElementById('noteModalMeta');
            const textarea = document.getElementById('noteTextarea');
            const existingNotesDiv = document.getElementById('existingNotes');

            header.textContent = '📝 Notes';
            meta.textContent = `${doc.title}`;
            
            const notes = getNotes();
            const currentNote = notes[currentNoteKey];
            
            // Show existing notes for this chapter
            const chapterNotes = Object.entries(notes).filter(([key]) => key.startsWith(doc.file));
            if (chapterNotes.length > 0) {
                existingNotesDiv.style.display = 'block';
                existingNotesDiv.innerHTML = `
                    <h4>Existing Notes (${chapterNotes.length})</h4>
                    ${chapterNotes.map(([key, note]) => {
                        const noteText = note.n || note.note || '';
                        const timestamp = note.ts || note.timestamp;
                        const date = new Date(timestamp);
                        return `
                            <div class="note-item">
                                <div class="note-item-header">
                                    <span class="note-item-date">${date.toLocaleDateString()} ${date.toLocaleTimeString()}</span>
                                    <button class="note-btn note-btn-danger note-btn-small" onclick="deleteNoteById('${key.replace(/'/g, "\\'")}')">🗑️</button>
                                </div>
                                <div class="note-item-text">${noteText}</div>
                            </div>
                        `;
                    }).join('')}
                `;
            } else {
                existingNotesDiv.style.display = 'none';
            }
            
            // Set textarea to blank for new note
            textarea.value = '';
            textarea.placeholder = 'Add a new note for this chapter...';

            modal.classList.add('active');
            textarea.focus();
        }

        function saveNote() {
            const textarea = document.getElementById('noteTextarea');
            let noteText = textarea.value.trim();
            
            if (!noteText) {
                alert('Please enter a note');
                return;
            }

            // Limit note length to prevent quota issues
            const MAX_NOTE_LENGTH = 1000;
            if (noteText.length > MAX_NOTE_LENGTH) {
                if (!confirm(`Note is ${noteText.length} characters. Truncate to ${MAX_NOTE_LENGTH} characters?`)) {
                    return;
                }
                noteText = noteText.substring(0, MAX_NOTE_LENGTH) + '...';
            }

            const notes = getNotes();
            const doc = documents.find(d => d.file === currentDoc);
            
            // Use shorter keys and minimal data
            const timestamp = new Date().toISOString();
            notes[currentNoteKey] = {
                n: noteText,  // shortened key
                d: doc.file,  // shortened key
                t: doc.title, // shortened key
                ts: timestamp // shortened key
            };

            saveNotes(notes);
            closeNoteModal();
            
            // Show confirmation
            const btn = document.querySelector('.note-button');
            const originalText = btn.textContent;
            btn.textContent = '✓';
            setTimeout(() => btn.textContent = originalText, 1000);
        }

        function deleteNote() {
            if (!confirm('Delete this note?')) return;
            
            const notes = getNotes();
            delete notes[currentNoteKey];
            saveNotes(notes);
            closeNoteModal();
        }

        function deleteNoteById(noteKey) {
            if (!confirm('Delete this note?')) return;
            
            const notes = getNotes();
            delete notes[noteKey];
            saveNotes(notes);
            
            // Refresh modal to show updated list
            addNoteToCurrentSection();
        }

        function closeNoteModal() {
            document.getElementById('noteModal').classList.remove('active');
            currentNoteKey = null;
        }

        function updateCharCount() {
            const textarea = document.getElementById('noteTextarea');
            const charCount = document.getElementById('charCount');
            if (textarea && charCount) {
                const len = textarea.value.length;
                charCount.textContent = len;
                charCount.style.color = len > 1000 ? '#dc3545' : len > 800 ? '#ffc107' : '#a0a0a0';
            }
        }

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

        // Use stats from welcome_stats.json if available, otherwise calculate
        if (typeof WELCOME_STATS !== 'undefined') {
            // Stats are pre-calculated and accurate
            wordCounts = {}; // Will use WELCOME_STATS directly
        } else {
            // Fallback: Calculate word counts from content (less accurate)
            documents.forEach(doc => {
                const content = EMBEDDED_CONTENT[doc.file] || '';
                wordCounts[doc.file] = content.split(/\\s+/).filter(w => w.length > 0).length;
            });
        }

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

            // Build HTML with Home button at top
            let html = `
                <div class="nav-item home-nav" id="homeNav" style="border-bottom: 2px solid #2c3e50; margin-bottom: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                    <span class="icon">🏠</span>
                    <span class="title" style="font-weight: 600;">Home</span>
                    <span class="word-count"></span>
                </div>
            `;
            
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

            // Add click handler for Home button
            document.getElementById('homeNav').addEventListener('click', () => {
                showWelcome();
                sidebar.classList.remove('open');
                sidebarOverlay.classList.remove('show');
            });

            // Add click handlers for document navigation
            document.querySelectorAll('.nav-item:not(.home-nav)').forEach(item => {
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
            
            // Use accurate stats from WELCOME_STATS if available
            const totalWords = (typeof WELCOME_STATS !== 'undefined') 
                ? WELCOME_STATS.total_words 
                : Object.values(wordCounts).reduce((a, b) => a + b, 0);
            const totalPages = Math.round(totalWords / 250);
            const readingTime = (typeof WELCOME_STATS !== 'undefined') 
                ? WELCOME_STATS.reading_time_hours 
                : Math.round(totalWords / 200 / 60);
            
            document.getElementById('content').innerHTML = `
                <div class="welcome">
                    <h1>Aethelgard Protocol</h1>
                    <div class="subtitle">A 5,000-Year Journey to Save Humanity</div>
                    <div class="description">
                        A comprehensive technical white paper detailing the plan to move Earth 
                        and Moon to a new star system, preserving 10 billion people and Earth's 
                        entire biosphere across interstellar space.
                    </div>

                    <!-- Cards Layout -->
                    <div class="welcome-cards">
                        <!-- Document Stats + Analytics Card -->
                        <div class="welcome-card">
                            <div class="welcome-card-header">
                                <div class="welcome-card-icon">📊</div>
                                <div class="welcome-card-title">Document Overview</div>
                            </div>
                            <div class="welcome-card-content">
                                <div class="card-stats">
                                    <div class="card-stat">
                                        <span class="card-stat-value">${documents.length}</span>
                                        <span class="card-stat-label">Chapters</span>
                                    </div>
                                    <div class="card-stat">
                                        <span class="card-stat-value">${totalWords.toLocaleString()}</span>
                                        <span class="card-stat-label">Words</span>
                                    </div>
                                    <div class="card-stat">
                                        <span class="card-stat-value">${totalPages}</span>
                                        <span class="card-stat-label">Pages</span>
                                    </div>
                                    <div class="card-stat">
                                        <span class="card-stat-value">~${readingTime} hrs</span>
                                        <span class="card-stat-label">Read Time</span>
                                    </div>
                                </div>
                                <a href="analytics.html" class="welcome-card-link">📈 View Analytics Dashboard →</a>
                            </div>
                        </div>

                        <!-- Feedback & Notes Card -->
                        <div class="welcome-card">
                            <div class="welcome-card-header">
                                <div class="welcome-card-icon">📝</div>
                                <div class="welcome-card-title">Feedback & Notes</div>
                            </div>
                            <div class="welcome-card-content">
                                <p style="margin-bottom: 12px;">Add notes while reading using the 📝 button (bottom-right). Notes are stored locally and can be exported.</p>
                                <a href="feedback.html" id="feedbackLink" class="welcome-card-link">📋 Review & Export Notes (${getNoteCount()}) →</a>
                                <div class="card-actions">
                                    <button onclick="checkStorageUsage()" class="card-btn card-btn-secondary">🔍 Check Storage</button>
                                    <button onclick="clearAllStorage()" class="card-btn card-btn-danger">🗑️ Clear Notes</button>
                                </div>
                                <div class="card-note">⚠️ If notes won't save, other projects may be using localStorage</div>
                            </div>
                        </div>

                        <!-- GitHub Card -->
                        <div class="welcome-card">
                            <div class="welcome-card-header">
                                <div class="welcome-card-icon">📦</div>
                                <div class="welcome-card-title">Open Source</div>
                            </div>
                            <div class="welcome-card-content">
                                <p style="margin-bottom: 12px;">This project is open source and available on GitHub. Contributions, issues, and feedback are welcome.</p>
                                <a href="https://github.com/timkey/Aethelgard-Protocol" target="_blank" rel="noopener noreferrer" class="welcome-card-link">⭐ View on GitHub →</a>
                            </div>
                        </div>

                        <!-- AI Citations Card -->
                        <div class="welcome-card">
                            <div class="welcome-card-header">
                                <div class="welcome-card-icon">🤖</div>
                                <div class="welcome-card-title">AI-Assisted Content</div>
                            </div>
                            <div class="welcome-card-content">
                                <p style="margin-bottom: 12px;">
                                    <strong>🧬 Origin:</strong> Framework generated by Google Gemini AI
                                </p>
                                <p style="margin-bottom: 12px;">
                                    <strong>🏗️ Structure:</strong> Document architecture & tooling by GitHub Copilot (Claude Sonnet 4.5)
                                </p>
                                <p style="margin-bottom: 12px; color: #a0a0a0; font-size: 13px;">
                                    This document was created with assistance from AI language models for research, analysis, and technical writing. All technical claims are based on established physics and engineering principles.
                                </p>
                                <a href="https://gemini.google.com/share/70d6ae8852cb" target="_blank" rel="noopener noreferrer" class="welcome-card-link">🔗 View Original Gemini Session →</a>
                            </div>
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
            
            // Count words more accurately (strip markdown syntax)
            const plainText = content
                .replace(/^#{1,6}\s+/gm, '')  // Remove headers
                .replace(/\*\*(.+?)\*\*/g, '$1')  // Remove bold
                .replace(/\*(.+?)\*/g, '$1')  // Remove italic
                .replace(/\[(.+?)\]\(.+?\)/g, '$1')  // Remove links
                .replace(/`(.+?)`/g, '$1')  // Remove inline code
                .replace(/^[-*+]\s+/gm, '')  // Remove list markers
                .replace(/^>\s+/gm, '')  // Remove blockquotes
                .replace(/^\s*\|.*\|\s*$/gm, '')  // Remove tables
                .replace(/---+/g, '');  // Remove horizontal rules
            const words = plainText.split(/\s+/).filter(w => w.length > 0).length;

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
        updateNoteCounts();
    </script>

    <!-- Note Modal -->
    <div class="note-modal" id="noteModal">
        <div class="note-modal-content">
            <h3 id="noteModalHeader">📝 Notes</h3>
            <div id="noteModalMeta" style="font-size: 14px; color: #a0a0a0; margin-bottom: 12px;"></div>
            
            <!-- Existing notes for this chapter -->
            <div id="existingNotes" class="existing-notes" style="display:none;"></div>
            
            <!-- New note input -->
            <textarea id="noteTextarea" class="note-textarea" placeholder="Add a new note for this chapter..." oninput="updateCharCount()"></textarea>
            <div style="font-size: 12px; color: #a0a0a0; margin-bottom: 12px;">
                <span id="charCount">0</span>/1000 characters
                <span style="margin-left: 16px; color: #6b8caf;">Max 30 notes stored (auto-trimmed by date)</span>
            </div>
            
            <div class="note-buttons">
                <button class="note-btn note-btn-primary" onclick="saveNote()">💾 Save Note</button>
                <button class="note-btn note-btn-secondary" onclick="closeNoteModal()">Cancel</button>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    return html_template

def main():
    print("Building self-contained static HTML...")
    print("=" * 60)
    
    # Load stats
    stats = load_welcome_stats()
    if stats:
        print(f"✓ Loaded stats: {stats['total_words']:,} words, {stats['total_sections']} sections")
    
    # Load content
    content_map = load_markdown_content()
    
    print("=" * 60)
    print(f"Loaded {len(content_map)} documents")
    
    # Generate HTML
    html = generate_html(content_map, stats)
    
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
