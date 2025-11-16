# FGLopt: Architecture & Development Plan

## 🥅 Goals

- Design a modular Python application for topology optimization and functionally graded lattice generation.
- Target mechanical parts with lightweight, stiff, printable lattice structures.
- Focus on FDM-compatible output for ABS, PLA, TPU.
- Build an interactive CLI first, with optional future GUI.


---

## Project Structure (initial)

fglopt/
├── fglopt # CLI launcher
├── config.yaml
├── requirements.txt
├── src/
│ └── fglopt/
│ ├── main.py # REPL + control logic
│ ├── optimization/ # SIMP + update rules
│ ├── fea/ # Solver stubs
│ ├── mesh/ # STL I/O, grid
│ ├── lattice/ # Density to lattice logic
│ └── utils/ # Shared helpers
└── tests/

---

## REPL Flow

load config.yaml
run topo-opt
export part stl
exit

---

## 🔄 Data Flow

```text
config.yaml
   ↓
parse config
   ↓
initialize domain grid
   ↓
topology optimization (density field)
   ↓
density → lattice mapping
   ↓
STL export (FDM-friendly)
