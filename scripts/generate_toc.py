#!/usr/bin/env python3
"""
Aethelgard Protocol - Table of Contents Generator
Creates hierarchical structure for the White Paper
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class TOCEntry:
    """Represents a single entry in the table of contents"""
    level: int
    title: str
    description: str
    page_estimate: int
    subsections: List['TOCEntry'] = None
    
    def __post_init__(self):
        if self.subsections is None:
            self.subsections = []

class TOCGenerator:
    """Generates the Master Table of Contents"""
    
    def __init__(self, metadata_dir: Path):
        self.metadata_dir = metadata_dir
        self.metadata = self.load_metadata()
        self.toc = []
    
    def load_metadata(self) -> Dict:
        """Load all metadata files"""
        metadata = {}
        
        files = [
            'technical_constants', 'key_concepts', 'sections',
            'timeline', 'oracles', 'religious_references'
        ]
        
        for filename in files:
            filepath = self.metadata_dir / f'{filename}.json'
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    metadata[filename] = json.load(f)
        
        return metadata
    
    def build_toc(self) -> List[TOCEntry]:
        """Build the complete table of contents structure"""
        
        toc = [
            self._build_executive_summary(),
            self._build_part1_foundations(),
            self._build_part2_technical(),
            self._build_part3_governance(),
            self._build_part4_implementation(),
            self._build_appendices()
        ]
        
        return toc
    
    def _build_executive_summary(self) -> TOCEntry:
        """Executive Summary section"""
        return TOCEntry(
            level=1,
            title="Executive Summary",
            description="High-level overview of the Aethelgard Protocol",
            page_estimate=10,
            subsections=[
                TOCEntry(2, "The Three Gaps", "Political, Ethical, and Knowledge gaps", 2),
                TOCEntry(2, "The Solution: Poly-Centric Oracle Architecture", "Four Oracles working in synthesis", 3),
                TOCEntry(2, "The Mission: A 5,000-Year Journey", "Timeline and destination", 2),
                TOCEntry(2, "Reading Guide", "How to use this document", 1),
            ]
        )
    
    def _build_part1_foundations(self) -> TOCEntry:
        """Part 1: Foundations and Rationale"""
        return TOCEntry(
            level=1,
            title="Part 1: Foundations and Rationale",
            description="Why we must move the Earth and the physics behind it",
            page_estimate=100,
            subsections=[
                TOCEntry(
                    level=2,
                    title="Chapter 1: The Solar Imperative",
                    description="The Sun's lifecycle and Earth's fate",
                    page_estimate=15,
                    subsections=[
                        TOCEntry(3, "1.1 Current Solar Status", "The stable yellow dwarf phase", 3),
                        TOCEntry(3, "1.2 The Brightness Creep", "10% increase every billion years", 4),
                        TOCEntry(3, "1.3 The Red Giant Phase", "5 billion year timeline", 4),
                        TOCEntry(3, "1.4 Critical Decision Windows", "When we must act", 4),
                    ]
                ),
                TOCEntry(
                    level=2,
                    title="Chapter 2: The Physics of Planetary Motion",
                    description="Understanding how to move a world",
                    page_estimate=20,
                    subsections=[
                        TOCEntry(3, "2.1 Earth's Mass and Inertia", "The scale of the challenge", 4),
                        TOCEntry(3, "2.2 Orbital Mechanics", "Escape velocity and trajectory", 5),
                        TOCEntry(3, "2.3 Energy Requirements", "Dyson-scale power needs", 5),
                        TOCEntry(3, "2.4 The Moon as Gravity Tractor", "Using gravitational coupling", 6),
                    ]
                ),
                TOCEntry(
                    level=2,
                    title="Chapter 3: Alternative Strategies Evaluated",
                    description="Why planetary migration is optimal",
                    page_estimate=15,
                    subsections=[
                        TOCEntry(3, "3.1 Generation Ships", "The ark model limitations", 4),
                        TOCEntry(3, "3.2 Embryo Seeding", "The genetic bottleneck risk", 3),
                        TOCEntry(3, "3.3 O'Neill Cylinders", "Space habitat constraints", 4),
                        TOCEntry(3, "3.4 The Biosphere Advantage", "Why Earth is irreplaceable", 4),
                    ]
                ),
                TOCEntry(
                    level=2,
                    title="Chapter 4: The 10 Billion Mandate",
                    description="Why we must save everyone",
                    page_estimate=12,
                    subsections=[
                        TOCEntry(3, "4.1 Genetic Diversity Requirements", "Population biology constraints", 3),
                        TOCEntry(3, "4.2 Knowledge Redundancy", "Civilizational resilience", 3),
                        TOCEntry(3, "4.3 The Ethical Foundation", "Universal human dignity", 3),
                        TOCEntry(3, "4.4 Social Stability", "Preventing sabotage and conflict", 3),
                    ]
                ),
            ]
        )
    
    def _build_part2_technical(self) -> TOCEntry:
        """Part 2: Technical Architecture"""
        return TOCEntry(
            level=1,
            title="Part 2: Technical Architecture",
            description="Engineering systems and specifications",
            page_estimate=150,
            subsections=[
                TOCEntry(
                    level=2,
                    title="Chapter 5: The Poly-Centric Oracle System",
                    description="The governance AI architecture",
                    page_estimate=25,
                    subsections=[
                        TOCEntry(3, "5.1 The Parliament of Oracles", "Four directive threads", 5),
                        TOCEntry(3, "5.2 Oracle Alpha: The Sentinel", "Planetary preservation", 5),
                        TOCEntry(3, "5.3 Oracle Beta: The Humanist", "Agency and dignity", 5),
                        TOCEntry(3, "5.4 Oracle Gamma: The Evolutionist", "Progress and adaptation", 5),
                        TOCEntry(3, "5.5 Oracle Delta: The Navigator", "Mission success", 5),
                    ]
                ),
                TOCEntry(
                    level=2,
                    title="Chapter 6: The Synthesis Engine",
                    description="How the Oracles find consensus",
                    page_estimate=20,
                    subsections=[
                        TOCEntry(3, "6.1 Red-Line Definition", "Non-negotiable constraints", 4),
                        TOCEntry(3, "6.2 Conflict Resolution Protocol", "Finding the third way", 5),
                        TOCEntry(3, "6.3 Recursive Reconciliation", "Iterative solution refinement", 5),
                        TOCEntry(3, "6.4 Deadlock Prevention", "Entropy clause and timeouts", 4),
                        TOCEntry(3, "6.5 Human Override Mechanisms", "The Jury of Observers", 2),
                    ]
                ),
                TOCEntry(
                    level=2,
                    title="Chapter 7: The Rug - Information Management",
                    description="Long-term knowledge preservation",
                    page_estimate=18,
                    subsections=[
                        TOCEntry(3, "7.1 The Living Manifesto", "Evolving documentation", 4),
                        TOCEntry(3, "7.2 Semantic Hashing", "Intent preservation", 4),
                        TOCEntry(3, "7.3 Temporal Latency Gates", "Preventing drift", 4),
                        TOCEntry(3, "7.4 The Ancestral Anchor", "Physical verification", 3),
                        TOCEntry(3, "7.5 Thinking Idea Objects", "Graph-based knowledge", 3),
                    ]
                ),
                TOCEntry(
                    level=2,
                    title="Chapter 8: Propulsion Systems",
                    description="The Moon-Tug and planetary engines",
                    page_estimate=22,
                    subsections=[
                        TOCEntry(3, "8.1 Lunar Mass Drivers", "Electromagnetic acceleration", 5),
                        TOCEntry(3, "8.2 Fusion Thrusters", "Primary propulsion", 5),
                        TOCEntry(3, "8.3 Gravitational Coupling", "Moon-Earth dynamics", 5),
                        TOCEntry(3, "8.4 Tidal Stress Management", "Crustal integrity", 4),
                        TOCEntry(3, "8.5 Navigation and Steering", "Interstellar guidance", 3),
                    ]
                ),
                TOCEntry(
                    level=2,
                    title="Chapter 9: Energy Infrastructure",
                    description="The Dyson Swarm and power systems",
                    page_estimate=18,
                    subsections=[
                        TOCEntry(3, "9.1 Solar Collection Arrays", "Swarm architecture", 4),
                        TOCEntry(3, "9.2 Power Transmission", "Beaming and distribution", 4),
                        TOCEntry(3, "9.3 Energy Storage", "Fuel moon reserves", 4),
                        TOCEntry(3, "9.4 Fusion Reactors", "Backup power systems", 3),
                        TOCEntry(3, "9.5 Efficiency Optimization", "Resource management", 3),
                    ]
                ),
                TOCEntry(
                    level=2,
                    title="Chapter 10: Defense Systems",
                    description="Planetary shield and navigation safety",
                    page_estimate=20,
                    subsections=[
                        TOCEntry(3, "10.1 Detection Horizon", "Early warning network", 4),
                        TOCEntry(3, "10.2 Kinetic Interceptors", "Active debris clearing", 5),
                        TOCEntry(3, "10.3 Magnetic Plow", "Dust and particle deflection", 4),
                        TOCEntry(3, "10.4 Laser Defense Grid", "Point defense systems", 4),
                        TOCEntry(3, "10.5 Vanguard Scout Fleet", "Forward pathfinding", 3),
                    ]
                ),
                TOCEntry(
                    level=2,
                    title="Chapter 11: Underground Hive Architecture",
                    description="The subterranean cities",
                    page_estimate=22,
                    subsections=[
                        TOCEntry(3, "11.1 Craton Site Selection", "Geological stability", 4),
                        TOCEntry(3, "11.2 Vitrified Construction", "Glass-rock permanence", 5),
                        TOCEntry(3, "11.3 Seismic Isolation", "Magnetic dampening", 4),
                        TOCEntry(3, "11.4 Life Support Systems", "Closed-loop ecology", 5),
                        TOCEntry(3, "11.5 Modular Design", "Adaptive expansion", 4),
                    ]
                ),
                TOCEntry(
                    level=2,
                    title="Chapter 12: Cryogenic Systems",
                    description="Managing 10 billion in stasis",
                    page_estimate=15,
                    subsections=[
                        TOCEntry(3, "12.1 Quantum Biology", "Cellular preservation", 4),
                        TOCEntry(3, "12.2 Rotation Protocol", "Generational awakening", 4),
                        TOCEntry(3, "12.3 Medical Monitoring", "Long-term health", 4),
                        TOCEntry(3, "12.4 Revival Procedures", "Safe awakening", 3),
                    ]
                ),
            ]
        )
    
    def _build_part3_governance(self) -> TOCEntry:
        """Part 3: Governance and Social Systems"""
        return TOCEntry(
            level=1,
            title="Part 3: Governance and Social Systems",
            description="How humanity maintains cohesion over 5,000 years",
            page_estimate=100,
            subsections=[
                TOCEntry(
                    level=2,
                    title="Chapter 13: The Transition from Democracy to Protocol",
                    description="Evolution of human governance",
                    page_estimate=18,
                    subsections=[
                        TOCEntry(3, "13.1 The Competence Collapse", "Why traditional governance fails", 4),
                        TOCEntry(3, "13.2 Agency Preservation", "Maintaining human sovereignty", 5),
                        TOCEntry(3, "13.3 The Creative Channel", "Human contribution space", 4),
                        TOCEntry(3, "13.4 The Jury of Observers", "Democratic oversight", 5),
                    ]
                ),
                TOCEntry(
                    level=2,
                    title="Chapter 14: Geopolitical Integration",
                    description="From nations to unified council",
                    page_estimate=20,
                    subsections=[
                        TOCEntry(3, "14.1 The Tower of Babel Problem", "Fragmentation risks", 4),
                        TOCEntry(3, "14.2 Federated Approach", "Sub-directives and local autonomy", 5),
                        TOCEntry(3, "14.3 The Ultimate Council", "Central coordination", 5),
                        TOCEntry(3, "14.4 Game Theory Adoption", "Competitive advantage drives unity", 4),
                        TOCEntry(3, "14.5 The Resource Magnet", "Energy access as catalyst", 2),
                    ]
                ),
                TOCEntry(
                    level=2,
                    title="Chapter 15: Theological Reconciliation",
                    description="Religious perspectives on planetary migration",
                    page_estimate=25,
                    subsections=[
                        TOCEntry(3, "15.1 The Transgression of Placement", "Enochic concerns", 5),
                        TOCEntry(3, "15.2 The Stewardship Mandate", "Biblical permission", 5),
                        TOCEntry(3, "15.3 The New Earth Interpretation", "Eschatological alignment", 5),
                        TOCEntry(3, "15.4 Islamic Amanah", "Trusteeship obligation", 4),
                        TOCEntry(3, "15.5 Dharmic Cycles", "Continuity of consciousness", 3),
                        TOCEntry(3, "15.6 Indigenous Homecoming", "Star ancestor return", 3),
                    ]
                ),
                TOCEntry(
                    level=2,
                    title="Chapter 16: Social Cohesion During the Journey",
                    description="Maintaining culture across generations",
                    page_estimate=17,
                    subsections=[
                        TOCEntry(3, "16.1 Generational Education", "Preserving purpose", 4),
                        TOCEntry(3, "16.2 Cultural Repositories", "Art and tradition", 4),
                        TOCEntry(3, "16.3 Virtual Reality Heritage", "Digital continuity", 4),
                        TOCEntry(3, "16.4 Conflict Resolution", "Deep-time diplomacy", 5),
                    ]
                ),
                TOCEntry(
                    level=2,
                    title="Chapter 17: Economic Models",
                    description="Resource allocation in closed systems",
                    page_estimate=15,
                    subsections=[
                        TOCEntry(3, "17.1 Post-Scarcity Transition", "Asteroid mining wealth", 4),
                        TOCEntry(3, "17.2 Labor and Purpose", "Meaningful work in automation", 4),
                        TOCEntry(3, "17.3 Energy Budgets", "The 20% human sandbox", 4),
                        TOCEntry(3, "17.4 Inheritance and Generational Wealth", "Deep-time economics", 3),
                    ]
                ),
            ]
        )
    
    def _build_part4_implementation(self) -> TOCEntry:
        """Part 4: Implementation Roadmap"""
        return TOCEntry(
            level=1,
            title="Part 4: Implementation Roadmap",
            description="The 2026-6000 timeline",
            page_estimate=80,
            subsections=[
                TOCEntry(
                    level=2,
                    title="Chapter 18: Phase Zero (2026-2050)",
                    description="Foundation and defense",
                    page_estimate=15,
                    subsections=[
                        TOCEntry(3, "18.1 Defense Network Deployment", "Sentinel infrastructure", 4),
                        TOCEntry(3, "18.2 Knowledge Ingestion", "Academic repository indexing", 3),
                        TOCEntry(3, "18.3 Crustal Mapping", "Neutrino tomography", 4),
                        TOCEntry(3, "18.4 MVP Oracle Development", "First synthesis engine", 4),
                    ]
                ),
                TOCEntry(
                    level=2,
                    title="Chapter 19: Phase One (2050-2150)",
                    description="Energy and construction",
                    page_estimate=18,
                    subsections=[
                        TOCEntry(3, "19.1 Dyson Swarm Construction", "Solar energy collection", 5),
                        TOCEntry(3, "19.2 Jupiter Siphoning", "Fuel extraction", 5),
                        TOCEntry(3, "19.3 Lunar Industrialization", "Moon-based manufacturing", 4),
                        TOCEntry(3, "19.4 Hive Excavation", "Underground city construction", 4),
                    ]
                ),
                TOCEntry(
                    level=2,
                    title="Chapter 20: Phase Two (2150-2500)",
                    description="The Great Migration",
                    page_estimate=15,
                    subsections=[
                        TOCEntry(3, "20.1 Surface Abandonment", "Population descent", 4),
                        TOCEntry(3, "20.2 Atmospheric Hardening", "Environmental sealing", 4),
                        TOCEntry(3, "20.3 Moon-Tug Ignition", "First orbital adjustment", 4),
                        TOCEntry(3, "20.4 System Testing", "Full integration", 3),
                    ]
                ),
                TOCEntry(
                    level=2,
                    title="Chapter 21: Phase Three (2500-3000)",
                    description="Solar escape",
                    page_estimate=12,
                    subsections=[
                        TOCEntry(3, "21.1 Escape Velocity Achievement", "Leaving the solar system", 4),
                        TOCEntry(3, "21.2 Surface Freeze", "Atmospheric preservation", 3),
                        TOCEntry(3, "21.3 Vanguard Deployment", "Scout fleet launch", 3),
                        TOCEntry(3, "21.4 The Long Dark Begins", "Interstellar transit start", 2),
                    ]
                ),
                TOCEntry(
                    level=2,
                    title="Chapter 22: Phase Four (3000-6000)",
                    description="The interstellar crossing",
                    page_estimate=15,
                    subsections=[
                        TOCEntry(3, "22.1 Cryo-Rotation Management", "Generational awakening", 4),
                        TOCEntry(3, "22.2 System Evolution", "Technological upgrades", 4),
                        TOCEntry(3, "22.3 Vanguard Arrival", "Destination preparation", 4),
                        TOCEntry(3, "22.4 Course Corrections", "Navigation adjustments", 3),
                    ]
                ),
                TOCEntry(
                    level=2,
                    title="Chapter 23: Phase Five (6000+)",
                    description="Arrival and renewal",
                    page_estimate=12,
                    subsections=[
                        TOCEntry(3, "23.1 Orbital Insertion", "New star system capture", 3),
                        TOCEntry(3, "23.2 The Great Thaw", "Atmospheric revival", 3),
                        TOCEntry(3, "23.3 Population Awakening", "Global revival", 3),
                        TOCEntry(3, "23.4 Protocol Sunset", "Oracle retirement", 3),
                    ]
                ),
            ]
        )
    
    def _build_appendices(self) -> TOCEntry:
        """Appendices and reference materials"""
        return TOCEntry(
            level=1,
            title="Appendices",
            description="Technical references and supplementary materials",
            page_estimate=50,
            subsections=[
                TOCEntry(2, "Appendix A: Technical Constants", "Master variable ledger", 10),
                TOCEntry(2, "Appendix B: Mathematical Proofs", "Energy and trajectory calculations", 10),
                TOCEntry(2, "Appendix C: Religious Source Texts", "Scriptural references", 8),
                TOCEntry(2, "Appendix D: Glossary", "Key terms and definitions", 8),
                TOCEntry(2, "Appendix E: Software Specifications", "Oracle implementation details", 10),
                TOCEntry(2, "Appendix F: Bibliography", "Academic and historical sources", 4),
            ]
        )
    
    def calculate_totals(self, entries: List[TOCEntry], level: int = 0) -> Dict:
        """Calculate total pages and sections"""
        total_pages = 0
        total_sections = 0
        
        for entry in entries:
            total_pages += entry.page_estimate
            total_sections += 1
            
            if entry.subsections:
                sub_totals = self.calculate_totals(entry.subsections, level + 1)
                total_pages += sub_totals['pages']
                total_sections += sub_totals['sections']
        
        return {'pages': total_pages, 'sections': total_sections}
    
    def render_markdown(self, entries: List[TOCEntry], level: int = 0) -> str:
        """Render TOC as markdown"""
        lines = []
        
        for entry in entries:
            indent = "  " * level
            
            # Format page estimate
            if entry.page_estimate > 0:
                page_info = f" [{entry.page_estimate}p]"
            else:
                page_info = ""
            
            # Add entry
            lines.append(f"{indent}- **{entry.title}**{page_info}")
            if entry.description:
                lines.append(f"{indent}  *{entry.description}*")
            
            # Add subsections recursively
            if entry.subsections:
                lines.append(self.render_markdown(entry.subsections, level + 1))
        
        return "\n".join(lines)
    
    def generate(self, output_file: Path):
        """Generate the complete TOC"""
        print("Building Table of Contents structure...")
        self.toc = self.build_toc()
        
        print("Calculating totals...")
        totals = self.calculate_totals(self.toc)
        
        # Generate markdown
        print("Rendering markdown...")
        toc_md = self.render_markdown(self.toc)
        
        # Create full document
        document = f"""# Aethelgard Protocol - Master Table of Contents
