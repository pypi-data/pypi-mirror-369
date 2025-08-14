# esi-utils-vectors

## Introduction

Utility package for doing math with vectors, used by ShakeMap. 

## Installation

From repository base, run
```
conda create --name vectors pip
conda activate vectors
pip install git+https://code.usgs.gov/ghsc/esi/esi-extern-openquake
pip install -r requirements.txt .
```

## Tests

```
pip install pytest
pytest .
```