# constraint-theory-distributed

> Extracted from a stray `master` branch on
> [`purplepincher/constraint-theory-core`](https://github.com/purplepincher/constraint-theory-core)
> (a different, unrelated Rust crate) during an org-wide branch cleanup —
> this is real, separately-authored work that doesn't belong mixed into
> that repo's history. Full commit history preserved on extraction.

A pure-Python library of geometric and algebraic primitives for constraint-theoretic problems: Eisenstein A₂ lattice quantization, narrowing deadband funnels, Laman (minimally rigid) graph topology, oscillator-based distributed consensus, and cycle-consistency (holonomy) verification. No runtime dependencies; the only third-party packages are test/dev tooling (pytest, hypothesis, ruff, pytest-benchmark).

## What It Is

The library addresses a set of recurring constraint problems: quantizing continuous values to a discrete lattice with a bounded error guarantee, narrowing an acceptance band over time so drift either vanishes or trips an anomaly, choosing a communication graph that is minimally rigid (every edge load-bearing), driving coupled agents toward consensus, and verifying that cycles of directed quantities close exactly. It provides the mathematical primitives that make those constraints precise and checkable.

Five mathematical modules form the core, plus two application-level modules:

- **Lattice** quantizes a point in the plane onto the Eisenstein A₂ lattice. Every point is within ρ = 1/√3 ≈ 0.577 of a lattice point, guaranteed by geometry.
- **Temporal** wraps that quantization in a narrowing deadband funnel — ε(t) = ε₀ · e^(−λt) — so error either converges below the band or trips an anomaly that resets it.
- **Rigidity** builds and checks Laman graphs — exactly 2n−3 edges, with every edge load-bearing and no redundancy.
- **Metronome** runs distributed consensus across agents connected by a Laman graph, correcting phase with coupling α* = 2/(λ₂ + λₙ).
- **Holonomy** verifies that cycles of 48-direction quantities close exactly (sum ≡ 0 mod 48), and locates a fault via binary bisection.

The two application modules sit on top of the core:

- **Genre Brain** maps a named style (serialism, jazz, ambient, …) to a per-constraint "softness" profile — five ε values that parameterize how strictly each core module enforces its constraint. This is the bridge from a named intent to the library's parameters.
- **Exercises** generates constrained-composition exercises (species counterpoint, voice leading, harmonic and rhythmic constraints) with starting notes, constraints, solutions, and scoring rubrics, for classroom use.

## How the modules relate

The package is not a single integrated pipeline; modules are imported where one genuinely needs another. The actual dependencies:

- **Temporal depends on Lattice** — `TemporalAgent.observe()` snaps each observation to the A₂ lattice, then applies the deadband.
- **Metronome depends on Lattice, Rigidity, and Temporal** — it computes α* via Rigidity's Laplacian, drives a phase via a TemporalAgent, and maps snapped lattice points to phase angles.
- **Holonomy depends on Lattice** only for the direction count (48); it is otherwise a standalone verifier.
- **Rigidity, Exercises, and Genre Brain are standalone** — they import no other module. Genre Brain's outputs are not wired in automatically; they parameterize the softness/ε of the core modules when you pass them in.

So a working composition that exists in code is: snap with Lattice, narrow the band with Temporal, and couple agents with Metronome over a Laman graph. Holonomy is a separate verification layer applied to cycles; it is not part of the consensus loop.

## Installation

Not published to PyPI. Install from source:

```bash
git clone https://github.com/purplepincher/constraint-theory-distributed.git
cd constraint-theory-distributed
pip install -e .
```

Requires Python ≥ 3.10. No runtime dependencies (all imports are standard library). Test/dev extras: `pytest`, `hypothesis`, `ruff`, `pytest-benchmark`.

## Quick Start

### Lattice — Snap to Eisenstein Lattice

```python
from constraint_theory_core import snap, covering_radius, is_safe

# Any point in the plane snaps to the nearest A₂ lattice point
pt, error = snap(0.5, 0.3)
print(f"Snapped to ({pt.a}, {pt.b}), error = {error:.4f}")

# Error is always ≤ 1/√3 ≈ 0.577 (covering radius guarantee)
assert error <= covering_radius()

# If error < 1/2√3 ≈ 0.289, the snap is unambiguous
print(f"Safe: {is_safe(error)}")
```

### Temporal — Deadband Funnel

```python
from constraint_theory_core.temporal import TemporalAgent, FunnelPhase

agent = TemporalAgent(decay_rate=0.1)

for t in range(1, 50):
    result = agent.observe(0.01, 0.01, t=float(t))
    print(f"t={t:2d}  phase={result.phase.value:10s}  ε={result.deadband:.4f}  err={result.error:.4f}")
    if result.phase == FunnelPhase.ANOMALY:
        print("  ⚠ Anomaly detected!")
```

### Rigidity — Laman Graphs

```python
from constraint_theory_core import henneberg_construct, is_laman, algebraic_connectivity, optimal_coupling

# Build a minimally rigid graph for 9 agents
edges = henneberg_construct(9)
print(f"Edges: {len(edges)} (expected {2*9-3})")
assert is_laman(9, edges)

# Compute convergence properties
lam2 = algebraic_connectivity(edges, 9)
alpha = optimal_coupling(edges, 9)
print(f"λ₂ = {lam2:.4f}, α* = {alpha:.4f}")
```

### Metronome — Distributed Consensus

```python
from constraint_theory_core import Metronome, henneberg_construct
import math

def neighbors_of(edges, i):
    """Neighbor indices for vertex i in an undirected edge list."""
    return [v if u == i else u for u, v in edges if u == i or v == i]

# 9 agents on a Laman graph
edges = henneberg_construct(9)
agents = [
    Metronome(T=1.0, phi0=math.pi * i / 9, epsilon=0.5, delta=0.6,
              neighbors=neighbors_of(edges, i),
              edges=edges, n_agents=9)
    for i in range(9)
]

# Run consensus
for tick in range(100):
    for agent in agents:
        agent.tick()
    phases = [a.phase for a in agents]
    for agent in agents:
        neighbor_phases = [phases[j] for j in agent.neighbors]
        agent.correct(neighbor_phases)

# Check convergence
print(f"All converged: {all(a.converged for a in agents)}")
```

### Holonomy — Cycle Verification

```python
from constraint_theory_core import verify_consistency, isolate_fault, fault_boundaries

# Each tile = (edges, direction_indices)
tiles = [
    ([(0,1), (1,2), (2,0)], [16, 16, 16]),  # consistent: 48 ≡ 0 mod 48
    ([(0,1), (1,3), (3,0)], [16, 16, 16]),  # consistent
    ([(2,3), (3,4), (4,2)], [1, 2, 3]),      # INCONSISTENT: 6 ≠ 0
]

print(f"All consistent: {verify_consistency(tiles)}")   # False
print(f"First fault at index: {isolate_fault(tiles)}")   # 2
print(f"All faults: {fault_boundaries(tiles)}")          # [2]
```

## Modules

| Module | What | Key Functions |
|--------|------|---------------|
| `lattice` | Eisenstein A₂ lattice | `snap`, `soft_snap`, `covering_radius`, `is_safe`, `norm_sq`, `A2Point`, `encode_dodecet`, `decode_dodecet`, `vector48_encode`, `vector48_decode`, `holonomy_product` |
| `temporal` | Deadband funnel | `TemporalAgent`, `FunnelPhase`, `FunnelResult` |
| `rigidity` | Laman graph topology | `is_laman`, `henneberg_construct`, `algebraic_connectivity`, `optimal_coupling`, `soft_rigidity` |
| `metronome` | Distributed consensus | `Metronome`, `MetronomeState` |
| `holonomy` | Cycle verification | `cycle_holonomy`, `verify_consistency`, `soft_verify_consistency`, `isolate_fault`, `fault_boundaries` |
| `genre_brain` | Named-style → softness profiles | `GenreEpsilons`, `get_genre`, `list_genres`, `custom_genre`, `sweep_genre` |
| `exercises` | Constrained-composition exercise generator | `generate_exercise` |

## Equations

| Concept | Equation | Meaning |
|---------|----------|---------|
| A₂ covering radius | ρ = 1/√3 ≈ 0.577 | Max distance from any point to nearest lattice point |
| Safe threshold | ρ/2 ≈ 0.289 | Below this, snap is unambiguous |
| Eisenstein norm | ‖(a,b)‖² = a² − ab + b² | Squared norm on the lattice |
| Deadband decay | ε(t) = ε₀ · e^(−λt) | Funnel narrows exponentially |
| Laman condition | \|E\| = 2n − 3 | Exactly the right number of edges |
| Algebraic connectivity | λ₂ (2nd Laplacian eigenvalue) | Convergence rate of consensus |
| Optimal coupling | α* = 2/(λ₂ + λₙ) | Fastest convergence without oscillation |
| Holonomy | Σ directions mod 48 | 0 means cycle closes exactly |

## Limitations & scope

- **α\* is an estimate, not exact.** `optimal_coupling` computes λ₂ by power iteration, but λₙ (the largest Laplacian eigenvalue) is approximated as `max_degree + 1` rather than computed exactly. The formula α\* = 2/(λ₂ + λₙ) is correct; the λₙ used in it is an approximation. For exact small-graph eigenvalues, use a dedicated linear-algebra backend.
- **`isolate_fault` finds one fault, not all.** It locates *an* inconsistent tile via binary bisection in O(log N) checks. To enumerate every inconsistent tile, use `fault_boundaries`, which is an O(N) scan.
- **Laman checking for large graphs is approximate.** `is_laman` brute-forces the subset condition for n ≤ 15 and falls back to a connectivity-based pebble-game approximation for larger graphs, rather than the full pebble game.
- **Genre/exercise modules are application-level.** Their parameters are not wired into the core modules automatically; you pass the softness/ε values through. They reflect the library's origin in musical constraint theory.
- **`soft_*` variants.** Several modules expose `soft_snap`, `soft_rigidity`, `soft_verify_consistency` — continuous ε-interpolations between a hard decision (ε=0) and a fully relaxed one (ε=1). These are the knobs Genre Brain's profiles are meant to drive.

## Testing

```bash
pip install -e ".[dev]"
pytest                          # 308 tests (83 core + property/edge-case/benchmark suites)
pytest -v --tb=short            # verbose
```

The 308 figure is the collected item count: 264 test functions, of which 4 are parametrized over the 4 topics × 3 difficulties in `exercises` (expanding to 48 items). "83 core" is the sum of the five per-module test files (`test_lattice` + `test_temporal` + `test_rigidity` + `test_metronome` + `test_holonomy`).

## Documentation

- [User Guide](docs/USER-GUIDE.md) — Complete usage documentation
- [Developer Guide](docs/DEVELOPER-GUIDE.md) — Contributing and internals
- [Examples](examples/) — Working code examples

## Related Projects

- [flux-tensor-midi](https://github.com/SuperInstance/flux-tensor-midi) — Musical constraint theory
- [plato](https://github.com/SuperInstance/plato) — PLATO tiling architecture (referenced by the holonomy module)
- [forgemaster](https://github.com/SuperInstance/forgemaster) — Constraint-theory specialist agent

## License

MIT