## The White Paper: A 5,000-Year Plan for Planetary Migration

**Document Status:** Draft v1.0  
**Date:** 2026-01-05  
**Total Estimated Pages:** {totals['pages']}  
**Total Sections:** {totals['sections']}

---

## Overview

This master table of contents outlines the complete structure of the Aethelgard Protocol White Paper. The document is organized into four major parts plus appendices:

1. **Foundations and Rationale** - Why we must move Earth
2. **Technical Architecture** - Engineering systems and specifications
3. **Governance and Social Systems** - Managing humanity over millennia
4. **Implementation Roadmap** - The 4,000-year timeline

Each section includes page estimates to guide document generation.

---

## Table of Contents

{toc_md}

---

## Document Statistics

- **Estimated Total Pages:** {totals['pages']}
- **Major Parts:** 4
- **Chapters:** {sum(1 for e in self.toc if e.level == 2 for s in (e.subsections or []))}
- **Subsections:** {sum(1 for e in self.toc for s1 in (e.subsections or []) for s2 in (s1.subsections or []))}

## Generation Notes

- Page estimates are conservative and may expand during writing
- Technical appendices may require additional pages for diagrams
- Cross-references will be added during final compilation
- Metadata extracted from {self.metadata_dir.parent}/data/raw.txt

---

*Generated by TOC Generator v1.0*  
*Part of the Aethelgard Protocol Documentation System*
"""
        
        # Save
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(document, encoding='utf-8')
        
        print(f"\nTable of Contents saved to: {output_file}")
        print(f"  Total estimated pages: {totals['pages']}")
        print(f"  Total sections: {totals['sections']}")
        
        return output_file


def main():
    metadata_dir = Path('/Volumes/mnt/LAB/Planetary Exodus/metadata')
    output_file = Path('/Volumes/mnt/LAB/Planetary Exodus/docs/00_Master_TOC.md')
    
    print("=" * 60)
    print("Aethelgard Protocol - TOC Generator")
    print("=" * 60)
    
    generator = TOCGenerator(metadata_dir)
    generator.generate(output_file)
    
    print("\n" + "=" * 60)
    print("TOC Generation Complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
