# simesens
Repository mainly intended as the main repository for Richard Johanssons Ph.D. project, where
measurement and simulation data is being worked with. There will be modules for pure simulations in
the microwave regime using the PyARTS library, as well as numerical inversions of forward models to
retrieve various units, mainly volume mixing ratios for ozone and carbon monoxide from two different
instruments located at the Swedish Institute of Space Physics in Kiruna, Sweden.

## Installation
To install dependencies required there exist a environment file `env.yaml` that is installed using
mamba/conda:

```bash
mamba install --file env.yaml
```

To install the local package this is done through pip:

```bash
pip install -e .
```

## Goal and todo´s
The main goal of this repository is to have a centralized codebase that can handle all processes
that is needed to perform volume mixing ratio retrievals from measurements. The goal is also that
all these processes should be easy to use and that it should scale with new concepts.

The project have pivoted since the start, since temperature retrievals from stratospheric oxygen
from our measurements seem not feasible due to to low sensitivity to temperature. Thus will AI
methods be investigated to create models or "emulators" for the computational heavy inversions.
