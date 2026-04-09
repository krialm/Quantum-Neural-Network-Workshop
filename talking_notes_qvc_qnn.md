# Talking Notes — QVC_QNN.ipynb (Training → Evaluation → Hardware)

**Total budget:** 22:30 (script runs to 21:45, leaving 45s end buffer). Back-loaded toward the hardware payoff.
**Format:** verbatim script. Read the quoted blocks aloud. Markers like `[WHILE RUNNING — CORE]` and `[STRETCH]` only appear in the live-training section and tell you how to flex with wall-clock.
**Tone:** neutral, conversational, no exclamation, no filler phrases like "alright folks."

---

## Section 1 — Choosing an ansatz `[00:00–01:15]`

### Cell 23 — What an ansatz is `[00:00–00:25]`
> "You've seen the data encoded into the quantum state with the feature map. Now we need the trainable part of the model, which is called the ansatz. If the feature map is the input layer of a neural network, the ansatz is the weights: a parameterized circuit with tunable thetas, and training the classifier means tuning those thetas. Three design pressures shape the choice of ansatz in practice: keep it shallow because hardware is noisy, match the structure of the problem, and do not over-parameterize."

### Cell 24 — Building the ansatz `[00:25–01:15]`
> "Here is the ansatz. Sixteen trainable parameters, two per qubit, arranged in three stacked layers: an RY rotation on every qubit, a set of CNOT gates, then an RX rotation on every qubit. Watch the CNOT pattern. The list is zero-one, one-two, two-three, then four-five, five-six, six-seven. Two linear chains. The data is a two-by-four image, so qubits zero through three are the top row and qubits four through seven are the bottom row. The CNOTs run along each row. We are telling the circuit, through the gate topology alone, that pixels on the same row can influence each other. No coupling between rows, no wrap-around. The entanglement pattern *is* the image geometry. That is what 'match the problem structure' gives you as an ansatz design choice."

---

## Section 2 — Full circuit and observable `[01:15–02:00]`

### Cells 25, 26 — Composing feature map and ansatz `[01:15–01:35]`
> "Now we stack the feature map and the ansatz into one circuit. One Qiskit call, `full_circuit.compose`, and we have a single parameterized model: pixels in, thetas as weights, one quantum circuit that runs them together. The classical analogue is stacking an input layer on top of a weights layer in a neural network."

### Cells 27, 28 — The observable `[01:35–02:00]`
> "The last piece is the observable: the quantity we measure to turn the quantum state into a classical number. We use Z-to-the-eighth, a tensor product of Pauli-Z on every qubit. What comes back is one real number between minus one and plus one per input image. Hold on to one detail, because it comes back in the hardware section: the classifier cares about the *sign* of that number, not its magnitude. Positive is one class, negative is the other."

---

## Section 3 — forward() and loss `[02:00–03:30]`

### Cell 30 — forward() `[02:00–03:00]`
> "This is the forward pass. It takes the circuit, a batch of input images, a set of weights, an estimator, and an observable, and returns one expectation value per input. This is the only function in the notebook that talks to the quantum backend. Everything else (loss, optimizer, accuracy metric) is classical Python. The hybrid pattern falls out of that split: classical code runs the loop and calls into the quantum chip only to evaluate the model."

### Cell 32 — mse_loss `[03:00–03:30]`
> "The loss is mean squared error. Predictions live in minus-one to plus-one, labels live in minus-one to plus-one, so MSE fits directly: no softmax, no cross-entropy. Push the prediction toward the label, square the error, average."

---

## Section 4 — Backend selection and pinning `[03:30–05:15]`

### Cell 38 — API key and service `[03:30–04:15]`
> "To run on real hardware we need an IBM Quantum API key. It lives in a dotenv file that we do not check into git, and the QiskitRuntimeService reads it from the environment. If you want to try this yourself after the talk, the IBM Quantum portal gives you a free-tier key in about two minutes."

