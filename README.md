# fglopt

A Python-based console application for topology optimization and functionally graded lattice (FGL) generation, targeting FDM 3D printing.

## Features

- Console-driven REPL interface
- Topology optimization via SIMP method (compliance + weight reduction)
- Export of printable graded lattice structures
- STL input and export support
- Modular design for future GUI integration

## Project Layout

src/
fglopt/
main.py # CLI entrypoint logic
fea/ # Finite element solver
mesh/ # STL loader + mesher
optimization/ # TO engine
lattice/ # Lattice generator + export

## Getting Started

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set PYTHONPATH so modules are discoverable
export PYTHONPATH=src

# Launch the interactive console
./fglopt

# Roadmap
- [ ] Hook up STL loading
- [ ] Add basic FEA solver
- [ ]  Enable lattice generation

