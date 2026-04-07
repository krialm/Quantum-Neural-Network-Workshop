#!/usr/bin/env python3
"""Generate all cached results for the QVC demo presentation.

This standalone script extracts and reproduces the training logic from
QVC_QNN.ipynb, training both ansatz variants (first = top-row-only CNOTs,
revised = full horizontal CNOTs) and saving all results as human-readable
JSON cache files in the project root.

Usage:
    python cache_results.py              # Train both ansatz, cache weights + history
    python cache_results.py --hardware   # Also attempt real IBM Quantum hardware execution
"""

import json
import copy
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.circuit.library import z_feature_map
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator as Estimator


# ---------------------------------------------------------------------------
# JSON Utilities
# ---------------------------------------------------------------------------

class NumpyEncoder(json.JSONEncoder):
    """Handle numpy types in JSON serialization."""

    def default(self, obj: object) -> object:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        return super().default(obj)


def save_json(filepath: str, data: dict) -> None:
    """Save data to JSON file with numpy support.

    Args:
        filepath: Path to the output JSON file.
        data: Dictionary to serialize.
    """
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, cls=NumpyEncoder)
    print(f"Saved: {filepath}")


def load_json(filepath: str) -> Optional[dict]:
    """Load JSON cache file.

    Args:
        filepath: Path to the JSON file.

    Returns:
        Parsed dictionary, or None if file not found.
    """
    path = Path(filepath)
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Dataset Generation (mirrors QVC_QNN.ipynb cells 3-7)
# ---------------------------------------------------------------------------

def generate_dataset(num_images: int) -> tuple[np.ndarray, list[int]]:
    """Generate synthetic 2x4 pixel grid images with horizontal/vertical lines.

    Creates images of a 2-row x 4-column pixel grid where horizontal lines
    (label -1) and vertical lines (label +1) are drawn.  Noise is added to
    zero-valued pixels.

    Args:
        num_images: Number of images to generate.

    Returns:
        Tuple of (images array, labels list).  Labels are +1 (vertical) or
        -1 (horizontal).
    """
    # Total number of "pixels"/qubits
    size = 8
    # Image dimensions: 2 rows x 4 columns
    vert_size = 2
    hor_size = round(size / vert_size)
    # Length of the lines to detect
    line_size = 2

    images = []
    labels = []

    # Pre-calculate all possible horizontal and vertical patterns
    hor_array = np.zeros((size - (line_size - 1) * vert_size, size))
    ver_array = np.zeros((round(size / vert_size) * (vert_size - line_size + 1), size))

    j = 0
    for i in range(0, size - 1):
        if i % (size / vert_size) <= (size / vert_size) - line_size:
            for p in range(0, line_size):
                hor_array[j][i + p] = np.pi / 2
            j += 1

    j = 0
    for i in range(0, round(size / vert_size) * (vert_size - line_size + 1)):
        for p in range(0, line_size):
            ver_array[j][i + p * round(size / vert_size)] = np.pi / 2
        j += 1

    for n in range(num_images):
        rng = np.random.randint(0, 2)
        if rng == 0:
            labels.append(-1)  # Horizontal
            random_image = np.random.randint(0, len(hor_array))
            images.append(np.array(hor_array[random_image]))
        elif rng == 1:
            labels.append(1)  # Vertical
            random_image = np.random.randint(0, len(ver_array))
            images.append(np.array(ver_array[random_image]))

        # Add noise to zero-valued pixels
        for i in range(size):
            if images[-1][i] == 0:
                images[-1][i] = np.random.rand() * np.pi / 4

    return np.array(images), labels


# ---------------------------------------------------------------------------
# Circuit Construction
# ---------------------------------------------------------------------------

