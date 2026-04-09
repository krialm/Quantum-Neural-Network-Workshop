# Roadmap: QVC Conference Presentation

## Overview

This roadmap delivers a 30-minute conference presentation with a live Jupyter notebook demo and PowerPoint slides covering quantum variational circuit training, evaluation, and hardware execution. The work flows sequentially: caching foundation first (nothing works reliably without it), then notebook polish and visualizations (figures must be final before slides), then slide deck generation (embeds the figures), then demo script and rehearsal (validates the complete pipeline). Each phase produces artifacts the next phase consumes.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Caching Foundation** - Pre-compute and cache all expensive operations (training, hardware) so live demo never stalls
- [ ] **Phase 2: Demo Notebook and Visualizations** - Build presentation-order demo notebook with projector-safe figures
- [ ] **Phase 3: Slide Deck** - Generate PowerPoint deck with embedded figures and speaker notes
- [ ] **Phase 4: Demo Script and Rehearsal** - Write timing script, fallback plans, and validate full pipeline end-to-end

## Phase Details

### Phase 1: Caching Foundation
**Goal**: Every expensive computation is pre-run and cached so the live demo loads results instantly
**Depends on**: Nothing (first phase)
**Requirements**: NTBK-02, NTBK-03, NTBK-04, NTBK-05
**Success Criteria** (what must be TRUE):
  1. Pre-trained model weights load from cache and produce correct predictions without retraining
  2. Hardware execution results load from cache without submitting an IBM Quantum job
  3. A single ansatz is chosen as the primary narrative; the alternative ansatz results are available as pre-computed comparison data
  4. Every cached-load cell executes in under 30 seconds
**Plans:** 2 plans

Plans:
- [x] 01-01-PLAN.md -- Build cache_results.py with dual-ansatz training, hardware caching, and JSON output
- [x] 01-02-PLAN.md -- Test suite validating cache schemas, load speed, and auto-detection logic

### Phase 2: Demo Notebook and Visualizations
**Goal**: A polished demo notebook runs top-to-bottom in presentation order, producing projector-readable figures
**Depends on**: Phase 1
**Requirements**: NTBK-01, VIZ-01, VIZ-02, VIZ-03, VIZ-04
**Success Criteria** (what must be TRUE):
  1. Demo notebook cells flow in presentation order (training explanation, evaluation, hardware comparison) and run top-to-bottom after Kernel > Restart and Run All
  2. All figures use large fonts (16pt+), thick lines, and high-contrast colors readable from the back of a conference room
  3. Loss curve plot clearly shows training convergence across epochs
  4. Simulator vs hardware results comparison plot shows both side-by-side with labeled axes
  5. Input data grid visualization shows the 2x4 pixel patterns (horizontal vs vertical lines) clearly
**Plans:** 2 plans
**UI hint**: yes

Plans:
- [x] 02-01-PLAN.md -- Create QVC_QNN_demo.ipynb with all cells, projector-safe styling, and three visualizations
- [x] 02-02-PLAN.md -- Test suite validating notebook structure, cell order, rcParams, and figure saves

### Phase 3: Slide Deck
**Goal**: A complete PowerPoint deck is ready with all figures embedded and speaker notes attached
**Depends on**: Phase 2
**Requirements**: SLID-01, SLID-02, SLID-03, SLID-04
**Success Criteria** (what must be TRUE):
  1. PowerPoint file opens in standard PowerPoint and covers training, evaluation, and hardware execution sections
  2. Transition slides exist between each demo segment (training-to-eval, eval-to-hardware) providing context for the audience
  3. All notebook-generated figures are embedded in relevant slides at readable resolution
  4. A summary/takeaway slide exists with key results and conclusions
**Plans:** 1 plan

Plans:
- [x] 03-01-PLAN.md -- Generate PowerPoint deck with python-pptx: figures, transitions, speaker notes, and test suite

### Phase 4: Demo Script and Rehearsal
**Goal**: The presenter can deliver the full 30-minute half confidently with timing marks, fallback plans, and validated artifacts
**Depends on**: Phase 3
**Requirements**: SCRP-01, SCRP-02, SCRP-03, SCRP-04
**Success Criteria** (what must be TRUE):
  1. A written timing breakdown accounts for every minute of the ~30-minute half with section durations
  2. Speaker notes exist for each slide and each demo segment, covering what to say and what to show
  3. A documented hardware fallback plan specifies exactly what to say and show if IBM Quantum queue delays occur
  4. Co-presenter handoff cues are marked at the beginning and end of the 30-minute half
**Plans:** 1 plan

Plans:
- [x] 04-01-PLAN.md -- Create demo_script.md with timing marks, speaker notes, hardware fallback, handoff cues, and test suite

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Caching Foundation | 2/2 | Complete | 2026-03-24 |
| 2. Demo Notebook and Visualizations | 2/2 | Complete | 2026-03-24 |
| 3. Slide Deck | 1/1 | Complete | 2026-03-24 |
| 4. Demo Script and Rehearsal | 1/1 | Complete | 2026-03-24 |
