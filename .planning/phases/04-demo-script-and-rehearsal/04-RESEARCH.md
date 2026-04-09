# Phase 4: Demo Script and Rehearsal - Research

**Researched:** 2026-03-24
**Domain:** Conference presentation scripting, timing, fallback planning
**Confidence:** HIGH

## Summary

Phase 4 produces the presenter-facing documents that tie together all previous artifacts (cached results from Phase 1, demo notebook from Phase 2, slide deck from Phase 3) into a deliverable 30-minute presentation half. The deliverables are a timing breakdown, speaker notes for every slide and demo segment, a hardware fallback plan, and co-presenter handoff cues.

This is a documentation-only phase -- no code changes, no new Python scripts. The inputs are fully built: a 14-cell demo notebook (QVC_QNN_demo.ipynb), an 11-slide PowerPoint deck (output/presentation.pptx) with existing speaker notes in generate_deck.py, and the cache infrastructure (trained_weights.json, training_history.json, hardware_results.json). The task is to create a single comprehensive demo script (demo_script.md) that the presenter reads during rehearsal and references during the live talk.

**Primary recommendation:** Create `demo_script.md` in the project root with section-by-section timing marks, enriched speaker notes that go beyond the slide-level notes already in generate_deck.py, a dedicated hardware fallback decision tree, and explicit co-presenter handoff protocol. Keep it as one file -- a presenter needs a single document to rehearse from, not scattered notes.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SCRP-01 | Timing breakdown per section (~30 min total) | Slide deck has 11 slides; notebook has 14 cells across 3 demo segments. Research maps both to a minute-by-minute timeline below. |
| SCRP-02 | Speaker notes for each slide and demo segment | generate_deck.py already has basic notes on all 11 slides. Research identifies gaps and prescribes enriched notes covering what to say, what to click, and what the audience sees. |
| SCRP-03 | Hardware fallback plan (what to say/show if queue delays) | PITFALLS.md Pitfall 1 and Phase 1 D-05/D-06 define the dual hardware strategy. Research provides the decision tree and exact fallback dialogue. |
| SCRP-04 | Co-presenter handoff cues | PITFALLS.md Pitfall 8 identifies the risk. Research defines the handoff protocol: transition phrase, slide number, notebook state. |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- GSD workflow enforcement: all file changes must go through GSD commands
- commit_docs is false: do not commit documentation files automatically
- nyquist_validation is enabled: include validation architecture section
- No linting/formatting configuration -- markdown files follow general readability
- Snake_case naming for any Python identifiers (not applicable here -- markdown only)

## Standard Stack

No new libraries or tools are needed for this phase. All deliverables are Markdown files.

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| Markdown | N/A | Demo script format | Human-readable, viewable in any editor, version-controllable |

### Supporting
| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| python-pptx | 1.0.2 | Already installed; speaker notes could be updated in generate_deck.py | Only if SCRP-02 requires updating the .pptx speaker notes programmatically |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Single demo_script.md | Separate files per section | Single file is easier to rehearse from; no navigation overhead |
| Updating generate_deck.py notes | Separate script notes file | Keep script separate -- generate_deck.py is a build tool, not a presenter document |

## Architecture Patterns

### Recommended Project Structure
```
Quantum_Variational_Circuits/
  demo_script.md              # NEW: Complete presenter script (SCRP-01 through SCRP-04)
  QVC_QNN_demo.ipynb          # Existing: 14-cell demo notebook
  output/presentation.pptx    # Existing: 11-slide deck
  slides/generate_deck.py     # Existing: slide generator (already has basic notes)
```

### Pattern 1: Single-Document Presenter Script
**What:** One Markdown file containing timing, speaker notes, fallback plans, and handoff cues in presentation order.
**When to use:** Conference presentations where the presenter needs a single reference during rehearsal.
**Structure:**
```markdown
# Demo Script: QVC Conference Presentation

## Pre-Talk Checklist
[Environment setup, file checks, JupyterLab font size]

## Timing Overview
[Table mapping each section to minutes]

## Section 1: [Name]
**Time:** MM:SS - MM:SS (X minutes)
**Artifact:** Slide N / Notebook Cell N
**Speaker Notes:** [What to say]
**Actions:** [What to click/show]
**Fallback:** [If something goes wrong]

## Hardware Fallback Decision Tree
[Dedicated section for SCRP-03]

## Co-Presenter Handoff
[Dedicated section for SCRP-04]
```

