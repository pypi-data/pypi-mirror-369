# mdsa-tools: A set of tools for performing systems analyses of Molecular Dynamics (MD) simulations.

![CI](https://img.shields.io/badge/CI-passing-brightgreen)
![Last commit](https://img.shields.io/github/last-commit/zeper-eng/workspace)
[![PyPI version](https://img.shields.io/pypi/v/mdsa-tools.svg)](https://pypi.org/project/mdsa-tools/)
[![Python versions](https://img.shields.io/pypi/pyversions/mdsa-tools.svg)](https://pypi.org/project/mdsa-tools/)
[![License](https://img.shields.io/pypi/l/mdsa-tools.svg)](https://github.com/<user>/<repo>/blob/main/LICENSE)
[![DOI](https://img.shields.io/badge/DOI--blue)]()

## A pipeline for performing systems analyses:
![Pipeline](https://raw.githubusercontent.com/zeper-eng/workspace/main/resources/Pipelineflic.png)

 Pictured is a directed graph describing the pipeline for our MD trajectory analysis. From left to right, we begin with a trajectory file, and convert it into a set of networks (one for each trajectory frame), which that can be represented as either graphs or adjacency matrices. Each frame adjacency is flattened into a vector by concatenating the matrix’s rows (vector reduction). The frame vectors are vertically concatenated to create a feature matrix that can be used as input to either K-means clustering or PCA, whose results can then be visualized using graphs, scatter plots, MDCcircos plots, (of residue H-bonding), or MD replicate maps of frame measurements of interest.


 We also provide an additional module for taking theese various results and using clustering results as input substates for markov state model analyses.

## Use pip install to get started:

```bash

pip install mdsa-tools

```

## Systems Problem Area:

![System panel](https://raw.githubusercontent.com/zeper-eng/workspace/main/resources/PanelA_summerposter.png)
At the Weir Lab at Wesleyan University, we perform molecular dynamics (MD) simulations of a ribosomal subsystem to study tuning of protein translation by the CAR interaction surface- a ribosomal interface identified by the lab that interacts with the +1 codon (poised to enter the ribosome A site). Our "computational genetics" research focuses on modifying adjacent codon identities at the A-site and the +1 positions to model how changes at these sites influence the behavior of the CAR surface and corellate with translation rate variations.






