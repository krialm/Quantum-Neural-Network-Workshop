---
phase: 02-demo-notebook-and-visualizations
plan: 01
subsystem: notebook
tags: [jupyter, matplotlib, visualization, demo]
dependency_graph:
  requires: [cache_results.py, trained_weights.json, training_history.json, hardware_results.json]
  provides: [QVC_QNN_demo.ipynb, figures/input_data_grid.png, figures/loss_curve.png, figures/hardware_comparison.png]
  affects: [Phase 3 slide deck (figures embedded), Phase 4 demo script (notebook flow)]
tech_stack:
  added: []
  patterns: [rcParams projector-safe block, cache-first cell structure, dual output display+save]
key_files:
  created: [QVC_QNN_demo.ipynb, figures/]
  modified: []
decisions:
  - Used import from cache_results.py (not copy) for generate_dataset, build_ansatz, build_full_circuit, forward, mse_loss
  - maxiter=3 for live training demo (upper end of D-07 range)
  - Notebook written as raw .ipynb JSON (no nbformat library needed)
metrics:
  duration: 2min
  completed: 2026-03-24
---

# Phase 02 Plan 01: Demo Notebook with Visualizations Summary

14-cell Jupyter notebook (QVC_QNN_demo.ipynb) with projector-safe rcParams (16pt+ fonts, 2.5 linewidth, high-contrast palette), three savefig outputs (input_data_grid.png, loss_curve.png, hardware_comparison.png), live 3-iteration training demo, and D-06 hardware auto-detection.

## What Was Done

### Task 1: Create QVC_QNN_demo.ipynb with all cells in presentation order

Created the complete demo notebook as valid .ipynb JSON (nbformat 4, nbformat_minor 5) with 14 cells in exact presentation order:

1. **Markdown: Title and Overview** - Introduces the QVC classifier demo
2. **Code: Setup** - Imports, rcParams block with all projector-safe settings, COLORS palette, figures/ directory creation
3. **Code: Cache File Guard** - Checks for all three JSON cache files, prints clear error if missing
4. **Markdown: Data Overview** - Explains the 2x4 pixel grid classification task
5. **Code: Data Generation + VIZ-04** - Imports generate_dataset from cache_results.py, produces 2x4 input data grid with horizontal/vertical examples, saves to figures/input_data_grid.png
6. **Markdown: Circuit Explanation** - Describes the VQC approach (feature map, ansatz, measurement)
7. **Code: Live Training Demo (D-07)** - Imports build_ansatz, build_full_circuit, forward, mse_loss from cache_results; runs 3 COBYLA iterations on 20 samples for visual effect
8. **Code: Load Cached Weights** - Loads trained_weights.json, prints primary ansatz details and accuracy
9. **Markdown: Training Results** - Introduces the loss curve visualization
10. **Code: VIZ-02 Loss Curve** - Loads training_history.json, plots loss convergence with batch boundary markers, saves to figures/loss_curve.png
11. **Code: Evaluation** - Forward pass on test set with cached weights, accuracy calculation via sklearn
12. **Markdown: Hardware Results** - Introduces simulator vs hardware comparison
13. **Code: VIZ-03 Hardware Comparison** - Auto-detects live_results.json > hardware_results.json (D-06), bar chart with value labels, saves to figures/hardware_comparison.png
14. **Markdown: Key Findings** - Summary of results and implications

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

All automated checks passed:
- Notebook is valid nbformat 4 with 14 cells (6 markdown + 8 code)
- rcParams block present with font.size 16, axes.titlesize 22, lines.linewidth 2.5
- Three fig.savefig calls: input_data_grid.png, loss_curve.png, hardware_comparison.png
- Imports from cache_results: generate_dataset, build_ansatz, build_full_circuit, forward, mse_loss
- Auto-detect pattern: live_results.json check present
- All three cache file loads: trained_weights.json, training_history.json, hardware_results.json

## Known Stubs

None - all cells contain complete implementation code. Figures are generated at runtime when notebook is executed (not pre-rendered stubs).

## Self-Check: PASSED

- QVC_QNN_demo.ipynb: EXISTS at project root
- figures/ directory: EXISTS
- All verification scripts: PASSED
