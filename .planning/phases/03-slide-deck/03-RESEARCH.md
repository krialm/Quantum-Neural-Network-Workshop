# Phase 3: Slide Deck - Research

**Researched:** 2026-03-24
**Domain:** Programmatic PowerPoint generation with python-pptx
**Confidence:** HIGH

## Summary

Phase 3 generates a complete PowerPoint deck using python-pptx to accompany the user's 30-minute conference presentation half (training, evaluation, hardware execution). The deck embeds pre-rendered matplotlib figures from Phase 2 and includes transition slides between live demo segments with speaker notes on every slide.

python-pptx 1.0.2 is the current stable release (major version bump from the 0.6.x line referenced in STACK.md). The API is backward-compatible for all patterns this phase uses: `Presentation()`, `add_slide()`, `add_picture()`, `add_textbox()`, speaker notes via `notes_slide.notes_text_frame`, and slide layouts. One breaking change in 1.0 (placeholder `shape_type` reporting) does NOT affect this phase since we use `add_picture()` shapes (non-placeholders), which still correctly report `MSO_SHAPE_TYPE.PICTURE (13)`.

The figures directory from Phase 2 contains generated PNGs at runtime but may be empty if the notebook hasn't been executed. The generation script must handle missing figures gracefully with placeholder text.

**Primary recommendation:** Use python-pptx 1.0.2 with the default template's built-in layouts. Keep the generation script simple -- one flat Python file, no custom template .pptx needed.

## Project Constraints (from CLAUDE.md)

- **Format**: .pptx format required (not HTML/reveal.js/Marp)
- **Time**: ~30 minutes for user's half of 60-minute session
- **Co-presenter split**: User handles training/eval/hardware; co-presenter handles intro/theory/circuit design
- **GSD Workflow**: All file changes through GSD commands
- **No linting/formatting config detected**: Follow PEP 8-like conventions by default
- **Naming**: Snake_case for functions and variables

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SLID-01 | PowerPoint deck covering training, evaluation, hardware execution | python-pptx slide generation with section slides for each topic; layouts 0, 1, 5, 6 verified working |
| SLID-02 | Transition slides between demo segments | Blank layout (6) + centered text box with 36pt bold font; 3 transitions (training, evaluation, hardware) |
| SLID-03 | Pre-rendered notebook figures embedded in slides | `slide.shapes.add_picture()` with Inches positioning; figures from Phase 2: input_data_grid.png, loss_curve.png, hardware_comparison.png |
| SLID-04 | Summary/takeaway slide | Content layout (1) with bullet points via `text_frame.add_paragraph()` |
</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| python-pptx | 1.0.2 | Programmatic .pptx creation | Only mature Python library for PowerPoint; verified on PyPI 2026-03-24 |
| Pillow | 11.3.0 | Image handling for embedded figures | Required by python-pptx for image operations; already installed |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | 8.3.5 | Test validation of generated deck | Already installed; validates SLID requirements |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| python-pptx | Manual PowerPoint editing | Not scriptable, not version-controllable |
| python-pptx | reveal.js / Marp | Project constraint: must be .pptx format |
| Default template | Custom .pptx template | Adds complexity; default layouts sufficient for this deck |

**Installation:**
```bash
pip install python-pptx
```

**Version verification:** python-pptx 1.0.2 confirmed current on PyPI (2026-03-24). Pillow 11.3.0 already installed.

## Architecture Patterns

### Recommended Project Structure
```
slides/
  generate_deck.py     # Standalone script: python slides/generate_deck.py
output/
  presentation.pptx    # Generated artifact (gitignored or regenerated)
figures/
  input_data_grid.png  # From Phase 2 notebook execution
  loss_curve.png       # From Phase 2 notebook execution
  hardware_comparison.png  # From Phase 2 notebook execution
tests/
  test_slide_deck.py   # pytest validation of generated deck
```

### Pattern 1: Slide Generation Script

