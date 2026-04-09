# Technology Stack

**Project:** QVC Conference Presentation
**Researched:** 2026-03-24
**Note:** WebSearch, WebFetch, and Bash unavailable during research. Versions based on training data (cutoff ~May 2025). All versions flagged for manual verification with `pip index versions <package>`.

## Recommended Stack

### Existing Core (Already in Notebook)

These are locked by the existing `QVC_QNN.ipynb` and should not change.

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| qiskit | >=1.2 | Quantum circuit construction, transpilation | Already used in notebook; Qiskit 1.x is the stable API post-migration | MEDIUM (verify current) |
| qiskit-ibm-runtime | >=0.28 | IBM hardware access, EstimatorV2 | Required for live hardware demo; notebook already imports it | MEDIUM (verify current) |
| numpy | >=1.26 | Numerical operations | Standard, already in notebook | HIGH |
| matplotlib | >=3.8 | Plotting (loss curves, accuracy, confusion matrices) | Already used; best for static publication-quality plots | HIGH |
| scikit-learn | >=1.4 | accuracy_score, train_test_split | Already used in notebook | HIGH |
| scipy | >=1.12 | minimize (optimizer for VQC) | Already used in training loop | HIGH |
| python-dotenv | >=1.0 | Load IBM Quantum API token from .env | Already in notebook for credential management | HIGH |

### Slide Deck Generation

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| python-pptx | >=0.6.23 | Programmatic .pptx creation | The only mature Python library for PowerPoint generation. Directly produces .pptx as required by project constraints. Supports slide masters, placeholders, charts, and embedded images. | HIGH |

**Why python-pptx and not alternatives:**
- **Not reveal.js/Marp/Slidev:** Project constraint explicitly requires `.pptx` format. HTML-based slide tools produce web slides, not PowerPoint files.
- **Not LibreOffice automation:** Heavyweight dependency, unreliable rendering fidelity, harder to script.
- **Not Google Slides API:** Adds cloud dependency and auth complexity for no benefit.

python-pptx lets us script slide generation from Python -- embed matplotlib figures directly as images, create consistent layouts programmatically, and version-control the generation script alongside the notebook.

### Notebook Polishing and Live Demo

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| jupyter / jupyterlab | >=4.0 | Live demo environment | Standard notebook environment. JupyterLab 4 has improved rendering, better cell output handling, and a cleaner presentation-ready UI. | HIGH |
| nbconvert | >=7.14 | Export notebook to HTML/slides for backup | Fallback: if live demo fails, present pre-rendered output. Also useful for generating slide-format HTML from notebook cells. | HIGH |
| jupyter-contrib-nbextensions | latest | Cell hiding, execution helpers | Hide code cells during demo (show only outputs), auto-run cells on open. Useful for "clean" presentation mode. | MEDIUM |

**Live demo strategy:** Run in JupyterLab with cells pre-organized into demo sections. Use cell tags to mark cells as "demo" vs "setup" vs "skip." Pre-run expensive cells (training) and cache results; only re-execute visualization and hardware cells live.

**Why not RISE (now `rise` or `nbslides`):**
- RISE converts notebook cells into reveal.js slides inside Jupyter. Sounds appealing but problematic in practice: cell outputs resize awkwardly, matplotlib figures don't scale well to slide format, and the tool has had inconsistent maintenance.
- Better approach: Use the notebook as-is for the live demo (audience sees real Jupyter), and use python-pptx for the structured slide content. Two tools, each doing what it does best.

### Visualization Libraries

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| matplotlib | >=3.8 | Loss curves, accuracy plots, confusion matrices, bar charts | Already in notebook. The standard for publication-quality static plots. Conference projectors need high-contrast, large-font figures -- matplotlib excels here with full styling control. | HIGH |
| seaborn | >=0.13 | Confusion matrix heatmaps, styled statistical plots | Builds on matplotlib with better defaults for heatmaps and categorical plots. `sns.heatmap()` for confusion matrices is cleaner than raw matplotlib. | HIGH |
| qiskit.visualization | (bundled) | Circuit diagrams, Bloch spheres | `circuit.draw('mpl')` produces publication-quality circuit diagrams. Built into qiskit, no extra install. Essential for showing the VQC architecture to audience. | HIGH |
| Pillow | >=10.0 | Image manipulation for slides | Required by python-pptx for embedding images. Also useful for resizing/compositing figures before slide insertion. | HIGH |

