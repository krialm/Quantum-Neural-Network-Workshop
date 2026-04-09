# Phase 2: Demo Notebook and Visualizations - Research

**Researched:** 2026-03-24
**Domain:** Jupyter notebook authoring, matplotlib visualization, conference presentation graphics
**Confidence:** HIGH

## Summary

Phase 2 creates a separate demo notebook (`QVC_QNN_demo.ipynb`) that loads pre-cached results from Phase 1's JSON files and produces projector-readable visualizations. The notebook must run top-to-bottom in under 30 seconds per cell, following the presentation flow: training demo (2-3 live iterations + load cached weights) -> evaluation -> hardware results comparison.

The primary technical work is (1) authoring a new `.ipynb` notebook programmatically or manually, (2) setting matplotlib rcParams for projector readability, (3) implementing four specific visualization types, and (4) saving all figures to `figures/` for later use in Phase 3 slides. All data is already available from Phase 1's `trained_weights.json`, `training_history.json`, and `hardware_results.json`.

**Primary recommendation:** Build the demo notebook as a hand-written `.ipynb` (not generated with nbformat -- nbformat is not installed and not needed for a single notebook). Use a matplotlib style block at the top with 16pt+ fonts, 2+ linewidth, high-contrast colors. Each visualization cell should both `plt.show()` and `fig.savefig()` to the `figures/` directory.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| NTBK-01 | Demo notebook with cells reorganized for presentation flow (training -> eval -> hardware) | Phase 1 provides all JSON caches; demo notebook loads them in presentation order; D-08 mandates separate notebook |
| VIZ-01 | Projector-safe matplotlib settings (large fonts, high contrast) | rcParams block documented in Architecture Patterns section; matplotlib 3.10.7 available |
| VIZ-02 | Loss curve plot that renders cleanly during demo | training_history.json provides loss_values and batch_boundaries for both ansatz |
| VIZ-03 | Simulator vs hardware results comparison plot | hardware_results.json provides expectation_values, predictions, test_accuracy; simulator results from trained_weights.json |
| VIZ-04 | Input data grid visualization (2x4 pixel patterns) | generate_dataset() function pattern from cache_results.py / original notebook cell 7 |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- **GSD Workflow:** All edits through GSD commands; no direct repo edits outside workflow
- **Naming:** Snake_case for functions/variables; descriptive names preferred over abbreviations
- **Type hints:** Used in function signatures with return annotations
- **Imports:** `import numpy as np`, `import matplotlib.pyplot as plt` standard aliases
- **Error handling:** Minimal; print statements for status (no logging framework)
- **Comments:** Explain non-obvious logic; domain-specific comments for quantum concepts
- **No linter/formatter enforced**
- **Cache files in project root** (D-04): `trained_weights.json`, `training_history.json`, `hardware_results.json`
- **JSON format** (D-03): human-readable with NumpyEncoder
- **Auto-detection** (D-06): `live_results.json` > `hardware_results.json`
- **Separate demo notebook** (D-08): not a toggle in the original
- **Revised ansatz is primary** (D-01): full horizontal CNOT coverage
- **2-3 live training iterations then load weights** (D-07)

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| matplotlib | 3.10.7 | All visualizations (loss curves, data grids, bar charts) | Already installed; only viz library in project |
| numpy | 1.26.4 | Array operations for data manipulation | Already installed; used throughout project |
| json (stdlib) | N/A | Load Phase 1 cache files | No additional dependency; JSON is the cache format |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| scipy | 1.15.3 | COBYLA optimizer for 2-3 live training iterations | Already installed; needed for live training demo |
| qiskit | (needs install) | Circuit construction and StatevectorEstimator for live iterations | Required for the 2-3 live training iteration cells |
| sklearn | (needs install) | accuracy_score for evaluation display | Required for accuracy calculation in eval cells |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| matplotlib | Plotly/Bokeh | Out of scope per REQUIREMENTS.md ("Static plots more reliable on projectors") |
| Hand-coded .ipynb | nbformat library | nbformat not installed; overkill for a single notebook; can write JSON directly or copy-edit |

## Architecture Patterns

### Recommended Project Structure
```
Quantum_Variational_Circuits/
  QVC_QNN.ipynb              # Original (reference, do not modify)
  QVC_QNN_demo.ipynb         # NEW: Polished demo notebook
  cache_results.py           # Phase 1 output
  trained_weights.json       # Phase 1 cache (generated by running cache_results.py)
  training_history.json      # Phase 1 cache
  hardware_results.json      # Phase 1 cache
  figures/                   # NEW: Saved figures for Phase 3 slides
    input_data_grid.png
    loss_curve.png
    hardware_comparison.png
```

