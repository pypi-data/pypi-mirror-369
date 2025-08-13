# Contributing guidelines

## Creating a development environment

```bash
git clone ssh://git@gitlab.cern.ch:7999/lhcb-core/LbProdRun.git
cd LbProdRun
mamba create --name lbprodrun-dev typer lbenv ipython black pre-commit pytest singularity
conda activate lbprodrun-dev
pip install -e .[testing]
pre-commit install
```

## Running the tests

```bash
pre-commit run --all-files
pytest
```
