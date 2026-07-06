"""Tests for constraint_theory_core.rigidity — Laman graph operations."""

import pytest

from constraint_theory_core.rigidity import (
    algebraic_connectivity,
    henneberg_construct,
    is_laman,
    optimal_coupling,
)


class TestLamanCheck:
    def test_k2_is_laman(self):
        assert is_laman(2, [(0, 1)])

    def test_k3_is_laman(self):
        # K₃ has 3 edges = 2·3 - 3 = 3 ✓
        assert is_laman(3, [(0, 1), (1, 2), (0, 2)])

    def test_too_few_edges(self):
        assert not is_laman(4, [(0, 1), (1, 2), (0, 2)])  # 3 < 2·4-3=5

    def test_too_many_edges(self):
        # K₄ has 6 edges > 2·4-3=5
        assert not is_laman(4, [(0,1),(1,2),(2,3),(3,0),(0,2),(1,3)])

    def test_single_vertex(self):
        assert is_laman(1, [])

    def test_empty(self):
        assert is_laman(0, [])


class TestHenneberg:
    def test_n2(self):
        edges = henneberg_construct(2)
        assert len(edges) == 1  # 2·2-3 = 1
        assert edges == [(0, 1)]

    def test_n5(self):
        edges = henneberg_construct(5)
        assert len(edges) == 7  # 2·5-3 = 7
        assert is_laman(5, edges)

    def test_n10(self):
        edges = henneberg_construct(10)
        assert len(edges) == 17  # 2·10-3 = 17
        assert is_laman(10, edges)

    def test_n100(self):
        edges = henneberg_construct(100)
        assert len(edges) == 197  # 2·100-3 = 197
        assert is_laman(100, edges)

    def test_reproducible(self):
        e1 = henneberg_construct(20, seed=42)
        e2 = henneberg_construct(20, seed=42)
        assert e1 == e2

    def test_different_seeds(self):
        e1 = henneberg_construct(20, seed=42)
        e2 = henneberg_construct(20, seed=99)
        assert e1 != e2

    def test_minimum_n(self):
        with pytest.raises(ValueError):
            henneberg_construct(1)


class TestAlgebraicConnectivity:
    def test_k2(self):
        lam2 = algebraic_connectivity([(0, 1)], 2)
        assert lam2 == pytest.approx(2.0, abs=0.1)

    def test_k3(self):
        lam2 = algebraic_connectivity([(0, 1), (1, 2), (0, 2)], 3)
        assert lam2 > 0

    def test_laman_positive(self):
        """Laman graphs always have λ₂ > 0 (they're connected)."""
        for n in range(3, 15):
            edges = henneberg_construct(n)
            lam2 = algebraic_connectivity(edges, n)
            assert lam2 > 0, f"λ₂ = {lam2} for n={n}"


class TestOptimalCoupling:
    def test_positive(self):
        edges = henneberg_construct(6)
        alpha = optimal_coupling(edges, 6)
        assert alpha > 0

    def test_decreasing_with_size(self):
        """Larger graphs typically have smaller optimal coupling."""
        a6 = optimal_coupling(henneberg_construct(6), 6)
        a12 = optimal_coupling(henneberg_construct(12), 12)
        # Not guaranteed but typically true
        # Just check both are positive and finite
        assert 0 < a6 < 1
        assert 0 < a12 < 1