### Pattern 1: Projector-Safe rcParams Block
**What:** Set matplotlib defaults once at notebook top
**When to use:** First code cell of demo notebook
**Example:**
```python
import matplotlib.pyplot as plt
import numpy as np

# Projector-friendly defaults (VIZ-01)
plt.rcParams.update({
    'font.size': 16,
    'axes.titlesize': 22,
    'axes.labelsize': 18,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 14,
    'figure.figsize': (12, 7),
    'figure.dpi': 100,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'lines.linewidth': 2.5,
    'axes.linewidth': 1.5,
    'axes.grid': True,
    'grid.alpha': 0.3,
})

# High-contrast color palette for projector visibility
COLORS = {
    'primary': '#1f77b4',    # Strong blue
    'secondary': '#d62728',  # Strong red
    'accent': '#2ca02c',     # Strong green
    'dark': '#333333',       # Near-black for text
}
```

### Pattern 2: Cache-First Cell Structure
**What:** Each cell loads from JSON cache, no expensive computation
**When to use:** Every cell that would otherwise require training or hardware access
**Example:**
```python
import json
from pathlib import Path

def load_json(filepath: str) -> dict:
    """Load a JSON cache file."""
    with open(filepath) as f:
        return json.load(f)

# Load pre-trained weights (skips 5-15 min training)
weights_data = load_json("trained_weights.json")
primary = weights_data["primary_ansatz"]
print(f"Loaded {primary['name']} ansatz: {primary['num_parameters']} parameters")
print(f"Train accuracy: {primary['training']['train_accuracy']:.1f}%")
print(f"Test accuracy:  {primary['training']['test_accuracy']:.1f}%")
```

### Pattern 3: Dual Output (Display + Save)
**What:** Every figure cell calls both `plt.show()` and `fig.savefig()`
**When to use:** Every visualization cell
**Example:**
```python
import os
os.makedirs("figures", exist_ok=True)

fig, ax = plt.subplots()
# ... plotting code ...
fig.savefig("figures/loss_curve.png")
plt.show()
```

### Pattern 4: Demo Notebook Presentation Flow
**What:** Cells ordered for 30-minute live presentation narrative
**When to use:** The overall notebook structure

Recommended cell order:
1. **Setup cell:** imports + rcParams + color definitions
2. **Data overview cell:** generate_dataset() + VIZ-04 input grid
3. **Circuit explanation cell:** markdown describing the VQC approach
4. **Live training demo cell:** 2-3 COBYLA iterations with print output (D-07)
5. **Load cached weights cell:** load trained_weights.json, print accuracy
6. **Loss curve cell:** VIZ-02 loss curve from training_history.json
7. **Evaluation cell:** forward pass on test data with cached weights
8. **Hardware results cell:** load hardware_results.json (with auto-detect per D-06)
9. **Comparison plot cell:** VIZ-03 simulator vs hardware bar chart
10. **Summary cell:** markdown with key findings

### Anti-Patterns to Avoid
- **Running full training live:** 100 COBYLA iterations per batch = 5-15 minutes. Only run 2-3 iterations for visual effect, then load cache.
- **Using original QVC_QNN.ipynb directly:** It has 70+ cells, two ansatz paths, CNN comparison, co-presenter sections. Demo notebook should have ~10-15 focused cells.
- **Default matplotlib styling:** Small fonts (10pt), thin lines (1px), pale colors -- all unreadable on projectors.
- **Forgetting `figures/` directory creation:** Will cause savefig to fail silently or error.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON loading with numpy | Custom deserializer | `json.load()` -- cache_results.py already stored as plain lists | JSON was designed for this in Phase 1 |
| Dataset generation | New generation function | Copy `generate_dataset()` from `cache_results.py` (or import it) | Exact same logic needed for consistent data |
| Loss function / forward pass | New implementations | Copy from `cache_results.py` | Must match training to get correct evaluation results |
| Projector color scheme | Custom palette | Use matplotlib's tab10 or the high-contrast palette above | Designed for visibility, already tested |

**Key insight:** The demo notebook is an assembly task, not a creation task. All logic already exists in `cache_results.py` and `QVC_QNN.ipynb`. The notebook imports/copies functions and arranges cells for presentation flow.

## Common Pitfalls

