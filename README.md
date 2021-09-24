# Load GitHub repository dependents (users)

A tool for finding the most starred repositories that depend on a given repository. Results are ordered by star count.

By default, only repositories with 5 or more stars are included. 

Requires Python 3.7 or later to guarantee that the results are sorted.

## Sample output

Output for 10 pages of [https://github.com/numba/numba/network/dependents](https://github.com/numba/numba/network/dependents), abbreviated:

```
   5280 | https://github.com/tensorflow/examples
   3914 | https://github.com/pycaret/pycaret
    365 | https://github.com/alteryx/evalml
    361 | https://github.com/ncoudray/DeepPATH
    286 | https://github.com/interpretml/interpret-community
    230 | https://github.com/PennyLaneAI/qml
     92 | https://github.com/AstroMatt/book-python
     17 | https://github.com/chanzuckerberg/single-cell-data-portal
     12 | https://github.com/biasvariancelabs/aitlas
     10 | https://github.com/hezhiqian01/image_retrieval
...
```

## Usage

1. Clone the repository

```cmd
git clone git@github.com:tpitkanen/github_dependents.git
cd github_dependents
```

2. Create a virtual environment

```cmd
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
```

3. Set the target URL:

```cmd
python load_dependents.py https://github.com/<owner>/<repository>
```

## Help

For argument help, run:

```cmd
python load_dependents.py -h
```
