#!/usr/bin/env python3
"""
Build a self-contained analytics page visualizing document structure,
semantics, timelines, dependencies, and quality metrics.
"""

import json
from pathlib import Path

def load_all_stats():
    """Load all available statistics and metadata"""
    base_path = Path(__file__).parent.parent
    stats = {}
    
    # Load welcome stats
    try:
        with open(base_path / 'metadata' / 'welcome_stats.json', 'r') as f:
            stats['welcome'] = json.load(f)
    except FileNotFoundError:
        stats['welcome'] = None
    
    # Load semantic graph
    try:
        with open(base_path / 'reports' / 'semantic_graph.json', 'r') as f:
            stats['semantic'] = json.load(f)
    except FileNotFoundError:
        stats['semantic'] = None
    
    # Load dependencies
    try:
        with open(base_path / 'reports' / 'dependencies.json', 'r') as f:
            stats['dependencies'] = json.load(f)
    except FileNotFoundError:
        stats['dependencies'] = None
    
    # Load timeline data
    try:
        with open(base_path / 'metadata' / 'timeline.json', 'r') as f:
            stats['timeline'] = json.load(f)
    except FileNotFoundError:
        stats['timeline'] = None
    
    # Load vector stats
    try:
        with open(base_path / 'metadata' / 'vector_stats.json', 'r') as f:
            stats['vector'] = json.load(f)
    except FileNotFoundError:
        stats['vector'] = None
    
    return stats

def escape_js_string(text):
    """Escape text for embedding in JavaScript"""
    return text.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

