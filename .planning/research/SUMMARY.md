# Project Research Summary

**Project:** QVC Conference Presentation
**Domain:** Technical conference presentation with live quantum ML demo
**Researched:** 2026-03-24
**Confidence:** MEDIUM-HIGH

## Executive Summary

This project is a 30-minute conference presentation delivering a polished Jupyter notebook live demo and a .pptx slide deck on Quantum Variational Circuits (VQC) for quantum machine learning classification. The recommended approach is a two-artifact system: a scripted `generate_deck.py` that produces the .pptx from embedded matplotlib figures, and a purpose-built demo notebook (`QVC_QNN_demo.ipynb`) that is a curated subset of the existing `QVC_QNN.ipynb`. The core philosophy is "boring technology that works reliably": static matplotlib figures over interactive JS plots, python-pptx over HTML slide frameworks, and JupyterLab as-is over slideshow plugins. The existing notebook stack (qiskit, numpy, matplotlib, scikit-learn, scipy) is already in place; the only new dependency that matters is python-pptx for slide generation. Everything installs via pip, runs locally, and produces artifacts (.pptx, .pkl, .png) that can be carried on a USB drive as backup.

The single most important risk is unreliable live execution. Two failure modes dominate: IBM Quantum hardware queue delays (5-60+ minutes on a shared system) and the VQC training loop taking 5-15 minutes on simulator. Both are preventable with a cache-first strategy: pre-run everything expensive before conference day, cache results as pickle files, and load them during the live demo. The live portion should execute only fast cells — model evaluation, visualization rendering, and optionally a new hardware job submission as a bonus. If this caching strategy is not implemented, demo failure is near-certain.

The secondary risk is environment drift. Qiskit has had breaking API changes across versions (0.x to 1.x, EstimatorV1 to V2). If the demo machine has a different version than the development machine, the demo fails on import or at runtime with no easy recovery during a talk. The mitigation is strict version pinning in requirements.txt and a full dry-run on the actual demo machine the day before.

## Key Findings

### Recommended Stack

The existing notebook stack is locked and should not change: qiskit (>=1.2), qiskit-ibm-runtime (>=0.28), numpy, matplotlib, scikit-learn, scipy, and python-dotenv are all already in use. The presentation layer adds python-pptx as the only essential new dependency — it is the only mature Python library that produces .pptx files directly, which is a hard project constraint. Supporting additions are seaborn (confusion matrix heatmaps), tqdm (progress bars for audience feedback), Pillow (required by python-pptx for image embedding), JupyterLab 4.x (improved rendering, better presentation mode), and nbconvert (pre-rendered HTML fallback if the live kernel fails).

**Core technologies:**
- `qiskit` + `qiskit-ibm-runtime`: Quantum circuit construction and IBM hardware access — already in notebook, locked
- `python-pptx`: Scripted .pptx generation — the only mature library producing the required format; version-controllable alongside the notebook
- `matplotlib` + `seaborn`: All visualizations — static figures embed cleanly into PowerPoint and render reliably on any projector
- `JupyterLab 4.x`: Live demo environment — standard, audience-recognizable; better rendering than VS Code notebooks
- `pickle` / `joblib`: Parameter and result caching — essential for cache-first strategy; no heavier tool needed
- `tqdm`: Progress bars — `tqdm.notebook` renders cleanly in JupyterLab; makes training playback believable
- `nbconvert`: Fallback rendering — pre-rendered HTML backup if live kernel fails

See `.planning/research/STACK.md` for full alternatives considered and version verification commands.

### Expected Features

**Must have (table stakes):**
- .pptx slide deck with clear structure — conference standard; organizers may require slides in advance
- Loss curve visualization — proves the model trains; audience expects to see convergence
- Accuracy metrics (train + test) — standard ML result reporting; already partially in notebook
- Circuit diagram visualization — visual anchor that makes the VQC concrete for the audience
- Live notebook execution — "live demo" means actually running code; pre-recorded video feels dishonest
- Speaker notes and demo script — 30-minute hard limit requires planned timing; co-presenter needs handoff marks
- Hardware vs simulator comparison — the core value proposition of the talk; shows quantum computing is real

**Should have (differentiators):**
- Confusion matrix heatmap — more informative than a single accuracy number; seaborn heatmap
- Side-by-side sim vs hardware bar chart — directly visualizes noise impact on real quantum hardware
- Pre-cached fallback for every live cell — seamless recovery if any cell fails; pickle/joblib
- Clean notebook with hidden setup cells — only relevant code visible; audience focus on concepts, not boilerplate

**Defer (after the talk):**
- Progressive per-epoch training visualization — static loss curve is sufficient; per-epoch snapshots add complexity
- Auto-regeneration pipeline (Makefile) — manual figure embedding is fine for a one-time event
- Audience follow-along notebook — this is a demo, not a workshop; share the link afterward

See `.planning/research/FEATURES.md` for anti-features to explicitly avoid (interactive Plotly/Bokeh, RISE slides, live hardware in critical path).

