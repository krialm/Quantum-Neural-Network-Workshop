# Phase 1: Caching Foundation - Research

**Researched:** 2026-03-24
**Domain:** Quantum ML training cache infrastructure, JSON serialization of numpy/qiskit results
**Confidence:** HIGH

## Summary

Phase 1 pre-computes and caches all expensive operations (VQC training, hardware execution) as JSON files in the project root so the live demo loads results instantly. The notebook contains two ansatz sections (first and revised), a COBYLA-based training loop with 3 batches of 100 iterations each, and commented-out hardware execution cells that use `QiskitRuntimeService` and `EstimatorV2`.

**Critical discovery:** The notebook's "two ansatz" implementations (Cell 16 and Cell 57) have *identical* CNOT lists: `[[0, 1], [1, 2], [2, 3], [4, 5], [5, 6], [6, 7]]`. The narrative says the first ansatz only connects the top row and the revised adds the bottom row, but the code was already updated to include both rows in both cells. The first ansatz was originally meant to use only `[[0, 1], [1, 2], [2, 3]]` (top row). To create a meaningful two-ansatz comparison for the demo, the caching script must fix the first ansatz to use the original smaller CNOT list, producing genuinely different results (the narrative says ~60% accuracy for first, ~83% for revised).

**Primary recommendation:** Build a standalone Python caching script (`cache_results.py`) that runs both ansatz variants through training, caches weights and loss curves as JSON, and optionally submits hardware jobs. The demo notebook will load from these JSON files.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Claude picks the primary ansatz based on which produces cleaner, more compelling results for the audience
- **D-02:** Both ansatz results are cached -- primary for the demo, alternative as pre-computed backup comparison if time allows or audience asks
- **D-03:** All cached data stored as JSON files (human-readable, easy to inspect and debug)
- **D-04:** Cache files live alongside the notebook in the project root (e.g., `trained_weights.json`, `hardware_results.json`), not in a subdirectory
- **D-05:** Dual hardware strategy: pre-run jobs hours/days before the conference AND attempt live submission during co-presenter's 30-minute half
- **D-06:** Notebook auto-detects if live hardware results are available and uses them over cached results; falls back to cache if live results aren't ready
- **D-07:** Live demo runs 2-3 training iterations to show the loop working, then loads full pre-trained weights from cache
- **D-08:** Create a separate demo notebook (not a toggle in the original) -- the demo notebook contains only presentation cells

### Claude's Discretion
- Which ansatz to select as primary (based on result quality)
- Exact JSON schema for cache files
- How many live training iterations to run (2-3 range)
- Auto-detection logic for live vs cached hardware results
- How to structure the separate demo notebook

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| NTBK-02 | Pre-trained weights cached so live demo skips full training | Training loop outputs `res["x"]` (numpy array of 16 floats) -- serialize via `.tolist()` to JSON. Both ansatz weights cached. |
| NTBK-03 | Hardware results pre-cached as fallback for IBM queue delays | Hardware execution produces expectation values (numpy array) -- same JSON serialization. Must also cache backend name and job metadata. |
| NTBK-04 | Each demo cell executes in under 30 seconds | Training takes 5-15 min per ansatz. Caching eliminates this. JSON load is <1 second. Hardware cache load is instant. Live 2-3 iterations ~10-20 seconds on simulator. |
| NTBK-05 | Single ansatz narrative (pick one, show other as pre-computed) | Revised ansatz (with full horizontal CNOT coverage) is the primary -- it achieves ~83% accuracy with a clear improvement story. First ansatz (~60%) cached as comparison. |
</phase_requirements>

## Standard Stack

### Core (Already Installed/Required)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| qiskit | >=1.2 | Circuit construction, transpilation | Already in notebook; required for training |
| qiskit-ibm-runtime | >=0.28 | Hardware access, EstimatorV2 | Required for hardware job submission |
| numpy | 1.26.4 | Array operations, weight parameters | Already installed; training loop core |
| scipy | 1.15.3 | `minimize` with COBYLA optimizer | Already installed; training optimizer |
| python-dotenv | 1.1.1 | IBM API credentials from `.env` | Already installed; credential management |

