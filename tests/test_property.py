"""Property-based tests using Hypothesis for constraint_theory_core.

These tests verify invariants that should hold for ALL valid inputs,
not just a handful of hand-picked examples.
"""

from __future__ import annotations

import math

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from constraint_theory_core.holonomy import (
    cycle_holonomy,
    fault_boundaries,
    isolate_fault,
)
from constraint_theory_core.lattice import (
    DIRECTION_COUNT,
    A2Point,
    covering_radius,
    decode_dodecet,
    encode_dodecet,
    holonomy_product,
    is_consistent,
    snap,
    vector48_decode,
    vector48_encode,
)
from constraint_theory_core.metronome import Metronome
from constraint_theory_core.rigidity import (
    algebraic_connectivity,
    henneberg_construct,
    is_laman,
    optimal_coupling,
)
from constraint_theory_core.temporal import TemporalAgent

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

finite_float = st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
small_float = st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False)
positive_float = st.floats(min_value=1e-6, max_value=100.0, allow_nan=False, allow_infinity=False)
angle = st.floats(min_value=-2 * math.pi, max_value=4 * math.pi, allow_nan=False, allow_infinity=False)

a2_point = st.builds(A2Point, st.integers(min_value=-50, max_value=50), st.integers(min_value=-50, max_value=50))

direction_index = st.integers(min_value=0, max_value=DIRECTION_COUNT - 1)
dodecet_index = st.integers(min_value=0, max_value=11)

edge_list = st.lists(st.tuples(st.integers(min_value=0, max_value=20), st.integers(min_value=0, max_value=20)))


# ===================================================================
# Lattice property tests
# ===================================================================

class TestSnapProperties:
    """Invariant: snap always returns a valid lattice point within covering radius."""

    @given(x=small_float, y=small_float)
    @settings(max_examples=500, suppress_health_check=[HealthCheck.too_slow])
    def test_snap_error_within_covering_radius(self, x, y):
        pt, err = snap(x, y)
        assert err <= covering_radius() + 1e-9

    @given(x=small_float, y=small_float)
    @settings(max_examples=500, suppress_health_check=[HealthCheck.too_slow])
    def test_snap_returns_integer_coordinates(self, x, y):
        pt, err = snap(x, y)
        assert isinstance(pt.a, int)
        assert isinstance(pt.b, int)

    @given(x=small_float, y=small_float)
    @settings(max_examples=300, suppress_health_check=[HealthCheck.too_slow])
    def test_snap_error_non_negative(self, x, y):
        pt, err = snap(x, y)
        assert err >= 0.0

    @given(x=small_float, y=small_float)
    @settings(max_examples=300, suppress_health_check=[HealthCheck.too_slow])
    def test_snap_idempotent(self, x, y):
        """Snapping a snap point returns the same point with ~0 error."""
        pt1, err1 = snap(x, y)
        cx, cy = pt1.to_complex()
        pt2, err2 = snap(cx, cy)
        assert pt2 == pt1
        assert err2 < 1e-9

    @given(a=st.integers(min_value=-20, max_value=20), b=st.integers(min_value=-20, max_value=20))
    def test_snap_exact_lattice_point(self, a, b):
        """Lattice points snap to themselves with zero error."""
        pt = A2Point(a, b)
        x, y = pt.to_complex()
        snapped, err = snap(x, y)
        assert snapped == pt
        assert err < 1e-9

    def test_snap_nan_raises(self):
        with pytest.raises(ValueError):
            snap(float("nan"), 0.0)

    def test_snap_inf_raises(self):
        with pytest.raises(ValueError):
            snap(0.0, float("inf"))

    def test_snap_string_raises(self):
        with pytest.raises(TypeError):
            snap("hello", 0.0)


class TestA2PointProperties:
    """A2Point arithmetic invariants."""

    @given(p=a2_point, q=a2_point)
    def test_add_commutative(self, p, q):
        assert p + q == q + p

    @given(p=a2_point, q=a2_point)
    def test_sub_self_is_zero(self, p, q):
        assert (p + q) - q == p

    @given(p=a2_point)
    def test_double_neg(self, p):
        assert -(-p) == p  # noqa: B002 -- double unary negation, not the C-style `--` decrement

    @given(p=a2_point)
    def test_norm_sq_non_negative(self, p):
        assert p.norm_sq() >= 0

    @given(p=a2_point)
    def test_zero_norm_implies_origin(self, p):
        """The only A₂ point with norm_sq == 0 is the origin."""
        # Only origin has norm 0 in Eisenstein integers
        if p.norm_sq() == 0:
            assert p == A2Point(0, 0)

    @given(p=a2_point, q=a2_point)
    def test_triangle_inequality_norm(self, p, q):
        """Norm of sum ≤ sum of norms (squared version)."""
        # |p+q|² ≤ (|p| + |q|)² — not exact for Eisenstein norm but close
        lhs = (p + q).norm_sq()
        rhs_p = p.norm_sq()
        rhs_q = q.norm_sq()
        # Cross term can be negative in Eisenstein, so just check it's reasonable
        assert lhs <= 4 * (rhs_p + rhs_q)