### Cell 40 — Backend pin `[04:15–05:15]`
> "We're explicitly pinning the backend to `ibm_fez`. In production you would call `service.least_busy` and let the runtime pick a machine with the shortest queue. We're not doing that here, and the reason is worth stating directly. The hardware results later in the notebook were run ahead of time on `ibm_fez`, and the transpiled circuit in the next section is tied to fez's specific qubit layout and gate set. If we let the backend float, the cached results would not match. So: pinning for reproducibility, not as best practice."

---

## Section 5 — Transpilation `[05:15–06:45]`

### Cells 42, 44 — Pass manager `[05:15–06:45]`
> "Before we can run the circuit on fez we have to transpile it. A real quantum computer has a native gate set, a fixed qubit connectivity graph, and timing constraints, none of which match the abstract circuit we just built. The pass manager handles the translation. It decomposes our rotations and entanglers into fez's native gates, picks a physical qubit layout that respects the connectivity, and schedules the operations in time. We also attach a dynamical decoupling pass, which inserts pairs of X gates on qubits sitting idle so they refocus instead of decohering while they wait. One line of Python runs all of that."

---

## Section 6 — Live training slice `[06:45–09:15]`

### Cell 47 — Run the 10 COBYLA iterations `[06:45–09:15]`

`[PRE-RUN — say this before hitting Shift-Enter]`
> "We're about to train the classifier. You'll watch ten iterations of the optimization loop on a twenty-sample mini-batch, running on a local statevector simulator. This is not a trained model. The real run was a hundred iterations on the full dataset, and we'll load those weights in a moment. The point of running it live is to see the loop turn: the optimizer propose weights, the circuit evaluate, the loss print, the next proposal. Don't judge the final loss number. Judge the fact that it moved."

`[Hit Shift-Enter]`

`[WHILE RUNNING — CORE, ~45 seconds, always delivered]`
> "The optimizer is COBYLA. It is gradient-free, meaning it never asks for a derivative of the loss with respect to the weights, and that constraint is load-bearing on quantum hardware. Gradients of a quantum circuit with respect to its parameters do exist (they're called parameter-shift gradients), but estimating them requires running the circuit twice per parameter, per data point, and on noisy hardware each run comes back with shot noise on top. The cost of a single gradient step scales badly, and the estimate itself is noisy. Gradient-free methods sidestep this. They propose weights, evaluate the loss, compare, propose again. COBYLA, SPSA, and Nelder-Mead dominate variational quantum training in the NISQ era because they tolerate the kind of noise quantum hardware produces."

`[STRETCH A — drop in if still running]`
> "There is a second reason gradient-free fits here. The ansatz has sixteen trainable parameters, which is small by machine-learning standards, and COBYLA behaves well in low-dimensional parameter spaces. Scale up to a hundred or a thousand parameters and COBYLA starts to struggle. At that point you reach for SPSA (simultaneous perturbation), which estimates a noisy gradient from two function evaluations regardless of dimension. For sixteen weights, COBYLA is fine."

`[STRETCH B — drop in if still running after STRETCH A]`
> "One more thing to watch while this runs. Every printed loss came from running the full eight-qubit circuit on a simulator, once per image, across twenty images per loss call. COBYLA calls the loss many times per iteration. Even on a statevector simulator, that is where the wall-clock goes. On real hardware it would be slower by orders of magnitude, which is why the cached hundred-iteration run we're about to load was done once, ahead of time."

`[CUT TO HERE IF DONE — graceful landing, always delivered once the cell finishes]`
> "Done. The loss moved, not dramatically, because ten iterations on twenty samples is a peek, not a training run. But the loop turned, and every printed number came from a quantum circuit evaluation. That is training a quantum classifier."

`[FALLBACK IF HANG >90s]`
> "While this finishes up in the background, let's look at what a hundred iterations on the full dataset gave us."
→ jump to cell 49.