### Cache-Specific (No New Dependencies)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| json (stdlib) | builtin | Serialize/deserialize cache files | All cache read/write operations |
| pathlib (stdlib) | builtin | File path handling | Cache file location management |
| datetime (stdlib) | builtin | Timestamp cache metadata | Record when cache was generated |

**No new pip installs required for Phase 1.** JSON serialization uses stdlib only. Numpy's `.tolist()` converts arrays to JSON-native Python lists.

## Architecture Patterns

### Recommended Project Structure (Phase 1 additions)
```
Quantum_Variational_Circuits/
  QVC_QNN.ipynb              # Original notebook (reference, unchanged)
  cache_results.py           # NEW: Standalone script to generate all caches
  trained_weights.json       # NEW: Pre-trained weights for both ansatz
  training_history.json      # NEW: Loss curves for both ansatz
  hardware_results.json      # NEW: Pre-cached hardware execution results
  live_results.json          # NEW: Written by live hardware job (auto-detected)
```

All cache files in project root per D-04.

### Pattern 1: JSON Cache Schema

**What:** A consistent JSON structure for all cache files with metadata for human inspection.
**When:** Every cached computation result.
**Example:**

```python
# trained_weights.json schema
{
    "metadata": {
        "generated": "2026-03-24T10:30:00",
        "generator": "cache_results.py",
        "qiskit_version": "1.2.x",
        "random_seed": 42
    },
    "primary_ansatz": {
        "name": "revised",
        "description": "Full horizontal CNOT coverage (rows 0-3 and 4-7)",
        "cnot_pairs": [[0,1],[1,2],[2,3],[4,5],[5,6],[6,7]],
        "num_parameters": 16,
        "weights": [0.123, 0.456, ...],  # 16 floats from res["x"].tolist()
        "training": {
            "optimizer": "COBYLA",
            "max_iter_per_batch": 100,
            "num_epochs": 1,
            "batch_size": 140,
            "num_batches": 3,
            "final_loss": 0.503,
            "train_accuracy": 83.0,
            "test_accuracy": 83.0
        }
    },
    "alternative_ansatz": {
        "name": "first",
        "description": "Top-row-only CNOT coverage (qubits 0-3)",
        "cnot_pairs": [[0,1],[1,2],[2,3]],
        "num_parameters": 16,
        "weights": [0.789, 0.012, ...],
        "training": {
            "optimizer": "COBYLA",
            "max_iter_per_batch": 100,
            "num_epochs": 1,
            "batch_size": 140,
            "num_batches": 3,
            "final_loss": 0.870,
            "train_accuracy": 60.0,
            "test_accuracy": 60.0
        }
    }
}
```

```python
# training_history.json schema
{
    "metadata": { ... },
    "primary_ansatz": {
        "loss_values": [1.01, 0.98, ...],  # All iteration losses
        "batch_boundaries": [0, 100, 200]   # Where batches start in the array
    },
    "alternative_ansatz": {
        "loss_values": [1.05, 1.02, ...],
        "batch_boundaries": [0, 100, 200]
    }
}
```

```python
# hardware_results.json schema
{
    "metadata": {
        "generated": "2026-03-24T10:30:00",
        "backend_name": "ibm_brisbane",
        "job_id": "abc123",
        "is_live": false
    },
    "expectation_values": [0.12, -0.34, ...],
    "predictions": [1, -1, ...],
    "test_accuracy": 75.0
}
```

```python
# live_results.json schema (same as hardware_results.json but with is_live: true)
{
    "metadata": {
        "generated": "2026-03-24T14:00:00",
        "backend_name": "ibm_brisbane",
        "job_id": "xyz789",
        "is_live": true
    },
    "expectation_values": [...],
    "predictions": [...],
    "test_accuracy": 72.0
}
```

### Pattern 2: Numpy-to-JSON Serialization

**What:** Use `.tolist()` for all numpy arrays before JSON serialization.
**Why:** Cleanest approach -- produces plain Python lists of floats that are human-readable in JSON. No custom encoders needed.

```python
import json
import numpy as np

def save_cache(filepath, data):
    """Save cache data to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def load_cache(filepath):
    """Load cache data from JSON file, return None if not found."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

# Converting training results to cache format
weights_list = res["x"].tolist()  # numpy array -> Python list
loss_list = [float(v) for v in objective_func_vals]  # ensure native floats
```

