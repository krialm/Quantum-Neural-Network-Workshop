# Feature Landscape

**Domain:** Technical conference presentation with live quantum ML demo
**Researched:** 2026-03-24

## Table Stakes

Features the audience expects. Missing = presentation feels unprofessional or incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| .pptx slide deck with clear structure | Conference standard; organizers may require slides in advance | Medium | python-pptx scripted generation |
| Loss curve visualization | Proves the model actually trains; audience expects convergence plot | Low | matplotlib, already partially in notebook |
| Accuracy metrics (train + test) | Quantifies classifier performance; standard ML result reporting | Low | scikit-learn accuracy_score already in notebook |
| Circuit diagram visualization | Audience needs to see what the VQC looks like; visual anchor for the talk | Low | qiskit.visualization circuit.draw('mpl') |
| Live notebook execution | "Live demo" means actually running code; pre-recorded video feels dishonest | Medium | JupyterLab with pre-cached expensive operations |
| Speaker notes / demo script | 30-minute timing requires preparation; co-presenter needs to know handoff points | Low | Markdown or .pptx notes field |
| Hardware vs simulator comparison | Core value prop of the talk; shows quantum computing is real, not just simulation | Medium | Pre-cached hardware results + live simulator comparison |

## Differentiators

Features that elevate from "adequate talk" to "memorable presentation."

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Confusion matrix heatmap | Visual, intuitive way to show classifier performance beyond a single accuracy number | Low | seaborn heatmap |
| Side-by-side sim vs hardware bar chart | Directly shows noise impact on real quantum hardware; compelling visual | Low | matplotlib grouped bar chart |
| Progressive training loss display | Show loss decreasing over iterations as a progression, not just final plot | Medium | Pre-render per-epoch snapshots or use IPython.display.clear_output loop |
| Pre-cached fallback for every live cell | If any cell fails live, seamlessly show pre-computed output | Medium | pickle/joblib cached outputs loaded on failure |
| Clean notebook with hidden setup cells | Audience sees only relevant code and outputs, not boilerplate imports | Low | Cell tags + JupyterLab cell visibility |
| Slide deck auto-generated from latest figures | Run script, get updated slides -- no manual copy-paste of figures | Medium | python-pptx script reads from figures/ directory |

## Anti-Features

Features to explicitly NOT build.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Interactive Plotly/Bokeh visualizations | Projectors show static frames; interactivity adds load time and failure modes; audience cannot interact | Use matplotlib static figures with large fonts and high contrast |
| Full reveal.js/RISE slide conversion | Fragile rendering, fights with cell output sizing, requires browser full-screen | Keep slides (.pptx) and notebook as separate artifacts |
| Live IBM hardware execution in the critical path | Queue times of 5-60+ minutes will kill the talk | Pre-cache hardware results; attempt live as a bonus only |
| Audience follow-along notebook | This is a demo, not a workshop; managing audience environments wastes time | Share notebook link after the talk for self-study |
| Video recording integration | Out of scope per PROJECT.md; adds complexity | Focus on the live experience |
| Custom Jupyter themes/CSS | Time sink with little audience impact; risks breaking rendering | Use JupyterLab defaults with font size increase |

## Feature Dependencies

```
Cell organization -> Visualization styling -> Slide generation (slides embed styled figures)
Cell organization -> Pre-cached results -> Fallback strategy (fallbacks load cached results)
Hardware execution (pre-conference) -> Hardware results cache -> Sim vs hardware comparison
Speaker notes -> Demo script with timing (notes inform script structure)
```

## MVP Recommendation

Prioritize:
1. **Pre-cached training results** -- Without this, nothing else works reliably live
2. **Loss curve + accuracy visualizations** -- Table stakes; core evidence of the talk
3. **Circuit diagram** -- Visual anchor that makes the VQC concrete
4. **Slide deck with embedded figures** -- The deliverable the conference expects
5. **Sim vs hardware comparison** -- The "wow" moment of the talk

Defer:
- **Progressive training visualization**: Nice-to-have; static loss curve is sufficient
- **Auto-regeneration pipeline**: Manual figure embedding is fine for a one-time talk
- **Hidden setup cells**: Cosmetic; audience tolerates seeing imports

## Sources

- PROJECT.md requirements and constraints
- Notebook analysis (QVC_QNN.ipynb imports and structure)
- Training data knowledge of conference presentation best practices