### Pattern 2: Timing Mark Format
**What:** Each section header includes cumulative time and section duration.
**When to use:** Any timed presentation script.
**Example:**
```markdown
## [00:00-03:00] Introduction and Data Overview (3 min)
```
This format lets the presenter glance at the clock and know exactly where they should be.

### Anti-Patterns to Avoid
- **Separate notes per slide:** Forces presenter to flip between documents. Use one file.
- **Vague timing ("about 5 minutes"):** Use specific minute marks so the presenter can self-correct during delivery.
- **Fallback plan buried in general notes:** Hardware fallback (SCRP-03) needs a dedicated, clearly labeled section -- in a crisis the presenter needs to find it instantly.
- **Assuming co-presenter coordination happens naturally:** Pitfall 8 from PITFALLS.md warns this causes awkward handoffs. Script must have explicit cues.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Speaker notes in slides | Custom note-injection script | Keep demo_script.md as the primary reference; slides/generate_deck.py already has basic notes | Presenter reads from script, not from PowerPoint presenter view |
| Timing validation | Automated timer tool | Manual rehearsal with a stopwatch | A script that checks timing adds complexity with no value -- just rehearse |

## Common Pitfalls

### Pitfall 1: Timing Drift from Demo Segments
**What goes wrong:** The notebook demo segments (live training, evaluation, hardware comparison) take longer than planned because the presenter explains code, answers questions, or waits for cells to execute.
**Why it happens:** Demo cells have variable execution time and audience interaction is unpredictable.
**How to avoid:** Build 2-3 minutes of buffer into the 30-minute plan. Mark which sections can be shortened if running long. The live training demo (Cell 6, 3 COBYLA iterations) is the most variable -- time it during rehearsal.
**Warning signs:** If the first demo segment runs over its time mark by >1 minute, cut explanations in later segments.

### Pitfall 2: Hardware Fallback Not Rehearsed
**What goes wrong:** The presenter has a written fallback plan but has never actually delivered it. When hardware fails live, they freeze or stumble through an improvised explanation.
**Why it happens:** Rehearsals tend to practice the happy path. The fallback path feels like a failure scenario nobody wants to rehearse.
**How to avoid:** The script must include exact words for the fallback. Rehearse the fallback path at least once.
**Warning signs:** If the presenter cannot deliver the hardware fallback explanation without reading it word-for-word, they need more practice.

### Pitfall 3: Co-Presenter Handoff Without Signal
**What goes wrong:** User finishes their half but the co-presenter doesn't know it's their turn (or vice versa). Awkward pause, both talking at once, or the transition slide gets skipped.
**Why it happens:** No agreed-upon verbal cue or physical signal.
**How to avoid:** Script defines an explicit verbal handoff phrase (e.g., "Now I'll hand it back to [name] who will walk us through the circuit design") AND a physical cue (e.g., stepping away from the podium). Both presenters rehearse the transition.

### Pitfall 4: JupyterLab Setup Forgotten
**What goes wrong:** Presenter opens JupyterLab at default font size, dark theme, or with distracting sidebars. Audience can't read code cells on the projector.
**Why it happens:** Demo machine setup happens under time pressure before the talk. Easy to forget cosmetic settings.
**How to avoid:** Pre-talk checklist in the script covers: font size (Ctrl+= multiple times), theme, sidebar hidden, kernel restarted, all cells collapsed.

## Existing Content Inventory

The script phase does not start from scratch. These speaker notes already exist in `slides/generate_deck.py`:

| Slide | Existing Note Content | Gap for SCRP-02 |
|-------|----------------------|------------------|
| 1: Title | Handoff intro from co-presenter | Needs timing mark, transition action |
| 2: Overview | "Three sections, switch between slides and notebook" | Needs specific notebook cell references |
| 3: Data Overview | "2x4 pixel grids, 8 qubits" | Needs what to point out in the figure |
| 4: Transition - Training | "Switch to notebook, run 3 iterations, load weights" | Needs exact cell numbers (6, 7) and what to say during execution |
| 5: Training Convergence | "Loss drops steadily, full training ran to convergence" | Needs pointer to batch boundaries, what to emphasize |
| 6: Transition - Evaluation | "Back to notebook, run on test set" | Needs cell numbers (10, 11) |
| 7: Classification Accuracy | "Strong accuracy, validates learning" | Needs specific accuracy number to state verbally |
| 8: Transition - Hardware | "Real test, noise and decoherence" | Needs reference to D-05 dual strategy, live job status check |
| 9: Hardware Comparison | "Side-by-side, noise resilience" | Needs what to say about sim vs hw gap |
| 10: Key Takeaways | "Four things to remember" | Needs pacing guidance (pause between points) |
| 11: Q&A | "If asked about noise/scaling..." | Needs anticipated questions list |