### Pattern 3: Auto-Detection for Live vs Cached Hardware Results

**What:** Check for `live_results.json` first; fall back to `hardware_results.json`.
**When:** Demo notebook loads hardware results.

```python
import json
from pathlib import Path

def load_hardware_results():
    """Load hardware results with live > cached priority."""
    live_path = Path("live_results.json")
    cache_path = Path("hardware_results.json")

    if live_path.exists():
        with open(live_path) as f:
            data = json.load(f)
        print("Using LIVE hardware results from", data["metadata"]["backend_name"])
        return data

    if cache_path.exists():
        with open(cache_path) as f:
            data = json.load(f)
        print("Using CACHED hardware results from", data["metadata"]["backend_name"])
        return data

    print("WARNING: No hardware results available. Showing simulator results only.")
    return None
```

### Pattern 4: Caching Script Structure

**What:** Standalone `cache_results.py` that reproduces training from `QVC_QNN.ipynb` and saves results.
**Why:** Separates cache generation from demo execution. Can be re-run independently.

```python
#!/usr/bin/env python3
"""Generate all cached results for the QVC demo presentation."""

import json
import numpy as np
from datetime import datetime
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.circuit.library import z_feature_map
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator as Estimator

def main():
    # 1. Generate dataset (same seed as notebook)
    # 2. Build both ansatz circuits
    # 3. Train first ansatz (top-row CNOTs only)
    # 4. Train revised ansatz (full horizontal CNOTs)
    # 5. Evaluate both on test set
    # 6. Save trained_weights.json
    # 7. Save training_history.json
    # 8. Optionally submit hardware job and save hardware_results.json

if __name__ == "__main__":
    main()
```

### Anti-Patterns to Avoid
- **Pickle for caching:** User decision D-03 explicitly requires JSON. Do not use pickle, joblib, or any binary format even though the prior ARCHITECTURE.md research suggested pickle. JSON is the locked decision.
- **Cache in a subdirectory:** User decision D-04 explicitly requires files alongside the notebook in project root. Do not create a `cache/` directory.
- **Modifying the original notebook:** D-08 says create a separate demo notebook. The caching script extracts logic from `QVC_QNN.ipynb` but does not change it.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Numpy JSON serialization | Custom recursive encoder | `array.tolist()` | Built-in, handles all numpy numeric types, produces clean JSON |
| Training loop | New optimizer wrapper | Copy existing COBYLA/minimize pattern from notebook cells 45/59 | Proven to converge; same seed for reproducibility |
| Circuit construction | New ansatz designs | Reuse exact `QuantumCircuit` + `ParameterVector` patterns from cells 16/57 | Must match what the demo notebook loads |
| Hardware job management | Custom queue monitor | Qiskit Runtime job API (`service.job()`, `job.status()`) | Built-in retry and status tracking |

## Critical Finding: Ansatz Identity Bug

**Severity:** HIGH -- affects the entire "two ansatz" narrative

**What:** Cells 16 and 57 in `QVC_QNN.ipynb` define supposedly different ansatz circuits, but both use the identical CNOT list: `[[0, 1], [1, 2], [2, 3], [4, 5], [5, 6], [6, 7]]`.

**The narrative intent (from markdown cells 55-56):**
- First ansatz: only top-row connections `[[0, 1], [1, 2], [2, 3]]` -- should achieve ~60% accuracy
- Revised ansatz: adds bottom-row connections to get `[[0, 1], [1, 2], [2, 3], [4, 5], [5, 6], [6, 7]]` -- should achieve ~83% accuracy

