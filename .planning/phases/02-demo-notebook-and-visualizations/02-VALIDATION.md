---
phase: 2
slug: demo-notebook-and-visualizations
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-24
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (installed in Phase 1) |
| **Config file** | none — uses existing pytest setup |
| **Quick run command** | `python -m pytest tests/test_demo_notebook.py -x -q` |
| **Full suite command** | `python -m pytest tests/test_demo_notebook.py -v` |
| **Estimated runtime** | ~5 seconds (no kernel needed — structural tests only) |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_demo_notebook.py -x -q`
- **After every plan wave:** Run `python -m pytest tests/test_demo_notebook.py -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 02-01 | 1 | NTBK-01 | structural | `python -c "import json; nb=json.load(open('QVC_QNN_demo.ipynb')); assert len(nb['cells'])>=14"` | ❌ W0 | ⬜ pending |
| 02-01-01 | 02-01 | 1 | VIZ-01 | structural | `grep -c 'rcParams' QVC_QNN_demo.ipynb` | ❌ W0 | ⬜ pending |
| 02-01-01 | 02-01 | 1 | VIZ-02 | structural | `grep -c 'loss' QVC_QNN_demo.ipynb` | ❌ W0 | ⬜ pending |
| 02-01-01 | 02-01 | 1 | VIZ-03 | structural | `grep -c 'hardware' QVC_QNN_demo.ipynb` | ❌ W0 | ⬜ pending |
| 02-01-01 | 02-01 | 1 | VIZ-04 | structural | `grep -c 'imshow' QVC_QNN_demo.ipynb` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02-02 | 2 | NTBK-01, VIZ-01-04 | unit | `python -m pytest tests/test_demo_notebook.py -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_demo_notebook.py` — structural validation of notebook JSON (created in Plan 02-02)

*Existing infrastructure (pytest, conftest.py) covers framework needs.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Figures readable from back of room | VIZ-01 | Visual judgment | Open notebook, run all cells, view figures at 50% zoom |
| Loss curve shows clear convergence | VIZ-02 | Visual pattern recognition | Run training cells, check loss trend is clearly downward |
| Notebook runs top-to-bottom | NTBK-01 | Requires Jupyter + qiskit env | Kernel > Restart and Run All — no errors |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