---

## Section 7 — Cached weights and convergence `[09:15–11:15]`

### Cell 49 — Load trained weights `[09:15–10:00]`
> "Here are the real weights. A hundred COBYLA iterations, full training set, cached to `trained_weights.json`. Sixteen numbers. That is the trained model. If I wanted to hand this classifier to a colleague, I would email them this file and the circuit definition, and they would have everything."

### Cell 51 — Convergence plot `[10:00–11:15]`
> "Here is the full loss curve from that training run. A hundred data points, one per COBYLA iteration, pulled straight from `training_history.json`. Two things about this shape. First, it is not monotonic. COBYLA occasionally accepts a step that makes the loss worse because it is probing the local geometry, and you can see those small upticks. Second, it flattens out the way a classical training curve does, because the outer loop *is* classical. A machine-learning person looking at this plot could not tell, from the shape alone, that the inner loss evaluations were running on a quantum circuit."

---

## Section 8 — Test eval on simulator `[11:15–12:45]`

### Cell 53 — Test set predictions `[11:15–12:45]`
> "The real test: images the classifier has never seen. We held out thirty percent of the dataset at the start. Run the trained weights forward through the circuit on every test image, take the sign of the expectation value (positive becomes plus one, negative becomes minus one), compare to the true labels. One hundred percent test accuracy. A flat training loss is necessary but not sufficient; the test accuracy is the real claim. One detail to hold on to: the classifier does not care about the magnitude of $\langle Z^{\otimes 8}\rangle$. It cares only about which side of zero it lands on. That distinction matters in the next section."

---

## Section 9 — Hardware payoff `[12:45–19:45]`

### [12:45–13:15] WOW OPEN — Cell 58 left panel
> "We took the trained model and ran the full test set on a real quantum computer. A hundred-and-fifty-six-qubit superconducting processor called `ibm_fez`, IBM's current Heron-r2 generation. The left panel shows what came back. Simulator: one hundred percent. Hardware: one hundred percent. A variational quantum classifier, trained on a laptop, running on real quantum hardware, correctly classifying every image in the test set."

`[pause briefly — let the bar chart land]`

### [13:15–18:15] THE REAL STORY — Cell 57 and Cell 58 right panel

> "That chart is misleading. Not wrong, misleading. The accuracy plot hides what is happening on the chip. Look at the right panel. Those are the mean absolute expectation values. On the simulator, the average magnitude is about zero-point-four-four. On hardware, it drops to about zero-point-four-zero. A nine percent reduction. That nine percent is not a bug. It is decoherence. It is readout error. It is what makes a real quantum computer different from an abstract mathematical model. The noise channel on fez is, to first approximation, *contractive*: it pulls every expectation value toward zero. Think of it as multiplying every output by a number slightly less than one. Simulator says zero-point-eight, hardware says zero-point-seven-two. Simulator says minus-zero-point-five, hardware says minus-zero-point-four-five. Every prediction is numerically degraded."

> "And now the part that matters. All sixty prediction signs are preserved. Every single one. Noise shrank the magnitudes, but never enough to push any expectation value across zero. I told you two minutes ago that the classifier only looks at the sign. So the predictions, the actual output of the model, are unaffected. The chip is noisy, the numbers are wrong, and the answers are still right."

> "Variational quantum classifiers work on today's hardware for one structural reason, and you are looking at it. They do not need clean magnitudes. They need clean signs. As long as the noise is contractive, as long as it pulls toward zero rather than randomly flipping things, the decision boundary survives. Write this down as a design principle: *choose an observable and a loss so that the quantity you care about depends only on a coarse feature of a noisy estimate.* That principle is called sign-robustness, and it is why VQCs run on NISQ hardware at all."

### [18:15–18:45] TRANSPILATION ASIDE
> "A short aside on why the number is nine percent and not ninety. The transpilation pass we ran a few cells back did real work, and the dynamical decoupling pulses on idle qubits did most of it. Without them, the expectation values would collapse much further, and the accuracy chart on the left would not look the way it does."