**The reality:** Both cells already have the extended list. The notebook outputs show ~90% accuracy for both (because they're the same circuit). The markdown text claiming 60% and 83% reflects intended/original results, not current outputs.

**Impact on caching:** The caching script MUST use genuinely different CNOT lists:
- First ansatz: `[[0, 1], [1, 2], [2, 3]]` (top row only, as originally intended)
- Revised ansatz: `[[0, 1], [1, 2], [2, 3], [4, 5], [5, 6], [6, 7]]` (both rows)

This will produce the different accuracy numbers the narrative requires and create a meaningful comparison for the audience.

**Confidence:** HIGH -- verified by directly comparing Cell 16 and Cell 57 source code.

## Common Pitfalls

### Pitfall 1: Random Seed Drift
**What goes wrong:** Caching script produces different weights than the notebook because random state diverges.
**Why it happens:** `np.random.seed(42)` is set in the notebook, but any intermediate random calls between seed and training can shift the sequence.
**How to avoid:** Use `np.random.seed(42)` immediately before weight initialization in the caching script, matching the notebook exactly. Also seed `generate_dataset(200)` with the same seed/call pattern.
**Warning signs:** Cached weights produce different accuracy than expected when loaded.

### Pitfall 2: JSON Float Precision Loss
**What goes wrong:** Trained weights lose precision when round-tripped through JSON, producing slightly different predictions.
**Why it happens:** JSON floats are text-encoded; Python `json.dumps` may truncate.
**How to avoid:** This is acceptable for demo purposes. The precision difference is negligible (<1e-15). If needed, use `json.dumps(data, indent=2)` which preserves full float64 representation.
**Warning signs:** If accuracy differs by more than 0.1% between live training and cached weights, investigate.

### Pitfall 3: Qiskit Not Installed
**What goes wrong:** The caching script fails because qiskit and qiskit-ibm-runtime are not in the current Python environment.
**Why it happens:** The system Python (3.10.7 via pyenv) does not have qiskit installed. The notebook was likely run in a different environment (possibly a Jupyter kernel with a venv).
**How to avoid:** Create a virtualenv with all dependencies before running the caching script. Document the setup steps.
**Warning signs:** `ModuleNotFoundError: No module named 'qiskit'`

### Pitfall 4: Hardware Job Caching Without IBM Account Verification
**What goes wrong:** The hardware caching step fails because the IBM Quantum API token is missing, expired, or the free tier has no minutes remaining.
**Why it happens:** `.env` file not present, token expired, or 10-minute free tier already consumed.
**How to avoid:** Make hardware caching optional in the script. Simulator-based caches should be generated first. Hardware cache is a separate step that can fail gracefully.
**Warning signs:** `IBMNotAuthorizedError` or connection timeout.

### Pitfall 5: Notebook State Pollution (Already Present)
**What goes wrong:** The existing notebook has cell 57 (revised ansatz) overwriting `qnn_circuit` in global scope, so re-running cell 45 (first ansatz training) actually trains the revised ansatz.
**Why it happens:** Jupyter notebooks share global state. Cell 57 mutates `qnn_circuit` which is referenced by `ansatz` in cell 18.
**How to avoid:** The caching script avoids this by constructing each ansatz in its own scope (separate functions). The demo notebook will only use the primary ansatz.
**Warning signs:** Both ansatz produce identical results (as they do in current notebook outputs).

## Code Examples

### Complete JSON Cache Save/Load Pattern
```python
import json
import numpy as np
from datetime import datetime
from pathlib import Path

class NumpyEncoder(json.JSONEncoder):
    """Handle numpy types in JSON serialization."""
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        return super().default(obj)

def save_json(filepath: str, data: dict) -> None:
    """Save data to JSON file with numpy support."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, cls=NumpyEncoder)
    print(f"Saved: {filepath}")

def load_json(filepath: str) -> dict | None:
    """Load JSON cache file. Returns None if not found."""
    path = Path(filepath)
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)
```

### Building Both Ansatz Circuits
```python
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector

SIZE = 8  # 2x4 pixel grid = 8 qubits

def build_ansatz(cnot_pairs: list[list[int]], name: str) -> QuantumCircuit:
    """Build a VQC ansatz with specified CNOT connectivity."""
    qc = QuantumCircuit(SIZE)
    params = ParameterVector("theta", length=2 * SIZE)

    # First variational layer: RY rotations
    for i in range(SIZE):
        qc.ry(params[i], i)

    # Entanglement layer: CNOTs
    for pair in cnot_pairs:
        qc.cx(pair[0], pair[1])

    # Second variational layer: RX rotations
    for i in range(SIZE):
        qc.rx(params[SIZE + i], i)

    return qc

# First ansatz: top-row only (as originally intended)
first_ansatz = build_ansatz(
    cnot_pairs=[[0, 1], [1, 2], [2, 3]],
    name="first"
)

# Revised ansatz: full horizontal coverage
revised_ansatz = build_ansatz(
    cnot_pairs=[[0, 1], [1, 2], [2, 3], [4, 5], [5, 6], [6, 7]],
    name="revised"
)
```

### Training and Caching One Ansatz
```python
from qiskit.circuit.library import z_feature_map
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator as Estimator
from scipy.optimize import minimize

def train_and_cache(ansatz, train_images, train_labels, test_images, test_labels):
    """Train one ansatz variant and return results for caching."""
    num_qubits = len(train_images[0])
    feature_map = z_feature_map(num_qubits, parameter_prefix="a")

    # Build full circuit
    full_circuit = QuantumCircuit(num_qubits)
    full_circuit.compose(feature_map, range(num_qubits), inplace=True)
    full_circuit.compose(ansatz, range(num_qubits), inplace=True)

    observable = SparsePauliOp.from_list([("Z" * num_qubits, 1)])
    estimator = Estimator()

    # Training loop (mirrors notebook cells 45/59)
    np.random.seed(42)
    weight_params = np.random.rand(len(ansatz.parameters)) * 2 * np.pi
    objective_func_vals = []
    batch_size = 140
    num_samples = len(train_images)

    for epoch in range(1):
        for i in range((num_samples - 1) // batch_size + 1):
            start_i = i * batch_size
            end_i = start_i + batch_size
            batch_images = np.array(train_images[start_i:end_i])
            batch_labels = np.array(train_labels[start_i:end_i])

            # Closure for optimizer
            def cost_fn(w):
                preds = forward(full_circuit, batch_images, w, estimator, observable)
                loss = float(((preds - batch_labels) ** 2).mean())
                objective_func_vals.append(loss)
                return loss

            res = minimize(cost_fn, weight_params, method="COBYLA",
                          options={"maxiter": 100})
            weight_params = res["x"]

    return {
        "weights": weight_params.tolist(),
        "loss_values": objective_func_vals,
        "final_loss": float(objective_func_vals[-1]) if objective_func_vals else None,
    }
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pickle/joblib for caching | JSON per user decision D-03 | N/A (user choice) | Human-readable, inspectable cache files |
| EstimatorV1 | EstimatorV2 (qiskit-ibm-runtime) | Qiskit 1.0 (2024) | Different API: `run([pub])` instead of `run(circuit, observable, params)` |
| `cache/` subdirectory | Project root (D-04) | N/A (user choice) | Simpler path references, visible alongside notebook |
| Single notebook with toggles | Separate demo notebook (D-08) | N/A (user choice) | Cleaner demo, no toggle complexity |

## Open Questions

1. **Which Python environment has qiskit installed?**
   - What we know: System Python 3.10.7 does NOT have qiskit. The notebook was previously executed (outputs exist).
   - What's unclear: Whether a venv, conda env, or different pyenv version has qiskit.
   - Recommendation: Plan includes a "setup environment" step that creates a venv and installs from `requirements.txt`. Verify qiskit version before running cache script.

2. **IBM Quantum account status?**
   - What we know: `.env` setup is in the notebook. There's a `QiskitRuntimeService.save_account()` call. Notebook output shows a warning about "free and trial plan instances."
   - What's unclear: Whether the account still has hardware minutes available.
   - Recommendation: Make hardware caching a separate, optional step. All other caching works on simulator.

3. **Expected accuracy for the corrected first ansatz?**
   - What we know: The narrative says ~60% but the current code (which is actually the revised ansatz) gives ~90%. With the corrected smaller CNOT list, we expect lower accuracy (~60%) as intended.
   - What's unclear: Exact accuracy until we actually run it.
   - Recommendation: Run the caching script and verify. If first ansatz accuracy is not meaningfully different from revised, the "improvement story" needs adjusting.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.10+ | All code | Yes | 3.10.7 (pyenv) | -- |
| numpy | Training, data | Yes | 1.26.4 | -- |
| scipy | Training optimizer | Yes | 1.15.3 | -- |
| matplotlib | Loss curve caching (optional) | Yes | 3.10.7 | -- |
| python-dotenv | IBM credentials | Yes | 1.1.1 | -- |
| qiskit | Circuit construction | No (not in system Python) | -- | Install in venv |
| qiskit-ibm-runtime | Hardware access | No (not in system Python) | -- | Install in venv |
| scikit-learn | Accuracy metrics | No (not in system Python) | -- | Install in venv |
| IBM Quantum API access | Hardware caching | Unknown | -- | Skip hardware cache, use simulator only |

**Missing dependencies with no fallback:**
- qiskit, qiskit-ibm-runtime, scikit-learn must be installed before cache generation

**Missing dependencies with fallback:**
- IBM Quantum API access -- hardware caching is optional; simulator caching works offline

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (to be installed) |
| Config file | none -- see Wave 0 |
| Quick run command | `python -m pytest tests/ -x -q` |
| Full suite command | `python -m pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| NTBK-02 | Trained weights cache loads and produces valid predictions | unit | `python -m pytest tests/test_cache.py::test_weights_cache_roundtrip -x` | Wave 0 |
| NTBK-03 | Hardware results cache loads with correct schema | unit | `python -m pytest tests/test_cache.py::test_hardware_cache_schema -x` | Wave 0 |
| NTBK-04 | Cache loading completes in under 1 second (proxy for 30s cell limit) | unit | `python -m pytest tests/test_cache.py::test_cache_load_speed -x` | Wave 0 |
| NTBK-05 | Both ansatz caches exist with different weights and different accuracies | unit | `python -m pytest tests/test_cache.py::test_dual_ansatz_cached -x` | Wave 0 |
| -- | Auto-detect logic prefers live_results.json over hardware_results.json | unit | `python -m pytest tests/test_cache.py::test_live_detection_priority -x` | Wave 0 |
| -- | First ansatz uses smaller CNOT list than revised | unit | `python -m pytest tests/test_cache.py::test_ansatz_cnot_difference -x` | Wave 0 |
| -- | JSON files are valid, human-readable, and match schema | unit | `python -m pytest tests/test_cache.py::test_json_schema_validation -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_cache.py -x -q`
- **Per wave merge:** `python -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_cache.py` -- covers NTBK-02, NTBK-03, NTBK-04, NTBK-05
- [ ] `tests/conftest.py` -- shared fixtures (sample datasets, mock circuits)
- [ ] pytest install: `pip install pytest` in the project venv

## Project Constraints (from CLAUDE.md)

- GSD workflow enforcement: all file changes through GSD commands
- `python-dotenv` for IBM credentials (not hardcoded)
- Snake_case naming convention for all functions and variables
- Type hints in function signatures
- Descriptive function names (no abbreviations)
- Comments explain non-obvious logic
- 4-space indentation, PEP 8-like style
- Print statements for progress (no logging framework)

## Sources

### Primary (HIGH confidence)
- `QVC_QNN.ipynb` -- Direct analysis of all 70 cells, cell outputs, both ansatz definitions, training loops, hardware access patterns
- `CONTEXT.md` -- User decisions D-01 through D-08
- `REQUIREMENTS.md` -- NTBK-02 through NTBK-05 requirement definitions
- `.planning/research/PITFALLS.md` -- Hardware queue delays, training time, version mismatch pitfalls
- `.planning/research/ARCHITECTURE.md` -- Cache-first demo pattern, directory structure
- `.planning/research/STACK.md` -- Technology stack analysis

### Secondary (MEDIUM confidence)
- [NumPy JSON serialization best practices](https://pynative.com/python-serialize-numpy-ndarray-into-json/) -- `.tolist()` method verified as standard approach
- [Qiskit IBM Runtime JSON utilities](https://github.com/Qiskit/qiskit-ibm-runtime/blob/main/qiskit_ibm_runtime/utils/json.py) -- RuntimeEncoder/Decoder for hardware results
- [IBM Quantum save-jobs guide](https://docs.quantum.ibm.com/guides/save-jobs) -- Job result persistence patterns

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- verified against installed packages and notebook imports
- Architecture: HIGH -- patterns derived directly from notebook code analysis and user decisions
- Pitfalls: HIGH -- ansatz identity bug confirmed by source code comparison; environment gaps confirmed by pip
- JSON serialization: HIGH -- stdlib approach, well-documented

**Research date:** 2026-03-24
**Valid until:** 2026-04-24 (stable domain; qiskit versions should be re-verified on demo machine)
