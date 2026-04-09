# QML Cheat Sheet — Talk Prep

Personal vocabulary + concept reference for the **Quantum Machine Learning with Qiskit** talk. Print or open on phone. Study time: ~30 min.

---

## Presentation surface

Single deliverable: continue the co-presented talk by driving live from `QVC_QNN.ipynb` (53-cell source notebook after the Friday hardening pass). Cells 0–14 (data generation + feature map) are pre-run in kernel warmup before the audience arrives; the visible portion starts at Section 1 of the talking notes (cell 15, "Choosing an Ansatz") and runs through Section 10 (cell 52, recap). The verbatim script, with timing markers and stretch/core/fallback fallbacks for the live-training cell, lives in `talking_notes_qvc_qnn.md`. Budget: 22:30, back-loaded toward the hardware payoff (§9 gets 7 minutes).

---

## Vocabulary (memorize the bold parts)

| Term | Plain-English meaning | Why it matters for your talk |
|---|---|---|
| **Qubit** | A quantum bit. Unlike a classical bit (0 or 1), it can be in a **superposition** of both at once. Has 2 basis states written as \|0⟩ and \|1⟩. | Your circuit has **8 qubits**, one per pixel of the 2x4 grid. |
| **Superposition** | A quantum state that is a mix of \|0⟩ and \|1⟩ with complex coefficients. Only collapses to a definite value when measured. | This is what makes quantum computers different from classical. The entire training happens in superposition. |
| **Measurement** | The act of observing a qubit. Forces the superposition to collapse to a single classical outcome (0 or 1) probabilistically. | Every prediction your VQC makes ends with measurement. |
| **Shots** | Number of times you run the circuit and measure to build statistics. More shots = more accurate results. | You used **4096 shots** per inference sample on ibm_fez. |
| **Expectation value** | The average measurement outcome over many shots. For the Z-observable, ranges from **-1 to +1**. | This is what your model outputs. Negative = "horizontal", positive = "vertical". |
| **Observable** | The thing you measure. For your talk: the **Z-observable on all 8 qubits** (`Z⊗Z⊗...⊗Z`). | Your slides mention "Z-observable" — this is what you're measuring. |
| **Quantum gate** | An operation on qubits. Like a function that transforms quantum states. | Your ansatz uses **RY**, **RX** (single-qubit rotations) and **CNOT** (entangling gate). |
| **CNOT gate** | "Controlled-NOT" — a 2-qubit gate. Flips the target qubit if the control qubit is \|1⟩. **Creates entanglement.** | Your revised ansatz uses 6 CNOTs to connect all 8 qubits across both rows of the pixel grid. |
| **Entanglement** | A correlation between qubits that is stronger than any classical correlation. Created by 2-qubit gates like CNOT. | The 6-CNOT ansatz from `QVC_QNN.ipynb` entangles both rows of the 2×4 pixel grid so the model can learn correlations across the spatial structure of the input. |
| **Ansatz** | A parameterized quantum circuit. The parameters are **tuned by classical optimization** during training. Greek for "starting point". | Your ansatz has **16 parameters** (2 per qubit: one RY rotation + one RX rotation). |
| **Variational Quantum Circuit (VQC)** | A hybrid classical-quantum algorithm. The quantum circuit is the model, the classical optimizer trains it. | The whole talk is about VQCs. |
| **Feature map** | A quantum circuit that encodes classical data into a quantum state. Your case: each pixel value becomes a Z-rotation angle. | The co-presenter covers this in their half. You can defer feature-map questions to them. |
| **NISQ** | "Noisy Intermediate-Scale Quantum". The current era — quantum hardware exists but is noisy and small (50-1000 qubits). Pronounced "nisk". | You can casually drop "NISQ" — sounds expert without being pretentious. |
| **Decoherence** | The loss of quantum information over time. Qubits "forget" their state due to environmental noise. Two timescales: **T1** (relaxation) and **T2** (dephasing). | One of three reasons your hardware results show 9% signal reduction. |
| **Transpilation** | The process of adapting an abstract circuit to a specific hardware's native gate set and qubit topology. **Adds SWAP gates** when needed. | Your circuit went from depth 9 → depth 24 after transpilation for ibm_fez. |
| **COBYLA** | "Constrained Optimization BY Linear Approximation". A **gradient-free** classical optimizer. Pronounced "ko-BEE-la". | You used COBYLA because computing quantum gradients is expensive on NISQ devices. |
| **Estimator** (Qiskit primitive) | The Qiskit object that runs a circuit and returns expectation values. **Same API for simulator and real hardware.** | This is your "killer feature" point — your code didn't change between simulator and ibm_fez. |
| **Heron r2** | IBM's current generation of superconducting qubit processor. 156 qubits. Successor to "Eagle r3". | Your backend, **ibm_fez**, is a Heron r2. |