**What:** A single Python script that creates the entire deck when run.
**When to use:** Always -- the deck is generated, not hand-edited.

```python
# Verified working with python-pptx 1.0.2
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

prs = Presentation()
# Default slide size: 10.0 x 7.5 inches (standard widescreen)

# Title slide (layout 0)
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "Slide Title"
slide.placeholders[1].text = "Subtitle"

# Speaker notes
notes = slide.notes_slide.notes_text_frame
notes.text = "Speaker note text"

# Content slide with bullets (layout 1)
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = "Content Title"
body = slide.placeholders[1]
tf = body.text_frame
tf.text = "First bullet"
p = tf.add_paragraph()
p.text = "Second bullet"

# Blank slide for transitions/figures (layout 6)
slide = prs.slides.add_slide(prs.slide_layouts[6])
txBox = slide.shapes.add_textbox(Inches(1), Inches(3), Inches(8), Inches(2))
p = txBox.text_frame.paragraphs[0]
p.text = "Transition Text"
p.font.size = Pt(36)
p.font.bold = True
p.alignment = PP_ALIGN.CENTER

# Figure embedding
import os
if os.path.exists("figures/loss_curve.png"):
    slide.shapes.add_picture("figures/loss_curve.png", Inches(1), Inches(1.5), Inches(8), Inches(5.5))
else:
    # Placeholder text if figure missing
    txBox = slide.shapes.add_textbox(Inches(2), Inches(3), Inches(6), Inches(1))
    txBox.text_frame.text = "[Figure: loss_curve.png -- run notebook first]"

prs.save("output/presentation.pptx")
```

### Pattern 2: Graceful Figure Handling

**What:** Check for figure existence before embedding; show placeholder if missing.
**When to use:** Always -- figures/ may be empty if notebook hasn't been run.

```python
import os

def add_figure_or_placeholder(slide, figure_path, left, top, width, height):
    """Embed figure if it exists, otherwise add placeholder text."""
    if os.path.exists(figure_path):
        slide.shapes.add_picture(figure_path, left, top, width, height)
    else:
        filename = os.path.basename(figure_path)
        txBox = slide.shapes.add_textbox(left, top, width, Inches(1))
        txBox.text_frame.text = f"[Figure: {filename} -- run notebook first]"
```

### Pattern 3: Test Validation of Generated Deck

**What:** pytest tests that run the generation script, load the .pptx, and validate structure.
**When to use:** Every test run regenerates the deck to ensure script+output consistency.

```python
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

prs = Presentation("output/presentation.pptx")

# Count embedded images (NOT placeholders)
image_count = sum(
    1 for slide in prs.slides
    for shape in slide.shapes
    if shape.shape_type == MSO_SHAPE_TYPE.PICTURE  # int value 13
)

# Check speaker notes
for i, slide in enumerate(prs.slides):
    notes_text = slide.notes_slide.notes_text_frame.text.strip()
    assert len(notes_text) > 0, f"Slide {i+1} missing speaker notes"
```

### Anti-Patterns to Avoid

- **Custom .pptx template for simple decks:** The default template has 11 layouts that cover all needs. A custom template adds a binary file to the repo and maintenance burden.
- **Hardcoded EMU values:** Use `Inches()` and `Pt()` helpers, not raw EMU integers. `Inches(1)` is far more readable than `914400`.
- **Ignoring slide dimensions:** Default is 10.0 x 7.5 inches (widescreen). All positioning must fit within this. Centering an 8-inch-wide figure: `left = Inches(1)`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PowerPoint creation | XML manipulation | python-pptx | .pptx is a complex ZIP/XML format; python-pptx handles all the packaging |
| Image sizing/centering | Manual pixel math | `Inches()` / `Pt()` helpers | EMU units are error-prone; helpers are readable and correct |
| Slide layout design | Custom XML templates | Default presentation layouts | 11 built-in layouts cover title, content, blank, section header |

## Common Pitfalls

### Pitfall 1: Missing Figures at Generation Time

