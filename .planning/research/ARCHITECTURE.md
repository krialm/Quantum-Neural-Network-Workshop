# Architecture Patterns

**Domain:** Technical conference presentation with live quantum ML demo
**Researched:** 2026-03-24

## Recommended Architecture

Two-artifact system: a **scripted .pptx slide deck** and a **polished Jupyter notebook** with pre-cached results. The slide deck provides narrative structure; the notebook provides live proof.

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| `slides/generate_deck.py` | Script that builds .pptx from template + figures | Reads from `figures/`, writes to `output/presentation.pptx` |
| `figures/` directory | Stores all rendered matplotlib/seaborn figures as .png | Written by notebook cells, read by slide generator |
| `QVC_QNN_demo.ipynb` | Polished demo notebook (subset of original) | Reads cached params from `cache/`, writes figures to `figures/` |
| `cache/` directory | Pre-trained parameters, hardware results, fallback outputs | Written during prep, read during live demo |
| `demo_script.md` | Speaker notes, timing marks, fallback instructions | Human reads during rehearsal and presentation |

### Data Flow

```
[Pre-conference prep]
  QVC_QNN.ipynb (full notebook)
    -> train model -> cache/trained_params.pkl
    -> run on hardware -> cache/hardware_results.pkl
    -> generate all figures -> figures/*.png

[Slide generation]
  generate_deck.py
    -> reads figures/*.png
    -> reads slide structure (hardcoded or from config)
    -> writes output/presentation.pptx

[Live demo day]
  QVC_QNN_demo.ipynb (polished subset)
    -> loads cache/trained_params.pkl (skip training)
    -> runs evaluation cells live (fast, seconds)
    -> renders visualizations live (matplotlib, fast)
    -> loads cache/hardware_results.pkl (shows pre-run results)
    -> optionally submits new hardware job (bonus, not critical path)
```

## Patterns to Follow

### Pattern 1: Cache-First Demo Cells

**What:** Every expensive operation has a cached fallback. The cell tries to compute, catches failure, loads cache.
**When:** Any cell that takes >5 seconds or depends on external services (IBM Quantum).
**Example:**
```python
import pickle
from pathlib import Path

CACHE_DIR = Path("cache")

def load_or_compute(cache_key, compute_fn):
    """Try cache first, compute as fallback, cache result."""
    cache_path = CACHE_DIR / f"{cache_key}.pkl"
    if cache_path.exists():
        with open(cache_path, "rb") as f:
            print(f"Loaded {cache_key} from cache")
            return pickle.load(f)
    result = compute_fn()
    cache_path.parent.mkdir(exist_ok=True)
    with open(cache_path, "wb") as f:
        pickle.dump(result, f)
    return result
```

### Pattern 2: Presentation-Quality Figure Defaults

**What:** Set matplotlib defaults once at notebook top for projector readability.
**When:** Every notebook used for live presentation.
**Example:**
```python
import matplotlib.pyplot as plt

# Projector-friendly defaults
plt.rcParams.update({
    'font.size': 16,
    'axes.titlesize': 20,
    'axes.labelsize': 18,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 14,
    'figure.figsize': (10, 6),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})
```

### Pattern 3: Figure Export Alongside Display

**What:** Every visualization cell both displays inline AND saves to figures/ directory.
**When:** Any figure that might appear in slides.
**Example:**
```python
fig, ax = plt.subplots()
ax.plot(losses)
ax.set_title("Training Loss")
ax.set_xlabel("Iteration")
ax.set_ylabel("Loss")

fig.savefig("figures/training_loss.png")
plt.show()
```

### Pattern 4: Slide Generation Script

**What:** A Python script that reads .png figures and assembles a .pptx with python-pptx.
**When:** Generating the slide deck artifact.
**Example:**
```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

def add_figure_slide(prs, title, image_path, notes=""):
    slide_layout = prs.slide_layouts[5]  # Blank layout
    slide = prs.slides.add_slide(slide_layout)

    # Title
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(32)
    p.font.bold = True

    # Figure
    slide.shapes.add_picture(image_path, Inches(1), Inches(1.5), Inches(8), Inches(5))

    # Speaker notes
    if notes:
        slide.notes_slide.notes_text_frame.text = notes

prs = Presentation()
add_figure_slide(prs, "Training Convergence", "figures/training_loss.png",
                 notes="Point out: loss converges in ~50 iterations")
prs.save("output/presentation.pptx")
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Live Training During Talk
**What:** Running the full training loop (50+ iterations of VQC optimization) during the live demo.
**Why bad:** Takes 5-15 minutes. Audience disengages. If it fails, no recovery.
**Instead:** Pre-train, cache parameters, load them live. Show the training code, explain it, but do not execute it.

### Anti-Pattern 2: Single Monolithic Notebook
**What:** Using the original QVC_QNN.ipynb directly for the demo without creating a presentation-focused subset.
**Why bad:** The original has exploratory cells, commented-out code, alternative approaches, and sections belonging to the co-presenter. Scrolling past irrelevant cells during a live demo looks unprofessional.
**Instead:** Create a QVC_QNN_demo.ipynb with only the cells needed for your 30-minute half, in presentation order.

### Anti-Pattern 3: Hardcoded IBM Credentials
**What:** Pasting API tokens directly in notebook cells.
**Why bad:** Audience sees your credentials on the projector. Security risk. Also breaks portability.
**Instead:** Use python-dotenv to load from .env file (already in the existing notebook pattern).

### Anti-Pattern 4: Default Matplotlib Styling
**What:** Using matplotlib defaults (small fonts, thin lines, light colors) for projected figures.
**Why bad:** Unreadable on projectors, especially in large or bright rooms. Conference projectors wash out colors.
**Instead:** Set rcParams for large fonts, thick lines, high-contrast colors at notebook start.

## Directory Structure

```
Quantum_Variational_Circuits/
  QVC_QNN.ipynb              # Original full notebook (reference)
  QVC_QNN_demo.ipynb         # Polished demo notebook (new)
  slides/
    generate_deck.py          # python-pptx slide generation script
    template.pptx             # Optional: branded slide template
  figures/
    training_loss.png
    accuracy_comparison.png
    confusion_matrix.png
    circuit_diagram.png
    hardware_vs_sim.png
  cache/
    trained_params.pkl
    hardware_results.pkl
    training_history.pkl
  output/
    presentation.pptx         # Generated slide deck
  demo_script.md              # Speaker notes and timing
  requirements.txt            # Updated with presentation deps
  .env                        # IBM Quantum API token (gitignored)
```

## Scalability Considerations

Not applicable -- this is a one-time conference presentation, not a production system. Optimize for reliability on demo day, not scalability.

## Sources

- PROJECT.md constraints (30 minutes, .pptx format, co-presenter split)
- QVC_QNN.ipynb analysis (existing imports, structure, hardware access pattern)
- Training data knowledge of conference demo best practices