### Vocabulary — hardware and transpilation additions

Terms that come up during the IBM-setup, transpilation, and hardware-payoff sections of the notebook. Memorize these for the hardware discussion — they are the technical handles the audience expects you to be able to unpack if asked.

| Term | Plain-English meaning | Why it matters for the workshop |
|---|---|---|
| **ECR gate** | "Echoed cross-resonance" — Heron r2's *native* two-qubit gate. CNOT compiles down to roughly one ECR plus a handful of single-qubit rotations. | When you say "Heron natively executes ECR, not CNOT", you sound like you actually know the device. |
| **Tunable couplers** | A physical mechanism on Heron that lets the chip switch *off* always-on qubit-qubit interactions when two qubits are not being entangled. | This is the main reason Heron crosstalk is noticeably lower than the older Eagle generation. Mention it when explaining the backend choice. |
| **Heavy-hex connectivity** | IBM's standard chip topology. Every qubit has at most 3 neighbors. | Forces the transpiler to insert SWAPs for any non-local CNOT — the dominant reason your circuit went from depth 9 to depth 24. |
| **Dynamical decoupling** | Refocusing pulses inserted by the preset pass manager during qubit *idle time* to recover some T2 coherence for free. | Comes up in the transpilation slide. "The pass manager also inserts DD pulses on idle qubits" is a one-liner that sounds expert. |
| **Parameter-shift rule** | The canonical way to compute exact gradients of a quantum circuit. Costs $2P$ extra circuit runs per optimizer step (P = parameter count). | Already in your COBYLA explanation, but say the *name* of the rule on Friday — workshop audiences want the technical handle. |
| **Sign-robust observable** | Design principle: structure the loss so the prediction depends only on the *sign* of a noisy quantity, not its magnitude. | This is the workshop's punchline. Drop the phrase by name in the closing recap. |
| **Density matrix attenuation** | The mechanism: decoherence shrinks the off-diagonal elements of the density matrix, which is exactly what an expectation value depends on. | The "why" behind the magnitude-shrinks-but-sign-survives observation. One layer deeper than the main narrative if pressed. |
| **`StatevectorEstimator`** | Qiskit's exact, noiseless simulator estimator class. Imported in the workshop notebook directly. | Workshop audience will see the import — be ready to say "this is Qiskit's exact simulator, no shot noise, no hardware noise". |

---

## Key concepts (understand, don't memorize)

### 1. Why expectation values are between -1 and +1

The Z-observable for one qubit has eigenvalues +1 (for \|0⟩) and -1 (for \|1⟩). When you measure many times and average, you get a number between these two extremes. **+1 means you always measured \|0⟩**, **-1 means you always measured \|1⟩**, and **0 means a 50/50 mix**.

### 2. Why your binary classifier uses sign

Your model output is the expectation value (a continuous number in [-1, +1]). You binarize it: positive → vertical (+1), negative → horizontal (-1). This is the classification rule.

### 3. Why noise reduces magnitude but rarely flips sign

