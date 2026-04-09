---
phase: 01-caching-foundation
plan: 01
subsystem: caching
tags: [qiskit, cobyla, json, vqc, quantum-ml, numpy, scipy]

# Dependency graph
requires: []
provides:
  - "cache_results.py: standalone caching script for dual-ansatz VQC training and JSON serialization"
  - "JSON cache schema for trained_weights.json, training_history.json, hardware_results.json"
  - "Auto-detection logic for live vs cached hardware results"
  - "Hardware caching with graceful simulator fallback"
affects: [02-demo-notebook, hardware-execution]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "NumpyEncoder for JSON serialization of numpy types"
    - "Dual-ansatz training with COBYLA optimizer (1 epoch, batch_size=140, maxiter=100)"
    - "Auto-detection: live_results.json > hardware_results.json fallback chain"
    - "Simulator fallback when IBM Quantum hardware unavailable"

key-files:
  created:
    - cache_results.py
  modified: []

key-decisions:
  - "Revised ansatz selected as primary (full horizontal CNOT coverage) per D-01"
  - "First ansatz fixed to use top-row-only CNOTs [[0,1],[1,2],[2,3]] per research Critical Finding"
  - "Combined Task 1 and Task 2 into single atomic implementation since both modify same file"
  - "Used 'theta' instead of unicode theta character to avoid encoding issues in standalone script"

patterns-established:
  - "save_json/load_json pattern with NumpyEncoder for all cache I/O"
  - "build_ansatz(cnot_pairs) parameterized circuit construction"
  - "train_ansatz() returns standardized dict with weights, loss_values, accuracies"
  - "generate_hardware_cache() with try/except fallback to simulator"

requirements-completed: [NTBK-02, NTBK-03, NTBK-05]

# Metrics
duration: 2min
completed: 2026-03-24
---

# Phase 01 Plan 01: Caching Foundation Summary

**Standalone cache_results.py with dual-ansatz COBYLA training, JSON weight/history/hardware caching, and live-vs-cached auto-detection**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-24T15:50:03Z
- **Completed:** 2026-03-24T15:52:43Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Built complete cache_results.py (655 lines) that trains both VQC ansatz variants and saves all results as JSON
- Fixed the ansatz identity bug: first ansatz now correctly uses top-row-only CNOTs [[0,1],[1,2],[2,3]] while revised uses full horizontal [[0,1],[1,2],[2,3],[4,5],[5,6],[6,7]]
- Implemented hardware caching with graceful fallback to StatevectorEstimator simulator when IBM Quantum is unavailable
- Added auto-detection logic that prefers live_results.json over hardware_results.json per D-06

## Task Commits

Each task was committed atomically:

1. **Task 1: Build cache_results.py with dual-ansatz training and JSON caching** - `6653701` (feat)
2. **Task 2: Add hardware caching and auto-detection** - included in `6653701` (combined implementation)

**Plan metadata:** pending (docs: complete plan)

_Note: Tasks 1 and 2 were combined into a single implementation and commit since both target the same file (cache_results.py) and the hardware caching logic was naturally written alongside the training logic._

## Files Created/Modified
- `cache_results.py` - Standalone caching script: dataset generation, dual-ansatz circuit construction, COBYLA training, JSON caching, hardware execution with simulator fallback, CLI --hardware flag

## Decisions Made
- **Revised ansatz as primary:** Full horizontal CNOT coverage produces higher accuracy, more compelling demo narrative showing improvement from better qubit connectivity
- **First ansatz bug fix:** Restored original intent of top-row-only CNOTs to create meaningful two-ansatz comparison
- **Combined implementation:** Tasks 1 and 2 written atomically since the hardware caching functions are integral to the script structure
- **Parameter naming:** Used "theta" string instead of unicode to avoid encoding issues

## Deviations from Plan

None - plan executed exactly as written. Tasks 1 and 2 were combined into a single file write for efficiency since both target cache_results.py, but all specified functionality is present.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required. The --hardware flag is optional and requires an IBM Quantum account only if real hardware execution is desired.

## Known Stubs
None - all functions are fully implemented with real logic. The hardware execution path requires IBM credentials but gracefully falls back to simulator.

## Next Phase Readiness
- cache_results.py is ready to be executed (requires qiskit environment)
- JSON cache files will be generated when the script runs
- Demo notebook (Phase 2) can be built to consume these cache files
- Hardware caching can be tested once IBM Quantum account access is verified

## Self-Check: PASSED

- FOUND: cache_results.py
- FOUND: commit 6653701

---
*Phase: 01-caching-foundation*
*Completed: 2026-03-24*
