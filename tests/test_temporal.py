"""Tests for constraint_theory_core.temporal — deadband funnel."""

import math
import pytest
from constraint_theory_core.temporal import TemporalAgent, FunnelPhase


class TestTemporalAgent:
    def test_initial_epsilon(self):
        agent = TemporalAgent(decay_rate=0.1, epsilon_0=0.5)
        assert agent.epsilon == pytest.approx(0.5)

    def test_decay_on_observe(self):
        agent = TemporalAgent(decay_rate=1.0, epsilon_0=0.5)
        agent._last_t = 0.0  # seed previous time so decay kicks in
        agent.observe(0.0, 0.0, t=1.0)
        assert agent.epsilon < 0.5  # decayed

    def test_anomaly_resets(self):
        agent = TemporalAgent(decay_rate=0.0, epsilon_0=0.01, delta=0.01)
        # Snap error will be ~0.5 for point far from lattice — anomaly
        result = agent.observe(10.0, 10.0, t=1.0)
        assert result.phase == FunnelPhase.ANOMALY
        assert agent.anomaly_count == 1

    def test_narrowing_when_safe(self):
        agent = TemporalAgent(decay_rate=0.01, epsilon_0=0.6, delta=1.0)
        # Snap to origin — error ≈ 0, well within deadband
        result = agent.observe(0.01, 0.01, t=1.0)
        assert result.phase == FunnelPhase.NARROWING

    def test_manual_decay(self):
        agent = TemporalAgent(decay_rate=1.0, epsilon_0=1.0)
        agent.decay(1.0)
        assert agent.epsilon == pytest.approx(math.exp(-1.0))

    def test_manual_reset(self):
        agent = TemporalAgent(decay_rate=1.0, epsilon_0=1.0)
        agent.decay(5.0)
        assert agent.epsilon < 0.01
        agent.reset(0, 0)
        assert agent.epsilon == 1.0

    def test_convergence_over_time(self):
        """Deadband should narrow with repeated safe observations."""
        agent = TemporalAgent(decay_rate=0.5, epsilon_0=0.5)
        for t in range(1, 100):
            agent.observe(0.0, 0.0, t=float(t))
        assert agent.epsilon < 0.01