Noise tends to push states **toward the maximally mixed state** (the "uniform random" state, which has expectation value 0 for any observable). So noisy expectation values are pulled toward 0 — they shrink in magnitude. But unless the original value was already close to 0, the shrinkage isn't enough to flip the sign. **This is the entire reason your demo works on noisy hardware.**

### 4. Why gradient-free optimization matters

To compute the gradient of a quantum circuit's output with respect to its parameters, you use the "**parameter shift rule**". For each parameter, you have to run the circuit twice (with the parameter shifted by ±π/2) and take the difference. With 16 parameters, that's **32 extra circuit runs per gradient step**. On real hardware, that's expensive (more queue time) and noisy (more measurements averaged together). COBYLA avoids gradients entirely by using a simpler "test points and find the minimum" approach.

### 5. Why both rows of the pixel grid need to be entangled

The 2×4 pixel grid has spatial structure both horizontally and vertically. The 6-CNOT ansatz from `QVC_QNN.ipynb` connects qubits 0–3 (top row) and 4–7 (bottom row), so each row forms its own connected sub-graph and the parameter updates flowing through the circuit can learn correlations across both halves of the input. The general principle: **the entanglement graph of the ansatz should roughly match the spatial structure of the data.** If half your qubits were isolated from the other half, the model would not be able to learn correlations between the corresponding halves of the input.

### 6. Why shots matter (and why 4096 is enough) — *workshop only*

A quantum measurement gives you one outcome at a time, not an expectation value. To estimate $\langle Z^{\otimes 8}\rangle$ on hardware, you actually run the circuit S times, count how many bitstring parities are even versus odd, and form the empirical average. Standard sampling theory says the standard error of that estimate scales as $1/\sqrt{S}$. With **S = 4096**, the per-sample statistical error is about **0.016** — much smaller than the 9% magnitude shift we measured between simulator and hardware. Translation: what you see in the comparison chart is **real device noise**, not shot noise. If anyone asks "could the difference just be sampling noise?", that is your answer.

### 7. Why decoherence specifically attenuates expectation values — *workshop only*

Decoherence is not random bit-flip noise. The technical content: pure dephasing (T2) decays the off-diagonal elements of the density matrix, and amplitude damping (T1) drives the state toward the ground state. Both effects move the density matrix toward the maximally mixed state, which has expectation value zero for *any* traceless observable. So the visible signature of decoherence on a VQC is that magnitudes shrink — they get pulled toward zero. The reason VQCs survive: as long as the original prediction was not already on the decision boundary, "shrunk toward zero" still has the same sign.

### 8. Why 23 minutes is the right shape for the workshop — *workshop only*

Three substantive blocks (training, evaluation, hardware) at roughly 6.5 / 4.5 / 8.5 minutes, plus a 2-min intro and a 1.5-min recap. Tight enough to keep momentum, loose enough that one slow cell does not derail the session. The 2:00–8:30 stretch is the tightest — that is the section where the live training loop runs and where the prose-to-code ratio is highest. If you are running long anywhere, that is the section to compress (skip the loss-trajectory narration after cell 8).

---

## Numbers to know cold

| Number | What it is |
|---|---|
| **8** | qubits in your circuit |
| **16** | parameters in the ansatz (2 per qubit) |
| **200** | total images in dataset (140 train + 60 test) |
| **100** | COBYLA iterations on a single 140-sample training batch (the cached run) |
| **6** | CNOT gates in the revised ansatz |
| **4096** | shots per inference sample |
| **24** | depth of transpiled circuit on ibm_fez (was 9 before transpilation) |
| **156** | qubits on ibm_fez (Heron r2) |
| **100%** | test accuracy on both simulator and ibm_fez |
| **0.444** | mean expectation value magnitude on simulator |
| **~0.40** | mean expectation value magnitude on ibm_fez |
| **9%** | signal reduction from quantum noise |
| **60/60** | predictions where the sign was preserved despite noise |
| **22:30** | total runtime budget for the user's portion of the talk (`QVC_QNN.ipynb` cells 15–52) |
| **3** | substantive blocks in the workshop (training / evaluation / hardware) |
| **0.016** | approximate statistical error per expectation value at 4096 shots ($1/\sqrt{S}$) |
| **9** | depth of the abstract circuit before transpilation |
| **24** | depth of the same circuit after transpilation onto `ibm_fez` |

