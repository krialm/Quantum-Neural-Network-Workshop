---
phase: 1
slug: caching-foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-24
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (not yet installed — Wave 0 installs) |
| **Config file** | none — Wave 0 creates pytest.ini |
| **Quick run command** | `python -m pytest tests/ -x -q` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/ -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | NTBK-02 | unit | `pytest tests/test_cache.py::test_weights_load` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | NTBK-03 | unit | `pytest tests/test_cache.py::test_hardware_results_load` | ❌ W0 | ⬜ pending |
| 01-01-03 | 01 | 1 | NTBK-05 | unit | `pytest tests/test_cache.py::test_both_ansatz_cached` | ❌ W0 | ⬜ pending |
| 01-01-04 | 01 | 1 | NTBK-04 | timing | `pytest tests/test_cache.py::test_cell_execution_time` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_cache.py` — stubs for NTBK-02, NTBK-03, NTBK-04, NTBK-05
- [ ] `tests/conftest.py` — shared fixtures (cache file paths, sample data)
- [ ] `pip install pytest` — framework not yet installed

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live hardware auto-detect | NTBK-03 | Requires IBM Quantum account and live job | Submit a test job, verify notebook detects and uses live results over cache |
| Cell timing under 30s | NTBK-04 | Jupyter cell timing depends on runtime environment | Run demo notebook cells, verify each completes in <30s via %%time |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