### Pitfall 1: Notebook State Pollution
**What goes wrong:** Cells depend on variables defined in other cells; running out of order causes NameError.
**Why it happens:** Jupyter notebooks have shared global scope. Demo nerves cause skipping or re-running cells.
**How to avoid:** Design for strict top-to-bottom execution. Test with Kernel > Restart and Run All after every edit. Each cell should be self-sufficient or depend only on cells above it.
**Warning signs:** Any cell that references a variable not defined in a cell above it.

### Pitfall 2: Figure Sizing for Projector vs Export
**What goes wrong:** Figures look good inline in Jupyter but are wrong size when saved to PNG for slides.
**Why it happens:** `figure.dpi` affects inline display differently than `savefig.dpi`. figsize in inches interacts with DPI.
**How to avoid:** Set `savefig.dpi: 300` and `savefig.bbox: 'tight'` in rcParams. Always open saved PNGs to verify before using in slides.
**Warning signs:** Saved figures that look tiny or have cut-off labels.

### Pitfall 3: Missing Cache Files on First Run
**What goes wrong:** Demo notebook errors because `trained_weights.json` etc. don't exist yet (cache_results.py hasn't been run).
**Why it happens:** Phase 1 created the script but the JSON files are only generated when the script is executed.
**How to avoid:** Add a guard cell at the top that checks for required files and prints a clear message if missing. Document the dependency in a markdown cell.
**Warning signs:** FileNotFoundError on first cell execution.

### Pitfall 4: Dataset Seed Mismatch
**What goes wrong:** Demo notebook generates a different dataset than what was used for training, so cached weights produce wrong predictions.
**Why it happens:** `generate_dataset()` uses `np.random` internally. If the seed or call order differs between cache_results.py and the demo notebook, the data differs.
**How to avoid:** Use the exact same seed (42) and split parameters (test_size=0.3, random_state=246) as in cache_results.py. Better yet, import generate_dataset from cache_results.py directly.
**Warning signs:** Test accuracy from cached weights doesn't match the cached accuracy number.

### Pitfall 5: Hardware Auto-Detection Requires Working Directory
**What goes wrong:** `load_hardware_results()` from cache_results.py uses relative paths (`Path("live_results.json")`). If notebook's working directory differs from project root, files aren't found.
**Why it happens:** Jupyter sets cwd to the notebook's directory, but if the notebook is in a subdirectory, relative paths break.
**How to avoid:** Keep the demo notebook in the project root (same level as cache files). Or use `Path(__file__).parent` pattern adapted for notebooks.
**Warning signs:** "WARNING: No hardware results available" when the files actually exist.

## Code Examples

### VIZ-02: Loss Curve Plot
```python
# Load training history
history = load_json("training_history.json")
primary_loss = history["primary_ansatz"]["loss_values"]
primary_boundaries = history["primary_ansatz"]["batch_boundaries"]

fig, ax = plt.subplots(figsize=(12, 7))
ax.plot(primary_loss, color=COLORS['primary'], linewidth=2.5, label="Revised Ansatz")

# Mark batch boundaries with vertical lines
for b in primary_boundaries[1:]:  # Skip first (always 0)
    ax.axvline(x=b, color=COLORS['dark'], linestyle='--', alpha=0.4, linewidth=1)

ax.set_xlabel("Optimizer Iteration")
ax.set_ylabel("MSE Loss")
ax.set_title("VQC Training Loss Convergence")
ax.legend()

fig.savefig("figures/loss_curve.png")
plt.show()
```

### VIZ-03: Simulator vs Hardware Comparison
```python
# Load data from caches
weights_data = load_json("trained_weights.json")
sim_accuracy = weights_data["primary_ansatz"]["training"]["test_accuracy"]

# Auto-detect hardware results (D-06 pattern)
from pathlib import Path
hw_path = "live_results.json" if Path("live_results.json").exists() else "hardware_results.json"
hw_data = load_json(hw_path)
hw_accuracy = hw_data["test_accuracy"]
backend_name = hw_data["metadata"]["backend_name"]
is_live = hw_data["metadata"]["is_live"]

fig, ax = plt.subplots(figsize=(10, 7))
bars = ax.bar(
    ["Simulator", f"Hardware\n({backend_name})"],
    [sim_accuracy, hw_accuracy],
    color=[COLORS['primary'], COLORS['secondary']],
    width=0.5,
    edgecolor='black',
    linewidth=1.5,
)

# Add value labels on bars
for bar, val in zip(bars, [sim_accuracy, hw_accuracy]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f"{val:.1f}%", ha='center', va='bottom', fontsize=18, fontweight='bold')

ax.set_ylabel("Test Accuracy (%)")
ax.set_title("Simulator vs Hardware Results")
ax.set_ylim(0, 105)
status = "LIVE" if is_live else "Pre-cached"
ax.annotate(f"Hardware results: {status}", xy=(0.98, 0.02),
            xycoords='axes fraction', ha='right', fontsize=12, fontstyle='italic')

fig.savefig("figures/hardware_comparison.png")
plt.show()
```