---

## Things you can deflect to the co-presenter

If asked something deep about these topics, redirect: "My co-presenter covered that in their half — happy to discuss after."

- The detailed math of the Z-feature map
- Why the specific CNOT pattern was chosen for the ansatz architecture
- The Bloch sphere representation of single qubits
- Density matrices vs state vectors
- The mathematical derivation of the parameter shift rule

---

## What to confidently say (your "I know this" answers)

1. "**The variational circuit takes classical pixel data, encodes it into qubit rotations, runs through a parameterized circuit, and measures the Z-observable to get a prediction in the range -1 to +1.**"

2. "**Training is a hybrid classical-quantum loop. COBYLA proposes parameters, we run the circuit on all training samples, compute MSE loss on the predictions, and feed it back to the optimizer.**"

3. "**Real hardware execution requires transpilation — adapting our abstract circuit to ibm_fez's native gate set and qubit topology. The depth went from 9 to 24 after transpilation.**"

4. "**The noise on hardware shrunk our signal magnitudes by 9%, but the signs were preserved on all 60 test samples — which is exactly why variational circuits work on NISQ devices.**"

5. "**Same Qiskit Estimator API for simulator and hardware — only the backend object changes. That's the killer feature for accessibility.**"

---

## Execution sequence — what to run, what to read, what to skip

Three kinds of cells: **PRE-WARM** (run by you in kernel warmup, audience never sees them execute), **LIVE** (Shift-Enter during the demo, audience watches the output), **READ** (markdown — scroll through, deliver the quoted line from the talking notes, no execution).

| Cell | Type | Action | Notes |
|---|---|---|---|
| 0–4   | READ     | pre-audience scroll-past | title/overview/data-gen headings |
| 5     | PRE-WARM | kernel warmup            | dataset + stratified split; populates `train_images`, `test_images` |
| 6     | READ     | (pre-warm zone)          | — |
| 7     | PRE-WARM | kernel warmup            | sample-image grid; seeded, reproducible figure |
| 8–13  | READ     | (pre-warm zone)          | data-encoding narrative, owned by co-presenter |
| 14    | PRE-WARM | kernel warmup            | `z_feature_map` build; populates `feature_map`, `num_qubits` |
| 15    | READ     | **SECTION 1 START**      | "Choosing an Ansatz" — land here when you begin |
| 16    | LIVE     | Shift-Enter              | ansatz diagram appears |
| 17    | READ     | deliver §2 first quote   | — |
| 18    | LIVE     | Shift-Enter              | full-circuit diagram appears |
| 19    | READ     | deliver §2 second quote  | — |
| 20    | LIVE     | Shift-Enter              | observable — no visible output, run silently |
| 21    | READ     | deliver §3 first quote   | — |
| 22    | LIVE     | Shift-Enter              | `forward()` defined — no output |
| 23    | READ     | deliver §3 second quote  | — |
| 24    | LIVE     | Shift-Enter              | `mse_loss()` defined — no output |
| 25    | READ     | scroll past `---`        | — |
| 26–29 | READ     | deliver §4 first quote   | 26/27/28 = pin + API key invitation + setup header; 29 = env-var format block |
| 30    | LIVE     | Shift-Enter              | loads `.env`, saves IBM credentials — no visible output |
| 31    | READ     | deliver §4 second quote  | pin rationale (`ibm_fez`) |
| 32    | LIVE     | Shift-Enter              | ⚠️ hits IBM live; prints `ibm_fez` — pre-warm before stage |
| 33    | READ     | deliver §5 intro         | — |
| 34    | LIVE     | Shift-Enter              | pass manager setup — no visible output |
| 35    | READ     | (continue §5 quote)      | — |
| 36    | LIVE     | Shift-Enter              | ⚠️ hits IBM target; prints transpiled depth 9 → 24 |
| 37–38 | READ     | deliver §6 PRE-RUN quote | training loop intro |
| 39    | LIVE     | Shift-Enter              | ⚠️ **RISKY CELL** — 10 COBYLA iterations, narrate with CORE/STRETCH/FALLBACK from §6 |
| 40    | READ     | deliver §7 first quote   | — |
| 41    | LIVE     | Shift-Enter              | loads `trained_weights.json`, prints train/test accuracy |
| 42    | READ     | deliver §7 second quote  | — |
| 43    | LIVE     | Shift-Enter              | convergence plot from `training_history.json` |
| 44    | READ     | deliver §8 quote         | — |
| 45    | LIVE     | Shift-Enter              | test-set eval, prints `Test accuracy on simulator: 100.0%` |
| 46–48 | READ     | deliver §9 WOW OPEN prep | hardware-results headers |
| 49    | LIVE     | Shift-Enter              | loads `hardware_results.json`, prints comparison stats |
| 50    | LIVE     | Shift-Enter              | sim-vs-hw bar chart — **the WOW OPEN visual** |
| 51    | READ     | deliver §9 NISQ HOOK     | sign-robustness markdown |
| 52    | READ     | deliver §10 Recap        | closing |

