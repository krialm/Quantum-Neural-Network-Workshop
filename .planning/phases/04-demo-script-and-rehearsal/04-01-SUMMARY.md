---
phase: 04-demo-script-and-rehearsal
plan: 01
subsystem: documentation
tags: [markdown, presenter-script, timing, fallback, handoff, pytest]

# Dependency graph
requires:
  - phase: 03-slide-deck
    provides: "11-slide PowerPoint deck with speaker notes"
  - phase: 02-demo-notebook-and-visualizations
    provides: "14-cell demo notebook with projector-safe figures"
  - phase: 01-caching-foundation
    provides: "Cache JSON files for training weights, history, and hardware results"
provides:
  - "Complete 30-minute presenter script with timing marks, speaker notes, fallback plans, and handoff cues"
  - "Test suite validating SCRP-01 through SCRP-04 requirements"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Single-document presenter script with timing marks in section headers"
    - "Markdown content-presence tests parsing the script file"

key-files:
  created:
    - demo_script.md
    - tests/test_demo_script.py
  modified: []

key-decisions:
  - "Used [co-presenter] placeholder throughout -- presenter fills in before rehearsal"
  - "Rephrased fallback IMPORTANT note to avoid containing the word 'unfortunately' which would fail the no-apologetic-language test"
  - "Handoff test searches for 'Handoff Protocol' specifically to avoid matching the introduction section header"

patterns-established:
  - "Markdown content-presence testing: read file, extract section by heading, assert keywords"

requirements-completed: [SCRP-01, SCRP-02, SCRP-03, SCRP-04]

# Metrics
duration: 3min
completed: 2026-03-24
---

# Phase 4 Plan 1: Demo Script and Rehearsal Summary

**Complete 30-minute presenter script with timing table, enriched speaker notes for all 11 slides and 3 demo segments, hardware fallback decision tree, co-presenter handoff protocol, and 12-item pre-talk checklist**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-03-24T17:24:32Z
- **Completed:** 2026-03-24T17:27:32Z
- **Tasks:** 2
- **Files created:** 2

## Accomplishments
- Created demo_script.md (288 lines) as a single rehearsal document covering timing, speaker notes, fallback plans, and handoff cues
- Created tests/test_demo_script.py with 5 pytest tests validating all 4 SCRP requirements plus the pre-talk checklist
- Full test suite passes: 21 passed, 8 skipped (cache tests)

## Task Commits

No git commits made (user controls commits manually).

1. **Task 1: Create test suite for demo script validation** - tests/test_demo_script.py
2. **Task 2: Create demo_script.md with timing, speaker notes, fallback plan, and handoff cues** - demo_script.md

## Files Created/Modified
- `demo_script.md` - Complete presenter script for the 30-minute conference half
- `tests/test_demo_script.py` - 5 pytest tests validating SCRP-01 through SCRP-04 plus checklist

## Decisions Made
- Used `[co-presenter]` placeholder for the co-presenter's name throughout the script
- Rephrased the fallback instruction to avoid the literal word "unfortunately" appearing in the section (would trigger the no-apologetic-language test)
- Made handoff test search for "Handoff Protocol" to disambiguate from the "[00:00-02:00] Handoff and Introduction" section header

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fallback section contained test-triggering word**
- **Found during:** Task 2
- **Issue:** The instruction "Do NOT say 'unfortunately'" contained the word itself, causing test_hardware_fallback to fail
- **Fix:** Rephrased to "Do NOT use apologetic language"
- **Files modified:** demo_script.md
- **Verification:** test_hardware_fallback passes

**2. [Rule 1 - Bug] Handoff test matched wrong section**
- **Found during:** Task 2
- **Issue:** _get_section(content, "Handoff") matched "[00:00-02:00] Handoff and Introduction" instead of "Co-Presenter Handoff Protocol"
- **Fix:** Changed test to search for "Handoff Protocol" instead of "Handoff"
- **Files modified:** tests/test_demo_script.py
- **Verification:** test_copresenter_handoff passes

---

**Total deviations:** 2 auto-fixed (2 bugs)
**Impact on plan:** Minor test refinements. No scope creep.

## Issues Encountered
None beyond the two auto-fixed items above.

## User Setup Required
None - no external service configuration required.

## Known Stubs
None - demo_script.md is a complete document with no placeholder data or TODO items (the `[co-presenter]` placeholder is intentional and documented).

## Next Phase Readiness
- All 4 phases complete. The project deliverables are ready:
  - Cache infrastructure (Phase 1)
  - Demo notebook with visualizations (Phase 2)
  - PowerPoint slide deck (Phase 3)
  - Presenter script with timing, fallback, and handoff (Phase 4)
- Next step: rehearse with the actual demo machine and a stopwatch

## Self-Check: PASSED

---
*Phase: 04-demo-script-and-rehearsal*
*Completed: 2026-03-24*