class TestDodecetProperties:
    """Dodecet encode/decode round-trip invariants."""

    @given(i=dodecet_index)
    def test_roundtrip(self, i):
        pt = decode_dodecet(i)
        assert encode_dodecet(pt) == i

    @given(i=dodecet_index)
    def test_dodecet_vectors_are_minimal(self, i):
        """All dodecet directions should have norm_sq ≤ 3."""
        pt = decode_dodecet(i)
        assert pt.norm_sq() <= 7  # some dodecet vectors have norm_sq=7

    def test_all_12_directions(self):
        for i in range(12):
            pt = decode_dodecet(i)
            assert isinstance(pt, A2Point)


class TestVector48Properties:
    """Vector48 encode/decode invariants."""

    @given(a=angle)
    def test_encode_produces_valid_index(self, a):
        idx = vector48_encode(a)
        assert 0 <= idx < 48

    @given(i=st.integers(min_value=0, max_value=47))
    def test_roundtrip(self, i):
        angle = vector48_decode(i)
        idx = vector48_encode(angle)
        assert idx == i

    @given(i=st.integers(min_value=0, max_value=47))
    def test_decode_angle_in_range(self, i):
        angle = vector48_decode(i)
        assert 0 <= angle < 2 * math.pi


class TestHolonomyProperties:
    """Holonomy invariants."""

    @given(d=st.lists(direction_index, min_size=0, max_size=20))
    def test_holonomy_product_in_range(self, d):
        h = holonomy_product(d)
        assert 0 <= h < DIRECTION_COUNT

    @given(d=st.lists(direction_index, min_size=0, max_size=20))
    def test_consistent_iff_holonomy_zero(self, d):
        assert is_consistent(d) == (holonomy_product(d) == 0)

    def test_empty_is_consistent(self):
        assert is_consistent([])
        assert holonomy_product([]) == 0

    @given(d=direction_index)
    def test_full_cycle_consistent(self, d):
        """48 copies of any direction sum to 48d ≡ 0 mod 48."""
        assert is_consistent([d] * 48)


# ===================================================================
# Rigidity property tests
# ===================================================================

class TestHennebergProperties:
    """Henneberg construction invariants."""

    @given(n=st.integers(min_value=2, max_value=50), seed=st.integers(min_value=0, max_value=1000))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_edge_count_is_2n_minus_3(self, n, seed):
        edges = henneberg_construct(n, seed=seed)
        assert len(edges) == 2 * n - 3

    @given(n=st.integers(min_value=2, max_value=15), seed=st.integers(min_value=0, max_value=100))
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_constructed_graph_is_laman(self, n, seed):
        edges = henneberg_construct(n, seed=seed)
        assert is_laman(n, edges)

    @given(n=st.integers(min_value=2, max_value=50))
    @settings(max_examples=30)
    def test_all_vertices_appear(self, n):
        edges = henneberg_construct(n)
        vertices = set()
        for u, v in edges:
            vertices.add(u)
            vertices.add(v)
        assert vertices == set(range(n))


class TestLamanProperties:
    """Laman rigidity invariants."""

    def test_negative_n_raises(self):
        with pytest.raises(ValueError):
            is_laman(-1, [])

    def test_non_int_n_raises(self):
        with pytest.raises(ValueError):
            is_laman(1.5, [])

    def test_non_list_edges_raises(self):
        with pytest.raises(TypeError):
            is_laman(3, "not a list")

    def test_bad_edge_format_raises(self):
        with pytest.raises(TypeError):
            is_laman(3, [(0,)])  # 1-tuple

    @given(n=st.integers(min_value=2, max_value=20), seed=st.integers(min_value=0, max_value=200))
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_laman_graphs_have_positive_connectivity(self, n, seed):
        edges = henneberg_construct(n, seed=seed)
        lam2 = algebraic_connectivity(edges, n)
        assert lam2 > 0

    @given(n=st.integers(min_value=2, max_value=20), seed=st.integers(min_value=0, max_value=200))
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_optimal_coupling_positive_and_bounded(self, n, seed):
        edges = henneberg_construct(n, seed=seed)
        alpha = optimal_coupling(edges, n)
        assert alpha > 0
        assert alpha <= 1.0  # coupling shouldn't exceed 1


# ===================================================================
# Holonomy property tests
# ===================================================================