## Timing Architecture

Based on the 11 slides and 14 notebook cells, here is the recommended timing structure for the 30-minute half:

| Section | Slides | Notebook Cells | Target Time | Notes |
|---------|--------|----------------|-------------|-------|
| Handoff + Intro | 1-2 | -- | 2 min | Receive from co-presenter, set context |
| Data Overview | 3 | 0-4 (setup, guard, data gen, viz) | 3 min | Show input grid figure, explain task |
| Training Demo | 4-5 | 5-9 (circuit, live train, load weights, loss curve) | 10 min | Heaviest section: live code + explanation |
| Evaluation | 6-7 | 10 (forward pass + accuracy) | 5 min | Run eval cell, discuss accuracy |
| Hardware Execution | 8-9 | 11-12 (hardware comparison) | 7 min | Show hardware results, discuss noise |
| Takeaways + Q&A | 10-11 | 13 (key findings) | 3 min | Summary, open for questions |
| **Buffer** | -- | -- | **~2 min** | Distributed across sections |
| **TOTAL** | | | **~30 min** | |

The training demo section (10 min) is the largest because it includes:
- Switching to notebook
- Running Cell 6 (live 3-iteration training -- variable time, typically 10-30 seconds)
- Running Cell 7 (load cached weights -- instant)
- Running Cell 9 (loss curve plot -- instant)
- Explaining what the audience is seeing at each step
- Switching back to slides for the convergence figure

## Hardware Fallback Decision Tree

From PITFALLS.md Pitfall 1 and Phase 1 decisions D-05/D-06:

```
Pre-talk (during co-presenter's half):
  -> Submit live hardware job via QVC_QNN.ipynb
  -> Note job ID and estimated queue time

When reaching Hardware section (Slide 8-9, ~22 min in):
  IF live_results.json exists:
    -> "We submitted this job during [co-presenter]'s half, and it completed!"
    -> Show live results (Cell 12 auto-detects live_results.json)
    -> Highlight "LIVE" annotation on figure
  ELSE IF hardware_results.json exists (always true -- cached):
    -> "We pre-ran this on IBM hardware yesterday. Let me show you those results."
    -> Cell 12 falls back to hardware_results.json automatically
    -> Do NOT apologize or dwell on the queue -- present it confidently
  ELSE (should never happen if Phase 1 cache exists):
    -> "Hardware results are being processed. Let me show you what we expect..."
    -> Show the simulator results and explain expected hardware degradation verbally
```

Key script language for the fallback: Do NOT say "unfortunately the hardware is slow" or "sorry, the queue was too long." Instead say "We pre-ran this on IBM Quantum hardware to ensure we have results to show you." This frames the cache as preparation, not failure.

## Co-Presenter Handoff Protocol (SCRP-04)

Two handoff points:

1. **Incoming handoff (start of your half):**
   - Co-presenter finishes circuit design section
   - Co-presenter says: "[Your name] will now show us this circuit in action"
   - You take the podium, advance to Slide 1 (your title slide)
   - Opening line: "Thanks [co-presenter]. You've seen the theory -- now let's train this classifier and run it on real hardware."

2. **Outgoing handoff (end of your half, if applicable):**
   - After Slide 11 (Q&A), if co-presenter handles closing
   - Verbal cue: "I'll hand it back to [co-presenter] for any final thoughts"
   - OR: if you handle Q&A jointly, no outgoing handoff needed

## Pre-Talk Checklist (for demo_script.md)

Items the presenter must verify before the talk:

- [ ] JupyterLab open with QVC_QNN_demo.ipynb
- [ ] JupyterLab font size increased (Ctrl/Cmd+= several times)
- [ ] JupyterLab sidebar collapsed
- [ ] Kernel restarted, no cells pre-executed
- [ ] Cache files present: trained_weights.json, training_history.json, hardware_results.json
- [ ] PowerPoint presentation.pptx open in presenter mode
- [ ] .env file with IBM_QUANTUM_API_KEY on demo machine (for optional live job)
- [ ] WiFi confirmed working (or mobile hotspot ready)
- [ ] Optional: submit hardware job during co-presenter's half (note job ID)
- [ ] Screen sharing / projector tested with both JupyterLab and PowerPoint

## Code Examples

No code is written in this phase. The demo_script.md is pure Markdown. Here is the recommended structure:

