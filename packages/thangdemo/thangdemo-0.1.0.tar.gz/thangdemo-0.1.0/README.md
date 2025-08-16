# thangdemo

A tiny example Python library for demonstration. Provides a couple of utility functions and a CLI.

## Installation

```bash
pip install thangdemo
```

## Usage

```python
from thangdemo import add, mean

print(add(2, 3))    # 5
print(mean([1, 2])) # 1.5
```

### CLI

```bash
thangdemo-cli 7
# prints: 49
```

## Development

- Run tests: `pytest -q`
- Build: `python -m build`