### Architecture Approach

The architecture is a two-artifact pipeline with a shared `figures/` directory as the integration point. The full original notebook (`QVC_QNN.ipynb`) serves as reference and pre-conference prep tool: run it to train the model, execute hardware jobs, and generate all figures. A purpose-built demo notebook (`QVC_QNN_demo.ipynb`) contains only the cells needed for the 30-minute presentation half, in presentation order, with cache-first loading for every expensive operation. A slide generation script (`slides/generate_deck.py`) reads the saved .png figures and assembles the final .pptx. A `cache/` directory stores trained parameters, hardware results, and training history as pickle files.

**Major components:**
1. `QVC_QNN_demo.ipynb` — polished demo notebook; runs top-to-bottom; loads from cache; exports figures to `figures/`
2. `cache/` directory — pre-trained params, hardware results, training history; written before conference day, read during demo
3. `figures/` directory — all matplotlib/seaborn .png outputs; integration point between notebook and slide generator
4. `slides/generate_deck.py` — python-pptx script; reads figures; writes `output/presentation.pptx`
5. `demo_script.md` — speaker notes with timing marks and fallback instructions for both presenters

See `.planning/research/ARCHITECTURE.md` for concrete code patterns: cache-first loader, rcParams defaults, figure export pattern, and slide generation pattern.

### Critical Pitfalls

1. **IBM Quantum queue delays** — Pre-run all hardware jobs before the conference. Cache results. Never put hardware submission in the critical demo path. Queue times are 15-60+ minutes on a shared system; your talk is 30 minutes.

2. **Training loop too slow live** — Pre-train and cache optimal parameters with pickle. Show the training code and explain it, but do not execute it live. Any cell taking >30 seconds needs a cached fallback.

3. **Qiskit API version mismatch** — Pin exact versions in requirements.txt. Test on the actual demo machine the day before. Never run `pip install --upgrade` on demo day. Diff `pip freeze` output between dev and demo machines.

4. **Projector readability failure** — Set matplotlib rcParams globally at notebook top: font size 16pt+, linewidth 2+, high-contrast colors. Test figures on an external monitor at arm's length before the conference.

5. **Notebook state pollution** — Design the demo notebook to run top-to-bottom with no skips. Test with Kernel > Restart and Run All before every rehearsal. Use cache-first cells so each cell is self-contained.

See `.planning/research/PITFALLS.md` for moderate pitfalls (WiFi failure, co-presenter handoff, python-pptx layout limitations) and minor pitfalls (missing .env, JupyterLab font size, stale figures in slides).

## Implications for Roadmap

The work separates into sequential phases where each phase's output is a hard dependency for the next. The critical path runs: caching foundation first (nothing else works reliably without it), then visualization polish (figures must exist and be final before slides), then slide generation, then demo rehearsal and coordination.

### Phase 1: Environment and Caching Foundation

**Rationale:** The cache-first strategy is the load-bearing constraint of the entire presentation. Everything downstream — the live demo, the slides, the fallback strategy — depends on having pre-computed results. Version pinning must also happen here, before any other work is done on the notebook, so the environment is stable throughout development.

**Delivers:** `requirements.txt` with pinned versions, `cache/` directory with `trained_params.pkl`, `hardware_results.pkl`, and `training_history.pkl`, and a working `load_or_compute()` utility function.

**Addresses:** Table-stakes feature "Live notebook execution" (the reliable version); enables "Hardware vs simulator comparison"

**Avoids:** Pitfall 1 (IBM queue delays), Pitfall 2 (slow training loop live), Pitfall 3 (version mismatch)

**Note:** Hardware caching requires IBM Quantum account access. Must be done when the quantum system is accessible, not the morning of the conference.

### Phase 2: Notebook Polish and Visualization

**Rationale:** With the cache in place, the demo notebook can be built and all figures generated. Setting matplotlib rcParams globally at this phase prevents projector readability failures from ever entering the pipeline. Figures must be final before slide generation is meaningful.

**Delivers:** `QVC_QNN_demo.ipynb` (presentation-order, cache-loading, clean cells), all figures in `figures/` directory (loss curve, accuracy comparison, confusion matrix, circuit diagram, hardware vs simulator bar chart), and projector-safe styling throughout.

**Uses:** matplotlib + seaborn with rcParams defaults (16pt+ fonts, thick lines, high-contrast colors), qiskit.visualization for circuit diagrams, tqdm for progress display, IPython.display for clean outputs

**Implements:** "Presentation-Quality Figure Defaults" and "Figure Export Alongside Display" architecture patterns from ARCHITECTURE.md

**Avoids:** Pitfall 4 (projector readability), Pitfall 5 (notebook state pollution)

### Phase 3: Slide Deck Generation

**Rationale:** Once all figures exist in `figures/`, the slide deck can be generated programmatically. python-pptx handles structure and figure embedding; a manual polish pass in PowerPoint handles branding and transitions afterward. Keeping generation scripted ensures figures stay in sync with the notebook across revisions.

