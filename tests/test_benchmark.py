"""Benchmarks for hot paths in constraint_theory_core.

Run with: python -m pytest tests/test_benchmark.py --benchmark-only
"""

from __future__ import annotations

import math

import pytest

from constraint_theory_core.lattice import snap, A2Point, norm_sq
from constraint_theory_core.rigidity import (
    is_laman,
    henneberg_construct,
    algebraic_connectivity,
)
from constraint_theory_core.holonomy import (
    cycle_holonomy,
    verify_consistency,
    isolate_fault,
)
from constraint_theory_core.temporal import TemporalAgent
from constraint_theory_core.metronome import Metronome


# ---------------------------------------------------------------------------
# Snap benchmarks
# ---------------------------------------------------------------------------

class TestSnapBenchmark:
    def test_snap_single(self, benchmark):
        benchmark(snap, 0.5, 0.3)

    def test_snap_many(self, benchmark):
        def snap_many():
            for x in range(-50, 50):
                for y in range(-50, 50):
                    snap(float(x) * 0.1, float(y) * 0.1)
        benchmark(snap_many)

    def test_snap_large_coordinates(self, benchmark):
        benchmark(snap, 1e6, 1e6)

    def test_snap_near_boundary(self, benchmark):
        """Points near Voronoi cell boundaries are the hardest."""
        # Approximately at the edge of a Voronoi cell
        x = 1.0 / (2.0 * math.sqrt(3))
        benchmark(snap, x, 0.001)


# ---------------------------------------------------------------------------
# Rigidity benchmarks
# ---------------------------------------------------------------------------

class TestRigidityBenchmark:
    def test_is_laman_small(self, benchmark):
        edges = henneberg_construct(10)
        benchmark(is_laman, 10, edges)

    def test_is_laman_medium(self, benchmark):
        edges = henneberg_construct(50)
        benchmark(is_laman, 50, edges)

    def test_henneberg_construct(self, benchmark):
        benchmark(henneberg_construct, 100)

    def test_algebraic_connectivity(self, benchmark):
        edges = henneberg_construct(20)
        benchmark(algebraic_connectivity, edges, 20)


# ---------------------------------------------------------------------------
# Holonomy benchmarks
# ---------------------------------------------------------------------------

class TestHolonomyBenchmark:
    def test_cycle_holonomy(self, benchmark):
        edges = [(i, i + 1) for i in range(9)] + [(9, 0)]
        dirs = list(range(10))
        benchmark(cycle_holonomy, edges, dirs)

    def test_verify_consistency_many_tiles(self, benchmark):
        tri = [(0, 1), (1, 2), (2, 0)]
        tiles = [(tri, [16, 16, 16])] * 1000
        benchmark(verify_consistency, tiles)

    def test_isolate_fault_large(self, benchmark):
        tri = [(0, 1), (1, 2), (2, 0)]
        good = (tri, [16, 16, 16])
        bad = (tri, [1, 2, 3])
        tiles = [good] * 500 + [bad] + [good] * 499
        benchmark(isolate_fault, tiles)


# ---------------------------------------------------------------------------
# Temporal / Metronome benchmarks
# ---------------------------------------------------------------------------

class TestMetronomeBenchmark:
    def test_tick(self, benchmark):
        m = Metronome(T=1.0, phi0=0.0)
        benchmark(m.tick)

    def test_observe(self, benchmark):
        m = Metronome(T=1.0, phi0=0.0, epsilon=0.5, delta=1.0)
        benchmark(m.observe, 0.5, 0.3)

    def test_consensus_round(self, benchmark):
        """Benchmark a full consensus round for 5 agents."""
        n = 5
        edges = henneberg_construct(n)
        metronomes = [
            Metronome(
                T=1.0,
                phi0=i * 0.3,
                epsilon=0.5,
                delta=1.0,
                neighbors=[j for j in range(n) if j != i],
                edges=edges,
                n_agents=n,
            )
            for i in range(n)
        ]

        def consensus_round():
            phases = [m.phase for m in metronomes]
            for i, m in enumerate(metronomes):
                neighbor_phases = [phases[j] for j in range(n) if j != i]
                m.correct(neighbor_phases)

        benchmark(consensus_round)

    def test_temporal_observe(self, benchmark):
        agent = TemporalAgent(decay_rate=0.5, epsilon_0=0.6, delta=1.0)
        t = 1.0
        agent.observe(0.0, 0.0, t=0.0)
        benchmark(lambda: agent.observe(0.1, 0.2, t=1.0))
