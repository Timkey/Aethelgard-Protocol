```mermaid
flowchart TD
    Start[Proposal Submitted]
    
    Start --> CH{Source?}
    
    CH -->|Human| CC[Creative Channel<br/>Citizen or Expert Input]
    CH -->|Oracle| OI[Oracle Initiative<br/>Based on New Data]
    
    CC --> SE[Synthesis Engine]
    OI --> SE
    
    SE --> OA[Oracle Alpha Check<br/>Planetary Safety]
    SE --> OB[Oracle Beta Check<br/>Human Agency]
    SE --> OG[Oracle Gamma Check<br/>Progress Enabled]
    SE --> OD[Oracle Delta Check<br/>Mission Success]
    
    OA --> RL1{Red-Line<br/>Violated?}
    OB --> RL2{Red-Line<br/>Violated?}
    OG --> RL3{Red-Line<br/>Violated?}
    OD --> RL4{Red-Line<br/>Violated?}
    
    RL1 -->|Yes| REJ[Proposal Rejected]
    RL2 -->|Yes| REJ
    RL3 -->|Yes| REJ
    RL4 -->|Yes| REJ
    
    RL1 -->|No| CON[Consensus Check]
    RL2 -->|No| CON
    RL3 -->|No| CON
    RL4 -->|No| CON
    
    CON --> ALL{All Oracles<br/>Agree?}
    
    ALL -->|Yes| SH[Semantic Hashing<br/>Compare to Genesis Block]
    ALL -->|No| RP[Reconciliation Protocol<br/>Generate Third-Way]
    
    RP --> TW[Third-Way Proposal]
    TW --> SE
    
    SH --> DR{Semantic<br/>Drift?}
    
    DR -->|>10%| TLG[Temporal Latency Gate<br/>150-Year Human Review]
    DR -->|<10%| IMP[Implementation]
    
    TLG --> JO{Jury of<br/>Observers}
    
    JO -->|Approve| IMP
    JO -->|Reject| REJ
    
    IMP --> LM[Update Living Manifesto]
    LM --> AA[Verify Against<br/>Ancestral Anchor]
    AA --> END[Proposal Executed]
    
    REJ --> LOG[Log Rejection Rationale]
    LOG --> END
    
    style Start fill:#3498db,color:#fff
    style SE fill:#9b59b6,color:#fff
    style REJ fill:#e74c3c,color:#fff
    style IMP fill:#2ecc71,color:#fff
    style TLG fill:#f39c12,color:#fff
    style END fill:#34495e,color:#fff
```

**Figure 4: Governance Decision Flow**

Every proposal—whether from humans or Oracles—follows this verification pathway:

**Stage 1: Source Identification**
- Human proposals enter via Creative Channel
- Oracle proposals triggered by new scientific data

**Stage 2: Red-Line Verification**
Each of the four Oracles checks if the proposal violates its non-negotiable constraints:
- **Alpha:** Would it harm the planet's physical integrity?
- **Beta:** Would it coerce humans or reduce agency?
- **Gamma:** Would it suppress scientific progress?
- **Delta:** Would it endanger the mission?

**Stage 3: Conflict Resolution**
- If any Oracle rejects: Proposal fails
- If Oracles disagree on details: Reconciliation Protocol generates alternatives
- If all agree: Proceed to drift check

**Stage 4: Anti-Drift Verification**
- **Semantic Hashing:** Compare proposal to 2026 Genesis Block
- If drift >10%: Trigger Temporal Latency Gate (150-year human review)
- If drift <10%: Proceed to implementation

**Stage 5: Human Oversight**
- Jury of Observers can force review of any decision
- Major changes require multi-generational consensus
- All decisions logged for transparency

**Stage 6: Execution**
- Living Manifesto updated with rationale
- Changes verified against physical Ancestral Anchor
- Implementation proceeds with monitoring

This multi-layer process ensures no single entity—human or AI—can hijack the mission.