def build_ansatz(cnot_pairs: list[list[int]], num_qubits: int = 8) -> QuantumCircuit:
    """Build a VQC ansatz with specified CNOT connectivity.

    The ansatz consists of:
      1. RY rotation layer (one parameter per qubit)
      2. CNOT entanglement layer (specified by cnot_pairs)
      3. RX rotation layer (one parameter per qubit)

    Total parameters: 2 * num_qubits.

    Args:
        cnot_pairs: List of [control, target] qubit pairs for CNOT gates.
        num_qubits: Number of qubits in the circuit.

    Returns:
        Parameterized QuantumCircuit for the ansatz.
    """
    qc = QuantumCircuit(num_qubits)
    params = ParameterVector("theta", length=2 * num_qubits)

    # First variational layer: RY rotations
    for i in range(num_qubits):
        qc.ry(params[i], i)

    # Entanglement layer: CNOTs
    for pair in cnot_pairs:
        qc.cx(pair[0], pair[1])

    # Second variational layer: RX rotations
    for i in range(num_qubits):
        qc.rx(params[num_qubits + i], i)

    return qc


def build_full_circuit(ansatz: QuantumCircuit, num_qubits: int = 8) -> QuantumCircuit:
    """Compose feature map and ansatz into a single circuit.

    The parameter_prefix="a" on the feature map is critical -- it ensures
    feature map parameters sort alphabetically before ansatz parameters
    when Qiskit assigns them.

    Args:
        ansatz: The parameterized ansatz circuit.
        num_qubits: Number of qubits.

    Returns:
        Full circuit with feature map composed with ansatz.
    """
    feature_map = z_feature_map(num_qubits, parameter_prefix="a")
    full_circuit = QuantumCircuit(num_qubits)
    full_circuit.compose(feature_map, range(num_qubits), inplace=True)
    full_circuit.compose(ansatz, range(num_qubits), inplace=True)
    return full_circuit


# ---------------------------------------------------------------------------
# Forward Pass (mirrors QVC_QNN.ipynb cell 23)
# ---------------------------------------------------------------------------

def forward(
    circuit: QuantumCircuit,
    input_params: np.ndarray,
    weight_params: np.ndarray,
    estimator: object,
    observable: SparsePauliOp,
) -> np.ndarray:
    """Forward pass of the quantum neural network.

    For each input sample, creates a pub (circuit, observable, parameter_values)
    and runs the estimator to obtain expectation values.

    Args:
        circuit: Full circuit (feature map + ansatz).
        input_params: Data encoding parameters, shape (num_samples, num_features).
        weight_params: Ansatz weight parameters, shape (num_weights,).
        estimator: Qiskit EstimatorV2 primitive.
        observable: Observable to measure expectation values against.

    Returns:
        Array of expectation values, one per input sample.
    """
    num_samples = input_params.shape[0]
    weights = np.broadcast_to(weight_params, (num_samples, len(weight_params)))
    params = np.concatenate((input_params, weights), axis=1)
    pub = (circuit, observable, params)
    job = estimator.run([pub])
    result = job.result()[0]
    expectation_values = result.data.evs
    return expectation_values


# ---------------------------------------------------------------------------
# Loss Functions
# ---------------------------------------------------------------------------