def generate_analytics_html(stats):
    """Generate the complete analytics HTML"""
    
    # Prepare stats as JavaScript
    stats_json = json.dumps(stats, indent=2)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aethelgard Protocol - Analytics</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/d3@7.8.5/dist/d3.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #0a0e27;
            color: #e0e0e0;
            line-height: 1.6;
        }}

        .header {{
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
        }}

        .header-title {{
            font-size: 20px;
            font-weight: 600;
            color: #4a90e2;
        }}

        .header-nav {{
            display: flex;
            gap: 16px;
        }}

        .nav-link {{
            color: #e0e0e0;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 6px;
            transition: all 0.2s;
            background: rgba(74, 144, 226, 0.1);
        }}

        .nav-link:hover {{
            background: rgba(74, 144, 226, 0.2);
            color: #4a90e2;
        }}

        .container {{
            margin-top: 64px;
            padding: 24px;
            max-width: 1800px;
            margin-left: auto;
            margin-right: auto;
        }}

        .section {{
            background: #141b2d;
            border: 1px solid #2a3f5f;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }}

        .section-title {{
            font-size: 24px;
            font-weight: 600;
            color: #4a90e2;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .section-subtitle {{
            font-size: 14px;
            color: #a0a0a0;
            margin-bottom: 20px;
        }}

        .grid {{
            display: grid;
            gap: 24px;
        }}

        .grid-2 {{
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
        }}

        .grid-3 {{
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        }}

        .chart-container {{
            background: #0f1419;
            border-radius: 8px;
            padding: 20px;
            height: 400px;
            position: relative;
        }}

        .chart-title {{
            font-size: 16px;
            font-weight: 600;
            color: #e0e0e0;
            margin-bottom: 16px;
        }}

        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}

        .stat-card {{
            background: rgba(74, 144, 226, 0.1);
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #4a90e2;
        }}

        .stat-value {{
            font-size: 32px;
            font-weight: 700;
            color: #4a90e2;
            margin-bottom: 4px;
        }}

        .stat-label {{
            font-size: 14px;
            color: #a0a0a0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .search-container {{
            background: #0f1419;
            padding: 24px;
            border-radius: 8px;
            margin-bottom: 16px;
        }}

        .search-input {{
            width: 100%;
            padding: 12px 16px;
            background: #1a1f2e;
            border: 1px solid #2a3f5f;
            border-radius: 6px;
            color: #e0e0e0;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }}

        .search-input:focus {{
            border-color: #4a90e2;
        }}

        .search-results {{
            margin-top: 16px;
            max-height: 500px;
            overflow-y: auto;
        }}

        .result-item {{
            background: #1a1f2e;
            padding: 16px;
            border-radius: 6px;
            margin-bottom: 12px;
            border-left: 3px solid #4a90e2;
        }}

        .result-score {{
            display: inline-block;
            background: rgba(74, 144, 226, 0.2);
            color: #4a90e2;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            margin-right: 8px;
        }}

        .result-doc {{
            color: #a0a0a0;
            font-size: 12px;
            margin-bottom: 8px;
        }}

        .result-content {{
            color: #e0e0e0;
            line-height: 1.6;
        }}

        .network-canvas {{
            width: 100%;
            height: 500px;
            background: #0f1419;
            border-radius: 8px;
        }}

        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin-top: 12px;
            font-size: 12px;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
        }}

        .accordion {{
            margin-top: 16px;
        }}

        .accordion-item {{
            background: #0f1419;
            border: 1px solid #2a3f5f;
            border-radius: 8px;
            margin-bottom: 12px;
            overflow: hidden;
        }}

        .accordion-header {{
            padding: 16px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
            transition: background 0.2s;
        }}

        .accordion-header:hover {{
            background: rgba(74, 144, 226, 0.05);
        }}

        .accordion-title {{
            font-weight: 600;
            color: #e0e0e0;
            font-size: 15px;
        }}

        .accordion-icon {{
            color: #4a90e2;
            font-size: 14px;
            transition: transform 0.3s;
        }}

        .accordion-icon.open {{
            transform: rotate(180deg);
        }}

        .accordion-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }}

        .accordion-content.open {{
            max-height: 1000px;
            transition: max-height 0.5s ease-in;
        }}

        .accordion-content.default-open {{
            max-height: 1000px;
        }}

        .accordion-body {{
            padding: 0 20px 20px 20px;
        }}

        @media (max-width: 768px) {{
            .grid-2, .grid-3 {{
                grid-template-columns: 1fr;
            }}
            
            .header {{
                padding: 0 16px;
            }}
            
            .header-title {{
                font-size: 16px;
            }}
            
            .container {{
                padding: 16px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-title">🧬 Aethelgard Protocol - Document Analytics</div>
        <div class="header-nav">
            <a href="index.html" class="nav-link">← Back to Document</a>
        </div>
    </div>

    <div class="container">
        <!-- Overview Stats -->
        <div class="section">
            <div class="section-title">📊 Document Overview</div>
            <div class="stat-grid" id="overview-stats"></div>
        </div>

        <!-- Document Structure -->
        <div class="section">
            <div class="section-title">📚 Document Structure & Composition</div>
            <div class="section-subtitle">Word distribution, section density, and hierarchical organization</div>
            
            <div class="accordion">
                <div class="accordion-item">
                    <div class="accordion-header" onclick="toggleAccordion(this)">
                        <div class="accordion-title">📊 Word Distribution Charts</div>
                        <div class="accordion-icon open">▼</div>
                    </div>
                    <div class="accordion-content open default-open">
                        <div class="accordion-body">
                            <div class="grid grid-2">
                                <div class="chart-container">
                                    <div class="chart-title">Words per Chapter</div>
                                    <canvas id="wordDistChart"></canvas>
                                </div>
                                <div class="chart-container">
                                    <div class="chart-title">Content by Part</div>
                                    <canvas id="partDistChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Semantic Analysis -->
        <div class="section">
            <div class="section-title">🧠 Semantic Analysis</div>
            <div class="section-subtitle">Paragraph connections, concept frequency, and semantic clusters</div>
            
            <div class="accordion">
                <div class="accordion-item">
                    <div class="accordion-header" onclick="toggleAccordion(this)">
                        <div class="accordion-title">📈 Concept & Network Analysis</div>
                        <div class="accordion-icon open">▼</div>
                    </div>
                    <div class="accordion-content open default-open">
                        <div class="accordion-body">
                            <div class="grid grid-2">
                                <div class="chart-container">
                                    <div class="chart-title">Top Concepts</div>
                                    <canvas id="conceptChart"></canvas>
                                </div>
                                <div class="chart-container">
                                    <div class="chart-title">Semantic Network Stats</div>
                                    <canvas id="networkStatsChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="accordion-item">
                    <div class="accordion-header" onclick="toggleAccordion(this)">
                        <div class="accordion-title">🔷 Cluster Distribution</div>
                        <div class="accordion-icon">▼</div>
                    </div>
                    <div class="accordion-content">
                        <div class="accordion-body">
                            <div class="chart-container">
                                <div class="chart-title">Semantic Cluster Distribution</div>
                                <canvas id="clusterChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Timeline Analysis -->
        <div class="section">
            <div class="section-title">⏰ Timeline & Phase Analysis</div>
            <div class="section-subtitle">Temporal references and phase coverage across chapters</div>
            
            <div class="accordion">
                <div class="accordion-item">
                    <div class="accordion-header" onclick="toggleAccordion(this)">
                        <div class="accordion-title">📅 Phase Coverage & Corrections</div>
                        <div class="accordion-icon">▼</div>
                    </div>
                    <div class="accordion-content">
                        <div class="accordion-body">
                            <div class="grid grid-2">
                                <div class="chart-container">
                                    <div class="chart-title">Phase Coverage by Chapter</div>
                                    <canvas id="phaseCoverageChart"></canvas>
                                </div>
                                <div class="chart-container">
                                    <div class="chart-title">Timeline Corrections</div>
                                    <canvas id="timelineCorrectionChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Dependencies -->
        <div class="section">
            <div class="section-title">🔗 Chapter Dependencies & Interconnections</div>
            <div class="section-subtitle">Cross-references and concept flow between chapters</div>
            
            <div class="accordion">
                <div class="accordion-item">
                    <div class="accordion-header" onclick="toggleAccordion(this)">
                        <div class="accordion-title">🕸️ Reference Network & Premises</div>
                        <div class="accordion-icon">▼</div>
                    </div>
                    <div class="accordion-content">
                        <div class="accordion-body">
                            <div class="grid grid-2">
                                <div class="chart-container">
                                    <div class="chart-title">Cross-Reference Network</div>
                                    <canvas id="dependencyChart"></canvas>
                                </div>
                                <div class="chart-container">
                                    <div class="chart-title">Core Premises Distribution</div>
                                    <canvas id="premiseChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Interactive Search -->
        <div class="section">
            <div class="section-title">🔍 Interactive Semantic Search</div>
            <div class="section-subtitle">Enter text to find semantically similar paragraphs across the document</div>
            <div class="search-container">
                <input type="text" 
                       class="search-input" 
                       id="searchInput" 
                       placeholder="Enter text to search semantically (e.g., 'population migration strategy', 'Dyson Swarm energy', 'Oracle governance')...">
                <div class="search-results" id="searchResults"></div>
            </div>
        </div>
    </div>

    <script>
        // Accordion toggle function (must be in global scope for onclick handlers)
        function toggleAccordion(header) {{
            const content = header.nextElementSibling;
            const icon = header.querySelector('.accordion-icon');
            content.classList.toggle('open');
            icon.classList.toggle('open');
        }}

        // Embedded stats data
        const STATS = {stats_json};

        // Initialize charts
        Chart.defaults.color = '#e0e0e0';
        Chart.defaults.borderColor = '#2a3f5f';

        // Overview Stats
        function renderOverviewStats() {{
            const container = document.getElementById('overview-stats');
            const stats = STATS.welcome || {{}};
            
            const items = [
                {{ value: stats.total_words?.toLocaleString() || '—', label: 'Total Words' }},
                {{ value: stats.total_sections || '—', label: 'Sections' }},
                {{ value: '28', label: 'Chapters' }},
                {{ value: `~${{stats.reading_time_hours || 2}} hrs`, label: 'Reading Time' }},
                {{ value: STATS.semantic?.paragraphs?.length || '—', label: 'Paragraphs' }},
                {{ value: STATS.semantic?.edges?.length || '—', label: 'Connections' }},
                {{ value: STATS.semantic?.clusters ? Object.keys(STATS.semantic.clusters).length : '—', label: 'Clusters' }},
                {{ value: STATS.dependencies?.cross_references ? Object.values(STATS.dependencies.cross_references).reduce((sum, refs) => sum + refs.length, 0) : '—', label: 'Cross-Refs' }}
            ];
            
            items.forEach(item => {{
                const card = document.createElement('div');
                card.className = 'stat-card';
                card.innerHTML = `
                    <div class="stat-value">${{item.value}}</div>
                    <div class="stat-label">${{item.label}}</div>
                `;
                container.appendChild(card);
            }});
        }}

        // Word Distribution Chart
        function renderWordDistribution() {{
            const ctx = document.getElementById('wordDistChart');
            if (!ctx) return;
            
            // Calculate word counts from document structure (hardcoded from actual counts)
            const docStats = {{
                '21_Chapter_20': 4130,
                '20_Chapter_19': 3685,
                '22_Chapter_21': 3667,
                '02_Chapter_01': 2884,
                '13_Chapter_12': 2812,
                '19_Chapter_18': 2743,
                '24_Appendix_A': 2721,
                '11_Chapter_10': 2576,
                '26_Conclusion': 2567,
                '12_Chapter_11': 2434,
                '09_Chapter_08': 2348,
                '15_Chapter_14': 2252,
                '08_Chapter_07': 2205,
                '10_Chapter_09': 2195
            }};
            
            const sortedDocs = Object.entries(docStats)
                .sort((a, b) => b[1] - a[1]);
            
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: sortedDocs.map(d => d[0]),
                    datasets: [{{
                        label: 'Words',
                        data: sortedDocs.map(d => d[1]),
                        backgroundColor: 'rgba(74, 144, 226, 0.6)',
                        borderColor: 'rgba(74, 144, 226, 1)',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }}
                    }},
                    scales: {{
                        x: {{ ticks: {{ color: '#a0a0a0' }} }},
                        y: {{ ticks: {{ color: '#a0a0a0', font: {{ size: 10 }} }} }}
                    }}
                }}
            }});
        }}

        // Part Distribution Chart
        function renderPartDistribution() {{
            const ctx = document.getElementById('partDistChart');
            if (!ctx) return;
            
            const parts = {{
                'Overview': 2,
                'Foundations': 4,
                'Technical Architecture': 8,
                'Governance & Social': 5,
                'Implementation Roadmap': 5,
                'Appendices': 3,
                'Conclusion': 1
            }};
            
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: Object.keys(parts),
                    datasets: [{{
                        data: Object.values(parts),
                        backgroundColor: [
                            'rgba(74, 144, 226, 0.8)',
                            'rgba(80, 200, 120, 0.8)',
                            'rgba(255, 159, 64, 0.8)',
                            'rgba(153, 102, 255, 0.8)',
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 206, 86, 0.8)'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'right',
                            labels: {{ color: '#e0e0e0', padding: 12 }}
                        }}
                    }}
                }}
            }});
        }}

        // Concept Frequency Chart
        function renderConceptChart() {{
            const ctx = document.getElementById('conceptChart');
            if (!ctx || !STATS.welcome?.top_concepts) return;
            
            const concepts = STATS.welcome.top_concepts.slice(0, 10);
            
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: concepts.map(c => c[0]),
                    datasets: [{{
                        label: 'Mentions',
                        data: concepts.map(c => c[1]),
                        backgroundColor: 'rgba(80, 200, 120, 0.6)',
                        borderColor: 'rgba(80, 200, 120, 1)',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }}
                    }},
                    scales: {{
                        x: {{ ticks: {{ color: '#a0a0a0' }} }},
                        y: {{ ticks: {{ color: '#a0a0a0' }} }}
                    }}
                }}
            }});
        }}

        // Network Stats Chart
        function renderNetworkStats() {{
            const ctx = document.getElementById('networkStatsChart');
            if (!ctx || !STATS.semantic) return;
            
            const data = {{
                'Paragraphs': STATS.semantic.paragraphs?.length || 0,
                'Connections': STATS.semantic.edges?.length || 0,
                'Clusters': STATS.semantic.clusters ? Object.keys(STATS.semantic.clusters).length : 0,
                'Avg Connections': Math.round((STATS.semantic.edges?.length || 0) * 2 / (STATS.semantic.paragraphs?.length || 1) * 10) / 10
            }};
            
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: Object.keys(data),
                    datasets: [{{
                        label: 'Count',
                        data: Object.values(data),
                        backgroundColor: [
                            'rgba(74, 144, 226, 0.6)',
                            'rgba(255, 159, 64, 0.6)',
                            'rgba(153, 102, 255, 0.6)',
                            'rgba(80, 200, 120, 0.6)'
                        ],
                        borderColor: [
                            'rgba(74, 144, 226, 1)',
                            'rgba(255, 159, 64, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(80, 200, 120, 1)'
                        ],
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }}
                    }},
                    scales: {{
                        y: {{ ticks: {{ color: '#a0a0a0' }} }},
                        x: {{ ticks: {{ color: '#a0a0a0' }} }}
                    }}
                }}
            }});
        }}

        // Cluster Distribution Chart
        function renderClusterChart() {{
            const ctx = document.getElementById('clusterChart');
            if (!STATS.semantic?.clusters) return;
            
            // Clusters is an object with cluster IDs as keys and arrays of paragraph IDs as values
            const clusterSizes = Object.values(STATS.semantic.clusters).map(paragraphIds => paragraphIds.length);
            const bins = [0, 5, 10, 15, 20, 25, 30, 100];
            const histogram = new Array(bins.length - 1).fill(0);
            
            clusterSizes.forEach(size => {{
                for (let i = 0; i < bins.length - 1; i++) {{
                    if (size >= bins[i] && size < bins[i + 1]) {{
                        histogram[i]++;
                        break;
                    }}
                }}
            }});
            
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: bins.slice(0, -1).map((b, i) => `${{b}}-${{bins[i+1]-1}}`),
                    datasets: [{{
                        label: 'Number of Clusters',
                        data: histogram,
                        backgroundColor: 'rgba(153, 102, 255, 0.6)',
                        borderColor: 'rgba(153, 102, 255, 1)',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }},
                        title: {{
                            display: true,
                            text: 'Cluster Size Distribution (paragraphs per cluster)',
                            color: '#a0a0a0'
                        }}
                    }},
                    scales: {{
                        y: {{ 
                            title: {{ display: true, text: 'Number of Clusters', color: '#a0a0a0' }},
                            ticks: {{ color: '#a0a0a0' }}
                        }},
                        x: {{ 
                            title: {{ display: true, text: 'Cluster Size (paragraphs)', color: '#a0a0a0' }},
                            ticks: {{ color: '#a0a0a0' }}
                        }}
                    }}
                }}
            }});
        }}

        // Phase Coverage Chart
        function renderPhaseCoverage() {{
            const ctx = document.getElementById('phaseCoverageChart');
            if (!STATS.welcome?.phase_coverage) return;
            
            const phases = STATS.welcome.phase_coverage;
            
            new Chart(ctx, {{
                type: 'radar',
                data: {{
                    labels: Object.keys(phases).map(p => `Phase ${{p}}`),
                    datasets: [{{
                        label: 'Mentions',
                        data: Object.values(phases),
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 2,
                        pointBackgroundColor: 'rgba(255, 99, 132, 1)',
                        pointRadius: 4
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        r: {{
                            ticks: {{ color: '#a0a0a0' }},
                            grid: {{ color: '#2a3f5f' }},
                            pointLabels: {{ color: '#e0e0e0' }}
                        }}
                    }},
                    plugins: {{
                        legend: {{ display: false }}
                    }}
                }}
            }});
        }}

        // Timeline Corrections Chart
        function renderTimelineCorrections() {{
            const ctx = document.getElementById('timelineCorrectionChart');
            
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ['Before Corrections', 'After Corrections'],
                    datasets: [
                        {{
                            label: 'HIGH Priority Issues',
                            data: [37, 9],
                            backgroundColor: 'rgba(255, 99, 132, 0.6)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 1
                        }},
                        {{
                            label: 'Documents Edited',
                            data: [0, 8],
                            backgroundColor: 'rgba(80, 200, 120, 0.6)',
                            borderColor: 'rgba(80, 200, 120, 1)',
                            borderWidth: 1
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#e0e0e0' }}
                        }},
                        title: {{
                            display: true,
                            text: '76% reduction in timeline inconsistencies',
                            color: '#a0a0a0'
                        }}
                    }},
                    scales: {{
                        y: {{ ticks: {{ color: '#a0a0a0' }} }},
                        x: {{ ticks: {{ color: '#a0a0a0' }} }}
                    }}
                }}
            }});
        }}

        // Dependency Chart
        function renderDependencyChart() {{
            const ctx = document.getElementById('dependencyChart');
            if (!STATS.dependencies) return;
            
            // cross_references is an object with document names as keys and arrays of references as values
            const crossRefsObj = STATS.dependencies.cross_references || {{}};
            const crossRefs = [];
            
            // Flatten the object into an array of references with source info
            Object.entries(crossRefsObj).forEach(([source, refs]) => {{
                refs.forEach(ref => {{
                    crossRefs.push({{
                        from: source,
                        to: ref.target,
                        type: ref.type
                    }});
                }});
            }});
            
            const refCounts = {{}};
            
            crossRefs.forEach(ref => {{
                const source = ref.from.replace('.md', '');
                const target = ref.to.replace('.md', '');
                refCounts[source] = (refCounts[source] || 0) + 1;
                refCounts[target] = (refCounts[target] || 0) + 1;
            }});
            
            const sortedRefs = Object.entries(refCounts)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 10);
            
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: sortedRefs.map(r => r[0]),
                    datasets: [{{
                        label: 'References',
                        data: sortedRefs.map(r => r[1]),
                        backgroundColor: 'rgba(255, 159, 64, 0.6)',
                        borderColor: 'rgba(255, 159, 64, 1)',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }},
                        title: {{
                            display: true,
                            text: 'Most interconnected chapters',
                            color: '#a0a0a0'
                        }}
                    }},
                    scales: {{
                        x: {{ ticks: {{ color: '#a0a0a0' }} }},
                        y: {{ ticks: {{ color: '#a0a0a0', font: {{ size: 10 }} }} }}
                    }}
                }}
            }});
        }}

        // Premise Distribution Chart
        function renderPremiseChart() {{
            const ctx = document.getElementById('premiseChart');
            if (!STATS.dependencies?.key_premises) return;
            
            const premises = STATS.dependencies.key_premises.slice(0, 9);
            
            new Chart(ctx, {{
                type: 'polarArea',
                data: {{
                    labels: premises.map(p => p.replace(/_/g, ' ').replace(/^(.)/, m => m.toUpperCase())),
                    datasets: [{{
                        data: premises.map(() => 1),
                        backgroundColor: [
                            'rgba(74, 144, 226, 0.6)',
                            'rgba(80, 200, 120, 0.6)',
                            'rgba(255, 159, 64, 0.6)',
                            'rgba(153, 102, 255, 0.6)',
                            'rgba(255, 99, 132, 0.6)',
                            'rgba(54, 162, 235, 0.6)',
                            'rgba(255, 206, 86, 0.6)',
                            'rgba(231, 233, 237, 0.6)',
                            'rgba(255, 127, 80, 0.6)'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'right',
                            labels: {{ color: '#e0e0e0', font: {{ size: 10 }}, padding: 8 }}
                        }}
                    }},
                    scales: {{
                        r: {{
                            ticks: {{ display: false }},
                            grid: {{ color: '#2a3f5f' }}
                        }}
                    }}
                }}
            }});
        }}

        // Simple semantic search
        function initSearch() {{
            const input = document.getElementById('searchInput');
            const results = document.getElementById('searchResults');
            
            if (!STATS.semantic?.paragraphs) {{
                results.innerHTML = '<div class="result-item">Semantic data not available</div>';
                return;
            }}
            
            input.addEventListener('input', debounce(() => {{
                const query = input.value.trim().toLowerCase();
                if (query.length < 3) {{
                    results.innerHTML = '';
                    return;
                }}
                
                // Simple keyword matching (would use embeddings in full implementation)
                const matches = STATS.semantic.paragraphs
                    .map(p => ({{
                        ...p,
                        score: calculateSimpleScore(query, p.content)
                    }}))
                    .filter(p => p.score > 0)
                    .sort((a, b) => b.score - a.score)
                    .slice(0, 10);
                
                if (matches.length === 0) {{
                    results.innerHTML = '<div class="result-item">No matches found</div>';
                    return;
                }}
                
                results.innerHTML = matches.map(m => `
                    <div class="result-item">
                        <div>
                            <span class="result-score">${{(m.score * 100).toFixed(1)}}%</span>
                            <span class="result-doc">${{m.document}} - ${{m.section}}</span>
                        </div>
                        <div class="result-content">${{m.content.substring(0, 200)}}...</div>
                    </div>
                `).join('');
            }}, 300));
        }}
        
        function calculateSimpleScore(query, text) {{
            const queryWords = query.toLowerCase().split(/\\s+/);
            const textLower = text.toLowerCase();
            let score = 0;
            
            queryWords.forEach(word => {{
                if (textLower.includes(word)) {{
                    score += 1 / queryWords.length;
                }}
            }});
            
            return score;
        }}
        
        function debounce(func, wait) {{
            let timeout;
            return function executedFunction(...args) {{
                const later = () => {{
                    clearTimeout(timeout);
                    func(...args);
                }};
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            }};
        }}

        // Initialize all visualizations
        window.addEventListener('DOMContentLoaded', () => {{
            renderOverviewStats();
            renderWordDistribution();
            renderPartDistribution();
            renderConceptChart();
            renderNetworkStats();
            renderClusterChart();
            renderPhaseCoverage();
            renderTimelineCorrections();
            renderDependencyChart();
            renderPremiseChart();
            initSearch();
        }});
    </script>
</body>
</html>
"""
    
    return html

def main():
    print("Building analytics page...")
    print("=" * 60)
    
    # Load all stats
    stats = load_all_stats()
    
    print(f"✓ Loaded stats:")
    if stats['welcome']:
        print(f"  - Welcome stats: {stats['welcome']['total_words']:,} words")
    if stats['semantic']:
        print(f"  - Semantic graph: {len(stats['semantic']['paragraphs'])} paragraphs")
    if stats['dependencies']:
        print(f"  - Dependencies: {len(stats['dependencies']['cross_references'])} cross-refs")
    
    # Generate HTML
    html = generate_analytics_html(stats)
    
    # Write to output file
    output_path = Path(__file__).parent.parent / 'analytics.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    # Get file size
    size_kb = output_path.stat().st_size / 1024
    
    print("=" * 60)
    print(f"✓ Generated {output_path}")
    print(f"  File size: {size_kb:.1f} KB")
    print()
    print("Analytics page includes:")
    print("  • Document structure & word distribution")
    print("  • Semantic network analysis & clustering")
    print("  • Timeline & phase coverage")
    print("  • Chapter dependencies & premises")
    print("  • Interactive semantic search")

if __name__ == '__main__':
    main()
