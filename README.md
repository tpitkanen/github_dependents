# Load GitHub repository dependents (users)

A tool for finding the most starred repositories that depend on a given repository. Results are ordered by star count.

By default, only repositories with 5 or more stars are included. 

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

3. Set the target URL in load_dependents.py

```python
def main():
    # Add target URL here:
    dependents_url = "https://github.com/<owner>/<repository>/network/dependents"
    # ...
```

4. Run the program

```
python load_dependents.py
```
