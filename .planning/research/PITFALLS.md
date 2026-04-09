# Domain Pitfalls

**Domain:** Technical conference presentation with live quantum ML demo
**Researched:** 2026-03-24

## Critical Pitfalls

Mistakes that cause demo failure or major presentation issues.

### Pitfall 1: IBM Quantum Hardware Queue Delays
**What goes wrong:** You submit a job to IBM Quantum hardware during the live demo. The queue is 15-60+ minutes. Your talk is 30 minutes. You stand there waiting.
**Why it happens:** IBM Quantum is a shared resource. Queue times are unpredictable and vary by device, time of day, and system maintenance schedules.
**Consequences:** Dead air during your talk. Audience loses interest. You run over time. Co-presenter's section gets cut.
**Prevention:** Pre-run all hardware jobs before the conference. Cache results in pickle files. Show cached hardware results as "here is what we got when we ran this yesterday." Optionally submit a new job live as a bonus -- "we will check the results at the end if it finishes."
**Detection:** If your demo plan includes "wait for hardware results" as a blocking step, you have this pitfall.

### Pitfall 2: Training Loop Takes Too Long Live
**What goes wrong:** Running 50-100 iterations of VQC training with scipy.optimize.minimize takes 5-15 minutes even on simulator. Audience watches a progress bar for half your talk.
**Why it happens:** Each iteration requires multiple circuit evaluations. StatevectorEstimator is faster than hardware but still not instant for iterative optimization.
**Consequences:** Boring demo. Time pressure on remaining sections. Cannot recover if it hangs or errors.
**Prevention:** Pre-train and cache optimal parameters. Load cached params live. Show the training code and explain it, but skip execution. Show the pre-computed loss curve as evidence training was done.
**Detection:** Time any cell that takes >30 seconds. If it is in the live demo path, it needs caching.

### Pitfall 3: Qiskit API Version Mismatch
**What goes wrong:** You develop the notebook on one version of qiskit/qiskit-ibm-runtime, but the demo machine has a different version. Imports fail, APIs have changed, transpilation behaves differently.
**Why it happens:** Qiskit has been through major API changes (0.x to 1.x migration). qiskit-ibm-runtime iterates on primitives (EstimatorV1 to V2). Even minor updates can change behavior.
**Consequences:** Import errors or runtime errors during live demo. Cannot recover without debugging, which is not possible during a talk.
**Prevention:** Pin exact versions in requirements.txt. Test on the actual demo machine the day before. Use a virtualenv/conda env specific to this presentation. Never `pip install --upgrade` on demo day.
**Detection:** Run `pip freeze` on dev machine and demo machine. Diff the outputs.

### Pitfall 4: Projector Resolution and Color Issues
**What goes wrong:** Figures that look great on your laptop are unreadable on the conference projector. Small fonts, thin lines, low-contrast colors (light blue on white), and default matplotlib sizing all fail on projectors.
**Why it happens:** Conference projectors have lower resolution, lower contrast, and different color reproduction than laptop screens. Rooms may be bright.
**Consequences:** Audience cannot read your visualizations. The core evidence of your talk is invisible.
**Prevention:** Set matplotlib rcParams for large fonts (16pt+), thick lines (linewidth 2+), high-contrast colors (dark blue, red, black on white). Test figures on an external monitor at arm's length. If you can read it at arm's length on a laptop screen, it is probably fine on a projector.
**Detection:** Squint at your figures. If you have to lean in to read axis labels, they are too small.

## Moderate Pitfalls

### Pitfall 5: Notebook State Pollution
**What goes wrong:** You run cells out of order during the demo, or a cell depends on state from a cell you skipped. NameError, KeyError, or wrong values silently used.
**Prevention:** Design the demo notebook to be run top-to-bottom with no skips. If you must skip cells, use the cache-first pattern so each cell is self-contained. Test by doing Kernel > Restart and Run All before every rehearsal.

### Pitfall 6: WiFi Failure at Venue
**What goes wrong:** IBM Quantum access requires internet. Conference WiFi is notoriously unreliable. Your hardware demo cell hangs or errors.
**Prevention:** All hardware results are pre-cached. The entire demo can run offline except the optional "bonus" hardware submission. Bring a mobile hotspot as backup if you want to attempt live hardware.

### Pitfall 7: python-pptx Layout Limitations
**What goes wrong:** python-pptx produces functional but plain slides. No transitions, limited animation, basic text formatting compared to manual PowerPoint editing.
**Prevention:** Accept this limitation. Use python-pptx for structure and figure embedding. Do final visual polish (transitions, alignment tweaks, branding) manually in PowerPoint after generation. The script gets you 80% there; manual polish does the last 20%.

### Pitfall 8: Co-Presenter Handoff Awkwardness
**What goes wrong:** Unclear transition between your half and co-presenter's half. Duplicate content. Mismatched slide styles. Awkward "okay your turn" moment.
**Prevention:** Agree on exact handoff point, shared slide template, and transition slide. Practice the handoff at least once. Share slide decks in advance for style consistency.

## Minor Pitfalls

### Pitfall 9: Forgotten .env File on Demo Machine
**What goes wrong:** IBM Quantum API token is in .env on your dev machine but not on the demo laptop.
**Prevention:** Add .env setup to your pre-demo checklist. Or hardcode a fallback that detects missing .env and prints a clear message instead of crashing.

### Pitfall 10: JupyterLab Font Size Too Small
**What goes wrong:** Code cells and output text are unreadable on the projector at default JupyterLab font size.
**Prevention:** Increase JupyterLab font size before the demo: Settings > Theme > Increase Content Font Size (Ctrl/Cmd + = several times). Practice at the target font size so you know cells still fit on screen.

### Pitfall 11: Matplotlib Figure Not Saved Before Slide Generation
**What goes wrong:** You update a visualization in the notebook but forget to re-save the .png. The slide generator uses the stale figure.
**Prevention:** Every visualization cell should both display and save to figures/. Run all notebook cells before running the slide generator. Consider a Makefile or script that runs notebook then generates slides.

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Notebook polish | State pollution from cell reordering | Test Kernel > Restart and Run All after every edit |
| Visualization | Projector readability | Set rcParams globally; test on external monitor |
| Slide generation | python-pptx layout limitations | Plan for manual polish pass after generation |
| Hardware caching | API version mismatch with runtime | Pin versions; test on demo machine |
| Demo rehearsal | Training loop too slow | Cache everything >30 seconds; only run viz and eval live |
| Presentation day | WiFi failure, queue delays | Full offline capability; all results pre-cached |

## Sources

- PROJECT.md constraints (IBM Quantum dependency, .pptx format, 30-minute time limit)
- QVC_QNN.ipynb analysis (training loop structure, hardware access pattern)
- Training data knowledge of conference demo failure modes and quantum computing operational challenges
