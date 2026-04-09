# Phase 1: Caching Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-24
**Phase:** 01-caching-foundation
**Areas discussed:** Ansatz selection, Cache format, Hardware pre-run, Demo flow strategy

---

## Ansatz Selection

| Option | Description | Selected |
|--------|-------------|----------|
| Revised ansatz only | Show only the better-performing one. Simpler narrative, less time. | |
| Both as a story | Show first ansatz failing/underperforming, then revised succeeding. | |
| You decide | Claude picks based on which produces cleaner results | ✓ |

**User's choice:** You decide
**Notes:** Claude has discretion to pick the primary ansatz based on result quality

| Option | Description | Selected |
|--------|-------------|----------|
| Pre-computed backup | Cache both, show comparison if time allows | ✓ |
| Omit entirely | Keep it simple — one ansatz, one story | |
| You decide | Claude decides based on demo timing | |

**User's choice:** Pre-computed backup
**Notes:** Both ansatz results cached; alternative available as backup comparison

---

## Cache Format

| Option | Description | Selected |
|--------|-------------|----------|
| JSON files | Human-readable, easy to inspect and debug | ✓ |
| Numpy .npz | Native numpy format, fast array loading | |
| You decide | Claude picks best format for demo reliability | |

**User's choice:** JSON files

| Option | Description | Selected |
|--------|-------------|----------|
| cache/ directory | Dedicated folder at project root | |
| Same directory | Alongside the notebook | ✓ |
| You decide | Claude picks based on project structure | |

**User's choice:** Same directory

---

## Hardware Pre-run

| Option | Description | Selected |
|--------|-------------|----------|
| Pre-run before talk | Submit job hours/days before, cache results | |
| Fire during co-pres | Submit during co-presenter's 30 min, check when your half starts | |
| Both strategies | Pre-cache as fallback, also try live during co-presenter's half | ✓ |

**User's choice:** Both strategies

| Option | Description | Selected |
|--------|-------------|----------|
| Auto-detect | Check for live results first, fall back to cache | ✓ |
| Manual switch | Decide on stage whether to show live or cached | |
| You decide | Claude picks safer approach | |

**User's choice:** Auto-detect

---

## Demo Flow Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Few live iterations | Run 2-3 iterations live, then load pre-trained weights | ✓ |
| Skip training live | Load pre-trained weights directly | |
| You decide | Claude picks based on timing | |

**User's choice:** Few live iterations

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, toggle cell | DEMO_MODE = True at top of notebook | |
| Separate notebook | Create separate demo notebook with only presentation cells | ✓ |
| You decide | Claude picks safest approach | |

**User's choice:** Separate notebook

---

## Claude's Discretion

- Primary ansatz selection (based on result quality)
- Exact JSON schema for cache files
- Number of live training iterations (2-3 range)
- Auto-detection logic implementation
- Demo notebook structure

## Deferred Ideas

None — discussion stayed within phase scope
