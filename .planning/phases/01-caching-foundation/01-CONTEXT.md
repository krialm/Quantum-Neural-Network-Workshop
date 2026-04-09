# Phase 1: Caching Foundation - Context

**Gathered:** 2026-03-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Pre-compute and cache all expensive operations (model training, hardware execution) so the live conference demo loads results instantly. Build the caching infrastructure that Phase 2 (demo notebook) will consume.

</domain>

<decisions>
## Implementation Decisions

### Ansatz Selection
- **D-01:** Claude picks the primary ansatz based on which produces cleaner, more compelling results for the audience
- **D-02:** Both ansatz results are cached — primary for the demo, alternative as pre-computed backup comparison if time allows or audience asks

### Cache Format
- **D-03:** All cached data stored as JSON files (human-readable, easy to inspect and debug)
- **D-04:** Cache files live alongside the notebook in the project root (e.g., `trained_weights.json`, `hardware_results.json`), not in a subdirectory

### Hardware Pre-run
- **D-05:** Dual hardware strategy: pre-run jobs hours/days before the conference AND attempt live submission during co-presenter's 30-minute half
- **D-06:** Notebook auto-detects if live hardware results are available and uses them over cached results; falls back to cache if live results aren't ready

### Demo Flow Strategy
- **D-07:** Live demo runs 2-3 training iterations to show the loop working, then loads full pre-trained weights from cache
- **D-08:** Create a separate demo notebook (not a toggle in the original) — the demo notebook contains only presentation cells

### Claude's Discretion
- Which ansatz to select as primary (based on result quality)
- Exact JSON schema for cache files
- How many live training iterations to run (2-3 range)
- Auto-detection logic for live vs cached hardware results
- How to structure the separate demo notebook

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

No external specs — requirements fully captured in decisions above.

### Notebook
- `QVC_QNN.ipynb` — Source notebook with both ansatz implementations, training loops, and hardware execution cells

### Research
- `.planning/research/PITFALLS.md` — Hardware queue delays, training time, dual-ansatz trap
- `.planning/research/ARCHITECTURE.md` — Presentation flow, fallback architecture
- `.planning/research/STACK.md` — Technology choices and version concerns

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Training loop with COBYLA optimizer (maxiter=100, 3 batches) — needs to be wrapped with cache save/load
- Hardware execution via `least_busy()` backend selection — needs cache layer around it
- Both ansatz circuit definitions — can be extracted and evaluated independently

### Established Patterns
- `python-dotenv` for IBM API credentials — reuse for hardware access
- `scipy.optimize.minimize` for training — standard pattern to wrap
- `QiskitRuntimeService` for backend access — established connection pattern

### Integration Points
- Training loop produces optimized weight parameters — these become the cache payload
- Hardware execution produces measurement results — these become the hardware cache payload
- The separate demo notebook will import/load from cache files created in this phase

</code_context>

<specifics>
## Specific Ideas

- JSON cache files should be human-inspectable so the presenter can verify results before the talk
- Auto-detect logic for hardware: check for a "live_results.json" or similar marker file that gets written when a live job completes
- The few live training iterations should produce visible output (print statements or progress) so the audience sees something happening

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-caching-foundation*
*Context gathered: 2026-03-24*
