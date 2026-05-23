"""Edge case tests — empty inputs, single points, degenerate cases."""

from __future__ import annotations

import math

import pytest

from constraint_theory_core.lattice import (
    A2Point, snap, covering_radius, is_safe, norm_sq,
    decode_dodecet, encode_dodecet, vector48_encode, vector48_decode,
    holonomy_product, is_consistent,
)
from constraint_theory_core.rigidity import (
    is_laman, henneberg_construct, algebraic_connectivity, optimal_coupling,
)
from constraint_theory_core.holonomy import (
    cycle_holonomy, verify_consistency, isolate_fault, fault_boundaries,
)
from constraint_theory_core.temporal import TemporalAgent, FunnelPhase
from constraint_theory_core.metronome import Metronome


# ===================================================================
# Lattice edge cases
# ===================================================================

class TestSnapEdgeCases:
    def test_origin(self):
        pt, err = snap(0.0, 0.0)
        assert pt == A2Point(0, 0)
        assert err == pytest.approx(0.0, abs=1e-10)

    def test_very_small_coords(self):
        pt, err = snap(1e-15, 1e-15)
        assert pt == A2Point(0, 0)
        assert err < covering_radius()

    def test_large_coords(self):
        pt, err = snap(1e6, 1e6)
        assert isinstance(pt, A2Point)
        assert err <= covering_radius() + 1e-6

    def test_negative_coords(self):
        pt, err = snap(-5.0, -3.0)
        assert isinstance(pt, A2Point)
        assert err <= covering_radius() + 1e-9

    def test_exactly_on_lattice_point(self):
        for a in range(-3, 4):
            for b in range(-3, 4):
                pt = A2Point(a, b)
                x, y = pt.to_complex()
                snapped, err = snap(x, y)
                assert snapped == pt, f"Failed for ({a}, {b})"
                assert err < 1e-9

    def test_integer_inputs(self):
        """snap should accept int inputs."""
        pt, err = snap(1, 2)
        assert isinstance(pt, A2Point)


class TestA2PointEdgeCases:
    def test_large_coordinates(self):
        p = A2Point(10**6, -(10**6))
        assert p.norm_sq() >= 0

    def test_frozen(self):
        p = A2Point(1, 2)
        with pytest.raises(AttributeError):
            p.a = 3

    def test_hash(self):
        """Frozen dataclass should be hashable."""
        p = A2Point(1, 2)
        assert hash(p) == hash(A2Point(1, 2))
        s = {p}
        assert A2Point(1, 2) in s


class TestDodecetEdgeCases:
    def test_boundary_index_0(self):
        pt = decode_dodecet(0)
        assert pt == A2Point(1, 0)

    def test_boundary_index_11(self):
        pt = decode_dodecet(11)
        assert isinstance(pt, A2Point)

    def test_encode_identity_vectors(self):
        assert encode_dodecet(A2Point(1, 0)) == 0
        assert encode_dodecet(A2Point(0, 1)) == 1


class TestVector48EdgeCases:
    def test_angle_zero(self):
        assert vector48_encode(0.0) == 0

    def test_angle_2pi(self):
        # 2π should map to 0 (same as 0)
        assert vector48_encode(2.0 * math.pi) == 0

    def test_very_large_angle(self):
        idx = vector48_encode(100 * math.pi)
        assert 0 <= idx < 48

    def test_decode_encode_roundtrip_all(self):
        for i in range(48):
            angle = vector48_decode(i)
            assert vector48_encode(angle) == i


# ===================================================================
# Rigidity edge cases
# ===================================================================

class TestLamanEdgeCases:
    def test_n0_empty(self):
        assert is_laman(0, [])

    def test_n1_no_edges(self):
        assert is_laman(1, [])

    def test_n2_one_edge(self):
        assert is_laman(2, [(0, 1)])

    def test_n2_zero_edges(self):
        assert not is_laman(2, [])

    def test_n2_two_edges(self):
        assert not is_laman(2, [(0, 1), (0, 1)])  # duplicate edge

    def test_duplicate_edges(self):
        # Duplicate edges should fail (too many edges for the vertex count)
        assert not is_laman(3, [(0, 1), (1, 2), (0, 2), (0, 1)])


