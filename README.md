# Bloom Filter

[![Tests](https://github.com/codefromlani/bloom-filter/actions/workflows/tests.yml/badge.svg)](https://github.com/codefromlani/bloom-filter/actions/workflows/tests.yml)

A small Bloom filter implementation in Python, built to understand
the data structure and the mathematics behind its false-positive rate.

## Features

- Configurable capacity and target false-positive rate
- Integer-backed bit array
- Double hashing
- No false negatives for inserted items
- Configurable false-positive probability

## Installation

Clone the repository and install it in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

## Usage
```python
from bloomfilter.bloom import BloomFilter

bf = BloomFilter(capacity=10_000, error_rate=0.01)

bf.add("alice")

print(bf.contains("alice"))
# True 

print(bf.contains("bob"))
# Usually False
```

- If `contains()` returns False, the item is definitely not in the filter. If it returns True, the item may be present because Bloom filters can produce false positives.


## Running tests
```bash
python3 -m pytest
```

## Experiments
The `experiments/` directory contains experiments measuring the
observed false-positive rate against the theoretical rate.

The experiments investigate:

- what happens when more items are inserted than the configured capacity
- how the target error rate affects the false-positive rate
- how the number of queries affects the stability of the observed estimate

Run the experiment with:

```bash
python3 experiments/false_positive_rate.py
```


## Design notes

See [docs/notes.md](docs/notes.md) for the reasoning behind the
implementation mathematical assumptions, and design decisions.



## Reference
Research paper: ["Space/Time Trade-offs in Hash Coding with Allowable Errors"](https://pages.cs.wisc.edu/~markhill/restricted/cacm70_bloom.pdf)

