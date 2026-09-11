# Installation

## Requirements

* **Python ≥ 3.9** (tested through 3.14)
* **PyYAML ≥ 6**, (runtime dependency)

### Dev Dependencies

* **mkdocs >=1.6, <2**

## Installing

```bash
pip install .
```

Development:

```bash
pip install -e ".[docs]" pytest
pytest                           # test suite
mkdocs serve                     # docs site at http://127.0.0.1:8000
mkdocs build --strict            # validate and build docs
```

## File formats

YAML is the default and recommended format for configuration and
character files.  JSON is accepted as well, `.json` files and JSON 
strings load with the very same structure. There is no XML. The paper's 
AffectML documents are represented in YAML. 
See [Configuration](configuration.md) for the mapping.