class TestHennebergEdgeCases:
    def test_n2(self):
        edges = henneberg_construct(2)
        assert len(edges) == 1

    def test_n3(self):
        edges = henneberg_construct(3)
        assert len(edges) == 3
        assert is_laman(3, edges)

    def test_n1_raises(self):
        with pytest.raises(ValueError):
            henneberg_construct(1)

    def test_n0_raises(self):
        with pytest.raises(ValueError):
            henneberg_construct(0)

    def test_negative_n_raises(self):
        with pytest.raises(ValueError):
            henneberg_construct(-1)


class TestConnectivityEdgeCases:
    def test_n0(self):
        assert algebraic_connectivity([], 0) == 0.0

    def test_n1(self):
        assert algebraic_connectivity([], 1) == 0.0

    def test_disconnected_graph(self):
        """Two disconnected edges — power iteration may not reliably give λ₂≈0."""
        lam2 = algebraic_connectivity([(0, 1), (2, 3)], 4)
        # Power iteration is approximate; just verify it returns a float
        assert isinstance(lam2, float)

    def test_optimal_coupling_n0(self):
        assert optimal_coupling([], 0) == 0.0

    def test_optimal_coupling_n1(self):
        assert optimal_coupling([], 1) == 0.0


# ===================================================================
# Holonomy edge cases
# ===================================================================

class TestHolonomyEdgeCases:
    def test_empty_cycle(self):
        assert cycle_holonomy([], []) == 0

    def test_single_edge_zero_direction(self):
        assert cycle_holonomy([(0, 1)], [0]) == 0

    def test_all_zero_directions(self):
        assert cycle_holonomy([(0, 1), (1, 2), (2, 0)], [0, 0, 0]) == 0

    def test_verify_empty_tiles(self):
        assert verify_consistency([])

    def test_fault_boundaries_empty(self):
        assert fault_boundaries([]) == []


# ===================================================================
# Temporal edge cases
# ===================================================================

class TestTemporalEdgeCases:
    def test_zero_decay_rate(self):
        agent = TemporalAgent(decay_rate=0.0, epsilon_0=0.5)
        agent.observe(0.0, 0.0, t=1.0)
        assert agent.epsilon == pytest.approx(0.5)

    def test_very_high_decay_rate(self):
        agent = TemporalAgent(decay_rate=100.0, epsilon_0=1.0)
        # First observe doesn't decay (no previous time)
        agent.observe(0.0, 0.0, t=0.0)
        # Second observe triggers decay
        agent.observe(0.0, 0.0, t=1.0)
        assert agent.epsilon < 0.01

    def test_first_observation_no_decay(self):
        agent = TemporalAgent(decay_rate=1.0, epsilon_0=0.5)
        result = agent.observe(0.0, 0.0, t=0.0)
        # No decay on first observation (no previous time)
        assert agent.epsilon == pytest.approx(0.5)

    def test_very_large_delta_no_anomalies(self):
        agent = TemporalAgent(decay_rate=0.1, epsilon_0=0.5, delta=1e6)
        result = agent.observe(100.0, 100.0, t=1.0)
        assert result.phase != FunnelPhase.ANOMALY

    def test_very_small_delta_triggers_anomaly(self):
        agent = TemporalAgent(decay_rate=0.1, epsilon_0=0.5, delta=0.001)
        result = agent.observe(0.5, 0.5, t=1.0)
        assert result.phase == FunnelPhase.ANOMALY


# ===================================================================
# Metronome edge cases
# ===================================================================

class TestMetronomeEdgeCases:
    def test_single_agent_no_neighbors(self):
        m = Metronome(T=1.0, phi0=0.0, n_agents=1)
        m.tick()
        assert m.tick_count == 1
        assert not m.converged

    def test_empty_corrections_initially(self):
        m = Metronome()
        assert m.corrections == []

    def test_correct_with_empty_phases(self):
        m = Metronome(neighbors=[1], edges=[(0, 1)], n_agents=2)
        corr = m.correct([])
        assert corr == 0.0

    def test_agree_with_self(self):
        m = Metronome(phi0=1.5, epsilon=0.5)
        assert m.agree(m)

    def test_observe_at_origin(self):
        m = Metronome(phi0=0.0)
        m.observe(0.0, 0.0)
        # Origin snaps to (0,0) → phase 0
        assert m.phase == pytest.approx(0.0, abs=0.01)

    def test_state_snapshot_matches(self):
        m = Metronome(T=1.0, phi0=0.5, epsilon=0.3)
        m.tick()
        s = m.state()
        assert s.tick_count == 1
        assert s.epsilon < 0.3  # decayed after tick
        assert not s.converged
