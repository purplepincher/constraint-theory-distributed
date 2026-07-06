# Contributing

## Development Setup

Create a virtual environment and install the package in editable mode with the development dependencies:

```bash
python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Running Tests

Run the full test suite with pytest:

```bash
pytest tests/
```

## Linting

Use Ruff to lint the Python code:

```bash
ruff check .
```

## Rust Crate

The `rust/` directory is a separate Cargo crate (`constraint-theory-world-music`) that implements world‑music scales and tunings in Rust. To build and test it:

```bash
cd rust
cargo test
```

(Optional: Build a release binary with `cargo build --release`.)