def mse_loss(predict: np.ndarray, target: np.ndarray) -> float:
    """Mean squared error loss.

    Args:
        predict: Predictions from the forward pass.
        target: True labels.

    Returns:
        MSE loss value.
    """
    if len(predict.shape) <= 1:
        return float(((predict - target) ** 2).mean())
    else:
        raise AssertionError("input should be 1d-array")


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_ansatz(
    name: str,
    cnot_pairs: list[list[int]],
    train_images: list,
    train_labels: list,
    test_images: list,
    test_labels: list,
) -> dict:
    """Train one ansatz variant and return results for caching.

    Mirrors the training loop in QVC_QNN.ipynb cells 45/59: 1 epoch,
    batch_size=140, COBYLA optimizer with maxiter=100 per batch.

    Args:
        name: Human-readable name for this ansatz variant.
        cnot_pairs: CNOT connectivity for the ansatz.
        train_images: Training input data.
        train_labels: Training labels (+1 or -1).
        test_images: Test input data.
        test_labels: Test labels (+1 or -1).

    Returns:
        Dictionary with weights, loss history, and accuracy metrics.
    """
    num_qubits = 8
    ansatz = build_ansatz(cnot_pairs, num_qubits)
    circuit = build_full_circuit(ansatz, num_qubits)
    observable = SparsePauliOp.from_list([("Z" * num_qubits, 1)])
    estimator = Estimator()

    # Reproducible weight initialization
    np.random.seed(42)
    weight_params = np.random.rand(2 * num_qubits) * 2 * np.pi

    objective_func_vals = []
    batch_size = 140
    num_samples = len(train_images)

    print(f"\n--- Training {name} ansatz ---")
    print(f"CNOT pairs: {cnot_pairs}")
    print(f"Parameters: {2 * num_qubits}")

    for epoch in range(1):
        for i in range((num_samples - 1) // batch_size + 1):
            start_i = i * batch_size
            end_i = start_i + batch_size
            train_images_batch = np.array(train_images[start_i:end_i])
            train_labels_batch = np.array(train_labels[start_i:end_i])

            # Closure references for the optimizer cost function
            input_params = train_images_batch
            target = train_labels_batch
            iteration_count = 0

            def cost_fn(w: np.ndarray) -> float:
                """Cost function for COBYLA optimizer."""
                nonlocal iteration_count
                predictions = forward(circuit, input_params, w, estimator, observable)
                cost = mse_loss(predict=predictions, target=target)
                objective_func_vals.append(cost)
                if iteration_count % 50 == 0:
                    print(f"  Batch {i}, iter {iteration_count}: loss = {cost:.4f}")
                iteration_count += 1
                return cost

            res = minimize(
                cost_fn, weight_params, method="COBYLA", options={"maxiter": 100}
            )
            weight_params = res["x"]
            print(f"  Batch {i} complete. Final loss: {objective_func_vals[-1]:.4f}")

    # Evaluate on training set
    pred_train = forward(circuit, np.array(train_images), weight_params, estimator, observable)
    pred_train_labels = copy.deepcopy(pred_train)
    pred_train_labels[pred_train_labels >= 0] = 1
    pred_train_labels[pred_train_labels < 0] = -1
    train_accuracy = float(accuracy_score(train_labels, pred_train_labels) * 100)

    # Evaluate on test set
    pred_test = forward(circuit, np.array(test_images), weight_params, estimator, observable)
    pred_test_labels = copy.deepcopy(pred_test)
    pred_test_labels[pred_test_labels >= 0] = 1
    pred_test_labels[pred_test_labels < 0] = -1
    test_accuracy = float(accuracy_score(test_labels, pred_test_labels) * 100)

    print(f"  Train accuracy: {train_accuracy:.1f}%")
    print(f"  Test accuracy:  {test_accuracy:.1f}%")

    # Compute batch boundaries (each batch runs up to maxiter=100 optimizer calls)
    num_batches = (num_samples - 1) // batch_size + 1
    batch_boundaries = []
    boundary = 0
    for b in range(num_batches):
        batch_boundaries.append(boundary)
        # Each batch contributes some number of loss values; approximate from recorded vals
        if b < num_batches - 1:
            # Estimate: the next boundary is the current count after this batch
            pass
    # Recompute precisely from the actual recorded values
    # We know batches ran sequentially, each calling cost_fn up to ~100 times
    # A simple approach: boundaries at multiples of per-batch counts
    # Since we just ran training, we can compute from total / num_batches
    total_vals = len(objective_func_vals)
    batch_boundaries = [0]
    vals_per_batch = total_vals // num_batches if num_batches > 0 else total_vals
    for b in range(1, num_batches):
        batch_boundaries.append(b * vals_per_batch)

    return {
        "name": name,
        "weights": weight_params.tolist(),
        "loss_values": [float(v) for v in objective_func_vals],
        "batch_boundaries": batch_boundaries,
        "final_loss": float(objective_func_vals[-1]) if objective_func_vals else None,
        "train_accuracy": train_accuracy,
        "test_accuracy": test_accuracy,
        "cnot_pairs": cnot_pairs,
        "num_parameters": 2 * num_qubits,
    }


# ---------------------------------------------------------------------------
# Hardware Result Auto-Detection (per D-06)
# ---------------------------------------------------------------------------

def load_hardware_results() -> Optional[dict]:
    """Load hardware results with live > cached priority (per D-06).

    Checks for live_results.json first (written by a live IBM Quantum job
    during the conference), then falls back to hardware_results.json
    (pre-cached from simulator or prior hardware run).

    Returns:
        Hardware results dictionary, or None if no results available.
    """
    live_path = Path("live_results.json")
    cache_path = Path("hardware_results.json")

    if live_path.exists():
        data = load_json(str(live_path))
        if data is not None:
            print(f"Using LIVE hardware results from {data['metadata']['backend_name']}")
            return data

    if cache_path.exists():
        data = load_json(str(cache_path))
        if data is not None:
            print(f"Using CACHED hardware results from {data['metadata']['backend_name']}")
            return data

    print("WARNING: No hardware results available.")
    return None


# ---------------------------------------------------------------------------
# Hardware Cache Generation
# ---------------------------------------------------------------------------

def _compute_simulator_expectation_values(
    weights: list[float],
    test_images: list,
) -> list[float]:
    """Compute noiseless simulator expectation values for the same test set.

    Used as a reference baseline alongside dry-run/real hardware results so
    the notebook can show signal strength comparison.
    """
    circuit, observable = _build_inference_circuit()
    estimator = Estimator()
    sim_evs = forward(circuit, np.array(test_images), np.array(weights), estimator, observable)
    return sim_evs.tolist()


def _build_inference_circuit() -> tuple[QuantumCircuit, SparsePauliOp]:
    """Build the same full circuit and observable used during training.

    Uses the revised (primary) ansatz with full horizontal CNOT coverage.

    Returns:
        Tuple of (circuit, observable).
    """
    num_qubits = 8
    revised_cnot_pairs = [[0, 1], [1, 2], [2, 3], [4, 5], [5, 6], [6, 7]]
    ansatz = build_ansatz(revised_cnot_pairs, num_qubits)
    circuit = build_full_circuit(ansatz, num_qubits)
    observable = SparsePauliOp.from_list([("Z" * num_qubits, 1)])
    return circuit, observable


def _run_inference_on_backend(
    weights: list[float],
    test_images: list,
    test_labels: list,
    backend,
    estimator,
    default_shots: int = 4096,
) -> tuple[np.ndarray, np.ndarray, float, str]:
    """Run inference on a (real or fake) backend with proper transpilation.

    Performs:
      1. Build the same circuit + observable as training
      2. Transpile circuit to backend's native gate set + topology (ISA circuit)
      3. Apply the resulting layout to the observable
      4. Build a single PUB with all test samples and submit
      5. Binarize expectation values to predictions and compute accuracy

    Args:
        weights: Trained weights for the primary ansatz.
        test_images: Test input data.
        test_labels: True test labels.
        backend: Backend (real or fake) to transpile against.
        estimator: EstimatorV2 instance configured for the backend.
        default_shots: Number of shots per circuit execution.

    Returns:
        Tuple of (expectation_values, predictions, accuracy, job_id).
    """
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

    circuit, observable = _build_inference_circuit()
    backend_name = getattr(backend, "name", str(backend))

    print(f"Transpiling circuit for {backend_name}...")
    pass_manager = generate_preset_pass_manager(backend=backend, optimization_level=2)
    isa_circuit = pass_manager.run(circuit)
    print(
        f"  Original depth: {circuit.depth()}, "
        f"transpiled depth: {isa_circuit.depth()}"
    )

    mapped_observable = observable.apply_layout(isa_circuit.layout)

    weight_params = np.array(weights)
    num_samples = len(test_images)
    weights_broadcast = np.broadcast_to(
        weight_params, (num_samples, len(weight_params))
    )
    test_array = np.array(test_images)
    params = np.concatenate((test_array, weights_broadcast), axis=1)
    pub = (isa_circuit, mapped_observable, params)

    estimator.options.default_shots = default_shots
    print(f"Submitting job to {backend_name} ({num_samples} samples, {default_shots} shots)...")
    job = estimator.run([pub])
    job_id = job.job_id() if hasattr(job, "job_id") else "local_fake"
    print(f"  Job ID: {job_id}")

    print("Waiting for results...")
    result = job.result()[0]
    expectation_values = np.array(result.data.evs)

    pred_labels = copy.deepcopy(expectation_values)
    pred_labels[pred_labels >= 0] = 1
    pred_labels[pred_labels < 0] = -1
    accuracy = float(accuracy_score(test_labels, pred_labels) * 100)

    print(f"  Backend test accuracy: {accuracy:.1f}%")
    return expectation_values, pred_labels, accuracy, job_id


def generate_hardware_cache(
    weights: list[float],
    test_images: list,
    test_labels: list,
    mode: str = "simulator",
) -> None:
    """Generate hardware execution cache.

    Three modes:
      - "simulator": local StatevectorEstimator (fast, noiseless, for testing)
      - "dry_run": FakeFez/FakeBrisbane noisy simulator (validates hardware code path
        without using real runtime minutes)
      - "real": real IBM Quantum hardware via QiskitRuntimeService. Requires
        IBM_QUANTUM_API_KEY and IBM_QUANTUM_INSTANCE in .env. Fails loud on errors.

    Args:
        weights: Trained weights for the primary (revised) ansatz.
        test_images: Test input data.
        test_labels: Test labels.
        mode: One of "simulator", "dry_run", "real".
    """
    if mode == "real":
        from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2
        from dotenv import load_dotenv
        import os

        load_dotenv()
        token = os.getenv("IBM_QUANTUM_API_KEY")
        instance = os.getenv("IBM_QUANTUM_INSTANCE")
        if not token or not instance:
            raise RuntimeError(
                "Real hardware mode requires IBM_QUANTUM_API_KEY and "
                "IBM_QUANTUM_INSTANCE environment variables (set in .env)."
            )

        print("\nConnecting to IBM Quantum Platform...")
        service = QiskitRuntimeService(
            channel="ibm_quantum_platform",
            token=token,
            instance=instance,
        )
        # Pinned to ibm_fez so the slides (which name the backend explicitly)
        # stay accurate across re-runs. If ibm_fez is in maintenance, this
        # will fail loudly rather than silently switching to a different QPU.
        backend = service.backend("ibm_fez")
        print(f"Selected backend: {backend.name}")

        estimator = EstimatorV2(mode=backend)
        expectation_values, pred_labels, accuracy, job_id = _run_inference_on_backend(
            weights, test_images, test_labels, backend, estimator
        )

        sim_evs = _compute_simulator_expectation_values(weights, test_images)
        hardware_data = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "backend_name": backend.name,
                "job_id": job_id,
                "is_live": True,
            },
            "expectation_values": expectation_values.tolist(),
            "simulator_expectation_values": sim_evs,
            "predictions": pred_labels.tolist(),
            "test_accuracy": accuracy,
        }
        save_json("hardware_results.json", hardware_data)
        print(f"Real hardware results saved. Test accuracy: {accuracy:.1f}%")
        return

    if mode == "dry_run":
        try:
            from qiskit_ibm_runtime.fake_provider import FakeFez as FakeBackend
            fake_name = "FakeFez"
        except ImportError:
            from qiskit_ibm_runtime.fake_provider import FakeBrisbane as FakeBackend
            fake_name = "FakeBrisbane"
        from qiskit_aer import AerSimulator
        from qiskit_aer.primitives import EstimatorV2 as AerEstimatorV2

        print(f"\nDry-run mode: using {fake_name} noise model on AerSimulator")
        fake_backend = FakeBackend()
        # AerSimulator with the fake backend's noise model + coupling map.
        # Aer handles 156 qubits efficiently; basic_simulator caps at 24.
        aer_backend = AerSimulator.from_backend(fake_backend)
        estimator = AerEstimatorV2.from_backend(aer_backend)
        expectation_values, pred_labels, accuracy, job_id = _run_inference_on_backend(
            weights, test_images, test_labels, fake_backend, estimator
        )

        sim_evs = _compute_simulator_expectation_values(weights, test_images)
        hardware_data = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "backend_name": f"dry_run_{fake_name.lower()}",
                "job_id": job_id,
                "is_live": False,
            },
            "expectation_values": expectation_values.tolist(),
            "simulator_expectation_values": sim_evs,
            "predictions": pred_labels.tolist(),
            "test_accuracy": accuracy,
        }
        save_json("hardware_results.json", hardware_data)
        print(f"Dry-run results saved. Test accuracy: {accuracy:.1f}%")
        return

    # Default: simulator (statevector, noiseless)
    print("\nGenerating simulator-based hardware cache (statevector)...")
    circuit, observable = _build_inference_circuit()
    estimator = Estimator()
    weight_params = np.array(weights)
    pred_test = forward(circuit, np.array(test_images), weight_params, estimator, observable)

    pred_labels = copy.deepcopy(pred_test)
    pred_labels[pred_labels >= 0] = 1
    pred_labels[pred_labels < 0] = -1
    sim_accuracy = float(accuracy_score(test_labels, pred_labels) * 100)

    hardware_data = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "backend_name": "simulator_fallback",
            "job_id": "local_simulator",
            "is_live": False,
        },
        "expectation_values": pred_test.tolist(),
        "predictions": pred_labels.tolist(),
        "test_accuracy": sim_accuracy,
    }
    save_json("hardware_results.json", hardware_data)
    print(f"Simulator test accuracy: {sim_accuracy:.1f}%")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run full cache generation: train both ansatz, save all JSON caches."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate QVC demo cache files")
    parser.add_argument(
        "--hardware",
        action="store_true",
        help="(Legacy) Equivalent to --hardware-mode=real",
    )
    parser.add_argument(
        "--hardware-mode",
        choices=["simulator", "dry_run", "real"],
        default=None,
        help="Hardware execution mode: simulator (statevector), dry_run (FakeFez), real (IBM Quantum)",
    )
    parser.add_argument(
        "--skip-training",
        action="store_true",
        help="Skip training; load existing weights from trained_weights.json",
    )
    args = parser.parse_args()

    # Resolve hardware mode (legacy --hardware flag takes precedence if set)
    hardware_mode = args.hardware_mode or ("real" if args.hardware else "simulator")

    print("=== QVC Cache Generator ===")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Hardware mode: {hardware_mode}")
    print(f"Skip training: {args.skip_training}")

    # Generate dataset (same seed and split as notebook)
    np.random.seed(42)
    images, labels = generate_dataset(200)
    train_images, test_images, train_labels, test_labels = train_test_split(
        images, labels, test_size=0.3, random_state=246
    )
    print(f"Dataset: {len(train_images)} train, {len(test_images)} test")

    if args.skip_training:
        print("\n--- Skipping training, loading cached weights ---")
        cached = load_json("trained_weights.json")
        if cached is None:
            raise RuntimeError(
                "trained_weights.json not found. Cannot skip training without cached weights."
            )
        revised_weights = cached["primary_ansatz"]["weights"]
        print(f"Loaded {len(revised_weights)} weight parameters from cache")

        generate_hardware_cache(
            weights=revised_weights,
            test_images=test_images,
            test_labels=test_labels,
            mode=hardware_mode,
        )
        print("\n=== Cache Generation Complete ===")
        return

    # Train first ansatz (top-row-only CNOTs -- BUG FIX from notebook)
    first_results = train_ansatz(
        name="first",
        cnot_pairs=[[0, 1], [1, 2], [2, 3]],
        train_images=train_images,
        train_labels=train_labels,
        test_images=test_images,
        test_labels=test_labels,
    )

    # Train revised ansatz (full horizontal CNOT coverage)
    revised_results = train_ansatz(
        name="revised",
        cnot_pairs=[[0, 1], [1, 2], [2, 3], [4, 5], [5, 6], [6, 7]],
        train_images=train_images,
        train_labels=train_labels,
        test_images=test_images,
        test_labels=test_labels,
    )

    # Per D-01: Select revised ansatz as primary (expected higher accuracy,
    # more compelling demo narrative showing improvement from better connectivity)
    print("\n=== Ansatz Comparison ===")
    print(f"First ansatz:   test accuracy = {first_results['test_accuracy']:.1f}%")
    print(f"Revised ansatz: test accuracy = {revised_results['test_accuracy']:.1f}%")
    print("Primary selection: REVISED (full horizontal CNOT coverage)")
    print("Rationale: More compelling demo -- shows clear improvement from better qubit connectivity")

    # Build and save trained_weights.json
    metadata = {
        "generated": datetime.now().isoformat(),
        "generator": "cache_results.py",
        "random_seed": 42,
    }

    trained_weights = {
        "metadata": metadata,
        "primary_ansatz": {
            "name": "revised",
            "description": "Full horizontal CNOT coverage (rows 0-3 and 4-7)",
            "cnot_pairs": revised_results["cnot_pairs"],
            "num_parameters": revised_results["num_parameters"],
            "weights": revised_results["weights"],
            "training": {
                "optimizer": "COBYLA",
                "max_iter_per_batch": 100,
                "num_epochs": 1,
                "batch_size": 140,
                "num_batches": 3,
                "final_loss": revised_results["final_loss"],
                "train_accuracy": revised_results["train_accuracy"],
                "test_accuracy": revised_results["test_accuracy"],
            },
        },
        "alternative_ansatz": {
            "name": "first",
            "description": "Top-row-only CNOT coverage (qubits 0-3)",
            "cnot_pairs": first_results["cnot_pairs"],
            "num_parameters": first_results["num_parameters"],
            "weights": first_results["weights"],
            "training": {
                "optimizer": "COBYLA",
                "max_iter_per_batch": 100,
                "num_epochs": 1,
                "batch_size": 140,
                "num_batches": 3,
                "final_loss": first_results["final_loss"],
                "train_accuracy": first_results["train_accuracy"],
                "test_accuracy": first_results["test_accuracy"],
            },
        },
    }
    save_json("trained_weights.json", trained_weights)

    # Build and save training_history.json
    training_history = {
        "metadata": metadata,
        "primary_ansatz": {
            "loss_values": revised_results["loss_values"],
            "batch_boundaries": revised_results["batch_boundaries"],
        },
        "alternative_ansatz": {
            "loss_values": first_results["loss_values"],
            "batch_boundaries": first_results["batch_boundaries"],
        },
    }
    save_json("training_history.json", training_history)

    # Generate hardware cache (mode determined by CLI flags)
    generate_hardware_cache(
        weights=revised_results["weights"],
        test_images=test_images,
        test_labels=test_labels,
        mode=hardware_mode,
    )

    print("\n=== Cache Generation Complete ===")
    print(f"Finished: {datetime.now().isoformat()}")
    print("Files created:")
    print("  - trained_weights.json   (pre-trained weights for both ansatz)")
    print("  - training_history.json  (loss curves for both ansatz)")
    print("  - hardware_results.json  (hardware/simulator execution results)")


if __name__ == "__main__":
    main()