**What goes wrong:** Script crashes with FileNotFoundError when figures/ PNGs don't exist.
**Why it happens:** Figures are generated by running the demo notebook; they may not exist yet.
**How to avoid:** Always check `os.path.exists()` before `add_picture()`. Insert placeholder text box when figure is missing.
**Warning signs:** Script works on developer machine but fails in CI or fresh clone.

### Pitfall 2: Placeholder Index Errors

**What goes wrong:** `slide.placeholders[1]` throws KeyError on some layouts.
**Why it happens:** Not all slide layouts have a body placeholder at index 1. Layout 6 (Blank) has NO placeholders.
**How to avoid:** For Blank layouts, use `slide.shapes.add_textbox()` instead of placeholders. Only use `placeholders[1]` with layouts 0 (Title Slide) and 1 (Title and Content).
**Warning signs:** KeyError on `placeholders` access.

### Pitfall 3: python-pptx 1.0 shape_type Change

**What goes wrong:** Tests checking `shape.shape_type == 13` for placeholder-based pictures fail.
**Why it happens:** python-pptx 1.0 changed placeholder shapes to always report `MSO_SHAPE_TYPE.PLACEHOLDER`. However, this only affects placeholder shapes -- `add_picture()` shapes still report `MSO_SHAPE_TYPE.PICTURE (13)`.
**How to avoid:** Use `add_picture()` (not placeholder insertion) for figure embedding, and the shape_type == 13 check remains valid.
**Warning signs:** Tests passing on 0.6.x but failing on 1.0.x when using picture placeholders.

### Pitfall 4: Figure Aspect Ratio Distortion

**What goes wrong:** Embedded figures look stretched or squashed.
**Why it happens:** `add_picture()` with both width and height forces the image into that exact box, ignoring aspect ratio.
**How to avoid:** Specify only width OR only height (not both) to preserve aspect ratio. Or calculate the correct dimensions from the image's actual size. For consistent slide layout, specifying both is acceptable if the source figures are already the right proportions.
**Warning signs:** Figures look different in slides vs. in the notebook.

### Pitfall 5: Speaker Notes Text Encoding

**What goes wrong:** Special characters (em dashes, curly quotes) cause issues.
**Why it happens:** python-pptx handles Unicode fine, but copy-pasted text may have invisible characters.
**How to avoid:** Use plain ASCII for speaker notes. Avoid copy-paste from rich text sources.
**Warning signs:** Mojibake or missing text in PowerPoint notes view.

## Code Examples

### Complete Slide with Title, Figure, and Notes

```python
# Verified: python-pptx 1.0.2, 2026-03-24
from pptx import Presentation
from pptx.util import Inches, Pt
import os

prs = Presentation()

# Title Only layout (5) -- has title placeholder but blank body area for figures
slide = prs.slides.add_slide(prs.slide_layouts[5])
slide.shapes.title.text = "Training Convergence"

# Embed figure below title
fig_path = "figures/loss_curve.png"
if os.path.exists(fig_path):
    # Position: 1 inch from left, 1.5 inches from top, 8 inches wide, 5.5 inches tall
    slide.shapes.add_picture(fig_path, Inches(1), Inches(1.5), Inches(8), Inches(5.5))

# Speaker notes
slide.notes_slide.notes_text_frame.text = (
    "The loss curve shows convergence over the full training run. "
    "The MSE loss drops steadily, confirming the variational circuit "
    "is learning the classification boundary."
)
```

### Available Slide Layouts (Default Template)

```
Layout 0: Title Slide          -- title + subtitle placeholders
Layout 1: Title and Content    -- title + body with bullet support
Layout 2: Section Header       -- large text, good for transitions
Layout 3: Two Content          -- title + two side-by-side bodies
Layout 4: Comparison           -- title + two labeled comparison areas
Layout 5: Title Only           -- title placeholder, blank body area
Layout 6: Blank                -- completely empty, full control
Layout 7: Content with Caption
Layout 8: Picture with Caption
Layout 9: Title and Vertical Text
Layout 10: Vertical Title and Text
```