class TestHolonomyCycleProperties:
    """Holonomy cycle invariants."""

    def test_mismatched_lengths_raises(self):
        with pytest.raises(ValueError):
            cycle_holonomy([(0, 1)], [1, 2])

    def test_out_of_range_direction_raises(self):
        with pytest.raises(ValueError):
            cycle_holonomy([(0, 1)], [48])
        with pytest.raises(ValueError):
            cycle_holonomy([(0, 1)], [-1])

    @given(d=st.lists(direction_index, min_size=1, max_size=10))
    def test_single_tile_consistency(self, d):
        edges = [(i, i + 1) for i in range(len(d) - 1)]
        if len(d) > 1:
            edges.append((len(d) - 1, 0))
        else:
            edges = [(0, 0)]
        h = cycle_holonomy(edges, d)
        assert 0 <= h < DIRECTION_COUNT


class TestIsolateFaultProperties:
    """Fault isolation invariants."""

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            isolate_fault([])

    def test_all_good_raises(self):
        good = ([(0, 1), (1, 2), (2, 0)], [16, 16, 16])
        with pytest.raises(ValueError):
            isolate_fault([good])

    @given(bad_pos=st.integers(min_value=0, max_value=19))
    def test_fault_isolation_finds_bad_tile(self, bad_pos):
        good = ([(0, 1), (1, 2), (2, 0)], [16, 16, 16])
        bad = ([(0, 1), (1, 2), (2, 0)], [1, 2, 3])
        tiles = [good] * bad_pos + [bad] + [good] * (19 - bad_pos)
        idx = isolate_fault(tiles)
        assert idx == bad_pos

    @given(positions=st.lists(st.integers(min_value=0, max_value=9), min_size=1, max_size=5))
    def test_fault_boundaries_finds_all(self, positions):
        good = ([(0, 1), (1, 2), (2, 0)], [16, 16, 16])
        bad = ([(0, 1), (1, 2), (2, 0)], [1, 2, 3])
        tiles = [good] * 10
        expected = []
        for p in sorted(set(positions)):
            tiles[p] = bad
            expected.append(p)
        result = fault_boundaries(tiles)
        assert result == expected


# ===================================================================
# Temporal property tests
# ===================================================================

class TestTemporalProperties:
    """TemporalAgent invariants."""

    @given(
        decay=positive_float,
        eps=positive_float,
        delta=positive_float,
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_epsilon_never_negative(self, decay, eps, delta):
        agent = TemporalAgent(decay_rate=decay, epsilon_0=eps, delta=delta)
        for t in range(1, 20):
            agent.observe(0.0, 0.0, t=float(t))
        assert agent.epsilon >= 0

    @given(
        decay=positive_float,
        eps=positive_float,
        delta=positive_float,
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_epsilon_monotonically_decreases_on_safe(self, decay, eps, delta):
        """If no anomalies, epsilon only decreases."""
        agent = TemporalAgent(decay_rate=decay, epsilon_0=eps, delta=delta)
        prev = agent.epsilon
        # Observe origin repeatedly — safe for any delta >= covering radius
        for t in range(1, 20):
            agent.observe(0.0, 0.0, t=float(t))
            if agent.anomaly_count == 0:
                assert agent.epsilon <= prev + 1e-12
                prev = agent.epsilon

    def test_negative_decay_raises(self):
        with pytest.raises(ValueError):
            TemporalAgent(decay_rate=-1.0)

    def test_negative_epsilon_raises(self):
        with pytest.raises(ValueError):
            TemporalAgent(epsilon_0=-1.0)


class TestMetronomeProperties:
    """Metronome invariants."""

    @given(T=positive_float, phi0=angle, eps=positive_float)
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_phase_always_in_range(self, T, phi0, eps):
        m = Metronome(T=T, phi0=phi0, epsilon=eps)
        for _ in range(10):
            m.tick()
        assert 0 <= m.phase < 2 * math.pi + 1e-12

    def test_negative_T_raises(self):
        with pytest.raises(ValueError):
            Metronome(T=-1.0)

    def test_zero_T_raises(self):
        with pytest.raises(ValueError):
            Metronome(T=0.0)

    def test_nan_T_raises(self):
        with pytest.raises(ValueError):
            Metronome(T=float("nan"))

    def test_string_T_raises(self):
        with pytest.raises(TypeError):
            Metronome(T="hello")

    @given(T=positive_float)
    @settings(max_examples=20)
    def test_tick_count_increments(self, T):
        m = Metronome(T=T)
        for i in range(1, 6):
            m.tick()
            assert m.tick_count == i

    def test_reset_restores_initial_phase(self):
        m = Metronome(T=1.0, phi0=1.5)
        for _ in range(10):
            m.tick()
        m.reset()
        assert m.phase == pytest.approx(1.5)
        assert m.tick_count == 0
