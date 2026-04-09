# Requirements: QVC Conference Presentation

**Defined:** 2026-03-24
**Core Value:** The live demo clearly shows a quantum classifier being trained, evaluated, and run on real IBM hardware — making quantum ML tangible for a non-specialist audience.

## v1 Requirements

Requirements for conference presentation. Each maps to roadmap phases.

### Notebook

- [x] **NTBK-01**: Demo notebook with cells reorganized for presentation flow (training → eval → hardware)
- [x] **NTBK-02**: Pre-trained weights cached so live demo skips full training
- [x] **NTBK-03**: Hardware results pre-cached as fallback for IBM queue delays
- [x] **NTBK-04**: Each demo cell executes in under 30 seconds
- [x] **NTBK-05**: Single ansatz narrative (pick one, show other as pre-computed)

### Visualization

- [x] **VIZ-01**: Projector-safe matplotlib settings (large fonts, high contrast)
- [x] **VIZ-02**: Loss curve plot that renders cleanly during demo
- [x] **VIZ-03**: Simulator vs hardware results comparison plot
- [x] **VIZ-04**: Input data grid visualization (2x4 pixel patterns)

### Slides

- [x] **SLID-01**: PowerPoint deck covering training, evaluation, hardware execution
- [x] **SLID-02**: Transition slides between demo segments
- [x] **SLID-03**: Pre-rendered notebook figures embedded in slides
- [x] **SLID-04**: Summary/takeaway slide

### Script

- [x] **SCRP-01**: Timing breakdown per section (~30 min total)
- [x] **SCRP-02**: Speaker notes for each slide and demo segment
- [x] **SCRP-03**: Hardware fallback plan (what to say/show if queue delays)
- [x] **SCRP-04**: Co-presenter handoff cues

## v2 Requirements

Deferred to future. Not in current roadmap.

### Enhancements

- **ENH-01**: Animated/progressive loss curve that updates cell-by-cell during training
- **ENH-02**: Noise narrative visualization (explaining why hardware results differ from simulator)
- **ENH-03**: Full rehearsal script with detailed co-presenter coordination
- **ENH-04**: QNN vs CNN comparison slide/demo section

## Out of Scope

| Feature | Reason |
|---------|--------|
| Intro/theory/circuit design sections | Co-presenter's responsibility |
| Hands-on attendee exercises | Live demo format, not workshop |
| Video recording or post-event materials | Focus on live presentation |
| Interactive Plotly/Bokeh visualizations | Static plots more reliable on projectors |
| Jupyter slide mode (RISE/reveal.js) | Real notebook more authentic for demo |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| NTBK-01 | Phase 2 | Complete |
| NTBK-02 | Phase 1 | Complete |
| NTBK-03 | Phase 1 | Complete |
| NTBK-04 | Phase 1 | Complete |
| NTBK-05 | Phase 1 | Complete |
| VIZ-01 | Phase 2 | Complete |
| VIZ-02 | Phase 2 | Complete |
| VIZ-03 | Phase 2 | Complete |
| VIZ-04 | Phase 2 | Complete |
| SLID-01 | Phase 3 | Complete |
| SLID-02 | Phase 3 | Complete |
| SLID-03 | Phase 3 | Complete |
| SLID-04 | Phase 3 | Complete |
| SCRP-01 | Phase 4 | Complete |
| SCRP-02 | Phase 4 | Complete |
| SCRP-03 | Phase 4 | Complete |
| SCRP-04 | Phase 4 | Complete |

**Coverage:**
- v1 requirements: 17 total
- Mapped to phases: 17
- Unmapped: 0

---
*Requirements defined: 2026-03-24*
*Last updated: 2026-03-24 after Phase 4 completion*