**Recommended usage for this deck:**
- Layout 0: Title slide (slide 1)
- Layout 1: Content slides with bullets (overview, evaluation results, summary)
- Layout 5: Figure slides (title + embedded image below)
- Layout 6: Blank for transition slides (fully custom text positioning)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| python-pptx 0.6.x | python-pptx 1.0.2 | 2024 | Placeholder shape_type reporting changed; otherwise backward-compatible for our use cases |

**Deprecated/outdated:**
- STACK.md recommends `>=0.6.23` -- should target `>=1.0.0` since 1.0.2 is current and stable

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.3.5 |
| Config file | none -- pytest runs from project root |
| Quick run command | `python -m pytest tests/test_slide_deck.py -v` |
| Full suite command | `python -m pytest tests/ -v` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SLID-01 | Deck covers training, evaluation, hardware | unit | `pytest tests/test_slide_deck.py::test_training_section_exists tests/test_slide_deck.py::test_evaluation_section_exists tests/test_slide_deck.py::test_hardware_section_exists -x` | Wave 0 |
| SLID-02 | Transition slides between demo segments | unit | `pytest tests/test_slide_deck.py::test_transition_slides_exist -x` | Wave 0 |
| SLID-03 | Figures embedded in slides | unit | `pytest tests/test_slide_deck.py::test_figure_references -x` | Wave 0 |
| SLID-04 | Summary/takeaway slide | unit | `pytest tests/test_slide_deck.py::test_summary_slide_exists -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_slide_deck.py -v`
- **Per wave merge:** `python -m pytest tests/ -v`
- **Phase gate:** Full suite green before verify

### Wave 0 Gaps
- [ ] `tests/test_slide_deck.py` -- covers SLID-01 through SLID-04
- Framework (pytest) already installed

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| python-pptx | Slide generation | Installed | 1.0.2 | -- |
| Pillow | Image embedding | Installed | 11.3.0 | -- |
| pytest | Test validation | Installed | 8.3.5 | -- |
| figures/*.png | SLID-03 figure embedding | Not yet (notebook not run) | -- | Placeholder text boxes |

**Missing dependencies with no fallback:** None

**Missing dependencies with fallback:**
- figures/ PNGs: Not present until demo notebook is executed. Script handles gracefully with placeholder text.

## Open Questions

1. **Figure aspect ratios**
   - What we know: matplotlib default figure sizes vary; notebook saves with `fig.savefig()` defaults
   - What's unclear: Exact pixel dimensions of the Phase 2 figures
   - Recommendation: Use `Inches(8)` width only (let python-pptx preserve aspect ratio) OR specify both dimensions and accept minor stretch since figures are generated at consistent sizes

2. **Slide visual polish**
   - What we know: Default python-pptx template uses a plain white theme
   - What's unclear: Whether the presenter wants a specific color scheme or branding
   - Recommendation: Ship with defaults; presenter can apply a PowerPoint theme afterward. The generation script focuses on content and structure, not visual design.

## Sources

### Primary (HIGH confidence)
- python-pptx 1.0.2 PyPI page and changelog -- verified version, breaking changes
- Local environment testing -- all API patterns verified working on installed python-pptx 1.0.2
- Default template layout enumeration -- verified 11 layouts with names

### Secondary (MEDIUM confidence)
- [python-pptx documentation](https://python-pptx.readthedocs.io/en/latest/) -- official docs
- [python-pptx releases](https://github.com/scanny/python-pptx/releases) -- version history

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- python-pptx 1.0.2 verified installed and working
- Architecture: HIGH -- all patterns tested locally with actual API calls
- Pitfalls: HIGH -- shape_type change verified empirically; placeholder behavior confirmed

**Research date:** 2026-03-24
**Valid until:** 2026-04-24 (stable library, slow release cadence)