**Delivers:** `slides/generate_deck.py`, `output/presentation.pptx` with all required slides and embedded speaker notes, plus a manual polish pass for visual quality.

**Uses:** python-pptx, Pillow (image embedding), figures from Phase 2

**Implements:** "Slide Generation Script" architecture pattern from ARCHITECTURE.md

**Avoids:** Pitfall 7 (python-pptx layout limitations) — the manual polish pass is not optional; plan for it explicitly

### Phase 4: Demo Script and Rehearsal

**Rationale:** A written demo script with timing marks is table-stakes for a 30-minute split presentation with a co-presenter. Rehearsal validates the full pipeline runs top-to-bottom without intervention and catches any remaining issues in a controlled setting, not on presentation day.

**Delivers:** `demo_script.md` with per-section timing, fallback instructions, and co-presenter handoff marks; confirmed Kernel > Restart and Run All success; completed pre-demo checklist (.env on demo machine, JupyterLab font size verified, version match confirmed on demo machine).

**Avoids:** Pitfall 5 (state pollution — rehearsal confirms clean run), Pitfall 6 (WiFi failure — rehearsal confirms full offline capability), Pitfall 8 (co-presenter handoff awkwardness), Pitfall 9 (missing .env), Pitfall 10 (JupyterLab font size)

### Phase Ordering Rationale

- Phase 1 before Phase 2: The demo notebook will stall on training cells without the cache in place. Do not build the notebook before the cache exists.
- Phase 2 before Phase 3: Slides embed figures by file path. Figures must be final before slide generation produces a usable output.
- Phase 3 before Phase 4: Rehearsal must use the final slide deck and notebook together, not a draft. The co-presenter needs actual slides for coordination and timing.
- Hardware caching (Phase 1) must happen when IBM Quantum access is available — not under time pressure the week of the conference.

### Research Flags

Phases with standard patterns (skip deeper research):
- **Phase 2 (Visualization):** matplotlib rcParams and seaborn heatmaps are extremely well-documented. `circuit.draw('mpl')` is standard qiskit usage.
- **Phase 3 (Slide generation):** python-pptx has extensive documentation and examples for exactly this use case.
- **Phase 4 (Rehearsal):** No novel technical decisions; coordination and process work only.

Phases that may benefit from spot research during planning:
- **Phase 1 (Caching/Environment):** Verify current qiskit-ibm-runtime primitives interface before pinning versions. IBM has been iterating on EstimatorV1 vs V2. Run `pip index versions qiskit qiskit-ibm-runtime` to confirm current releases.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Core stack (qiskit, numpy, matplotlib) is HIGH — already proven in the notebook. python-pptx and JupyterLab additions are HIGH. Exact qiskit/qiskit-ibm-runtime version numbers are MEDIUM — IBM iterates frequently; verify before pinning |
| Features | HIGH | Requirements derived directly from PROJECT.md and the existing notebook. Conference presentation best practices are well-established and consistent across sources |
| Architecture | HIGH | Two-artifact system with shared figures/ directory is a clean, proven pattern with clear component boundaries and no ambiguous responsibilities |
| Pitfalls | HIGH | IBM Quantum queue behavior and VQC training time are well-understood failure modes specific to this domain. Version mismatch and projector readability are universal live demo risks with established mitigations |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **Exact qiskit/qiskit-ibm-runtime versions:** Research used training data with cutoff ~May 2025. Run `pip index versions qiskit qiskit-ibm-runtime` on the target machine before pinning requirements.txt. Confirm EstimatorV2 is still the current primitives interface.

- **Demo machine environment:** All research assumes the development machine and demo machine can be made identical via a shared virtualenv or conda env. If the demo machine is a shared conference computer with a locked environment, the strategy changes — bring a personal laptop you fully control.

- **IBM Quantum hardware access:** Hardware caching in Phase 1 assumes an active IBM Quantum account with real device access. Verify account status and device availability before beginning Phase 1, not after.

- **Co-presenter scope:** This research addresses only one presenter's 30-minute half. The co-presenter's notebook cells, figures, and slides are out of scope but need coordination during Phase 4 to ensure style consistency and a clean handoff slide.

## Sources

### Primary (HIGH confidence)
- `QVC_QNN.ipynb` — direct analysis of existing imports, structure, training loop, and hardware access pattern
- `PROJECT.md` — hard constraints (.pptx format, 30-minute split, live demo requirement, co-presenter split)

### Secondary (MEDIUM confidence)
- Training data knowledge (cutoff ~May 2025) — library recommendations, conference demo best practices, IBM Quantum operational characteristics (queue times, device availability patterns)

### Tertiary (LOW confidence — verify before use)
- Version numbers for qiskit and qiskit-ibm-runtime — fast-moving projects; run `pip index versions` to confirm current releases before pinning

---
*Research completed: 2026-03-24*
*Ready for roadmap: yes*
