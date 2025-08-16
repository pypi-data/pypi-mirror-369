# Systems and Controls Visualization

Library that is intended to create different forms of visualizations for dynamic systems but also for other purposes.

It will be more a wrapper of existing tools and maybe created such to compare them. (matplotlib, plotly, ...)

## Usage

```python
# integration with python
from syscovis import plotter
# create the plots
plotter.plot() # so far it creates the directory for the plots
```

```bash
# test from shell
uv run python -c "import syscovis; print(syscovis.hello())"
```

## Visualizations (in planning)

### Trajectories

Every possible combination of plots in 2d, with the idea to _just_ plot them, not spend hours with configuration.

Maybe there will be some experiments in 3d.

### Video rendering

### Classic control stuff

#### Bode

#### Nyquist