**Why NOT these visualization tools:**
- **Not Plotly:** Interactive plots are wasted on a projector. Adds JavaScript complexity. matplotlib static figures render faster, scale to any resolution, and embed cleanly into PowerPoint.
- **Not bokeh:** Same issue as Plotly -- interactivity not needed for conference projection.
- **Not manim/3Blue1Brown:** Overkill for this use case. We need charts and circuit diagrams, not mathematical animations.
- **Not qiskit-aer visualization:** Deprecated/merged into core qiskit. Use `qiskit.visualization` directly.

### Presentation Support Tools

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| IPython.display | (bundled) | Rich display in notebook (HTML, images, markdown) | Format notebook output for audience readability during live demo. Display pre-rendered images, styled tables, markdown explanations between code cells. | HIGH |
| tqdm | >=4.66 | Progress bars for training loop | Audience needs visual feedback during live training. `tqdm.notebook` provides clean progress bars in JupyterLab. | HIGH |
| pickle / joblib | (stdlib/bundled) | Cache trained model parameters | Pre-train and cache optimal parameters so live demo can skip 10+ minute training. Load cached params, show training was done, then demonstrate evaluation and hardware execution. | HIGH |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Slides | python-pptx | reveal.js / Marp | Project requires .pptx format; HTML slides not accepted |
| Slides | python-pptx | Manual PowerPoint | Scripted generation lets us embed figures consistently and version-control |
| Visualization | matplotlib + seaborn | Plotly | Interactivity wasted on projector; adds complexity |
| Visualization | matplotlib + seaborn | Altair | Less control over fine styling; smaller ecosystem for quantum viz |
| Live demo | JupyterLab | VS Code notebooks | JupyterLab has better full-screen presentation mode; audience recognizes Jupyter |
| Live demo | JupyterLab | Google Colab | Requires internet; can't control environment; latency risk for live demo |
| Caching | pickle/joblib | MLflow | Overkill; we just need to save/load numpy arrays of trained parameters |
| Progress | tqdm | custom print statements | tqdm.notebook renders clean progress bars; print output is ugly on projector |

## Installation

```bash
# Existing core (likely already installed)
pip install qiskit qiskit-ibm-runtime numpy matplotlib scikit-learn scipy python-dotenv

# Presentation stack (new)
pip install python-pptx seaborn tqdm Pillow jupyterlab nbconvert

# Optional: notebook extensions for demo polish
pip install jupyter-contrib-nbextensions
```

## Version Verification Required

**IMPORTANT:** All version numbers are from training data (cutoff ~May 2025). Before committing to the stack, verify current versions:

```bash
# Run this to check latest available versions
pip index versions python-pptx qiskit qiskit-ibm-runtime seaborn tqdm jupyterlab nbconvert
```

Key things to verify:
- **qiskit**: Verify you're on 1.x (not 0.x). The API changed significantly at 1.0.
- **qiskit-ibm-runtime**: Verify EstimatorV2 is still the current primitive interface. IBM has been iterating on this.
- **python-pptx**: Stable library, unlikely to have breaking changes. Last major release was 0.6.x line.
- **JupyterLab**: Verify 4.x is current. JupyterLab 4 was a major rewrite.

## Stack Philosophy

This stack follows a "boring technology" principle:

1. **matplotlib over fancy JS viz libraries** -- works on every projector, embeds in PowerPoint, no browser/rendering surprises during live demo.
2. **python-pptx over slide frameworks** -- produces the exact .pptx format required, scriptable, version-controllable.
3. **JupyterLab as-is over slideshow plugins** -- audience sees a real notebook. Authenticity matters for a technical demo. Don't hide the tool.
4. **Pre-cached results over live training** -- a 10-minute training loop will kill your talk. Cache the results, show the code, load the pre-trained parameters, then demo evaluation live.

## Sources

- Project notebook (`QVC_QNN.ipynb`) -- analyzed imports and existing dependencies
- Project requirements.txt -- confirmed existing stack
- PROJECT.md -- confirmed .pptx format requirement and constraints
- Training data knowledge (May 2025 cutoff) -- all library recommendations. Flagged as MEDIUM confidence where version-specific.