**Hardware dependency map:** Only cells **32** and **36** actually talk to IBM. Everything else — live training (39), cached weights (41), convergence (43), test eval (45), hardware results (49–50) — runs on cached JSONs or the local `StatevectorEstimator`. If IBM is down on stage, cells 32 and 36 throw but everything downstream still works; cover with "the transpilation step would normally run here, we cached the result" and move on.

**Risk budget:** Cell 39 is the only wall-clock gamble (10 COBYLA iter × 20 samples on an 8-qubit statevector simulator = ~5–60s depending on laptop). Everything else is either instant (cell drawings, JSON loads, matplotlib) or lives behind the IBM call in cells 32/36.

**Pre-warm checklist (do before audience arrives):**
1. Restart kernel.
2. Run cells 0–14 (menu: Cell → Run All Above at cell 15, or Shift-Enter through them manually).
3. Pre-run cells 32 and 36 once to warm the IBM connection; leave their outputs visible so you do not re-execute live.
4. Scroll back to cell 15. The audience should see the "Choosing an Ansatz" header when you take the keyboard.

---

## Study plan

Single-event study cadence. Everything you need sits in this cheatsheet plus `talking_notes_qvc_qnn.md` (the verbatim script) plus the notebook itself.

**Tonight (Tuesday):** Read this entire cheat sheet aloud, including the hardware-additions vocab subtable and key concepts 6–8. ~35 min. Mark anything that does not feel natural in your mouth — those are the things to study more.

**Wednesday:** Re-read the Vocabulary table *and* the workshop-additions subtable. Quiz yourself: cover the right column, see if you can explain each term in your own words. ~25 min.

**Thursday:** Re-read "Numbers to know cold" and "What to confidently say". Memorize the 5 confident answers. ~15 min. Walk through the 22:30 timing table in `talking_notes_qvc_qnn.md` once with a stopwatch.

**Friday morning:** Skim the whole cheat sheet one more time. ~10 min. Open `QVC_QNN.ipynb`, restart the kernel, and do one full Run All to confirm the cache files load and the figures regenerate. Pre-run cells 32 and 36 once so the IBM connection is warm (they hit ibm_fez live — the rest of the notebook runs from caches). Scroll to cell 15 so the audience sees the "Choosing an Ansatz" header when you begin. Then close the cheatsheet and trust yourself.