### VIZ-04: Input Data Grid (2x4 pixel patterns)
```python
# Generate dataset with same seed as training
np.random.seed(42)
from cache_results import generate_dataset
images, labels = generate_dataset(200)

# Show 8 examples: 4 horizontal (-1), 4 vertical (+1)
hor_imgs = [img for img, lbl in zip(images, labels) if lbl == -1][:4]
ver_imgs = [img for img, lbl in zip(images, labels) if lbl == 1][:4]

fig, axes = plt.subplots(2, 4, figsize=(14, 7))
for i, img in enumerate(hor_imgs):
    axes[0, i].imshow(img.reshape(2, 4), cmap='viridis', vmin=0, vmax=np.pi/2)
    axes[0, i].set_title("Horizontal" if i == 0 else "", fontsize=16)
    axes[0, i].axis('off')

for i, img in enumerate(ver_imgs):
    axes[1, i].imshow(img.reshape(2, 4), cmap='viridis', vmin=0, vmax=np.pi/2)
    axes[1, i].set_title("Vertical" if i == 0 else "", fontsize=16)
    axes[1, i].axis('off')

fig.suptitle("Input Data: 2x4 Pixel Grid Patterns", fontsize=22, y=1.02)
fig.tight_layout()
fig.savefig("figures/input_data_grid.png")
plt.show()
```