### [18:45–19:45] NISQ HOOK — Cell 59 rephrased
> "A note on the limits of what we just showed. This is a binary classification task, and binary classification is easy mode for NISQ hardware, precisely because of the sign-robustness we just walked through. Push this to multi-class, say ten digits instead of two line orientations, and the expectation-value degradation would start costing us accuracy, because the decision boundaries no longer reduce to crossing zero. Same for regression, where the magnitude *is* the output. So the demo is clear about what works on today's quantum hardware, and clear about where the ceiling is. The ceiling is real, and the research frontier is in finding more algorithm classes that share the sign-robustness property."

---

## Section 10 — Recap `[19:45–21:45]`

### Cell 60 — Closing `[19:45–21:45]`
> "Three things to take away. First: training a quantum classifier is a hybrid loop. The classical optimizer runs the show; the quantum chip evaluates the model. Gradient-free methods dominate because gradients on quantum circuits are expensive and noisy. Second: generalization is the real test. A flat training loss is not enough. We held out thirty percent of the data and verified one hundred percent accuracy on samples the model never saw. Third: variational quantum classifiers are sign-robust under NISQ noise. Real hardware on fez shrank our expectation values by nine percent and every prediction sign was preserved. Caring only about the sign of a noisy expectation value is the property that lets this algorithm class run on today's quantum hardware. The cheatsheet and the cached result files are in the repo if you want to reproduce any of this after the session."

---

## Operational reminders

- **Pre-run cells 0–22 in kernel warmup before the audience arrives.** This populates `train_images`, `test_images`, `feature_map`, `num_qubits`, and anything the co-presenter's half leaves in scope, so your demo can land directly on cell 23 without re-running the dataset or feature map live.
- **Cells you land on and execute live in §1–§2:** 24 (ansatz, shows circuit diagram), 26 (full circuit composition, shows the combined diagram), 28 (observable definition — fast, no output worth waiting for, run silently).
- **Do not re-execute cells 12, 13, or 22** (imports, dataset, feature map) — they were pre-warmed and re-running them wastes time.
- **Cell 47 is the only risky cell.** Pre-frame, narrate with CORE, extend with STRETCH A / STRETCH B as needed, land on CUT TO HERE, or pivot via FALLBACK to cell 49.
- **Exact numbers locked in the script**: simulator mean |EV| ≈ 0.444, hardware mean |EV| ≈ 0.40, reduction ≈ 9%, signs preserved 60/60. These are from cell 59's committed markdown. If a live hardware re-run produces different numbers, update both cell 59 and this file before the talk.
- **Seed 42 is set in cell 47**, so the live training curve is reproducible. Rehearse against the actual printed losses so the CUT TO HERE landing line matches what the audience sees.
- **Time the cell 47 wall-clock once on the presentation laptop.** If it is under 30s, drop STRETCH B. If it is over 75s, keep both stretches and tighten CORE.
- **Cells 40 and 44 hit IBM live.** They are NOT cached. If the IBM connection fails on stage, the transpilation section halts. Pre-run these once on the presentation laptop before going on stage. The rest of the script — training (47), cached weights (49), convergence (51), test eval (53), hardware results (57–58) — does not depend on them.
- **End buffer:** script lands at 21:45 against a 22:30 budget. 45 seconds of slack for Q&A handoff, slow cells, or the hardware section running long.
- **Backup:** git WIP commit `ca0a3bc` holds the pre-rebuild state. `git reset --hard HEAD` reverts the working-tree edits (rebuild + simplification + resources append).
- **Resources cell (61)** — optional scroll target after the recap. Holds the `Continue Your Quantum Journey` links and presenter LinkedIn handles. Not spoken during the script; bring it up if Q&A time allows or if an audience member asks where to learn more.