### demo_script.md Structure
```markdown
# QVC Conference Presentation - Demo Script

## Pre-Talk Checklist
- [ ] items...

## Timing Overview
| Section | Time | Duration | Slides | Notebook |
|---------|------|----------|--------|----------|

## [00:00-02:00] Handoff and Introduction
**Slides:** 1-2
**Actions:** [what to do]
**Say:** [what to say]

## [02:00-05:00] Data Overview
**Slides:** 3
**Notebook Cells:** 0-4
**Actions:** [switch to notebook, run cells]
**Say:** [talking points]

[... remaining sections ...]

## Hardware Fallback Decision Tree
[decision tree]

## Co-Presenter Handoff Protocol
[incoming/outgoing handoff details]

## Anticipated Questions
[Q&A preparation]
```

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.x (already in project) |
| Config file | none -- tests are in tests/ directory |
| Quick run command | `python -m pytest tests/ -x -q` |
| Full suite command | `python -m pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SCRP-01 | Timing breakdown present with minute marks | unit | `python -m pytest tests/test_demo_script.py::test_timing_breakdown -x` | Wave 0 |
| SCRP-02 | Speaker notes for all 11 slides and 3 demo segments | unit | `python -m pytest tests/test_demo_script.py::test_speaker_notes_coverage -x` | Wave 0 |
| SCRP-03 | Hardware fallback section with decision tree | unit | `python -m pytest tests/test_demo_script.py::test_hardware_fallback -x` | Wave 0 |
| SCRP-04 | Co-presenter handoff cues present | unit | `python -m pytest tests/test_demo_script.py::test_copresenter_handoff -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_demo_script.py -x -q`
- **Per wave merge:** `python -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_demo_script.py` -- covers SCRP-01 through SCRP-04 (validates demo_script.md content)
  - Tests parse the markdown file and check for: timing table with minute marks, speaker notes sections covering all slides, "fallback" section with hardware decision tree, "handoff" section with co-presenter cues
- No framework install needed (pytest already present)

### Test Strategy Notes
Since demo_script.md is a Markdown document, tests will:
- Read the file and check for required section headers
- Verify timing table has rows summing to ~30 minutes
- Check that all 11 slide numbers are referenced in speaker notes
- Verify "fallback" and "handoff" keywords appear in dedicated sections
- These are content-presence tests, not formatting tests

## Sources

### Primary (HIGH confidence)
- `slides/generate_deck.py` -- all 11 slide titles, layouts, and existing speaker notes read directly
- `QVC_QNN_demo.ipynb` -- all 14 cells read directly, execution flow understood
- `.planning/research/PITFALLS.md` -- Pitfalls 1, 2, 6, 8, 10 directly inform fallback and checklist
- `.planning/research/ARCHITECTURE.md` -- data flow and component boundaries confirmed
- `.planning/phases/01-caching-foundation/01-CONTEXT.md` -- D-05, D-06, D-07, D-08 decisions
- `.planning/REQUIREMENTS.md` -- SCRP-01 through SCRP-04 definitions

### Secondary (MEDIUM confidence)
- Timing estimates (10 min for training section, etc.) based on cell content analysis and typical conference pacing -- should be validated during actual rehearsal

### Tertiary (LOW confidence)
- None. All findings are based on direct analysis of existing project artifacts.

## Open Questions

1. **Co-presenter's name**
   - What we know: There is a co-presenter who handles intro/theory/circuit design
   - What's unclear: Their actual name for handoff cues in the script
   - Recommendation: Use placeholder "[co-presenter]" in the script; presenter fills in before rehearsal

2. **Exact cell execution times**
   - What we know: Cell 6 (live training) is the most variable, NTBK-04 requires <30s per cell
   - What's unclear: Actual execution time on the demo machine
   - Recommendation: Note in the script that Cell 6 timing should be measured during rehearsal

3. **Whether to update generate_deck.py speaker notes**
   - What we know: generate_deck.py has basic notes; demo_script.md will have enriched notes
   - What's unclear: Whether the user wants both kept in sync
   - Recommendation: Keep demo_script.md as the authoritative presenter document. Do NOT update generate_deck.py -- it serves a different purpose (slide generation). Avoids scope creep.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - no new tools needed, Markdown only
- Architecture: HIGH - single-file script pattern is well-understood; all input artifacts exist and were read
- Pitfalls: HIGH - all pitfalls derived from project's own PITFALLS.md and direct artifact analysis

**Research date:** 2026-03-24
**Valid until:** 2026-04-24 (stable -- conference presentation materials don't change rapidly)