### Live Training Demo Cell (D-07: 2-3 iterations)
```python
# Live training demo: show the optimizer working (2-3 iterations only)
from cache_results import build_ansatz, build_full_circuit, forward, mse_loss
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator as Estimator
from scipy.optimize import minimize

num_qubits = 8
revised_cnot_pairs = [[0, 1], [1, 2], [2, 3], [4, 5], [5, 6], [6, 7]]
ansatz = build_ansatz(revised_cnot_pairs, num_qubits)
circuit = build_full_circuit(ansatz, num_qubits)
observable = SparsePauliOp.from_list([("Z" * num_qubits, 1)])
estimator = Estimator()

np.random.seed(42)
initial_weights = np.random.rand(2 * num_qubits) * 2 * np.pi
demo_losses = []

def demo_cost(w):
    pred = forward(circuit, np.array(train_images[:20]), w, estimator, observable)
    loss = mse_loss(pred, np.array(train_labels[:20]))
    demo_losses.append(loss)
    print(f"  Iteration {len(demo_losses)}: loss = {loss:.4f}")
    return loss

print("Running 3 live training iterations...")
res = minimize(demo_cost, initial_weights, method="COBYLA", options={"maxiter": 3})
print(f"\nLive demo complete! Now loading full pre-trained weights...")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `plt.rcParams['font.size'] = 14` | `plt.rcParams.update({...})` batch update | Long-standing | Cleaner setup, one call |
| matplotlib 2.x default style | matplotlib 3.x improved defaults | 3.0 (2018) | Better default colors, but still need projector adjustments |
| `fig.savefig()` without bbox_inches | `savefig.bbox: 'tight'` in rcParams | Long-standing | Prevents clipped labels |

**Note:** matplotlib 3.10.7 is very recent. The API is stable for all patterns used here (subplots, imshow, bar, plot, rcParams). No breaking changes affect this phase.

## Open Questions

1. **Whether to import from cache_results.py or copy functions into the notebook**
   - What we know: `cache_results.py` has all needed functions. Importing keeps things DRY.
   - What's unclear: Will `cache_results.py` import cleanly in a Jupyter context? It has `if __name__ == "__main__"` guard but also imports qiskit at module level.
   - Recommendation: Import from `cache_results` for shared functions (generate_dataset, build_ansatz, forward, etc.). This works as long as qiskit is installed. If qiskit is not available, the live training cells fail anyway, so the import dependency is acceptable.

2. **Whether JSON cache files exist yet**
   - What we know: `cache_results.py` exists but `*.json` files were not found in the project root.
   - What's unclear: Whether the user has run `python cache_results.py` yet.
   - Recommendation: Add a guard cell that checks for required files. The notebook should print a clear error if caches are missing. Plan should include a step to run `cache_results.py` if needed.

3. **Exact number of live training iterations**
   - What we know: D-07 says "2-3 live training iterations"
   - Recommendation: Use `maxiter=3` for the live demo (upper end of range gives slightly more visual feedback without meaningful time cost on simulator).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Everything | Yes | 3.10.7 | -- |
| matplotlib | All visualizations | Yes | 3.10.7 | -- |
| numpy | Data manipulation | Yes | 1.26.4 | -- |
| scipy | Live training demo | Yes | 1.15.3 | -- |
| pytest | Test validation | Yes | 8.3.5 | -- |
| qiskit | Live training iterations, circuit construction | No | -- | Must be installed; or skip live training cells |
| sklearn | Accuracy calculation | No | -- | Must be installed; or compute accuracy manually |
| nbformat | Programmatic notebook creation | No | -- | Not needed: write .ipynb as JSON directly or create manually |
| jupyter/ipykernel | Running the notebook | No (shim only) | -- | Must be installed in target environment to run notebook |

**Missing dependencies with no fallback:**
- qiskit: Required for live training demo cells and circuit construction. Without it, the notebook can still display cached results but cannot run live training iterations.
- sklearn: Required for accuracy_score. Could be replaced with a 3-line manual implementation if needed.

**Missing dependencies with fallback:**
- nbformat: Not needed. The .ipynb format is just JSON -- can be written directly or created in Jupyter.
- jupyter: Needed to run the notebook, but the planner creates the notebook file; running it is a separate concern.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.3.5 |
| Config file | None (default discovery from `tests/` directory) |
| Quick run command | `python -m pytest tests/ -x -q` |
| Full suite command | `python -m pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| NTBK-01 | Demo notebook exists and has correct cell order | smoke | `python -m pytest tests/test_demo_notebook.py::test_notebook_exists -x` | No -- Wave 0 |
| NTBK-01 | Demo notebook runs top-to-bottom without error | integration | `python -m pytest tests/test_demo_notebook.py::test_notebook_runs_clean -x` | No -- Wave 0 |
| VIZ-01 | rcParams set for projector readability | unit | `python -m pytest tests/test_demo_notebook.py::test_rcparams_set -x` | No -- Wave 0 |
| VIZ-02 | Loss curve figure saved to figures/ | smoke | `python -m pytest tests/test_demo_notebook.py::test_loss_curve_saved -x` | No -- Wave 0 |
| VIZ-03 | Hardware comparison figure saved to figures/ | smoke | `python -m pytest tests/test_demo_notebook.py::test_hardware_comparison_saved -x` | No -- Wave 0 |
| VIZ-04 | Input data grid figure saved to figures/ | smoke | `python -m pytest tests/test_demo_notebook.py::test_data_grid_saved -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/ -x -q`
- **Per wave merge:** `python -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_demo_notebook.py` -- covers NTBK-01, VIZ-01 through VIZ-04
- [ ] Framework install: None needed (pytest 8.3.5 already available)

**Note on notebook testing:** Full notebook execution tests require qiskit + sklearn + jupyter kernel. A pragmatic approach is to test the notebook structure (cell count, markdown headers, required imports) and test figure generation functions independently, avoiding full kernel execution in CI.

## Sources

### Primary (HIGH confidence)
- `cache_results.py` -- direct source code reading; JSON schema, function signatures, training logic
- `QVC_QNN.ipynb` -- original notebook; existing visualization patterns (cells 7, 52, 54, 61, 65, 69)
- `tests/test_cache.py` -- existing test patterns, conftest.py setup
- `.planning/research/ARCHITECTURE.md` -- rcParams pattern, figure export pattern, directory structure
- `.planning/research/PITFALLS.md` -- projector readability, state pollution, cache dependency warnings
- Phase 1 CONTEXT.md and SUMMARY -- JSON cache design, D-01 through D-08 decisions

### Secondary (MEDIUM confidence)
- matplotlib 3.10.7 installed locally -- verified rcParams API compatibility

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- matplotlib 3.10.7, numpy 1.26.4, scipy 1.15.3 all verified installed
- Architecture: HIGH -- patterns directly from project's own ARCHITECTURE.md research + Phase 1 established patterns
- Pitfalls: HIGH -- drawn from project's PITFALLS.md + analysis of cache_results.py code

**Research date:** 2026-03-24
**Valid until:** 2026-04-24 (stable domain; matplotlib API doesn't change frequently)
